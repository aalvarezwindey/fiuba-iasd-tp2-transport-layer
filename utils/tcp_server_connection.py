from utils.tcp_connection import TCPConnection
import socket

class TCPServerConnection(TCPConnection):
    def __init__(self, sock, address):
        self.sock = sock
        self.address = address