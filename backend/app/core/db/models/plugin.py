import uuid
from sqlmodel import Field
from app.core.db.base import Base

class Plugin(Base, table=True):
    __tablename__ = "plugin"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(index=True, unique=True)
    description: str | None = Field(default=None, max_length=500)
    version: str
    enabled: bool = False
