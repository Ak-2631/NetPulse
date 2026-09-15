import time
import ping3
from datetime import datetime
from sqlalchemy.orm import Session
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

from app.core.database import SessionLocal
from app.models import models

logger = logging.getLogger(__name__)

MONITOR_INTERVAL = 5 # seconds

def ping_device(device_id: int, ip: str) -> dict:
    """Ping a single device and return its metrics."""
    try:
        delay = ping3.ping(ip, timeout=2, unit='ms')
        if delay is None or delay is False:
            return {"device_id": device_id, "status": "OFFLINE", "latency": None, "loss": 100.0}
        return {"device_id": device_id, "status": "ONLINE", "latency": delay, "loss": 0.0}
    except Exception as e:
        logger.error(f"Error pinging {ip}: {e}")
        return {"device_id": device_id, "status": "OFFLINE", "latency": None, "loss": 100.0}

def monitoring_loop():
    """Continuous background loop to monitor device health."""
    logger.info("Starting monitoring loop...")
    while True:
        try:
            db = SessionLocal()
            devices = db.query(models.Device).all()
            
            if not devices:
                db.close()
                time.sleep(MONITOR_INTERVAL)
                continue

            results = []
            with ThreadPoolExecutor(max_workers=50) as executor:
                future_to_device = {executor.submit(ping_device, d.id, d.ip_address): d for d in devices}
                for future in as_completed(future_to_device):
                    results.append(future.result())

            for res in results:
                metric = models.NetworkMetric(
                    device_id=res["device_id"],
                    timestamp=datetime.utcnow(),
                    latency_ms=res["latency"],
                    packet_loss_percent=res["loss"],
                    status=res["status"]
                )
                db.add(metric)
                
                # Update device status
                device = db.query(models.Device).filter(models.Device.id == res["device_id"]).first()
                if device:
                    device.status = res["status"]
                    if res["status"] == "ONLINE":
                        device.last_seen = datetime.utcnow()
                        device.is_in_latest_scan = True
            
            db.commit()
            db.close()
            
            time.sleep(MONITOR_INTERVAL)
        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")
            time.sleep(MONITOR_INTERVAL)

def start_monitoring():
    """Start the monitoring thread."""
    import threading
    t = threading.Thread(target=monitoring_loop, daemon=True)
    t.start()
