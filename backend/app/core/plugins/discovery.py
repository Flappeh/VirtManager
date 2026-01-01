import json
from pathlib import Path
from sqlalchemy import MetaData
from typing import List
import importlib
import sys

PLUGIN_DIR = Path(__file__).resolve().parents[2] / "plugins"

def discover_plugins():
    plugins = {}

    for path in PLUGIN_DIR.iterdir():
        if not path.is_dir():
            continue

        descriptor = path / "plugin.json"
        if not descriptor.exists():
            continue

        data = json.loads(descriptor.read_text())
        plugins[data["name"]] = {
            "path": path,
            "meta": data,
        }
    return plugins

# from app.core.plugins.discovery import discover_plugin_metadata
# mds = discover_plugin_metadata()
# print(mds)

def discover_plugin_metadata() -> List[tuple[MetaData, str]]:
    result = []
    discovered = discover_plugins()
    for name, info in discovered.items():
        schema = info["meta"]["schema"]
        base_file = Path(info["path"]) / "db" / "base.py"
        print(base_file)
        if not base_file.exists():
            continue
            
        spec = importlib.util.spec_from_file_location(f"app.plugins.{name}.db.base", base_file)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        
        # FIXED: Try ALL possible names from your debug output
        possible_names = [f"{name}_metadata", "metadata","PluginBase", "Base"]
        
        for attr_name in possible_names:
            if hasattr(module, attr_name):
                obj = getattr(module, attr_name)
                # Direct MetaData
                if isinstance(obj, MetaData):
                    if obj.tables:
                        result.append((obj, schema))
                        break
                
                # SQLModel class with metadata
                if hasattr(obj, 'metadata') and isinstance(obj.metadata, MetaData):
                    if obj.metadata.tables:
                        result.append((obj.metadata, schema))
                        break
    
    return result