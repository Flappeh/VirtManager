# app/plugins/vsphere/db/models/vcenter.py
import uuid
from typing import List, Optional
from pydantic import EmailStr
from sqlmodel import Field, Relationship
from app.plugins.vsphere.db.models import VCenter
from app.plugins.vsphere.db.base import VSphereBase  # Has schema="vsphere" + metadata

import uuid

from pydantic import EmailStr

class ClusterBase(VSphereBase):
    drs_enabled: bool = Field(default=False)
    cluster: str = Field()
    name: str = Field()
    has_enabled: bool = Field(default=False)

class Cluster(ClusterBase, table=True):
    __tablename__ = "vcenter_cluster"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="vsphere.vcenter.id", nullable=False, ondelete="CASCADE"
    )
    owner: VCenter | None = Relationship(back_populates="clusters")
