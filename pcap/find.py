from scapy.all import *
from scapy.layers.tls.cert import PrivKey
from scapy.layers.tls.record import TLS

# TLS handshake message type codes
# Gathered from scapy source code here: https://github.com/secdev/scapy/blob/master/scapy/layers/tls/handshake.py
CLIENT_HELLO = 1
SERVER_HELLO = 2
CLIENT_KEY_EXCHANGE = 16
SESSION_TICKET = 4

def getPacket(packets, packet_type):
    for packet in packets:
        if packet.haslayer(TLS):
            if packet[TLS].msg[0].msgtype == packet_type:
                return raw(packet[TLS])

load_layer("tls")

packets = rdpcap("best_game.pcap")
key = open("server.key", "r")

# client hello
ch_packet = getPacket(packets, CLIENT_HELLO)
ch = TLS(ch_packet)

# server hello
sh_packet = getPacket(packets, SERVER_HELLO)
sh = TLS(sh_packet, tls_session=ch.tls_session.mirror())

# Decode traffic with session key
sh.tls_session.server_rsa_key = PrivKey(key.read())

# client key exchange
cke_packet = getPacket(packets, CLIENT_KEY_EXCHANGE)
cke = TLS(cke_packet, tls_session=sh.tls_session.mirror())

# new session ticket
st_packet = getPacket(packets, SESSION_TICKET)
st = TLS(st_packet, tls_session=cke.tls_session.mirror())

# http request data
http_request = TLS(raw(packets[11][TLS]), tls_session=st.tls_session.mirror())

# http response data
http_response = TLS(raw(packets[13][TLS]), tls_session=http_request.tls_session.mirror())

# Get info from http application data
http_response.show()