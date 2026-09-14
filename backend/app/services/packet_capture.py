import threading
from scapy.all import sniff, IP, TCP, UDP, ICMP, DNS, ARP
from datetime import datetime
import logging
from app.core.database import SessionLocal
from app.models import models

logger = logging.getLogger(__name__)

MAX_DB_PACKETS = 5000

class PacketSniffer:
    def __init__(self):
        self._running = False
        self._thread = None

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._sniff_loop, daemon=True)
        self._thread.start()
        logger.info("Packet capture started.")

    def stop(self):
        self._running = False
        logger.info("Packet capture stopping...")

    def is_running(self):
        return self._running

    def _sniff_loop(self):
        # We use a relatively small timeout to periodically check if we should stop.
        while self._running:
            try:
                # sniff blocks, but with timeout it will return
                sniff(prn=self._process_packet, timeout=2, store=False)
            except Exception as e:
                logger.error(f"Error in sniff loop: {e}")
                # Wait a bit before retrying
                import time
                time.sleep(2)

    def _process_packet(self, packet):
        if not self._running:
            return

        db = SessionLocal()
        try:
            # We don't save payloads, only metadata
            proto_name = "OTHER"
            src_ip = "Unknown"
            dst_ip = "Unknown"
            src_port = None
            dst_port = None
            length = len(packet)

            if IP in packet:
                src_ip = packet[IP].src
                dst_ip = packet[IP].dst
                if TCP in packet:
                    proto_name = "TCP"
                    src_port = packet[TCP].sport
                    dst_port = packet[TCP].dport
                elif UDP in packet:
                    proto_name = "UDP"
                    src_port = packet[UDP].sport
                    dst_port = packet[UDP].dport
                    if DNS in packet:
                        proto_name = "DNS"
                elif ICMP in packet:
                    proto_name = "ICMP"
            elif ARP in packet:
                proto_name = "ARP"
                src_ip = packet[ARP].psrc
                dst_ip = packet[ARP].pdst

            # Save to database
            db_packet = models.Packet(
                timestamp=datetime.utcnow(),
                source_ip=src_ip,
                destination_ip=dst_ip,
                protocol=proto_name,
                source_port=src_port,
                destination_port=dst_port,
                length=length
            )
            db.add(db_packet)
            
            # Retention limit enforcement
            count = db.query(models.Packet).count()
            if count > MAX_DB_PACKETS:
                # Delete oldest 500 packets to batch deletions
                oldest = db.query(models.Packet.id).order_by(models.Packet.id.asc()).limit(500).all()
                oldest_ids = [p[0] for p in oldest]
                db.query(models.Packet).filter(models.Packet.id.in_(oldest_ids)).delete(synchronize_session=False)

            db.commit()
        except Exception as e:
            logger.error(f"Error processing packet: {e}")
        finally:
            db.close()

sniffer_instance = PacketSniffer()
