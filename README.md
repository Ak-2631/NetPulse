# NETPULSE - Smart Network Monitoring & Analytics Platform

## Description
NetPulse is a real-time network monitoring and analytics platform designed for local network environments. It discovers devices, monitors latency and packet loss, tracks host network interface traffic, captures packets, and generates rule-based alerts and PDF reports.

## Features
- **Local Network Discovery**: Uses ARP and ICMP ping to discover devices on the local subnet.
- **Device Monitoring**: Continuously measures latency and packet loss.
- **Host Traffic Monitoring**: Tracks download/upload bandwidth for the active network interface.
- **Packet Analyzer**: Background packet capture using Scapy with protocol analytics (TCP, UDP, ICMP, DNS).
- **Inferred Topology**: Visualizes the logical topology using React Flow.
- **Alert Engine**: Generates and deduplicates alerts for offline devices, high latency, packet loss, and statistical anomalies.
- **Network Health Score**: Evaluates the overall health of the network on a scale of 0-100.
- **Reports**: Generates downloadable PDF performance reports.

## Packet Capture Limitation
**Note on Packet Capture:** NetPulse captures traffic using the monitoring host's network interface. On a modern switched network, the interface will only see traffic destined for the host itself, broadcast traffic, and multicast traffic. It cannot capture arbitrary unicast traffic between other PCs on the network without port mirroring configured at the switch level. This is a fundamental limitation of switched ethernet networks.

## Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js & npm
- Npcap (Windows) or libpcap (Linux) for Scapy packet capture.

### Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```
*Note: Run as Administrator/Root to enable Scapy packet capture.*

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## Modes
- **LIVE MODE**: The primary mode where real network data is queried and monitored.
- **DEMO MODE**: If running in an environment without permissions or network access, a demo mode can be implemented to simulate UI updates.
