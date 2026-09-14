import time
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models import models

logger = logging.getLogger(__name__)

# Settings
ALERT_INTERVAL = 10
LATENCY_WARNING = 100
LATENCY_CRITICAL = 300
LOSS_WARNING = 5
LOSS_CRITICAL = 10

def generate_alert(db: Session, device_id: int, alert_type: str, severity: str, message: str):
    # Deduplication: Check if an unresolved alert of the same type exists for this device
    existing_alert = db.query(models.Alert).filter(
        models.Alert.device_id == device_id,
        models.Alert.alert_type == alert_type,
        models.Alert.resolved == False
    ).first()
    
    if existing_alert:
        # Avoid duplicating
        # But we could update the timestamp or message if needed
        return
        
    alert = models.Alert(
        timestamp=datetime.utcnow(),
        device_id=device_id,
        alert_type=alert_type,
        severity=severity,
        message=message,
        acknowledged=False,
        resolved=False
    )
    db.add(alert)
    logger.warning(f"ALERT [{severity}] - {message}")

def resolve_alert(db: Session, device_id: int, alert_type: str):
    active_alerts = db.query(models.Alert).filter(
        models.Alert.device_id == device_id,
        models.Alert.alert_type == alert_type,
        models.Alert.resolved == False
    ).all()
    
    for alert in active_alerts:
        alert.resolved = True
        logger.info(f"Alert resolved: {alert.alert_type} for device {device_id}")

def check_rules():
    db = SessionLocal()
    try:
        devices = db.query(models.Device).all()
        for device in devices:
            # Check DEVICE_DOWN
            if device.status == "OFFLINE":
                generate_alert(db, device.id, "DEVICE_DOWN", "CRITICAL", f"Device {device.ip_address} has become unreachable.")
            else:
                resolve_alert(db, device.id, "DEVICE_DOWN")
            
            # Get latest metric
            latest_metric = db.query(models.NetworkMetric).filter(
                models.NetworkMetric.device_id == device.id
            ).order_by(models.NetworkMetric.timestamp.desc()).first()
            
            if latest_metric:
                # Check LATENCY
                if latest_metric.latency_ms is not None:
                    if latest_metric.latency_ms > LATENCY_CRITICAL:
                        generate_alert(db, device.id, "HIGH_LATENCY", "CRITICAL", f"Device {device.ip_address} latency is critical ({latest_metric.latency_ms:.1f} ms).")
                    elif latest_metric.latency_ms > LATENCY_WARNING:
                        generate_alert(db, device.id, "HIGH_LATENCY", "WARNING", f"Device {device.ip_address} latency is high ({latest_metric.latency_ms:.1f} ms).")
                    else:
                        resolve_alert(db, device.id, "HIGH_LATENCY")
                
                # Check LOSS
                if latest_metric.packet_loss_percent is not None:
                    if latest_metric.packet_loss_percent > LOSS_CRITICAL:
                        generate_alert(db, device.id, "PACKET_LOSS", "CRITICAL", f"Device {device.ip_address} packet loss is critical ({latest_metric.packet_loss_percent}%).")
                    elif latest_metric.packet_loss_percent > LOSS_WARNING:
                        generate_alert(db, device.id, "PACKET_LOSS", "WARNING", f"Device {device.ip_address} packet loss is high ({latest_metric.packet_loss_percent}%).")
                    else:
                        resolve_alert(db, device.id, "PACKET_LOSS")

            # ANOMALY DETECTION
            # Require minimum historical baseline before calculating (e.g. 30 points = ~2.5 mins)
            recent_metrics = db.query(models.NetworkMetric).filter(
                models.NetworkMetric.device_id == device.id,
                models.NetworkMetric.latency_ms != None
            ).order_by(models.NetworkMetric.timestamp.desc()).limit(100).all()

            if len(recent_metrics) >= 30:
                latencies = [m.latency_ms for m in recent_metrics]
                avg = sum(latencies) / len(latencies)
                # Calculate standard deviation
                variance = sum((x - avg) ** 2 for x in latencies) / len(latencies)
                std_dev = variance ** 0.5
                
                if latest_metric and latest_metric.latency_ms is not None:
                    # z-score > 3 is a common anomaly threshold
                    if std_dev > 0 and (latest_metric.latency_ms - avg) / std_dev > 3 and latest_metric.latency_ms > 20:
                        generate_alert(db, device.id, "ANOMALY", "WARNING", f"Statistical anomaly detected for {device.ip_address}. Latency {latest_metric.latency_ms:.1f}ms deviates from baseline avg {avg:.1f}ms.")
                    else:
                        resolve_alert(db, device.id, "ANOMALY")
            else:
                # Insufficient data, resolve any existing anomaly alert just in case
                resolve_alert(db, device.id, "ANOMALY")

        db.commit()
    except Exception as e:
        logger.error(f"Error in alert engine: {e}")
    finally:
        db.close()

def alert_loop():
    logger.info("Starting alert engine loop...")
    while True:
        check_rules()
        time.sleep(ALERT_INTERVAL)

def start_alert_engine():
    import threading
    t = threading.Thread(target=alert_loop, daemon=True)
    t.start()
