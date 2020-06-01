import os
import argparse
import socket

def parse_arguments():
  parser = argparse.ArgumentParser()

  parser.add_argument("-f", "--file", help="the file to send", required=True)
  parser.add_argument("-H", "--host", default="127.0.0.1")
  parser.add_argument("-P", "--port", type=int, default="8080")
  # parser.add_argument("-O", "--own-host", default="127.0.0.1")
  # parser.add_argument("-p", "--own-port", type=int, default="8081")

  return parser.parse_args()

CHUNK_SIZE = 1024

def main():
  args = parse_arguments()
  server_address = (args.host, args.port)

  f = open(args.file, "rb")
  f.seek(0, os.SEEK_END)
  size = f.tell()
  f.seek(0, os.SEEK_SET)

  print("Sending {} bytes from {}".format(size, args.file))

  # Inicializo el cliente

  # Transferencia del archivo

  f.close()


if __name__ == "__main__":
    main()
