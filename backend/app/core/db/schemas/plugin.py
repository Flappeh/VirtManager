import uuid

from sqlmodel import Field,  SQLModel

# Shared properties
class PluginBase(SQLModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=500)
    version: str 
    schema: str = Field(default="")
    enabled: bool
    
# Properties to return via API, id is always required
class PluginPublic(PluginBase):
    id: uuid.UUID


class PluginsPublic(SQLModel):
    data: list[PluginPublic]
    count: int

class PluginMeta(SQLModel):
    name: str
    version: str
    description: str
    db_schema: str
    
class PluginDiscover(SQLModel):
    name: str
    path: str
    meta: PluginMeta
    
class PluginSync(SQLModel):
    count: int
    status: str
    
class PluginDownload(SQLModel):
    id: str
    name: str
    version: str
    download_url: str
    archive_url: str
    archive_type: str