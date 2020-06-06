import socket

from utils import constants, udp


def get_timestamp():
    pass


def start_server(server_address, storage_dir):
    # TODO: Implementar UDP server
    print('UDP: start_server({}, {})'.format(server_address, storage_dir))

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(constants.SERVER_ADDRESS)

    receptor = udp.ReceptorDePaquetes(sock)
    file_size = int(receptor.recibir_paquete().decode())

    filename = "./examples/file-{}.txt".format(get_timestamp())
    f = open(filename, "wb")
    receptor.recibir_archivo(f, file_size)
    print("Received file {}".format(filename))

    # Send number of bytes received
    # sock.sendto(str(bytes_received).encode(), addr)

    f.close()
    sock.close()
