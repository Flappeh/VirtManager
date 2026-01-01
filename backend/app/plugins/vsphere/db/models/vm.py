# app/plugins/vsphere/db/models/vcenter.py
import uuid
from typing import List, Optional
from pydantic import EmailStr
from sqlmodel import Field, Relationship
from app.plugins.vsphere.db.models import VCenter
from app.plugins.vsphere.db.base import VSphereBase  # Has schema="vsphere" + metadata

import uuid

from pydantic import EmailStr

class VMBase(VSphereBase):
    vm: str = Field()
    name: str = Field()
    power_state: str = Field()
    cpu_count: int = Field()
    memory_size: int = Field()
    
class VM(VMBase, table=True):
    __tablename__ = "vcenter_vm"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="vsphere.vcenter.id", nullable=False, ondelete="CASCADE"
    )
    owner: VCenter | None = Relationship(back_populates="vms")
