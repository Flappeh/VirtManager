# app/plugins/vsphere/db/models/vcenter.py
import uuid
from typing import List, Optional
from sqlmodel import Field, Relationship

from app.plugins.vsphere.db.base import VSphereBase  # Has schema="vsphere" + metadata

import uuid


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
