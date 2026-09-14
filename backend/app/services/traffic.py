import psutil
import time
from app.services.system_info import get_system_network_info

_last_net_io = None
_last_time = None

def get_host_traffic() -> dict:
    global _last_net_io, _last_time
    
    current_time = time.time()
    
    sys_info = get_system_network_info()
    active_interface = sys_info.get("active_interface")
    
    # We use psutil to get total host stats. 
    # The requirement says "Host/Interface Traffic", meaning the traffic of this PC, not the whole LAN.
    current_net_io = psutil.net_io_counters()
        
    bytes_sent = current_net_io.bytes_sent
    bytes_recv = current_net_io.bytes_recv
    
    upload_rate = 0.0
    download_rate = 0.0
    
    if _last_net_io is not None and _last_time is not None:
        dt = current_time - _last_time
        if dt > 0:
            upload_rate = (bytes_sent - _last_net_io.bytes_sent) / dt
            download_rate = (bytes_recv - _last_net_io.bytes_recv) / dt
            
    _last_net_io = current_net_io
    _last_time = current_time
    
    # Ensure rates are non-negative
    upload_rate = max(0.0, upload_rate)
    download_rate = max(0.0, download_rate)
    
    return {
        "interface": active_interface,
        "upload_rate_bps": upload_rate,
        "download_rate_bps": download_rate,
        "total_bytes_sent": bytes_sent,
        "total_bytes_recv": bytes_recv,
        "note": "This reflects host interface traffic, NOT total LAN bandwidth."
    }
