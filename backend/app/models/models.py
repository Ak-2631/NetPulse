from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Device(Base):
    __tablename__ = "devices"
    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String, unique=True, index=True)
    mac_address = Column(String, nullable=True)
    hostname = Column(String, nullable=True)
    status = Column(String, default="OFFLINE") # ONLINE, OFFLINE
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    
    metrics = relationship("NetworkMetric", back_populates="device", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="device", cascade="all, delete-orphan")

class NetworkMetric(Base):
    __tablename__ = "network_metrics"
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    latency_ms = Column(Float, nullable=True)
    packet_loss_percent = Column(Float, nullable=True)
    status = Column(String) # ONLINE, OFFLINE
    
    device = relationship("Device", back_populates="metrics")

class Packet(Base):
    __tablename__ = "packets"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    source_ip = Column(String, index=True)
    destination_ip = Column(String, index=True)
    protocol = Column(String, index=True)
    source_port = Column(Integer, nullable=True)
    destination_port = Column(Integer, nullable=True)
    length = Column(Integer)

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=True)
    alert_type = Column(String, index=True) # DEVICE_DOWN, HIGH_LATENCY, PACKET_LOSS, ANOMALY
    severity = Column(String) # INFO, WARNING, CRITICAL
    message = Column(String)
    acknowledged = Column(Boolean, default=False)
    resolved = Column(Boolean, default=False) # For alert recovery
    
    device = relationship("Device", back_populates="alerts")

class Setting(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    value = Column(String)
