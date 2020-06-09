import hashlib
from _socket import timeout

from utils import constants


class Socket:

    def __init__(self, socket, receptor=None):
        self.socket = socket
        self.receptor = receptor


class Paquete:
    """
    Modela un paquete de la capa de aplicación. El mismo se compone
    de:
      - Número de secuencia
      - Checksum
      - Payload
    """

    def __init__(self, contenido=None, numero_de_secuencia=None):
        """
        Si solo recibe el contenido, entonces extrae el checksum y
        número de secuencia. Si recibe el número de secuencia,
        entonces el contenido pasa a ser el "payload" del paquete.

        :param contenido:
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
        return contenido[constants.HEADER_SIZE:]

    def _extraer_numero_de_secuencia(self, contenido):
        return contenido[:constants.SEQUENCE_NUMBER_SIZE]

    def _extraer_checksum(self, contenido):
        return contenido[constants.SEQUENCE_NUMBER_SIZE:constants.HEADER_SIZE]

    def _calcular_checksum(self):
        data = self.contenido + self.numero_de_secuencia
        return hashlib \
            .blake2b(data, digest_size=constants.CHECKSUM_SIZE) \
            .digest()

    def valido(self):
        return self._calcular_checksum() == self.checksum

    def contenido_completo(self):
        """
        Devuelve el contenido del paquete completo (número de
        secuencia, checksum y contenido).
        """
        return self.numero_de_secuencia + self.checksum + self.contenido


class Ack:
    """
    Modela un Ack. El mismo se compone
    de:
      - Número de secuencia
      - Checksum
    """

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
        data = self.numero_de_secuencia
        return hashlib \
            .blake2b(data, digest_size=constants.CHECKSUM_SIZE) \
            .digest()

    def _extrer_numero_de_secuencia(self, contenido):
        return contenido[:constants.SEQUENCE_NUMBER_SIZE]

    def _extrer_checksum(self, contenido):
        return contenido[constants.SEQUENCE_NUMBER_SIZE:]

    def contenido_completo(self):
        """
        Devuelve el contenido completo del ack (número de secuencia y checksum).
        """
        return self.numero_de_secuencia + self.checksum


class Transmisor:

    def __init__(self, socket):
        self.socket = socket

    def enviar(self, mensaje):
        bytes_enviados = 0
        contenido = mensaje.contenido_completo()

        while bytes_enviados < len(contenido):
            bytes_enviados += self.socket.socket.sendto(
                contenido[bytes_enviados:],
                self.socket.receptor
            )


class Receptor:

    def __init__(self, socket, tipo_de_mensaje):
        self.socket = socket
        self.tipo_de_mensaje = tipo_de_mensaje

    def recibir(self):
        data, addr = self.socket.socket.recvfrom(constants.CHUNK_SIZE)
        self.socket.receptor = addr
        return self.tipo_de_mensaje(contenido=data)


class ReceptorDeContenido:

    def __init__(self, socket):
        self.receptor_de_paquetes = Receptor(socket, Paquete)
        self.transmisor_de_mensajes = Transmisor(socket)
        self.ultimo_numero_de_secuencia = 0
        self.cantidad_de_perdidas_seguidas = 0

    def recibir_contenido(self):
        try:
            paquete = self.receptor_de_paquetes.recibir()
        except timeout:  # Se perdió por RTO.
            print("RTO al recibir contenido")
            self.cantidad_de_perdidas_seguidas += 1
            if self.cantidad_de_perdidas_seguidas >= constants.RTOS_TO_DISCONNECT:
                raise Desconexion
            return self.recibir_contenido()
        self.cantidad_de_perdidas_seguidas = 0

        numero_de_secuencia_paquete = int.from_bytes(paquete.numero_de_secuencia, "big")
        if paquete.valido() and (self.ultimo_numero_de_secuencia + 1 == numero_de_secuencia_paquete):
            # Ok
            self.ultimo_numero_de_secuencia += 1
            ack = Ack(
                numero_de_secuencia=self.ultimo_numero_de_secuencia.to_bytes(constants.SEQUENCE_NUMBER_SIZE, "big"))
            self.transmisor_de_mensajes.enviar(ack)
            return paquete.contenido
        else:
            # Pedir retransmicion
            ack = Ack(
                numero_de_secuencia=self.ultimo_numero_de_secuencia.to_bytes(constants.SEQUENCE_NUMBER_SIZE, "big"))
            self.transmisor_de_mensajes.enviar(ack)
            return self.recibir_contenido()

    def recibir_archivo(self, archivo, file_size):
        bytes_received = 0

        while bytes_received < file_size:
            print("Bytes recibidos:", bytes_received)
            data = self.recibir_contenido()
            bytes_received += len(data)
            archivo.write(data)


class TransmisorDeContenido:

    def __init__(self, socket):
        self.socket = socket
        self.numero_de_secuencia = 1
        self.transmisor_de_paquetes = Transmisor(socket)
        self.receptor_de_acks = Receptor(socket, Ack)
        self.cantidad_de_perdidas_seguidas = 0

    def _crear_paquete(self, contenido):
        if len(contenido) > constants.PAYLOAD_SIZE:
            raise Exception('El contenido que se pretende enviar es '
                            'mayor que el permitido por paquete.')

        return Paquete(
            contenido=contenido,
            numero_de_secuencia=self.numero_de_secuencia
                .to_bytes(constants.SEQUENCE_NUMBER_SIZE, "big"))

    def enviar_contenido(self, contenido):
        paquete = self._crear_paquete(contenido)

        self.transmisor_de_paquetes.enviar(paquete)
        try:
            ack = self.receptor_de_acks.recibir()
        except timeout:  # Retransmisión por RTO.
            print("RTO al esperar ack")
            self.cantidad_de_perdidas_seguidas += 1
            if self.cantidad_de_perdidas_seguidas >= constants.RTOS_TO_DISCONNECT:
                raise Desconexion
            self.enviar_contenido(contenido)
            return
        self.cantidad_de_perdidas_seguidas = 0

        if not ack.valido() or not int.from_bytes(ack.numero_de_secuencia, "big") == self.numero_de_secuencia:
            self.enviar_contenido(contenido)  # Retransmición
        else:
            self.numero_de_secuencia += 1  # Ok

    def enviar_archivo(self, archivo):
        bytes_enviados = 0
        while True:
            chunk = archivo.read(constants.PAYLOAD_SIZE)
            bytes_enviados += len(chunk)
            print("Bytes enviados:", bytes_enviados)
            if not chunk:
                break
            self.enviar_contenido(chunk)

class Desconexion(Exception):
    pass
