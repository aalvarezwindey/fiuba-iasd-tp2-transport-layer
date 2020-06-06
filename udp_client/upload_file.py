import os
import socket

from utils import udp, constants


def upload_file(server_address, src, name):
    # TODO: Implementar UDP upload_file client
    print('UDP: upload_file({}, {}, {})'.format(server_address, src, name))

    f = open('./examples/example.txt', "rb")
    f.seek(0, os.SEEK_END)
    size = f.tell()
    f.seek(0, os.SEEK_SET)

    own_address = ('127.0.0.1', 8081)

    # Create socket and connect to server
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(own_address)

    transmisor = udp.Transmisor(sock, server_address)
    transmisor.enviar(str(size).encode())

    while True:
        chunk = f.read(constants.CHUNK_SIZE)
        if not chunk:
            break
        transmisor.enviar(chunk)

    f.close()
    sock.close()
