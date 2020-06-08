from utils.tcp_server_connection import TCPServerConnection
import socket

class TCPServerListener:
    def __init__(self, server_address):
        print('TCP: start_server({})'.format(server_address))  
        self.sock = 'no_socket'
        # Creation
        print('Attempting to create socket server on {}'.format(server_address))
        try:
            MAX_NOT_ACCEPTED_CONNECTIONS_QUEUED = 1
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((server_address))
            self.sock.listen(MAX_NOT_ACCEPTED_CONNECTIONS_QUEUED)
        except Exception as e:
            print('ERROR: could not create socket server')
            print('{}'.format(e))
            raise e
        self.server_address = server_address
        print('Socket server created {}'.format(self.sock))

    def destroy(self):
        print('Attempting to close socket server {}'.format(self.server_address))
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
        except Exception as e:
            print('ERROR: could not destroy socket server')
            print('{}'.format(e))
        print('Server socket destroyed {}'.format(self.sock))

    def accept(self):
        con_sock, addr = self.sock.accept()
        return TCPServerConnection(con_sock, addr)