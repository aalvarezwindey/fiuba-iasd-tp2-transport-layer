from utils.tcp_client_connection import TCPClientConnection
import os

UPLOAD_CMD = '1'
OK_RESPONSE = 'ok'
ERROR_RESPONSE = 'fail'

def upload_file(server_address, src, name):
  print('TCP: upload_file({}, {}, {})'.format(server_address, src, name))

  print('Attempting to open file {}'.format(src))
  try:
    the_file = open(src, "rb")
    the_file.seek(0, os.SEEK_END)
    file_size = the_file.tell()
    the_file.seek(0, os.SEEK_SET)
  except Exception as e:
    print('ERROR: could not open file at {}'.format(src))
    print('{}'.format(e))
    return -1
  print('File opened successfully')

  try:
    tcp_client_connection = TCPClientConnection(server_address)
  except Exception as e:
    print('ERROR: could not connect with server {}'.format(server_address))
    print('{}'.format(e))
    return -1

  # 0. Send command
  cmd_buffer = UPLOAD_CMD.encode()
  tcp_client_connection.send(cmd_buffer, len(cmd_buffer))

  # 1. Send file name
  file_name_buffer = name.encode()
  print('Sending file name "{}"'.format(name))
  tcp_client_connection.send_with_separator(file_name_buffer)

  # 2. Send file size
  print('Sending file size of {} bytes'.format(file_size))
  tcp_client_connection.send_with_separator(str(file_size).encode())
  
  # 3. Sending the file
  print('Sending the file')
  tcp_client_connection.send_file(the_file, file_size)
  print('Finish sending the file')
  tcp_client_connection.close_write()

  # 4. Waiting server finish processing
  print('Waiting server')
  sv_response = tcp_client_connection.receive_until_separator()
  print('Server response: {}'.format(sv_response))

  tcp_client_connection.close_read()
  tcp_client_connection.destroy()

  if (not sv_response == OK_RESPONSE):
    return -1

  return 0
