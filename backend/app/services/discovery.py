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
    Scan the network. Tries ARP to get MACs, and ICMP to get IPs if ARP is restricted (e.g. AP isolation).
    """
    logger.info(f"Starting discovery on {subnet}")
    
    arp_devices, pcap_available = discover_arp(subnet)
    mode = "ARP/Scapy"
    
    # Create a mapping of IP to MAC from the ARP results
    arp_macs = {d["ip"]: d["mac"] for d in arp_devices}
    
    # If ARP found very few devices (e.g., just the localhost due to Wi-Fi AP isolation)
    # or if pcap is entirely unavailable, run the ICMP sweep to discover IPs.
    if not pcap_available or len(arp_devices) <= 2:
        if pcap_available:
            logger.info("ARP discovery yielded few devices (possible AP isolation). Running ICMP sweep to find more IPs...")
            mode = "ARP + ICMP (Hybrid)"
        else:
            logger.info("Falling back to ICMP discovery...")
            mode = "ICMP Fallback"
            
        icmp_devices = discover_icmp(subnet)
        
        # Merge ICMP IPs into the final list, using ARP MACs if available
        final_devices = {}
        
        # First, add all ARP discovered devices
        for d in arp_devices:
            final_devices[d["ip"]] = d
            
        # Then, add ICMP discovered devices (overwriting MAC only if it was Unknown)
        for d in icmp_devices:
            ip = d["ip"]
            if ip not in final_devices:
                final_devices[ip] = {
                    "ip": ip,
                    "mac": arp_macs.get(ip, "Unknown"),
                    "hostname": "Unknown"
                }
                
        devices = list(final_devices.values())
    else:
        devices = arp_devices
        
    for device in devices:
        device["hostname"] = resolve_hostname(device["ip"])
        
    logger.info(f"Discovery complete. Found {len(devices)} devices using {mode}.")
    return {"devices": devices, "mode": mode, "pcap_available": pcap_available}
