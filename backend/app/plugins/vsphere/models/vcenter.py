import uuid

from pydantic import EmailStr
from sqlmodel import Field
from app.plugins.vsphere.models.base import VSphereBase

class VCenterBase(VSphereBase):
    url: str = Field(default=None)
    user: str = Field(unique=True, index=True, max_length=255)
    is_active: bool = False

class VCenterCreate(VCenterBase):
    password: str = Field(min_length=8, max_length=128)

class VCenterRegister(VSphereBase):
    url: str = Field(default=None)
    user: str = Field(unique=True, index=True, max_length=255)
    password: str = Field(min_length=8, max_length=128)
    
class VCenter(VCenterBase, table=True):
    __tablename__ = "vcenter"
    __table_args__ = {"schema":"plugin_vsphere"}
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str