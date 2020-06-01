import socket
import signal
import sys

def destroy_socket(sock, server_address):
  print('Attempting to close socket server {}'.format(server_address))
  try:
    sock.close()
  except Exception as e:
    print('ERROR: could not destroy socket server')
    print('{}'.format(e))
  print('Server socket destroyed {}'.format(sock))

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
    conn, addr = sock.accept()

  
  
  
