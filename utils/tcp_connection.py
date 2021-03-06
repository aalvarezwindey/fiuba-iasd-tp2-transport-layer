from abc import ABCMeta
import socket

MAX_CHUNK_SIZE = 2048

# metaclass=ABCMeta is for make an abstract class you know what i mean?
class TCPConnection(metaclass=ABCMeta):
    # returns a string of received data until the specified separator is found
    # Pos: the separator is discarded from the string
    def receive_until_separator(self, separator = '|'):
        buffer = ''
        A_BYTE = 1

        while True:
            byte = self.sock.recv(A_BYTE)

            if byte == b'':
                raise RuntimeError("[receive_until_separator] socket connection broken")

            char = byte.decode()

            if char != separator:
                buffer += char
            else:
                break

        return buffer

    # returns a buffer of size 'size' bytes readed from the socket
    def receive(self, size):
        chunks = []
        bytes_recvd = 0
        while bytes_recvd < size:
            chunk = self.sock.recv(min(size - bytes_recvd, MAX_CHUNK_SIZE))
            if chunk == b'':
                raise RuntimeError("[receive] socket connection broken")
            chunks.append(chunk)
            bytes_recvd = bytes_recvd + len(chunk)
        return b''.join(chunks)

    # send and recv implementation: https://docs.python.org/3/howto/sockets.html#socket-howto
    # Sends 'buffer' of size 'size' into the socket. Raises error on connection broken
    def send(self, buffer, size):
        total_sent = 0
        while total_sent < size:
            sent = self.sock.send(buffer[total_sent:])
            if sent == 0:
                raise RuntimeError("[my_send] socket connection broken")
            total_sent = total_sent + sent

    def receive_file(self, a_file, expected_file_size):
        bytes_received = 0

        while bytes_received < expected_file_size:
            data = self.receive(min(MAX_CHUNK_SIZE, expected_file_size - bytes_received))
            bytes_received += len(data)
            a_file.write(data)

    def send_file(self, a_file, file_size):
        read = 0
        CHUNK_SIZE = 1024
        while read < file_size:
            chunk = a_file.read(CHUNK_SIZE)
            if not chunk:
                break
            read += len(chunk)
            self.send(chunk, len(chunk))

    def close_write(self):
        try:
            self.sock.shutdown(socket.SHUT_WR)
        except Exception as e:
            print('ERROR: could not destroy socket client')
            print('{}'.format(e))

    def close_read(self):
        try:
            self.sock.shutdown(socket.SHUT_RD)
        except Exception as e:
            print('ERROR: could not destroy socket client')
            print('{}'.format(e))

    def destroy(self):
        print('Attempting to close socket client {}'.format(self.server_address))
        try:
            self.sock.close()
        except Exception as e:
            print('ERROR: could not destroy socket client')
            print('{}'.format(e))
        print('Client socket destroyed {}'.format(self.sock))

    def describe(self):
        print('{}'.format(self.server_address))

    def send_with_separator(self, data, separator = '|'):
        self.send(data, len(data))
        self.send(separator.encode(), len(separator.encode()))