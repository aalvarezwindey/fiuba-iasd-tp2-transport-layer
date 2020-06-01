import socket
import signal
import sys

COMMAND_LEN = 1
UPLOAD_CMD = '1'
DOWNLOAD_CMD = '2'

def handle_upload():
  print('Handling upload command')

def handle_download():
  print('Handling download command')

def handle_default(command):
  print('Unknown command {}. Just ignoring it'.format(command))

COMMAND_HANDLERS = {
  UPLOAD_CMD: handle_upload,
  DOWNLOAD_CMD: handle_download
}


def destroy_socket(sock, server_address):
  print('Attempting to close socket server {}'.format(server_address))
  try:
    sock.close()
  except Exception as e:
    print('ERROR: could not destroy socket server')
    print('{}'.format(e))
  print('Server socket destroyed {}'.format(sock))

# send and recv implementation: https://docs.python.org/3/howto/sockets.html#socket-howto
# Sends 'buffer' of size 'size' into the socket. Raises error on connection broken
def my_send(sock, buffer, size):
  total_sent = 0
  while total_sent < size:
    sent = sock.send(buffer[total_sent:])
    if sent == 0:
      raise RuntimeError("[my_send] socket connection broken")
    total_sent = total_sent + sent

# returns a buffer of size 'size' bytes readed from the socket
def my_receive(sock, size):
  chunks = []
  MAX_CHUNK_SIZE = 2048
  bytes_recd = 0
  while bytes_recd < size:
    chunk = sock.recv(min(size - bytes_recd, MAX_CHUNK_SIZE))
    if chunk == b'':
      raise RuntimeError("[my_receive] socket connection broken")
    chunks.append(chunk)
    bytes_recd = bytes_recd + len(chunk)
  return b''.join(chunks)

def start_server(server_address, storage_dir):
  print('TCP: start_server({}, {})'.format(server_address, storage_dir))  

  # Creation
  print('Attempting to create socket server on {}'.format(server_address))
  try:
    MAX_NOT_ACCEPTED_CONNECTIONS_QUEUED = 1
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((server_address))
    sock.listen(MAX_NOT_ACCEPTED_CONNECTIONS_QUEUED)
  except Exception as e:
    print('ERROR: could not create socket server')
    print('{}'.format(e))
  print('Socket server created {}'.format(sock))

  def signal_handler(sig, frame):
    # Destruction
    destroy_socket(sock, server_address)
    sys.exit(0)

  # Register handler for SIGINT (Ctrl + C)
  signal.signal(signal.SIGINT, signal_handler)

  while True:
    print('Waiting a new connection')
    conn, addr = sock.accept()

    if not conn:
      destroy_socket(sock, server_address)
      break

    print('New connection received {}'.format(addr))
    command = my_receive(conn, COMMAND_LEN).decode()

    print('Received command {}'.format(command))

    handler = COMMAND_HANDLERS.get(command)

    if handler == None:
      handle_default(command)
      continue
    
    handler()

    