from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class DeviceBase(BaseModel):
    ip_address: str
    mac_address: Optional[str] = None
    hostname: Optional[str] = None
    status: str

class DeviceCreate(DeviceBase):
    pass

class DeviceResponse(DeviceBase):
    id: int
    first_seen: datetime
    last_seen: datetime
    
    class Config:
        from_attributes = True

class SystemInfo(BaseModel):
    hostname: str
    local_ip: str
    mac_address: str
    active_interface: str
    subnet: str
    default_gateway: str
    pcap_available: bool
