# app/plugins/vsphere/db/models/vcenter.py
import uuid
from typing import List, Optional
from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

from app.plugins.vsphere.db.base import VSphereBase  # Has schema="vsphere" + metadata


class VCenterBase(SQLModel):
    url: str = Field(default=None, nullable=True)
    user: str = Field(unique=True, index=True, max_length=255)
    is_active: bool = Field(default=False)

class VCenterCreate(VCenterBase):
    password: str = Field(min_length=8, max_length=128)

class VCenterRegister(SQLModel):
    url: str = Field(default=None, nullable=True)
    user: str = Field(unique=True, index=True, max_length=255)
    password: str = Field(min_length=8, max_length=128)

class VCenter(VSphereBase, table=True):  # Inherits schema="vsphere"
    __tablename__ = "vcenter"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    
    datacenters: List["VCenterDatacenter"] = Relationship(back_populates="owner", cascade_delete=True)
    clusters: List["VCenterCluster"] = Relationship(back_populates="owner", cascade_delete=True)
    datastores: List["VCenterDatastore"] = Relationship(back_populates="owner", cascade_delete=True)
    hosts: List["VCenterHost"] = Relationship(back_populates="owner", cascade_delete=True)
    networks: List["VCenterNetwork"] = Relationship(back_populates="owner", cascade_delete=True)
    vms: List["VCenterVM"] = Relationship(back_populates="owner", cascade_delete=True)

# ... rest of your models exactly the same, inheriting VSphereBase ...
class VCenterDatacenter(VSphereBase, table=True):
    __tablename__ = "vcenter_datacenter"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(foreign_key="vsphere.vcenter.id", nullable=False, ondelete="CASCADE")
    owner: Optional[VCenter] = Relationship(back_populates="datacenters")

# Apply VSphereBase to ALL models (clusters, datastores, etc.)
