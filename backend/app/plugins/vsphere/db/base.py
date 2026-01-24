from sqlalchemy import MetaData
# from sqlmodel import SQLModel
from app.plugins.base import PluginBase

vsphere_metadata = MetaData(schema="vsphere")

class VSphereBase(PluginBase):
    __abstract__ = True
    metadata=vsphere_metadata
    
import app.plugins.vsphere.db.models