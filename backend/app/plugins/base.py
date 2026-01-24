from sqlmodel import SQLModel

class PluginBase(SQLModel):
    __abstract__ = True