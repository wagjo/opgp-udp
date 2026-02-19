import os
import random
import socket
import time

BROADCAST_IP = "255.255.255.255"
BROADCAST_IP = '<broadcast>'
BROADCAST_IP = "127.0.0.1"
PORT = 5005


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    IMAGE_PATH = ""

    while True:
        OLD_IMAGE_PATH = IMAGE_PATH
        IMAGE_PATH = "assets/" + random.choice(os.listdir("assets"))

        if IMAGE_PATH == OLD_IMAGE_PATH:
            continue

        if not os.path.exists(IMAGE_PATH):
            print(f"Image not found: {IMAGE_PATH}")
            return

        data = open(IMAGE_PATH, "rb").read()
        print(f"Broadcasting image: {IMAGE_PATH}")
        sock.sendto(data, (BROADCAST_IP, PORT))
        time.sleep(7)
    sock.close()


if __name__ == "__main__":
    main()
