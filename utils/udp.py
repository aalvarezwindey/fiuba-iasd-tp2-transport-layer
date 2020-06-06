import hashlib
from random import randint
from sys import maxsize, getsizeof
from utils import constants


class Paquete:
    """Modela un paquete de la capa de aplicación."""

    def __init__(self, contenido=None, numero_de_secuencia=None):
        """
        Si solo recibe el contenido, entonces extrae el checksum y
        número de secuencia. Si recibe el número de secuencia,
        entonces el contenido pasa a ser el "payload" del paquete.

        :param contenido:
        :param checksum:
        :param numero_de_secuencia:
        """
        if numero_de_secuencia:
            self.contenido = contenido
            self.numero_de_secuencia = numero_de_secuencia
            self.checksum = self._calcular_checksum()
        else:
            self.contenido = self._extraer_payload(contenido)
            self.numero_de_secuencia = self._extraer_numero_de_secuencia(contenido)
            self.checksum = self._extraer_checksum(contenido)

    def _extraer_payload(self, contenido):
        return contenido

    def _extraer_numero_de_secuencia(self, contenido):
        return b''

    def _extraer_checksum(self, contenido):
        return b''

    def _calcular_checksum(self):
        # return hash(self.contenido + bytes(self.numero_de_secuencia))
        return b''

    def valido(self):
        return self._calcular_checksum() == self.checksum

    def contenido_completo(self):
        """
        Devuelve el contenido del paquete completo (número de
        secuencia, checksum y contenido).
        """
        return bytes(self.numero_de_secuencia) + self.checksum + self.contenido


class Ack:
    """Modela un Ack."""

    def __init__(self, numero_de_secuencia=None, contenido=None):
        """
        Si recibe el número de secuencia, entonces crea el Ack
        calculando el checksum. En caso contrario extra del contenido
        el numero de secuencia y el checksum.

        :param numero_de_secuencia:
        :param contenido:
        """
        if numero_de_secuencia:
            self.numero_de_secuencia = numero_de_secuencia
            self.checksum = self._calcular_checksum()
        else:
            self.numero_de_secuencia = self._extrer_numero_de_secuencia(contenido)
            self.checksum = self._extrer_checksum(contenido)

    def valido(self):
        return self.checksum == self._calcular_checksum()

    def _calcular_checksum(self):
        # return hash(bytes(self.numero_de_secuencia))
        return b''

    def _extrer_numero_de_secuencia(self, contenido):
        return b''

    def _extrer_checksum(self, contenido):
        return b''

    def contenido_completo(self):
        """
        Devuelve el contenido completo del ack (número de secuencia y checksum).
        """
        return bytes(self.numero_de_secuencia) + self.checksum


class TransmisorDeMensajes:

    def __init__(self, socket, direccion_del_receptor):
        self.socket = socket
        self.direccion_del_receptor = direccion_del_receptor

    def enviar(self, mensaje):
        self.socket.sendto(
            mensaje.contenido_completo(),
            self.direccion_del_receptor
        )


class ReceptorDeMensajes:

    def __init__(self, socket, tipo_de_mensaje):
        self.socket = socket
        self.tipo_de_mensaje = tipo_de_mensaje
        self.direccion_del_transmisor = None

    def recibir(self):
        data, addr = self.socket.recvfrom(constants.CHUNK_SIZE)
        # self.direccion_del_transmisor = addr
        return self.tipo_de_mensaje(contenido=data)


class Receptor:

    def __init__(self, socket, direccion_del_receptor):
        self.socket = socket
        self.direccion_del_receptor = direccion_del_receptor
        self.receptor_de_paquetes = ReceptorDeMensajes(socket, Paquete)
        self.transmisor_de_mensajes = TransmisorDeMensajes(socket, direccion_del_receptor)

    def recibir(self):
        paquete = self.receptor_de_paquetes.recibir()
        self.transmisor_de_mensajes.enviar(Ack(numero_de_secuencia=b''))
        return paquete.contenido


class Transmisor:

    def __init__(self, socket, direccion_del_receptor):
        self.socket = socket
        self.direccion_de_receptor = direccion_del_receptor
        self.transmisor_de_paquetes = TransmisorDeMensajes(socket, direccion_del_receptor)
        self.receptor_de_acks = ReceptorDeMensajes(socket, Ack)

    def enviar(self, contenido):
        # print(contenido, getsizeof(contenido))
        if len(contenido) > constants.CHUNK_SIZE:
            raise Exception('El contenido que se pretende transmitir '
                            'es mayor que {}.'.format(constants.CHUNK_SIZE))

        self.transmisor_de_paquetes.enviar(Paquete(contenido=contenido, numero_de_secuencia=b''))
        ack = self.receptor_de_acks.recibir()
        return ack.valido()

# class EsperarAck:
#
#     def __init__(self, socket):
#         self.socket = socket
#         self.receptor_de_paquetes = ReceptorDePaquetes(socket)
#
#     def ack(self, numero_de_secuencia_esperado):
#         # TODO: agregar timeout.
#         paquete = self.receptor_de_paquetes.recibir()
#         return numero_de_secuencia_esperado == paquete.numero_de_secuencia
