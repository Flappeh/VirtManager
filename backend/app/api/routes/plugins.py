import uuid
from typing import Any, List

from fastapi import APIRouter, HTTPException, BackgroundTasks
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.core.crud.plugin import (
    list_downloaded, 
    synchronize_plugins, 
    get_plugin_by_name, 
    set_plugin_enabled, 
    delete_plugin,
    download_and_extract_archive,
    ensure_plugin_schema,
    run_plugin_migrations
)
from app.core.db.models.plugin import Plugin
from app.core.db.schemas.plugin import (
    PluginPublic, 
    PluginsPublic, 
    PluginDiscover, 
    PluginSync,
    PluginDownload
    )
from app.core.db.schemas.common import Message

router = APIRouter(prefix="/plugins", tags=["plugins"])


@router.get("/discover", response_model=List[PluginDiscover])
def read_downloaded_plugins(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> List[PluginDiscover]:
    """
    Retrieve discovered plugins.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    data = list_downloaded()
    
    return data

@router.post("/sync", response_model=PluginSync)
def sync_plugins(
    session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Retrieve Plugin.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=400, detail="Not enough permissions")

    count = synchronize_plugins(session=session)
    
    if count > 0:
        return PluginSync(count=count, status=f"Updated : {count} plugins.")
    else:
        return PluginSync(count=count, status=f"Already synchronized.")
    
@router.get("/", response_model=PluginsPublic)
def read_plugins(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve Plugin.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=400, detail="Not enough permissions")

    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Plugin)
        count = session.exec(count_statement).one()
        statement = select(Plugin).offset(skip).limit(limit)
        plugins = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(Plugin)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Plugin)
            .offset(skip)
            .limit(limit)
        )
        plugins = session.exec(statement).all()

    return PluginsPublic(data=plugins, count=count)


@router.get("/{id}", response_model=PluginPublic)
def read_plugin(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get item by ID.
    """
    plugin = session.get(Plugin, id)
    if not plugin:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return plugin

@router.delete("/{name}")
def delete_plugin_by_name(name: str, session: SessionDep):
    plugin = get_plugin_by_name(session, name)
    if plugin is None:
        raise HTTPException(status_code=404, detail="Plugin not registered in DB. Run /plugins/sync first.")
    result = delete_plugin(name=name, session=session)
    
    return {"name": name, "result": result, "restart_required": True}

@router.get("/catalog")
def get_plugin_catalog():
    """Catalog specifies ZIP or TAR.GZ URL explicitly."""
    return [
        {
            "id": "vsphere",
            "name": "VMware vSphere",
            "description": "vCenter inventory + monitoring", 
            "version": "1.0.0",
            "download_url": "/api/v1/plugins/download/vsphere/1.0.0",
            "archive_url": "https://github.com/.../vsphere-1.0.0.zip",
            "archive_type": "zip",
        },
        {
            "id": "prometheus",
            "name": "Prometheus Metrics",
            "description": "Metrics collection + alerting",
            "version": "2.1.0", 
            "download_url": "/api/v1/plugins/download/prometheus/2.1.0",
            "archive_url": "https://github.com/.../prometheus-2.1.0.tar.gz",
            "archive_type": "tar.gz",
        }
    ]

@router.post("/download/{plugin_id}/{version}")
async def download_plugin(
    details: PluginDownload,
    background_tasks: BackgroundTasks,
    session: SessionDep
):
    """Download SPECIFIC archive_type → extract → sync."""
    
    catalog = get_plugin_catalog()
    plugin_info = next((p for p in catalog if p["id"] == details.id), None)
    
    if not plugin_info:
        raise HTTPException(404, f"Plugin {details.id} not in catalog")
        
    # Download + extract SPECIFIC archive
    background_tasks.add_task(
        download_and_extract_archive, 
        details,
        session
    )
    
    return {
        "status": "processing",
        "plugin_id": details.id,
        "archive_type": plugin_info["archive_type"],
        "next_step": "syncing_metadata"
    }

@router.post("/{name}/deactivate")
def deactivate_plugin(name: str, session: SessionDep):
    plugin = get_plugin_by_name(session, name)
    if plugin is None:
        raise HTTPException(status_code=404, detail="Plugin not registered in DB.")
    if not plugin.enabled:
        raise HTTPException(400, "Already inactive")

    result, plugin = set_plugin_enabled(session, name, False)
    return {"name": plugin.name, "enabled": result, "restart_required": True}

# 3. ACTIVATE (Schema + enabled)
@router.post("/{name}/activate")
def activate_plugin(name: str, session: SessionDep):
    plugin = get_plugin_by_name(session, name)
    if plugin is None:
        raise HTTPException(status_code=404, detail="Plugin not registered in DB.")
    if plugin.enabled:
        raise HTTPException(400, "Already active")
    
    ensure_plugin_schema(session, name)
    run_plugin_migrations(session, plugin)
    
    result, plugin = set_plugin_enabled(session, name, True)
    
    return {"name": plugin.name, "enabled": result, "restart_required": True}
