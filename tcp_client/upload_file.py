import socket

UPLOAD_CMD = '1'

def destroy_socket(sock, server_address):
  print('Attempting to finish connection with {}'.format(server_address))
  try:
    sock.close()
  except Exception as e:
    print('ERROR: could not destroy socket client')
    print('{}'.format(e))
  print('Client socket destroyed successfully {}'.format(sock))

# TODO: Move duplicated code to a helper_sockets file
def my_send(sock, buffer, size):
  total_sent = 0
  while total_sent < size:
    sent = sock.send(buffer[total_sent:])
    if sent == 0:
      raise RuntimeError("[my_send] socket connection broken")
    total_sent = total_sent + sent

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

def send_with_separator(sock, data, separator = '|'):
  my_send(sock, data, len(data))
  my_send(sock, separator.encode(), len(separator.encode()))

def upload_file(server_address, src, name):
  print('TCP: upload_file({}, {}, {})'.format(server_address, src, name))

  # Creation / Connection
  print('Attempting to connect to server socket server on {}'.format(server_address))
  try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)
  except Exception as e:
    print('ERROR: could not connect to server at {}'.format(server_address))
    print('{}'.format(e))
  print('Client connected successfully {}'.format(sock))

  # 0. Send command
  cmd_buffer = UPLOAD_CMD.encode()
  my_send(sock, cmd_buffer, len(cmd_buffer))

  file_name_buffer = name.encode()

  # 1. Send file name
  print('Sending file name "{}"'.format(name))
  send_with_separator(sock, file_name_buffer)



  # Destruction
  destroy_socket(sock, server_address)
