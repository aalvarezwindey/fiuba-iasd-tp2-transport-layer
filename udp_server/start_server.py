import os
import select
import socket
import signal
import sys
from os import path

from utils import constants, udp


def get_timestamp():
    pass


def destroy(sock, server_address):
    print('Attempting to close socket server {}'.format(server_address))
    try:
        sock.close()
    except Exception as e:
        print('ERROR: could not destroy socket server')
        print('{}'.format(e))
    print('Server socket destroyed {}'.format(sock))


def start_server(server_address, storage_dir):
    """
    Recibe la acción a realizar (subida o descarga).

    :param server_address:
    :param storage_dir:
    :return:
    """
    print('UDP: start_server({}, {})'.format(server_address, storage_dir))

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        # Configuro Sockets.
        sock.bind(server_address)
        sock.settimeout(constants.RTO)

        # Creo abstracciones.
        socket_obj = udp.Socket(sock)
        receptor = udp.ReceptorDeContenido(socket_obj)
        transmisor = udp.TransmisorDeContenido(socket_obj)

        # Manejo SIGINT.
        def stop_server(sig, frame):
            destroy(sock, server_address)
            sys.exit(0)

        signal.signal(signal.SIGINT, stop_server)

        # Manejo pedidos de los clientes.
        while True:
            transmisor.numero_de_secuencia = 1
            receptor.ultimo_numero_de_secuencia = 0
            select.select([sock], [], [])  # Esperar a que haya algo para recibir.

            try:
                accion = receptor.recibir_contenido().decode()
                print("Se recibió la acción {}.".format(accion))

                if accion == constants.UPLOAD:
                    handle_upload(storage_dir, receptor)
                elif accion == constants.DOWNLOAD:
                    handle_download(storage_dir, receptor, transmisor)
                else:
                    print("Acción desconocida {}.".format(accion))
            except udp.Desconexion:
                print("Se desconectó el cliente")


def handle_upload(storage_dir, receptor):
    """
    1. Recibe el nombre del archivo a recibir.
    2. Recibe la longitud del archivo.
    3. Recibe el archivo.

    :param storage_dir:
    :param receptor:
    :return:
    """
    file_name = receptor.recibir_contenido().decode()
    file_size = int(receptor.recibir_contenido().decode())
    print("Se pidió subir el archivo {} con longitud {}.".format(file_name, file_size))

    filename = path.join(storage_dir, file_name)
    with open(filename, "wb") as f:
        receptor.recibir_archivo(f, file_size)

    print("Archivo recibido.")


def handle_download(storage_dir, receptor, transmisor):
    """
    1. Recibe el nombre del archivo a transmitir.
    2. Envía la longitud del archivo.
    3. Envía el archivo.

    :param storage_dir:
    :param receptor:
    :param transmisor:
    :return:
    """
    file_name = receptor.recibir_contenido().decode()
    print("Se pidió descargar el archivo {}.".format(file_name))

    filename = path.join(storage_dir, file_name)
    with open(filename, "rb") as f:
        f.seek(0, os.SEEK_END)
        size = f.tell()
        f.seek(0, os.SEEK_SET)

        transmisor.enviar_contenido(str(size).encode())
        transmisor.enviar_archivo(f)

    print("Archivo transmitido.")
