import socket
import psutil
import ipaddress
import platform
import logging

logger = logging.getLogger(__name__)

def get_default_gateway():
    """Attempt to find the default gateway."""
    try:
        from scapy.all import conf
        if conf.route and conf.route.route():
            for route in conf.route.routes:
                if route[0] == 0: # 0.0.0.0
                    return route[2] # Gateway IP
    except Exception:
        pass
    return "Unknown"

def get_system_network_info():
    hostname = socket.gethostname()
    
    # 1. Detect local IP using a UDP socket to an external address (Google DNS).
    # This forces the OS to use the interface associated with the default route (0.0.0.0/0).
    local_ip = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception as e:
        logger.error(f"Failed to detect IP via default route: {e}")
        # Fallback to gethostbyname if offline
        local_ip = socket.gethostbyname(hostname)

    # 2. Iterate over psutil interfaces to find the one matching the detected local_ip
    mac_address = "Unknown"
    active_interface = "Unknown"
    subnet_mask = "255.255.255.0"
    
    addrs = psutil.net_if_addrs()
    stats = psutil.net_if_stats()
    
    for interface_name, interface_addresses in addrs.items():
        if stats.get(interface_name, None) and stats[interface_name].isup:
            found_ip = False
            for addr in interface_addresses:
                if addr.family == socket.AF_INET and addr.address == local_ip:
                    found_ip = True
                    active_interface = interface_name
                    subnet_mask = addr.netmask
            
            if found_ip:
                # Also find MAC for this interface
                for addr in interface_addresses:
                    if addr.family == psutil.AF_LINK:
                        mac_address = addr.address
                break # We found our interface, stop searching

    if active_interface == "Unknown":
        logger.error(f"Could not match local IP {local_ip} to any active interface.")

    # 3. Calculate CIDR network (e.g. 172.17.96.0/21)
    try:
        network = ipaddress.IPv4Network(f"{local_ip}/{subnet_mask}", strict=False)
        subnet = str(network)
    except Exception as e:
        logger.error(f"Failed to calculate CIDR: {e}")
        subnet = f"{local_ip}/24" # Fallback

    gateway = get_default_gateway()

    # Log exactly what the user requested
    logger.info(f"Selected interface: {active_interface}")
    logger.info(f"Local IP: {local_ip}")
    logger.info(f"Network: {subnet}")
    logger.info(f"Gateway: {gateway}")

    # Detect pcap availability for the UI
    pcap_available = True
    try:
        from scapy.all import conf
        # L2socket will throw if pcap is completely missing on Windows
        import scapy.arch.pcapdnet
    except Exception:
        pcap_available = False

    return {
        "hostname": hostname,
        "local_ip": local_ip,
        "mac_address": mac_address,
        "active_interface": active_interface,
        "subnet": subnet,
        "default_gateway": gateway,
        "pcap_available": pcap_available
    }
