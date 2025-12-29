import uuid

from pydantic import EmailStr
from sqlmodel import Field, Relationship
from app.core.db.base import Base

# Database model, database table inferred from class name
class User(Base, table=True):
    __tablename__ = "user"
    id: uuid.UUID = Field(
        default_factory = uuid.uuid4, 
        primary_key = True,
        index = True
    )
    email: EmailStr = Field(
        unique=True, 
        index=True, 
        max_length=255
    )
    
    hashed_password: str
    
    is_active: bool = True
    is_superuser: bool = False
    
    full_name: str | None = Field(default=None, max_length=255)
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)
