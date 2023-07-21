#!/bin/bash

# Create network namespaces
sudo ip netns add client1
sudo ip netns add client2
sudo ip netns add server
sudo ip netns add firewall

# Create veth interfaces
sudo ip link add client1-veth0 type veth peer name fw-client1
sudo ip link add client2-veth0 type veth peer name fw-client2
sudo ip link add server-veth0 type veth peer name fw-server

# Move veth interfaces to respective namespaces
sudo ip link set client1-veth0 netns client1
sudo ip link set client2-veth0 netns client2
sudo ip link set server-veth0 netns server
sudo ip link set fw-client1 netns firewall
sudo ip link set fw-client2 netns firewall
sudo ip link set fw-server netns firewall

# Rename veth interfaces inside respective namespaces
sudo ip netns exec client1 ip link set dev client1-veth0 name eth0
sudo ip netns exec client2 ip link set dev client2-veth0 name eth0
sudo ip netns exec server ip link set dev server-veth0 name eth0
sudo ip netns exec firewall ip link set dev fw-client1 name eth-client1
sudo ip netns exec firewall ip link set dev fw-client2 name eth-client2
sudo ip netns exec firewall ip link set dev fw-server name eth-server

# Set up IP addresses for the interfaces
sudo ip netns exec client1 ip address add 192.0.2.1/26 dev eth0
sudo ip netns exec client2 ip address add 192.0.2.65/26 dev eth0
sudo ip netns exec server ip address add 192.0.2.129/26 dev eth0
sudo ip netns exec firewall ip address add 192.0.2.2/26 dev eth-client1
sudo ip netns exec firewall ip address add 192.0.2.66/26 dev eth-client2
sudo ip netns exec firewall ip address add 192.0.2.130/26 dev eth-server

# Bring up the interfaces
sudo ip netns exec client1 ip link set dev eth0 up
sudo ip netns exec client2 ip link set dev eth0 up
sudo ip netns exec server ip link set dev eth0 up
sudo ip netns exec firewall ip link set dev eth-client1 up
sudo ip netns exec firewall ip link set dev eth-client2 up
sudo ip netns exec firewall ip link set dev eth-server up

# Enable IP forwarding
sudo ip netns exec firewall sysctl -w net.ipv4.ip_forward=1

# Configure default gateway for the namespaces
sudo ip netns exec client1 ip route add default via 192.0.2.2
sudo ip netns exec client2 ip route add default via 192.0.2.66
sudo ip netns exec server ip route add default via 192.0.2.130

# Flush existing iptables rules
sudo ip netns exec firewall iptables -F
sudo ip netns exec firewall iptables -t nat -F

# Change policy to DROP (stateful firewall)
sudo ip netns exec firewall iptables -P INPUT DROP
sudo ip netns exec firewall iptables -P FORWARD DROP
sudo ip netns exec firewall iptables -P OUTPUT DROP

# Allow established communication (for request replies etc.)
sudo ip netns exec firewall iptables -A FORWARD -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# Allow ping from client1 to server
sudo ip netns exec firewall iptables -A FORWARD -p icmp -s 192.0.2.1/26 -d 192.0.2.129/26 -m conntrack --ctstate NEW -j ACCEPT

# Allow HTTP traffic from client2 to server
sudo ip netns exec firewall iptables -A FORWARD -p tcp -s 192.0.2.65/26 -d 192.0.2.129/26 -m conntrack --ctstate NEW -j ACCEPT 

# Allow ping from client2 to firewall
sudo ip netns exec firewall iptables -A INPUT -p icmp -s 192.0.2.65/26 -m conntrack --ctstate NEW,ESTABLISHED -j ACCEPT
sudo ip netns exec firewall iptables -A OUTPUT -p icmp -d 192.0.2.66/26 -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT

# Drop ping from client1 to firewall
# no rule necessary, default policy is to drop

# Enable masquerading for server access
sudo ip netns exec firewall iptables -t nat -A POSTROUTING -s 192.0.2.129/26 -o eth-host -j MASQUERADE

# Host http service with python
# sudo ip netns exec server python3 -m http.server 80

## host-to-firewall connection setup ###

# Create veth interface
sudo ip link add veth-host type veth peer name eth-host # veth-host is connected to the default namespace 

# Move veth interface to namespace
sudo ip link set eth-host netns firewall

# Setup IP addresses for the interface
sudo ip addr add 192.0.2.193/26 dev veth-host # operating in default namespace
sudo ip netns exec firewall ip addr add 192.0.2.194/26 dev eth-host

# Bring interfaces up
sudo ip link set veth-host up
sudo ip netns exec firewall ip link set eth-host up

# Configure routing gateway
sudo ip netns exec firewall ip route add default via 192.0.2.193

sudo ip route add 192.2.0.0/26 via 192.0.2.194 dev veth-host # client1
sudo ip route add 192.2.0.64/26 via 192.0.2.194 dev veth-host # client2
sudo ip route add 192.2.0.128/26 via 192.0.2.194 dev veth-host # server

# Setup forwarding permissions
sudo sysctl -w net.ipv4.ip_forward=1
sudo ip netns exec firewall sysctl -w net.ipv4.ip_forward=1

# Enable packet forwarding from default namespace internet connected device
sudo iptables -A FORWARD -o eno1 -i veth-host -j ACCEPT
sudo iptables -A FORWARD -i eno1 -o veth-host -j ACCEPT

# Enable forwarding from firewall to host
sudo ip netns exec firewall iptables -A FORWARD -s 192.0.2.1/26 -m conntrack --ctstate NEW -j ACCEPT #client1
# can specify icmp and tcp with -p flag, for now all connection protocols are allowed
sudo ip netns exec firewall iptables -A FORWARD -s 192.0.2.65/26 -m conntrack --ctstate NEW -j ACCEPT #client2
sudo ip netns exec firewall iptables -A FORWARD -s 192.0.2.129/26 -m conntrack --ctstate NEW -j ACCEPT #server

# Setup ip masquerading 
sudo iptables -t nat -A POSTROUTING -s 192.0.2.194/26 -o eno1 -j MASQUERADE
sudo ip netns exec firewall iptables -t nat -A POSTROUTING -s 192.0.2.0/26 -o eth-host -j MASQUERADE # client1
sudo ip netns exec firewall iptables -t nat -A POSTROUTING -s 192.0.2.64/26 -o eth-host -j MASQUERADE # client2
sudo ip netns exec firewall iptables -t nat -A POSTROUTING -s 192.0.2.128/26 -o eth-host -j MASQUERADE # server
