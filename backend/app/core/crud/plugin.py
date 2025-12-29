import uuid
from typing import Any, List, Dict

from sqlmodel import Session, select, delete
from app.core.db.schemas.plugin import PluginDiscover, PluginMeta
from app.core.db.models.plugin import Plugin
from app.core.plugins.discovery import discover_plugins


def list_downloaded() -> List[PluginDiscover]:
    discovered = discover_plugins()
    plugins : List[PluginDiscover] = []
    for key in discovered:
        meta = discovered[key]['meta']
        plugin_meta = PluginMeta(
            name=meta["name"],
            version=meta["version"],
            description=meta["description"],
            db_schema=meta["schema"]
        )
        data = PluginDiscover(
            name=meta["name"],
            path=discovered[key]['path'].as_uri(),
            meta=plugin_meta
        )
        plugins.append(data)
    
    return plugins

def synchronize_plugins(*, session: Session) -> int:
    
    discovered_plugins: Dict[str, dict] = discover_plugins()
    if not discovered_plugins:
        return 0
    stmt = select(Plugin)
    stored_plugins = session.exec(stmt).all()
    stored_by_name = {p.name: p for p in stored_plugins}

    changed = 0

    for name, info in discovered_plugins.items():
        meta = info["meta"]
        disk_name = meta["name"]
        disk_version = meta.get("version")
        disk_description = meta.get("description")

        # Sanity: enforce consistent naming
        if disk_name != name:
            # You can choose to raise instead of silently skipping
            raise ValueError(f"Descriptor name '{disk_name}' does not match directory key '{name}'")

        existing = stored_by_name.get(disk_name)

        if existing is None:
            # Insert new plugin, disabled by default
            plugin = Plugin(
                name=disk_name,
                description=disk_description,
                version=disk_version,
                enabled=False,
            )
            session.add(plugin)
            changed += 1 
        else:
            # Update metadata if changed; preserve enabled flag
            updated = False

            if existing.version != disk_version:
                existing.version = disk_version
                updated = True

            if existing.description != disk_description:
                existing.description = disk_description
                updated = True

            if updated:
                changed += 1 

    if changed > 0:
        session.commit()

    return changed

def get_plugin_by_name(session: Session, name: str) -> Plugin | None:
    stmt = select(Plugin).where(Plugin.name == name)
    return session.exec(stmt).first()

def set_plugin_enabled(session: Session, name: str, enabled: bool) -> tuple[bool, Plugin]:
    plugin = get_plugin_by_name(session, name)
    if plugin is None:
        raise ValueError(f"Plugin '{name}' not found in DB")

    plugin.enabled = enabled
    session.add(plugin)
    session.commit()
    session.refresh(plugin)
    return enabled, plugin 

def delete_plugin(session: Session, name: str) -> Plugin | None:
    stmt = delete(Plugin).where(Plugin.name == name)
    session.exec(stmt)
    session.commit()
    return True

# def enable_plugin(*, session: Session, plugin_name: str) -> bool | None:
#     plugins = discover_plugins()

#     if plugin_name not in plugins:
#         raise Exception("Plugin not found on disk")

#     meta = plugins[plugin_name]["meta"]
    
#     upsert Plugin(
#         name=name,
#         version=meta["version"],
#         description=meta.get("description"),
#         enabled=True,
#     )
