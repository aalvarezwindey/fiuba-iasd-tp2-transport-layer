from utils.tcp_server_listener import TCPServerListener
from utils.tcp_server_connection import TCPServerConnection

import signal
import sys
import os

COMMAND_LEN = 1
UPLOAD_CMD = '1'
DOWNLOAD_CMD = '2'

def handle_upload(tcp_server_connection, storage_dir):
  print('Handling upload command')

  # 1. Receive file name
  file_name = tcp_server_connection.receive_until_separator()
  print('File name received "{}"'.format(file_name))

  # 2. Receive the file size
  file_size_str = tcp_server_connection.receive_until_separator()
  print('File size to receive {}'.format(file_size_str))

  # 3. Receive the file
  # SUPUESTO: storage_dir must not cotain / at end
  new_file = open("{}{}".format(storage_dir, file_name), "wb")
  tcp_server_connection.receive_file(new_file, int(file_size_str))


def handle_download(conn, storage_dir):
  print('Handling download command')


def handle_default(command, storage_dir):
  print('Unknown command {}. Just ignoring it'.format(command))

COMMAND_HANDLERS = {
  UPLOAD_CMD: handle_upload,
  DOWNLOAD_CMD: handle_download
}



def start_server(server_address, storage_dir):
  if not os.path.isdir(storage_dir):
    print("Storage dir do not exist.")
    return
    
  storage_dir = storage_dir + '/' if not storage_dir.endswith('/') else storage_dir

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
      handle_default(command, storage_dir)
      continue
    
    handler(tcp_server_connection, storage_dir)

    