from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import models
from app.services.system_info import get_system_network_info

router = APIRouter()

@router.get("/")
def get_topology(db: Session = Depends(get_db)):
    """Returns inferred logical topology data for React Flow."""
    sys_info = get_system_network_info()
    gateway_ip = sys_info.get("default_gateway", "Unknown")
    
    nodes = []
    edges = []
    
    # Add Gateway node
    nodes.append({
        "id": "gateway",
        "type": "default",
        "data": {"label": f"Gateway\n{gateway_ip}"},
        "position": {"x": 400, "y": 50},
        "style": {"background": "#e2e8f0", "color": "#000", "border": "2px solid #64748b", "borderRadius": "50%"}
    })
    
    # Add Monitoring Host node
    host_ip = sys_info.get("local_ip", "Unknown")
    nodes.append({
        "id": "monitoring_host",
        "type": "default",
        "data": {"label": f"NetPulse Server\n{host_ip}"},
        "position": {"x": 200, "y": 150},
        "style": {"background": "#bfdbfe", "color": "#000", "border": "2px solid #3b82f6"}
    })
    
    edges.append({"id": "e-gateway-host", "source": "gateway", "target": "monitoring_host", "animated": True})
    
    devices = db.query(models.Device).all()
    
    x_pos = 100
    y_pos = 250
    
    for i, dev in enumerate(devices):
        if dev.ip_address == host_ip or dev.ip_address == gateway_ip:
            continue # Already added
            
        color = "#bbf7d0" if dev.status == "ONLINE" else "#fecaca"
        border = "#22c55e" if dev.status == "ONLINE" else "#ef4444"
        
        node_id = f"dev_{dev.id}"
        nodes.append({
            "id": node_id,
            "data": {"label": f"{dev.hostname or 'Device'}\n{dev.ip_address}"},
            "position": {"x": x_pos + (i % 4) * 150, "y": y_pos + (i // 4) * 100},
            "style": {"background": color, "color": "#000", "border": f"2px solid {border}"}
        })
        
        # Inferred connection to gateway
        edges.append({"id": f"e-gateway-{node_id}", "source": "gateway", "target": node_id})

    return {
        "nodes": nodes,
        "edges": edges,
        "note": "This is an inferred logical topology based on discovered devices, not physical cabling."
    }
