# PROJECT_PRESENTATION.md

## 1. Problem Statement
Network administrators and users often lack visibility into local network health, struggling to detect device outages, latency spikes, and abnormal traffic patterns without complex enterprise tools.

## 2. Proposed System
NetPulse: A lightweight, real-time network monitoring platform that provides immediate visibility into local subnet devices, health metrics, and packet-level analytics through a modern web dashboard.

## 3. System Architecture
- **Backend**: FastAPI (Python) handles background tasks (monitoring, discovery, packet capture) and exposes REST APIs and WebSockets.
- **Database**: SQLite with SQLAlchemy for persistent storage of metrics and alerts.
- **Frontend**: React (Vite) provides a responsive, interactive UI with Recharts and React Flow.

## 4. Key Modules
- **Discovery Engine**: ARP/ICMP scanning.
- **Monitoring Engine**: Continuous latency and packet loss tracking.
- **Packet Analyzer**: Scapy-based sniffer for protocol distribution.
- **Alert Engine**: Rule-based evaluation with anomaly detection (z-score on rolling latency baseline).
- **Report Generator**: Automated PDF generation using ReportLab.

## 5. Limitations
- Packet capture on switched LANs only sees traffic involving the monitoring host or broadcast traffic.
- ICMP pings may be blocked by host firewalls (e.g., Windows Defender).

## 6. Future Scope
- SNMP integration for switch port monitoring.
- Machine learning for advanced traffic classification.
- Email/SMS notification integration.
