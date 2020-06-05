from utils.tcp_server_listener import TCPServerListener
from utils.tcp_server_connection import TCPServerConnection

import signal
import sys

COMMAND_LEN = 1
UPLOAD_CMD = '1'
DOWNLOAD_CMD = '2'

def handle_upload(tcp_server_connection):
  print('Handling upload command')

  # 1. Receive file name
  file_name = tcp_server_connection.receive_until_separator()
  print('File name received "{}"'.format(file_name))

  # 2. Receive the file size
  file_size_str = tcp_server_connection.receive_until_separator()
  print('File size to receive {}'.format(file_size_str))

  # 3. Receive the file
  tcp_server_connection.receive_file(int(file_size_str), file_name)


def handle_download(conn):
  print('Handling download command')


def handle_default(command):
  print('Unknown command {}. Just ignoring it'.format(command))

COMMAND_HANDLERS = {
  UPLOAD_CMD: handle_upload,
  DOWNLOAD_CMD: handle_download
}



def start_server(server_address, storage_dir):
  tcp_server_listener = TCPServerListener(server_address)

  def stop_server(sig, frame):
      tcp_server_listener.destroy()
      sys.exit(0)

  # Register handler for SIGINT (Ctrl + C)
  signal.signal(signal.SIGINT, stop_server)

  while True:
    print('Waiting a new connection')
    tcp_server_connection = tcp_server_listener.accept()

    if not tcp_server_connection:
      tcp_server_listener.destroy()
      break

    print('New connection received:')
    tcp_server_connection.describe()

    command = tcp_server_connection.receive(COMMAND_LEN).decode()

    print('Received command {}'.format(command))

    handler = COMMAND_HANDLERS.get(command)

    if handler == None:
      handle_default(command)
      continue
    
    handler(tcp_server_connection)

    