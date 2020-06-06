from utils.tcp_client_connection import TCPClientConnection
import os

DOWNLOAD_CMD = '2'
ERROR_FILE_DOES_NOT_EXIST = '-1'

def download_file(server_address, name, dst):
  print('TCP: download_file({}, {}, {})'.format(server_address, name, dst))

  try:
    file_downloaded = open(dst, "wb")
  except Exception as e:
    print('ERROR: could not download file on "{}"'.format(dst))
    print('{}'.format(e))
    return -1

  
  try:
    tcp_client_connection = TCPClientConnection(server_address)
  except Exception as e:
    print('ERROR: could not connect with server {}'.format(server_address))
    print('{}'.format(e))
    return -1

  # 0. Send command
  cmd_buffer = DOWNLOAD_CMD.encode()
  tcp_client_connection.send(cmd_buffer, len(cmd_buffer))

  # 1. Send file name to download
  file_name_buffer = name.encode()
  print('Sending file name to download "{}"'.format(name))
  tcp_client_connection.send_with_separator(file_name_buffer)

  # 2. Receive file size
  file_size_str = tcp_client_connection.receive_until_separator()

  if file_size_str == ERROR_FILE_DOES_NOT_EXIST:
    print('ERROR: Server does not has file "{}"'.format(name))
    os.unlink(file_downloaded.name)
    return -1

  print('File size to receive {}'.format(file_size_str))

  # 3. Downloading the file
  print('Start downloading the file')
  tcp_client_connection.receive_file(file_downloaded, int(file_size_str))
  print('Finish downloading the file')

  tcp_client_connection.destroy()
  return 0
  
