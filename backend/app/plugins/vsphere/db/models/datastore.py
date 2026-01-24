# app/plugins/vsphere/db/models/vcenter.py
import uuid
from typing import List, Optional
from pydantic import EmailStr
from sqlmodel import Field, Relationship
from app.plugins.vsphere.db.models import VCenter
from app.plugins.vsphere.db.base import VSphereBase  # Has schema="vsphere" + metadata

import uuid

from pydantic import EmailStr

class DatastoreBase(VSphereBase):
    datastore: str = Field()
    name: str = Field()
    type: str = Field()
    free_space: int = Field()
    capacity: int = Field()

class Datastore(DatastoreBase, table=True):
    __tablename__ = "vcenter_datastore"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="vsphere.vcenter.id", nullable=False, ondelete="CASCADE"
    )
    owner: VCenter | None = Relationship(back_populates="datastores")
