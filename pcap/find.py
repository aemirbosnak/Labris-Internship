import re
from scapy.all import *
from scapy.layers.tls.cert import PrivKey
from scapy.layers.tls.record import TLS

# TLS handshake message type codes
# Gathered from scapy source code here: https://github.com/secdev/scapy/blob/master/scapy/layers/tls/handshake.py
CLIENT_HELLO = 1
SERVER_HELLO = 2
CLIENT_KEY_EXCHANGE = 16
SESSION_TICKET = 4

# TLS content type codes
ALERT = 21
HANDSHAKE = 22
APPLICATION_DATA = 23

# Packet source and destination ips
SRC_IP = "10.200.200.1"
DST_IP = "10.200.201.33"

# Relevant packet variables
(
    client_hello,
    server_hello,
    client_key_exchange,
    new_session_ticket,
    http_request,
    http_response,
    alert
) = (None, None, None, None, None, None, None)

def parsePacket(packet):
    packet_type = packet[TLS].type
    msg_type = None
    packet_src_ip = packet[IP].src

    if packet_type == HANDSHAKE:
        # Get handshake type
        msg_type = packet[TLS].msg[0].msgtype

        # Transform packet to raw for processing
        packet = raw(packet[TLS])

        if msg_type == CLIENT_HELLO:
            print("TLS handshake started - client hello")
            global client_hello
            client_hello = TLS(packet)
        if msg_type == SERVER_HELLO:
            print("server hello")
            global server_hello
            server_hello = TLS(packet, tls_session=client_hello.tls_session.mirror())
            server_hello.tls_session.server_rsa_key = PrivKey(key.read())
        if msg_type == CLIENT_KEY_EXCHANGE:
            print("client key exchange")
            global client_key_exchange
            client_key_exchange = TLS(packet, tls_session=server_hello.tls_session.mirror())
        if msg_type == SESSION_TICKET:
            print("new session ticket")
            global new_session_ticket
            new_session_ticket = TLS(packet, tls_session=client_hello.tls_session.mirror())

    if packet_type == APPLICATION_DATA:
        # Transform packet to raw for processing
        packet = raw(packet[TLS])

        if packet_src_ip == SRC_IP:
            global http_request
            http_request = TLS(packet, tls_session=new_session_ticket.tls_session.mirror())
            print("TLS handshake successful - http request decrypted")
        if packet_src_ip == DST_IP:
            global http_response
            http_response = TLS(packet, tls_session=http_request.tls_session.mirror())
            print("http response decrypted")

    if packet_type == ALERT:
        print("TLS session ending - printing decrypted data")
        global alert
        alert = 1

        target_data = (http_response.msg[0].data).decode("utf-8")
        printData(target_data)

def printData(data):
    url_pattern = r"https?://[^\s/$.?#].[^\s]*"
    urls = re.findall(url_pattern, data)
    print("\n***************Data***************")
    for url in urls:
        print(url)

load_layer("tls")

packets = rdpcap("best_game.pcap")
key = open("server.key", "r")

for packet in packets:
    if packet.haslayer(TLS):
        print("TLS packet - parsing...")
        parsePacket(packet)
        if alert == 1:
            exit()
    else:
        print("Other - skipping...")