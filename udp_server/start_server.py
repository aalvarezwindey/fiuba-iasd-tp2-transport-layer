import os
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
        sock.bind(server_address)
        receptor = udp.ReceptorDePaquetes(sock)
        transmisor = udp.TransmisorDeContenido(sock)

        def stop_server(sig, frame):
            destroy(sock, server_address)
            sys.exit(0)

        signal.signal(signal.SIGINT, stop_server)

        while True:
            accion = receptor.recibir_paquete().decode()
            print("Se recibió la acción {}.".format(accion))

            if accion == constants.UPLOAD:
                handle_upload(storage_dir, receptor)
            elif accion == constants.DOWNLOAD:
                handle_download(storage_dir, receptor, transmisor)
            else:
                print("Acción desconocida {}.".format(accion))


def handle_upload(storage_dir, receptor):
    """
    1. Recibe el nombre del archivo a recibir.
    2. Recibe la longitud del archivo.
    3. Recibe el archivo.

    :param storage_dir:
    :param receptor:
    :return:
    """
    file_name = receptor.recibir_paquete().decode()
    file_size = int(receptor.recibir_paquete().decode())
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
    transmisor.transmisor_de_paquetes.receptor = receptor.receptor_de_paquetes.transmisor
    file_name = receptor.recibir_paquete().decode()
    print("Se pidió descargar el archivo {}.".format(file_name))

    filename = path.join(storage_dir, file_name)
    with open(filename, "rb") as f:
        f.seek(0, os.SEEK_END)
        size = f.tell()
        f.seek(0, os.SEEK_SET)

        transmisor.enviar_contenido(str(size).encode())
        transmisor.enviar_archivo(f)
    print("Archivo transmitido.")
