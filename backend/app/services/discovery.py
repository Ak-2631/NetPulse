import ipaddress
import socket
from scapy.all import ARP, Ether, srp, conf
from concurrent.futures import ThreadPoolExecutor, as_completed
import ping3
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

def discover_arp(subnet: str) -> List[Dict]:
    """Discover devices on the subnet using ARP requests."""
    discovered = []
    try:
        # Create ARP packet
        arp = ARP(pdst=subnet)
        ether = Ether(dst="ff:ff:ff:ff:ff:ff")
        packet = ether/arp
        
        # Send packet and capture response
        # timeout=2, verbose=0 to prevent printing to stdout
        result = srp(packet, timeout=2, verbose=0)[0]
        
        for sent, received in result:
            discovered.append({
                "ip": received.psrc,
                "mac": received.hwsrc,
                "hostname": "Unknown" # Will resolve later
            })
    except Exception as e:
        logger.error(f"ARP discovery failed: {e}")
    return discovered

def ping_host(ip: str) -> str | None:
    """Ping a single host. Returns IP if online, else None."""
    try:
        delay = ping3.ping(ip, timeout=1)
        if delay is not None and delay is not False:
            return ip
    except Exception:
        pass
    return None

def discover_icmp(subnet: str) -> List[Dict]:
    """Discover devices using ICMP ping (Fallback)."""
    discovered = []
    try:
        network = ipaddress.IPv4Network(subnet, strict=False)
        hosts = [str(ip) for ip in network.hosts()]
        
        # Don't ping the whole /24 sequentially, use ThreadPool
        # If it's a large subnet, maybe limit it to /24 or first 256 hosts
        if network.num_addresses > 1024:
            logger.warning("Subnet too large for ICMP fallback scan, taking first 1024.")
            hosts = hosts[:1024]

        with ThreadPoolExecutor(max_workers=50) as executor:
            future_to_ip = {executor.submit(ping_host, ip): ip for ip in hosts}
            for future in as_completed(future_to_ip):
                ip = future.result()
                if ip:
                    discovered.append({
                        "ip": ip,
                        "mac": "Unknown", # Cannot get MAC easily with ICMP across OSes
                        "hostname": "Unknown"
                    })
    except Exception as e:
        logger.error(f"ICMP discovery failed: {e}")
    return discovered

def resolve_hostname(ip: str) -> str:
    """Attempt to resolve hostname from IP."""
    try:
        hostname, _, _ = socket.gethostbyaddr(ip)
        return hostname
    except Exception:
        return "Unknown"

def scan_network(subnet: str) -> List[Dict]:
    """
    Scan the network. Tries ARP first (requires admin/root or Npcap).
    Falls back to ICMP if ARP returns nothing or fails.
    """
    logger.info(f"Starting discovery on {subnet}")
    devices = discover_arp(subnet)
    
    if not devices:
        logger.info("ARP discovery yielded 0 devices. Trying ICMP fallback...")
        devices = discover_icmp(subnet)
        
    # Resolve hostnames for found devices
    for device in devices:
        device["hostname"] = resolve_hostname(device["ip"])
        
    logger.info(f"Discovery complete. Found {len(devices)} devices.")
    return devices
