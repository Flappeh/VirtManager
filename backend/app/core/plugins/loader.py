# app/core/plugins/loader.py
"""
Plugin loader: imports ONLY enabled plugins from DB.
Fail-fast validation, no hot-loading, restart required.
"""
import ast
import importlib
import sys
from typing import List
from pathlib import Path

from sqlalchemy import MetaData
from sqlmodel import Session, select

from app.core.init_db import engine
from app.core.db.models.plugin import Plugin
from app.core.plugins.discovery import discover_plugins


class PluginLoadError(Exception):
    """Raised when plugin fails validation or import."""


def validate_plugin_syntax(plugin_path: Path) -> None:
    """Syntax-check plugin.py without executing."""
    plugin_file = plugin_path / "plugin.py"
    if not plugin_file.exists():
        raise PluginLoadError(f"{plugin_path.name}: missing plugin.py")
    
    try:
        with open(plugin_file, "r", encoding="utf-8") as f:
            ast.parse(f.read())
    except SyntaxError as e:
        raise PluginLoadError(f"{plugin_path.name}: syntax error: {e}") from e


def validate_plugin_contract(plugin_instance: object, name: str) -> None:
    """Enforce plugin contract: register_metadata() + register_routers()."""
    if not hasattr(plugin_instance, "register_metadata"):
        raise PluginLoadError(
            f"{name}: missing register_metadata() method returning List[MetaData]"
        )
    
    if not hasattr(plugin_instance, "register_routers"):
        raise PluginLoadError(
            f"{name}: missing register_routers() method returning List[APIRouter]"
        )
    
    # Quick sanity check on return types (don't execute fully)
    metadata = plugin_instance.register_metadata()
    if not isinstance(metadata, list):
        raise PluginLoadError(f"{name}: register_metadata() must return List[MetaData]")
    
    routers = plugin_instance.register_routers()
    if not isinstance(routers, list):
        raise PluginLoadError(f"{name}: register_routers() must return List[APIRouter]")


def load_enabled_plugins() -> List:
    """
    Load ONLY enabled plugins from DB → disk → Python modules.
    
    Fail-fast on ANY error. No partial loading.
    
    Returns: List of plugin instances with .register_metadata() and .register_routers()
    """
    with Session(engine) as session:
        # Query enabled plugins from DB
        stmt = select(Plugin).where(Plugin.enabled == True)
        enabled_plugins = session.exec(stmt).all()
        
        print(enabled_plugins)
        if not enabled_plugins:
            return []
        
        # Cross-check against disk
        discovered = discover_plugins()
        loaded_plugins = []
        
        for plugin_record in enabled_plugins:
            name = plugin_record.name
            
            # 1. Must exist on disk
            if name not in discovered:
                raise PluginLoadError(
                    f"{name}: enabled in DB but missing from disk. Run /plugins/sync first."
                )
            
            plugin_path = discovered[name]["path"]
            
            # 2. Syntax validation (no execution)
            validate_plugin_syntax(plugin_path)
            
            # 3. Import module
            try:
                module = importlib.import_module(f"app.plugins.{name}.plugin")
            except ImportError as e:
                raise PluginLoadError(f"{name}: import failed: {e}") from e
            
            # 4. Enforce contract
            if not hasattr(module, "plugin"):
                raise PluginLoadError(f"{name}: missing 'plugin = PluginClass()' export")
            
            plugin_instance = module.plugin
            validate_plugin_contract(plugin_instance, name)
            
            loaded_plugins.append(plugin_instance)
        
        return loaded_plugins


def get_plugin_metadata(plugins: List) -> List[MetaData]:
    """Extract all metadata from loaded plugins."""
    metadata_list = []
    for plugin in plugins:
        metadata_list.extend(plugin.register_metadata())
    return metadata_list


def get_plugin_routers(plugins: List) -> List:
    """Extract all routers from loaded plugins."""
    routers_list = []
    for plugin in plugins:
        routers_list.extend(plugin.register_routers())
    return routers_list
