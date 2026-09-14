import socket
import psutil
import ipaddress
import platform

def get_default_gateway():
    """Attempt to find the default gateway."""
    try:
        # psutil net_if_stats or net_if_addrs doesn't give gateway directly
        # We can use scapy's conf.route if scapy is available, or use socket/os commands
        from scapy.all import conf
        if conf.route and conf.route.route():
            # In Scapy conf.route, typically the route with dest 0.0.0.0 is the default gateway
            for route in conf.route.routes:
                if route[0] == 0: # 0.0.0.0
                    return route[2] # Gateway IP
    except Exception:
        pass
    return "Unknown"

def get_system_network_info():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    # In case local_ip is 127.0.0.1, try to find a real one
    if local_ip.startswith("127."):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
        except Exception:
            pass

    mac_address = "Unknown"
    active_interface = "Unknown"
    subnet_mask = "255.255.255.0" # Default fallback
    
    addrs = psutil.net_if_addrs()
    stats = psutil.net_if_stats()
    
    for interface_name, interface_addresses in addrs.items():
        if stats.get(interface_name, None) and stats[interface_name].isup:
            for addr in interface_addresses:
                if addr.family == socket.AF_INET and addr.address == local_ip:
                    active_interface = interface_name
                    subnet_mask = addr.netmask
            # Also find MAC for this interface
            for addr in interface_addresses:
                if addr.family == psutil.AF_LINK:
                    mac_address = addr.address

    try:
        network = ipaddress.IPv4Network(f"{local_ip}/{subnet_mask}", strict=False)
        subnet = str(network)
    except Exception:
        subnet = f"{local_ip}/24"

    return {
        "hostname": hostname,
        "local_ip": local_ip,
        "mac_address": mac_address,
        "active_interface": active_interface,
        "subnet": subnet,
        "default_gateway": get_default_gateway()
    }
