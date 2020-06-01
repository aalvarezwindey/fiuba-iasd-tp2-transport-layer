import socket

def destroy_socket(sock, server_address):
  print('Attempting to finish connection with {}'.format(server_address))
  try:
    sock.close()
  except Exception as e:
    print('ERROR: could not destroy socket client')
    print('{}'.format(e))
  print('Client socket destroyed successfully {}'.format(sock))

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

  # Destruction
  destroy_socket(sock, server_address)
