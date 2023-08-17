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

def generateFilter(msgtype=None, packet_type=None, source_ip=None):
    def filterFunc(packet):
        if packet_type == APPLICATION_DATA and source_ip is not None:
            if packet[IP].src != source_ip:
                return False
        if packet_type is not None and packet[TLS].type != packet_type:
            return False
        if msgtype is not None and packet[TLS].msg[0].msgtype != msgtype:
            return False
        return True
    return filterFunc

def getPacket(packets, content_type, filterFunc):
    for packet in packets:
        if packet.haslayer(TLS) and packet[TLS].type == content_type and filterFunc(packet):
            return raw(packet[TLS])

load_layer("tls")

packets = rdpcap("best_game.pcap")
key = open("server.key", "r")

# client hello
ch_packet = getPacket(packets, HANDSHAKE, generateFilter(msgtype=CLIENT_HELLO))
ch = TLS(ch_packet)

# server hello
sh_packet = getPacket(packets, HANDSHAKE, generateFilter(msgtype=SERVER_HELLO))
sh = TLS(sh_packet, tls_session=ch.tls_session.mirror())

# Decode traffic with session key
sh.tls_session.server_rsa_key = PrivKey(key.read())

# client key exchange
cke_packet = getPacket(packets, HANDSHAKE, generateFilter(msgtype=CLIENT_KEY_EXCHANGE))
cke = TLS(cke_packet, tls_session=sh.tls_session.mirror())

# new session ticket
st_packet = getPacket(packets, HANDSHAKE, generateFilter(msgtype=SESSION_TICKET))
st = TLS(st_packet, tls_session=cke.tls_session.mirror())

# http request data
http_request_packet = getPacket(packets, APPLICATION_DATA, generateFilter(packet_type=APPLICATION_DATA, source_ip=SRC_IP))
http_request = TLS(http_request_packet, tls_session=st.tls_session.mirror())

# http response data
http_response_packet = getPacket(packets, APPLICATION_DATA, generateFilter(packet_type=APPLICATION_DATA, source_ip=DST_IP))
http_response = TLS(http_response_packet, tls_session=http_request.tls_session.mirror())

# Get info from http application data
http_response.show()