from sqlmodel import SQLModel
from sqlalchemy import MetaData

class Base(SQLModel):
    pass

_core_metadata: list[MetaData] = []
_plugins_metadata: list[MetaData] = []

def register_metadata(metadata: MetaData):
    _core_metadata.append(metadata)

def get_core_metadata() -> MetaData:
    from app.core.db.models import user, item, plugin
    combined = MetaData()
    for md in _core_metadata:
        for table in md.tables.values():
            table.to_metadata(combined)
    return combined


def get_plugins_metadata() -> MetaData:
    combined = MetaData()
    try:
        from app.core.plugins.discovery import discover_plugin_metadata
        plugin_mds = discover_plugin_metadata()  # Returns [(metadata, schema), ...]
        
        for metadata, schema in plugin_mds:
            # print(metadata, name)
            for table_name, table in metadata.tables.items():
                if table.schema == schema:  # DYNAMIC schema filter
                    table.tometadata(combined)
    except Exception as e:
        print(f"Plugin discovery failed: {e}")
    
    return combined
    
def get_combined_metadata() -> MetaData:
    combined = MetaData()
    for md in _core_metadata:
        for table in md.tables.values():
            table.to_metadata(combined)
    try:
        from app.core.plugins.discovery import discover_plugin_metadata
        plugin_mds = discover_plugin_metadata()  # Returns [(metadata, schema), ...]
        
        for metadata, schema in plugin_mds:
            # print(metadata, name)
            for table_name, table in metadata.tables.items():
                if table.schema == schema:  # DYNAMIC schema filter
                    table.tometadata(combined)
    except ImportError:
        print("No plugin metadata discovery yet")
    except Exception as e:
        print(f"Plugin discovery failed: {e}")
    return combined

register_metadata(Base.metadata)

def load_core_models() -> None:
    # Importing this module registers all core tables
    from app.core.db.models import user, item, plugin