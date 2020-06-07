import socket

from utils import udp, constants


def download_file(server_address, name, dst):
    """
    1. Envía la cadena correspondiente a la acción descargar.
    2. Envía el nombre del archivo a descargar.
    3. Recibe la longitud del archivo.
    4. Recibe el archivo.

    :param server_address:
    :param name:
    :param dst:
    :return:
    """
    print('UDP: download_file({}, {}, {})'.format(server_address, name, dst))

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        own_address = ('127.0.0.1', 0)
        sock.bind(own_address)

        receptor = udp.ReceptorDePaquetes(sock)
        transmisor = udp.TransmisorDeContenido(sock, server_address)

        transmisor.enviar_contenido(constants.DOWNLOAD.encode())
        transmisor.enviar_contenido(name.encode())
        file_size = int(receptor.recibir_paquete().decode())

        with open(dst, "wb") as f:
            receptor.recibir_archivo(f, file_size)
