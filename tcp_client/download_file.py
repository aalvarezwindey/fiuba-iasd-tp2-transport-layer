from utils.tcp_client_connection import TCPClientConnection
import os

DOWNLOAD_CMD = '2'
ERROR_FILE_DOES_NOT_EXIST = '-1'
OK_RESPONSE = 'ok'
ERROR_RESPONSE = 'fail'

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
    os.unlink(file_downloaded.name)
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
  file_downloaded.close()
  tcp_client_connection.close_read()
  print('Finish downloading the file')

  # 4. Telling the server that everything is OK
  # Check the stored file is of the same size as expected
  with open(dst, "rb") as the_file:
    the_file.seek(0, os.SEEK_END)
    file_size = the_file.tell()
    the_file.seek(0, os.SEEK_SET)

    if not file_size == int(file_size_str):
      tcp_client_connection.send_with_separator(ERROR_RESPONSE.encode())
      tcp_client_connection.close_write()
      raise ValueError('File stored is of {} bytes and it is expected to be of {} bytes'.format(file_size, file_size_str))

  tcp_client_connection.send_with_separator(OK_RESPONSE.encode())
  tcp_client_connection.close_write()
  tcp_client_connection.destroy()
  return 0
  
