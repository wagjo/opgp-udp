import socket

def send_messages(sock, addr):
    """Posiela správy načítané z konzoly"""
    print(f"Píš správy na {addr[0]}:{addr[1]}")
    while True:
        try:
            message = input(">> ")
            bytes = message.encode('utf-8')
            sock.sendto(bytes, addr)

        except Exception as e:
            print("Chyba v posielaní:", e)
            break
        except KeyboardInterrupt as e:
            print("Končím s posielaním")
            break

def main():
    # Vytvorenie UDP socketu
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    ## Adresa kam sa budú posielať správy
    host = input("Zadaj IP adresu, kam budeš posielať správy: ")
    port = input("Zadaj port, na ktorý budeš posielať správy: ")
    addr = (host, int(port))

    ## Posielaj správy
    send_messages(sock, addr)

    print("Vypínam server...")
    sock.close()

if __name__ == "__main__":
    main()
