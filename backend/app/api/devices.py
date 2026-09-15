from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.core.database import get_db, SessionLocal
from app.models import models
from app.schemas import schemas
from app.services.system_info import get_system_network_info
from app.services.discovery import scan_network

router = APIRouter()

def run_background_scan(subnet: str):
    scan_result = scan_network(subnet)
    devices = scan_result["devices"]
    db = SessionLocal()
    try:
        # Mark all devices as NOT in the latest scan
        db.query(models.Device).update({models.Device.is_in_latest_scan: False})
        
        for d in devices:
            mac = d.get("mac")
            ip = d.get("ip")
            hostname = d.get("hostname")
            
            existing = None
            if mac and mac != "Unknown":
                existing = db.query(models.Device).filter(models.Device.mac_address == mac).first()
            
            if not existing:
                existing = db.query(models.Device).filter(models.Device.ip_address == ip).first()
                
            if existing:
                if existing.ip_address != ip:
                    # Prevent unique constraint failure if IP was reassigned
                    conflict = db.query(models.Device).filter(models.Device.ip_address == ip).first()
                    if conflict and conflict.id != existing.id:
                        conflict.ip_address = f"{conflict.ip_address}_stale_{conflict.id}"
                        db.flush() # Force SQL execution order to prevent UNIQUE constraint failure
                    existing.ip_address = ip
                
                if mac and mac != "Unknown":
                    existing.mac_address = mac
                if hostname and hostname != "Unknown":
                    existing.hostname = hostname
                existing.status = "ONLINE"
                existing.last_seen = datetime.utcnow()
                existing.is_in_latest_scan = True
            else:
                new_dev = models.Device(
                    ip_address=ip,
                    mac_address=mac if mac != "Unknown" else None,
                    hostname=hostname if hostname != "Unknown" else None,
                    status="ONLINE",
                    is_in_latest_scan=True
                )
                db.add(new_dev)
        db.commit()
    finally:
        db.close()

@router.post("/scan")
def trigger_scan(background_tasks: BackgroundTasks):
    sys_info = get_system_network_info()
    subnet = sys_info.get("subnet")
    interface = sys_info.get("active_interface")
    
    if not subnet or interface == "Unknown":
        raise HTTPException(
            status_code=500, 
            detail=f"Network detection failed. Cannot determine primary LAN subnet. Detected IP: {sys_info.get('local_ip')}"
        )
    
    background_tasks.add_task(run_background_scan, subnet)
    return {"message": f"Scan started on {subnet} (Interface: {interface}) in the background."}

@router.get("/", response_model=List[schemas.DeviceResponse])
def get_devices(view: str = "current", skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    query = db.query(models.Device)
    if view == "current":
        query = query.filter(models.Device.is_in_latest_scan == True)
    devices = query.offset(skip).limit(limit).all()
    return devices

@router.get("/{device_id}", response_model=schemas.DeviceResponse)
def get_device(device_id: int, db: Session = Depends(get_db)):
    device = db.query(models.Device).filter(models.Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device
