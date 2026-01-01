# app/plugins/vsphere/db/models/vcenter.py
import uuid
from typing import List, Optional
from sqlmodel import Field, Relationship

from app.plugins.vsphere.db.base import VSphereBase  # Has schema="vsphere" + metadata
import uuid


class VCenter(VSphereBase, table=True):
    __tablename__ = "vcenter"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    datacenters: list["Datacenter"] = Relationship(back_populates="owner", cascade_delete=True)
    clusters: list["Cluster"] = Relationship(back_populates="owner", cascade_delete=True)
    datastores: list["Datastore"] = Relationship(back_populates="owner", cascade_delete=True)
    hosts: list["Host"] = Relationship(back_populates="owner", cascade_delete=True)
    networks: list["Network"] = Relationship(back_populates="owner", cascade_delete=True)
    vms: list["VM"] = Relationship(back_populates="owner", cascade_delete=True)
    url: str = Field(default=None)
    user: str = Field(unique=True, index=True, max_length=255)
    is_active: bool = False
    