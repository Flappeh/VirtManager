# app/plugins/vsphere/api/router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from app.api.deps.db import get_core_db  # Core session dependency
from app.plugins.vsphere.db.models.vcenter import (
    VCenter, VCenterCreate, VCenterRegister, 
    VCenterDatacenter, VCenterCluster, # etc.
)

router = APIRouter()

@router.get("/vcenters", response_model=List[dict])
def list_vcenters(session: Session = Depends(get_core_db)):
    """List all vCenter connections."""
    vcenters = session.exec(select(VCenter)).all()
    return [vc.dict() for vc in vcenters]

@router.post("/vcenters", status_code=201)
def create_vcenter(vcenter_in: VCenterCreate, session: Session = Depends(get_core_db)):
    """Register new vCenter connection."""
    # TODO: hash password
    hashed_password = vcenter_in.password  # Replace with proper hashing
    db_vcenter = VCenter(**vcenter_in.dict(), hashed_password=hashed_password)
    session.add(db_vcenter)
    session.commit()
    session.refresh(db_vcenter)
    return db_vcenter

@router.get("/vcenters/{vcenter_id}/inventory")
def get_vcenter_inventory(vcenter_id: uuid.UUID, session: Session = Depends(get_core_db)):
    """Get full inventory for vCenter (datacenters, clusters, VMs, etc.)."""
    vcenter = session.get(VCenter, vcenter_id)
    if not vcenter:
        raise HTTPException(status_code=404, detail="vCenter not found")
    
    return {
        "vcenter": vcenter.dict(),
        "datacenters": [dc.dict() for dc in vcenter.datacenters],
        "clusters": [c.dict() for c in vcenter.clusters],
        "datastores": [ds.dict() for ds in vcenter.datastores],
        "hosts": [h.dict() for h in vcenter.hosts],
        "networks": [n.dict() for n in vcenter.networks],
        "vms": [vm.dict() for vm in vcenter.vms],
    }
