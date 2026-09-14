from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app.models import models
from app.schemas.schemas import SystemInfo
from app.services.system_info import get_system_network_info
from app.api import devices, metrics, traffic, packets, alerts, reports, topology
from app.services.monitoring import start_monitoring
from app.services.alert_engine import start_alert_engine

from app.core.websocket import manager
import asyncio
from fastapi import WebSocket, WebSocketDisconnect

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="NetPulse API", description="Smart Network Monitoring & Analytics Platform API")

async def broadcast_live_data():
    while True:
        try:
            # We could fetch latest metrics, traffic, and alerts to broadcast
            # For simplicity, we just send a ping to keep WS alive and indicate LIVE state
            await manager.broadcast({"type": "ping", "status": "LIVE"})
        except Exception:
            pass
        await asyncio.sleep(2)

@app.on_event("startup")
async def on_startup():
    start_monitoring()
    start_alert_engine()
    asyncio.create_task(broadcast_live_data())

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection open
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development, allow all. In production, specify React app URL.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(devices.router, prefix="/api/devices", tags=["devices"])
app.include_router(metrics.router, prefix="/api/metrics", tags=["metrics"])
app.include_router(traffic.router, prefix="/api/traffic", tags=["traffic"])
app.include_router(packets.router, prefix="/api/packets", tags=["packets"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])
app.include_router(topology.router, prefix="/api/topology", tags=["topology"])

@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "NetPulse backend is running."}

@app.get("/api/system", response_model=SystemInfo)
def system_info():
    return get_system_network_info()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
