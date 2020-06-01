import os
import argparse
import socket
from constants import CHUNK_SIZE

def parse_arguments():
  parser = argparse.ArgumentParser()

  parser.add_argument("-f", "--file", help="the file to send", required=True)
  parser.add_argument("-H", "--host", default="127.0.0.1")
  parser.add_argument("-P", "--port", type=int, default="8080")
  parser.add_argument("-O", "--own-host", default="127.0.0.1")
  parser.add_argument("-p", "--own-port", type=int, default="8081")

  return parser.parse_args()

def main():
  args = parse_arguments()
  server_address = (args.host, args.port)
  own_address = (args.own_host, args.own_port)

  f = open(args.file, "rb")
  f.seek(0, os.SEEK_END)
  size = f.tell()
  f.seek(0, os.SEEK_SET)

  print("Sending {} bytes from {}".format(size, args.file))

  # Create socket and connect to server
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  sock.bind(own_address)

  sock.sendto(str(size).encode(), server_address)
  signal, addr = sock.recvfrom(CHUNK_SIZE)

  if signal.decode() != "start":
    print("There was an error on the server")
    return exit(1)

  while True:
    chunk = f.read(CHUNK_SIZE)
    if not chunk:
      break
    sock.sendto(chunk, server_address)

  # Recv amount of data received by the server
  num_bytes, addr = sock.recvfrom(CHUNK_SIZE)

  print("Server received {} bytes".format(num_bytes.decode()))

  f.close()
  sock.close()


if __name__ == "__main__":
    main()
