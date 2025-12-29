import uuid
from typing import Any, List

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.core.crud.plugin import list_downloaded, synchronize_plugins, get_plugin_by_name, set_plugin_enabled, delete_plugin
from app.core.db.models.plugin import Plugin
from app.core.db.schemas.plugin import PluginPublic, PluginsPublic, PluginDiscover, PluginSync
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

@router.post("/{name}/enable")
def enable_plugin(name: str, session: SessionDep):
    plugin = get_plugin_by_name(session, name)
    if plugin is None:
        raise HTTPException(status_code=404, detail="Plugin not registered in DB. Run /plugins/sync first.")

    result, plugin = set_plugin_enabled(session, name, True)
    return {"name": name, "enabled": result, "restart_required": True}


@router.post("/{name}/disable")
def disable_plugin(name: str, session: SessionDep):
    plugin = get_plugin_by_name(session, name)
    if plugin is None:
        raise HTTPException(status_code=404, detail="Plugin not registered in DB.")

    result, plugin = set_plugin_enabled(session, name, False)
    return {"name": plugin.name, "enabled": result, "restart_required": True}

# @router.post("/", response_model=PluginPublic)
# def create_item(
#     *, session: SessionDep, current_user: CurrentUser, item_in: ItemCreate
# ) -> Any:
#     """
#     Create new item.
#     """
#     item = Item.model_validate(item_in, update={"owner_id": current_user.id})
#     session.add(item)
#     session.commit()
#     session.refresh(item)
#     return item


# @router.put("/{id}", response_model=ItemPublic)
# def update_item(
#     *,
#     session: SessionDep,
#     current_user: CurrentUser,
#     id: uuid.UUID,
#     item_in: ItemUpdate,
# ) -> Any:
#     """
#     Update an item.
#     """
#     item = session.get(Item, id)
#     if not item:
#         raise HTTPException(status_code=404, detail="Item not found")
#     if not current_user.is_superuser and (item.owner_id != current_user.id):
#         raise HTTPException(status_code=400, detail="Not enough permissions")
#     update_dict = item_in.model_dump(exclude_unset=True)
#     item.sqlmodel_update(update_dict)
#     session.add(item)
#     session.commit()
#     session.refresh(item)
#     return item


# @router.delete("/{id}")
# def delete_item(
#     session: SessionDep, current_user: CurrentUser, id: uuid.UUID
# ) -> Message:
#     """
#     Delete an item.
#     """
#     item = session.get(Item, id)
#     if not item:
#         raise HTTPException(status_code=404, detail="Item not found")
#     if not current_user.is_superuser and (item.owner_id != current_user.id):
#         raise HTTPException(status_code=400, detail="Not enough permissions")
#     session.delete(item)
#     session.commit()
#     return Message(message="Item deleted successfully")
