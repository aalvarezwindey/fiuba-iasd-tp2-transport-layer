import socket

from utils import constants, udp


def get_timestamp():
    pass


def start_server(server_address, storage_dir):
    # TODO: Implementar UDP server
    print('UDP: start_server({}, {})'.format(server_address, storage_dir))

    own_address = ('127.0.0.1', 8080)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(own_address)

    direccion_del_receptor = ('127.0.0.1', 8081)
    receptor = udp.Receptor(sock, direccion_del_receptor)

    size = int(receptor.recibir().decode())

    # while True:
    print("Incoming file with size {} from {}".format(size, direccion_del_receptor))

    filename = "./examples/file-{}.txt".format(get_timestamp())
    f = open(filename, "wb")
    bytes_received = 0

    while bytes_received < size:
        data = receptor.recibir()
        bytes_received += len(data)
        f.write(data)

    print("Received file {}".format(filename))

    # Send number of bytes received
    # sock.sendto(str(bytes_received).encode(), addr)

    f.close()
    sock.close()
