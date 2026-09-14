from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.models import models
from app.services.packet_capture import sniffer_instance
from typing import List

router = APIRouter()

@router.post("/start")
def start_capture():
    if not sniffer_instance.is_running():
        sniffer_instance.start()
        return {"status": "started", "message": "Packet capture started (Limited to host interface traffic)."}
    return {"status": "running", "message": "Packet capture is already running."}

@router.post("/stop")
def stop_capture():
    if sniffer_instance.is_running():
        sniffer_instance.stop()
        return {"status": "stopped", "message": "Packet capture stopped."}
    return {"status": "stopped", "message": "Packet capture is not running."}

@router.get("/status")
def capture_status():
    return {"is_running": sniffer_instance.is_running()}

@router.get("/recent")
def get_recent_packets(limit: int = 100, db: Session = Depends(get_db)):
    packets = db.query(models.Packet).order_by(models.Packet.timestamp.desc()).limit(limit).all()
    return packets

@router.get("/stats")
def get_packet_stats(db: Session = Depends(get_db)):
    # Group by protocol
    stats = db.query(models.Packet.protocol, func.count(models.Packet.id)).group_by(models.Packet.protocol).all()
    total_packets = sum(count for _, count in stats)
    
    result = []
    for protocol, count in stats:
        percentage = (count / total_packets * 100) if total_packets > 0 else 0
        result.append({
            "protocol": protocol,
            "count": count,
            "percentage": round(percentage, 2)
        })
    
    return {
        "total": total_packets,
        "distribution": result
    }

@router.delete("/clear")
def clear_packets(db: Session = Depends(get_db)):
    db.query(models.Packet).delete()
    db.commit()
    return {"message": "All captured packets cleared."}
