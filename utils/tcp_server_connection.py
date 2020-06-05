import socket

class TCPServerConnection:
    def __init__(self, sock, address):
        self.sock = sock
        self.address = address

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
        MAX_CHUNK_SIZE = 2048
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
    def send(buffer, size):
        total_sent = 0
        while total_sent < size:
            sent = self.sock.send(buffer[total_sent:])
            if sent == 0:
                raise RuntimeError("[my_send] socket connection broken")
            total_sent = total_sent + sent

    def receive_file(self, file_size, file_name):
        # TODO: use storage dir configured for server
        filename = "./{}".format(file_name)
        new_file = open(filename, "wb")
        bytes_received = 0

        print('File created attemping to receive it')
        while bytes_received < file_size:
            # TODO: implement receiving the file in chunks and not load it all in memory
            data = self.receive(file_size)
            bytes_received += len(data)
            new_file.write(data)

    def describe(self):
        print('{}'.format(self.address))