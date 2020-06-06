from utils.tcp_connection import TCPConnection
import socket

class TCPClientConnection(TCPConnection):
    def __init__(self, server_address):
        print('Attempting to connect to server socket server on {}'.format(server_address))
        self.sock = 'no_socket'
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect(server_address)
        except Exception as e:
            print('ERROR: could not connect to server at {}'.format(server_address))
            print('{}'.format(e))
            return
        self.server_address = server_address
        print('Client connected successfully {}'.format(self.sock))