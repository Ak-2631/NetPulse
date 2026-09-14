from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime, timedelta
from app.core.database import get_db
from app.models import models

router = APIRouter()

@router.get("/health-score")
def get_health_score(db: Session = Depends(get_db)):
    """Calculate a 0-100 Network Health Score."""
    # Based on devices online, recent latency, recent packet loss, and active alerts
    devices = db.query(models.Device).all()
    if not devices:
        return {"score": 100, "status": "No devices to monitor"}
    
    total_devices = len(devices)
    online_devices = sum(1 for d in devices if d.status == "ONLINE")
    availability_score = (online_devices / total_devices) * 100

    # Recent metrics (last 5 minutes)
    five_mins_ago = datetime.utcnow() - timedelta(minutes=5)
    recent_metrics = db.query(models.NetworkMetric).filter(models.NetworkMetric.timestamp >= five_mins_ago).all()
    
    avg_latency = 0
    avg_loss = 0
    if recent_metrics:
        latencies = [m.latency_ms for m in recent_metrics if m.latency_ms is not None]
        losses = [m.packet_loss_percent for m in recent_metrics if m.packet_loss_percent is not None]
        avg_latency = sum(latencies) / len(latencies) if latencies else 0
        avg_loss = sum(losses) / len(losses) if losses else 0
        
    # Latency penalty: -1 point for every 10ms above 50ms
    latency_penalty = max(0, (avg_latency - 50) / 10)
    
    # Loss penalty: -5 points for every 1% loss
    loss_penalty = avg_loss * 5
    
    # Active alerts penalty: -10 for CRITICAL, -5 for WARNING
    active_alerts = db.query(models.Alert).filter(models.Alert.resolved == False).all()
    alerts_penalty = sum(10 if a.severity == "CRITICAL" else 5 for a in active_alerts)
    
    final_score = availability_score - latency_penalty - loss_penalty - alerts_penalty
    final_score = max(0, min(100, final_score)) # Clamp between 0 and 100
    
    return {
        "score": round(final_score),
        "availability": f"{(online_devices/total_devices)*100:.1f}%",
        "avg_latency_ms": round(avg_latency, 2),
        "avg_packet_loss": round(avg_loss, 2),
        "active_alerts": len(active_alerts)
    }

@router.get("/{device_id}")
def get_device_metrics(device_id: int, hours: int = 1, db: Session = Depends(get_db)):
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    metrics = db.query(models.NetworkMetric).filter(
        models.NetworkMetric.device_id == device_id,
        models.NetworkMetric.timestamp >= cutoff
    ).order_by(models.NetworkMetric.timestamp.asc()).all()
    
    return [
        {
            "timestamp": m.timestamp,
            "latency_ms": m.latency_ms,
            "packet_loss_percent": m.packet_loss_percent,
            "status": m.status
        } for m in metrics
    ]
