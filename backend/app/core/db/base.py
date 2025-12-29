from sqlmodel import SQLModel
from sqlalchemy import MetaData

class Base(SQLModel):
    pass

_core_metadata: list[MetaData] = []

def register_metadata(metadata: MetaData):
    _core_metadata.append(metadata)

def get_combined_metadata() -> MetaData:
    combined = MetaData()
    for md in _core_metadata:
        for table in md.tables.values():
            table.to_metadata(combined)
    return combined

register_metadata(Base.metadata)

def load_core_models() -> None:
    # Importing this module registers all core tables
    import app.core.db.models