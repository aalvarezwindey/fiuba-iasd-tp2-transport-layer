import argparse
import socket
import time

def get_timestamp():
  return int(round(time.time()*1000))

def parse_arguments():
  parser = argparse.ArgumentParser()

  parser.add_argument("-H", "--host", default="127.0.0.1")
  parser.add_argument("-P", "--port", type=int, default="8080")

  return parser.parse_args()

CHUNK_SIZE = 1024

def main():
  args = parse_arguments()
  address = (args.host, args.port)

  # Inicializo el servidor

  while True:
    # Acepto conexiones

    filename = "./file-{}.bin".format(get_timestamp())
    f = open(filename, "wb")
    bytes_received = 0

    # Recibo el archivo

    print("Received file {}".format(filename))

    f.close()

  # Cierro el socket

if __name__ == "__main__":
    main()
