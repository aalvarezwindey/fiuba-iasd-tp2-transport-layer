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

  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.bind(address)
  sock.listen(1)

  while True:
    conn, addr = sock.accept()
    if not conn:
      break

    print("Accepted connection from {}".format(addr))

    filename = "./file-{}.bin".format(get_timestamp())
    f = open(filename, "wb")
    bytes_received = 0

    size = int(conn.recv(CHUNK_SIZE).decode())
    conn.send(b'start')

    while bytes_received < size:
      data = conn.recv(CHUNK_SIZE)
      bytes_received += len(data)
      f.write(data)

    print("Received file {}".format(filename))

    # Send number of bytes received
    conn.send(str(bytes_received).encode())

    f.close()

  sock.close()

if __name__ == "__main__":
    main()
