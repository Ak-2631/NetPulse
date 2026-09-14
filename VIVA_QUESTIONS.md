# VIVA_QUESTIONS.md

1. **Why use ICMP for ping?**
   ICMP (Internet Control Message Protocol) is a network-layer protocol specifically designed for diagnostic functions and reporting errors.

2. **What is ARP and why is it used for discovery?**
   ARP (Address Resolution Protocol) maps an IP address to a MAC address on a local network. It is highly reliable for local discovery because it operates at the data link layer and is generally not blocked by local host firewalls.

3. **How is packet loss calculated?**
   Packet loss is the percentage of packets sent that do not receive a reply before a timeout. (Lost / Sent) * 100.

4. **How is latency measured?**
   Latency is the Round Trip Time (RTT) - the time taken for a packet (like an ICMP Echo Request) to reach the destination and the Echo Reply to return.

5. **TCP vs UDP?**
   TCP is connection-oriented, reliable, and guarantees delivery (e.g., HTTP). UDP is connectionless, faster, but does not guarantee delivery (e.g., DNS, Video streaming).

6. **What is a subnet?**
   A subnet is a logical subdivision of an IP network, allowing a large network to be divided into smaller, more efficient routing domains.

7. **What is a MAC address?**
   A Media Access Control address is a unique hardware identifier assigned to a network interface controller (NIC).

8. **How does packet capture work?**
   Packet capture tools (like Scapy/Npcap) put the network interface in promiscuous mode (or use raw sockets) to intercept and read copies of network packets bypassing the normal OS network stack.

9. **Why use Scapy?**
   Scapy is a powerful Python library that allows for custom packet generation, sniffing, dissecting, and network scanning.

10. **Why use SQLite?**
    SQLite is lightweight, serverless, and stores the entire database in a single file, making it perfect for an easy-to-deploy college project.

11. **Why FastAPI?**
    FastAPI is extremely fast, supports async operations natively, and automatically generates Swagger documentation.

12. **How does WebSocket communication work?**
    WebSocket provides full-duplex communication channels over a single TCP connection, allowing the server to push real-time updates to the client without the client polling.

13. **How does the anomaly detection work?**
    It calculates the rolling mean and standard deviation of historical latency (baseline). If a new reading deviates by more than 3 standard deviations (z-score > 3), it is flagged as an anomaly.

14. **What happens if ICMP is blocked?**
    If a host firewall blocks ICMP, pinging will fail, and the device might incorrectly be reported as offline or having 100% packet loss unless alternative ports (like TCP 80/443) are checked.

15. **What is the limitation of packet capture on a switched LAN?**
    Switches forward traffic only to the specific port where the destination MAC resides. Therefore, a sniffer on a regular port only sees broadcast traffic and traffic meant for its own MAC, not traffic between other PCs.
