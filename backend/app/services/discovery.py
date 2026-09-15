import ipaddress
import socket
from scapy.all import ARP, Ether, srp, conf
from concurrent.futures import ThreadPoolExecutor, as_completed
import ping3
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

def discover_arp(subnet: str) -> tuple[List[Dict], bool]:
    """Discover devices on the subnet using ARP requests. Returns (devices, pcap_available)."""
    discovered = []
    pcap_available = True
    try:
        arp = ARP(pdst=subnet)
        ether = Ether(dst="ff:ff:ff:ff:ff:ff")
        packet = ether/arp
        
        result = srp(packet, timeout=2, verbose=0)[0]
        
        for sent, received in result:
            discovered.append({
                "ip": received.psrc,
                "mac": received.hwsrc,
                "hostname": "Unknown"
            })
    except Exception as e:
        err_str = str(e).lower()
        if "winpcap is not installed" in err_str or "layer 2" in err_str:
            pcap_available = False
            logger.warning("Npcap/WinPcap is not installed. ARP discovery is unavailable.")
        else:
            logger.error(f"ARP discovery failed: {e}")
    return discovered, pcap_available

def ping_host(ip: str) -> str | None:
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
    try:
        hostname, _, _ = socket.gethostbyaddr(ip)
        return hostname
    except Exception:
        return "Unknown"

def scan_network(subnet: str) -> Dict:
    """
    Scan the network. Tries ARP first. 
    If Npcap is missing or ARP fails, uses ICMP.
    Returns dict with devices and the discovery mode used.
    """
    logger.info(f"Starting discovery on {subnet}")
    
    devices, pcap_available = discover_arp(subnet)
    mode = "ARP/Scapy"
    
    if not pcap_available or not devices:
        logger.info("Falling back to ICMP discovery...")
        mode = "ICMP Fallback"
        devices = discover_icmp(subnet)
        
    for device in devices:
        device["hostname"] = resolve_hostname(device["ip"])
        
    logger.info(f"Discovery complete. Found {len(devices)} devices using {mode}.")
    return {"devices": devices, "mode": mode, "pcap_available": pcap_available}
