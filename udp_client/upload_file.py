import os
import socket

from utils import udp, constants


def upload_file(server_address, src, name):
    """
    1. Envía la cadena correspondiente a la acción subir.
    2. Envía el nombre del archivo a subir.
    3. Envía la longitud del archivo.
    4. Envía el archivo.

    :param server_address:
    :param src:
    :param name:
    :return:
    """
    print('UDP: upload_file({}, {}, {})'.format(server_address, src, name))

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        own_address = ('127.0.0.1', 0)
        sock.bind(own_address)
        sock.settimeout(constants.RTO)

        socket_obj = udp.Socket(sock, server_address)
        transmisor = udp.TransmisorDeContenido(socket_obj)

        transmisor.enviar_contenido(constants.UPLOAD.encode())
        print("Upload enviado")
        transmisor.enviar_contenido(name.encode())

        with open(src, "rb") as f:
            f.seek(0, os.SEEK_END)
            size = f.tell()
            f.seek(0, os.SEEK_SET)
            transmisor.enviar_contenido(str(size).encode())
            transmisor.enviar_archivo(f)

        print("Archivo enviado")
