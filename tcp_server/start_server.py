from utils.tcp_server_listener import TCPServerListener
from utils.tcp_server_connection import TCPServerConnection

import signal
import sys
import os

import time

COMMAND_LEN = 1
UPLOAD_CMD = '1'
DOWNLOAD_CMD = '2'

ERROR_FILE_DOES_NOT_EXIST = '-1'
OK_RESPONSE = 'ok'
ERROR_RESPONSE = 'fail'

def handle_upload(tcp_server_connection, storage_dir):
  print('Handling upload command')

  # 1. Receive file name
  file_name = tcp_server_connection.receive_until_separator()
  print('File name received "{}"'.format(file_name))

  # 2. Receive the file size
  file_size_str = tcp_server_connection.receive_until_separator()
  print('File size to receive {}'.format(file_size_str))

  # 3. Receive the file
  file_path = "{}{}".format(storage_dir, file_name)
  print('Start receiving the file at: "{}"'.format(file_path))

  with open(file_path, "wb") as new_file:
    tcp_server_connection.receive_file(new_file, int(file_size_str))
    tcp_server_connection.close_read()
    
  print('Finish receiving the file')
  # 4. Telling the client that everything is OK
  # Check the stored file is of the same size
  with open(file_path, "rb") as the_file:
    the_file.seek(0, os.SEEK_END)
    file_size = the_file.tell()
    the_file.seek(0, os.SEEK_SET)

    if not file_size == int(file_size_str):
      tcp_server_connection.send_with_separator(ERROR_RESPONSE.encode())
      tcp_server_connection.close_write()
      raise ValueError('File stored is of {} bytes and it is expected to be of {} bytes'.format(file_size, file_size_str))

  tcp_server_connection.send_with_separator(OK_RESPONSE.encode())
  tcp_server_connection.close_write()
  tcp_server_connection.destroy()


def handle_download(tcp_server_connection, storage_dir):
  print('Handling download command')

  # 1. Receive file name to download
  file_name = tcp_server_connection.receive_until_separator()
  file_path = '{}{}'.format(storage_dir, file_name)
  print('File to download "{}"'.format(file_name))

  if not os.path.isfile(file_path):
    # File does not exists
    print('Sending error code {}: file does not exist'.format(ERROR_FILE_DOES_NOT_EXIST))
    tcp_server_connection.send_with_separator(str(ERROR_FILE_DOES_NOT_EXIST).encode())
  else:
    file_to_download = open(file_path, "rb")
    file_to_download.seek(0, os.SEEK_END)
    file_size = file_to_download.tell()
    file_to_download.seek(0, os.SEEK_SET)

    # 2. Send file size
    print('Sending file size of {} bytes'.format(file_size))
    tcp_server_connection.send_with_separator(str(file_size).encode())

    # 3. Sending the file
    print('Sending the file')
    tcp_server_connection.send_file(file_to_download, file_size)
    tcp_server_connection.close_write()
    print('Finish sending the file')

    # 4. Waiting server finish processing
    print('Waiting client finish downloading')
    client_response = tcp_server_connection.receive_until_separator()
    print('Client response: {}'.format(client_response))
    if (not client_response == OK_RESPONSE):
      tcp_server_connection.close_read()
      raise ValueError('Client {} fail downloading'.format(tcp_server_connection.describe()))

    tcp_server_connection.close_read()
    tcp_server_connection.destroy()




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
    
  # SUPUESTO: storage_dir puede contener o no una / al final del path
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

    try:
      if not tcp_server_connection:
        tcp_server_listener.destroy()
        break

      print('New connection received: {}'.format(tcp_server_connection.describe()))

      command = tcp_server_connection.receive(COMMAND_LEN).decode()

      print('Received command {}'.format(command))

      handler = COMMAND_HANDLERS.get(command)

      if handler == None:
        handle_default(command, storage_dir)
        continue
      
      handler(tcp_server_connection, storage_dir)
    except Exception as e:
      if tcp_server_connection:
        print('ERROR: during connection with {}'.format(tcp_server_connection.describe()))
        tcp_server_connection.destroy()
      
      print('{}'.format(e))
      # If any client fails, the server keeps attending new clients
      continue


  tcp_server_listener.destroy()
    