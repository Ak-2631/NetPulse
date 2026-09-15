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
def get_native_arp_cache() -> Dict[str, str]:
    """Parse the OS native ARP cache to get MAC addresses."""
    macs = {}
    try:
        import subprocess, re, platform
        if platform.system() == "Windows":
            out = subprocess.check_output("arp -a", shell=True).decode()
            # Windows arp -a format: 192.168.1.1    00-11-22-33-44-55
            matches = re.findall(r'(\d+\.\d+\.\d+\.\d+)\s+([0-9a-fA-F-]+)\s+', out)
            for ip, mac in matches:
                if mac != "---":
                    macs[ip] = mac.replace("-", ":").lower()
        else:
            # Linux fallback
            out = subprocess.check_output("arp -n", shell=True).decode()
            matches = re.findall(r'(\d+\.\d+\.\d+\.\d+)\s+dev\s+\S+\s+lladdr\s+([0-9a-fA-F:]+)', out)
            for ip, mac in matches:
                macs[ip] = mac.lower()
    except Exception as e:
        logger.error(f"Failed to read native ARP cache: {e}")
    return macs

def scan_network(subnet: str) -> Dict:
    """
    Scan the network. Tries ARP to get MACs, and ICMP to get IPs if ARP is restricted (e.g. Wi-Fi Npcap bug).
    """
    logger.info(f"Starting discovery on {subnet}")
    
    arp_devices, pcap_available = discover_arp(subnet)
    mode = "ARP/Scapy"
    
    # Create a mapping of IP to MAC from the ARP results
    arp_macs = {d["ip"]: d["mac"] for d in arp_devices}
    
    # If ARP found very few devices (e.g., Npcap fails to inject raw frames on Windows Wi-Fi)
    # run the ICMP sweep to discover IPs, which will force the OS to populate its native ARP cache!
    if not pcap_available or len(arp_devices) <= 2:
        if pcap_available:
            logger.info("ARP discovery yielded few devices (Npcap Wi-Fi injection limitation). Running ICMP sweep...")
            mode = "ARP + ICMP (Hybrid Cache)"
        else:
            logger.info("Falling back to ICMP discovery...")
            mode = "ICMP Fallback"
            
        icmp_devices = discover_icmp(subnet)
        
        # Now read the OS's native ARP cache (populated by the ICMP pings)
        native_macs = get_native_arp_cache()
        
        # Merge results
        final_devices = {}
        for d in arp_devices:
            final_devices[d["ip"]] = d
            
        for d in icmp_devices:
            ip = d["ip"]
            if ip not in final_devices:
                # Try Scapy ARP first, then Native ARP cache
                mac = arp_macs.get(ip) or native_macs.get(ip) or "Unknown"
                final_devices[ip] = {
                    "ip": ip,
                    "mac": mac,
                    "hostname": "Unknown"
                }
                
        devices = list(final_devices.values())
    else:
        devices = arp_devices
        
    def _resolve_and_update(d):
        d["hostname"] = resolve_hostname(d["ip"])

    with ThreadPoolExecutor(max_workers=50) as executor:
        for d in devices:
            executor.submit(_resolve_and_update, d)
        
    logger.info(f"Discovery complete. Found {len(devices)} devices using {mode}.")
    return {"devices": devices, "mode": mode, "pcap_available": pcap_available}
