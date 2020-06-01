import argparse
import socket
import time
from constants import CHUNK_SIZE

def get_timestamp():
  return int(round(time.time()*1000))

def parse_arguments():
  parser = argparse.ArgumentParser()

  parser.add_argument("-H", "--host", default="127.0.0.1")
  parser.add_argument("-P", "--port", type=int, default="8080")

  return parser.parse_args()

def main():
  args = parse_arguments()
  address = (args.host, args.port)

  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  sock.bind(address)

  while True:
    data, addr = sock.recvfrom(CHUNK_SIZE)
    size = int(data.decode())
    print("Incoming file with size {} from {}".format(size, addr))

    filename = "./file-{}.bin".format(get_timestamp())
    f = open(filename, "wb")
    bytes_received = 0

    sock.sendto(b'start', addr)

    while bytes_received < size:
      data, addr = sock.recvfrom(CHUNK_SIZE)
      bytes_received += len(data)
      f.write(data)

    print("Received file {}".format(filename))

    # Send number of bytes received
    sock.sendto(str(bytes_received).encode(),addr)

    f.close()

  sock.close()

if __name__ == "__main__":
    main()
