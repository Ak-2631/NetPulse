from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import models

router = APIRouter()

@router.get("/")
def get_alerts(status: str = "all", db: Session = Depends(get_db)):
    query = db.query(models.Alert).order_by(models.Alert.timestamp.desc())
    
    if status == "unacknowledged":
        query = query.filter(models.Alert.acknowledged == False)
    elif status == "active":
        query = query.filter(models.Alert.resolved == False)
        
    alerts = query.limit(100).all()
    
    result = []
    for a in alerts:
        # Join device info manually or let Pydantic handle it.
        device = db.query(models.Device).filter(models.Device.id == a.device_id).first()
        dev_ip = device.ip_address if device else "System"
        
        result.append({
            "id": a.id,
            "timestamp": a.timestamp,
            "device": dev_ip,
            "alert_type": a.alert_type,
            "severity": a.severity,
            "message": a.message,
            "acknowledged": a.acknowledged,
            "resolved": a.resolved
        })
    return result

@router.patch("/{alert_id}/acknowledge")
def acknowledge_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.acknowledged = True
    db.commit()
    return {"message": "Alert acknowledged"}

@router.delete("/clear")
def clear_resolved_alerts(db: Session = Depends(get_db)):
    # Clear only resolved alerts to keep history clean if requested
    db.query(models.Alert).filter(models.Alert.resolved == True).delete()
    db.commit()
    return {"message": "Resolved alerts cleared."}
