from sqlalchemy import MetaData
from fastapi import APIRouter

from app.plugins.vsphere.db.base import VSphereBase
from app.plugins.vsphere.api.router import router as vsphere_router


class VSpherePlugin:
    name = "vsphere"
    version = "1.0.0"

    def register_metadata(self) -> list[MetaData]:
        """Return plugin's database metadata."""
        return [VSphereBase.metadata]

    def register_routers(self) -> list[APIRouter]:
        """Return plugin's API routers."""
        return [vsphere_router]


plugin = VSpherePlugin()
