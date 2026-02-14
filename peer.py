import socket
import threading

# Konfigurácia
HOST = "0.0.0.0" # počúva na všetkých rozhraniach
PORT = 55777 # ľubovoľný voľný port > 1024
BUFFER_SIZE = 1024

def receive_messages(sock):
    """Načítava nové správy a vypisuje ich do konzoly"""
    while True:
        try:
            # Prijatie správy (datagramu)
            data, addr = sock.recvfrom(BUFFER_SIZE)
            # Dekódovanie správy
            message = data.decode('utf-8')
            # Vypísanie správy do konzoly
            print(f"!!! Nová správa od {addr[0]}:{addr[1]}: {message}\n>> ", end='')
        except Exception as e:
            print("Chyba v príjme:", e)
            break
        except KeyboardInterrupt as e:
            print("Končím s počúvaním")
            break

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

    # Port na počúvanie
    listen_port = input(f"Zadaj port, na ktorom budeš počúvať (defaultne {PORT}): ")
    if listen_port == "":
        listen_port = PORT
    else:
        listen_port = int(listen_port)

    # Nastavenie počúvania na danej adrese
    listen_addr = (HOST, listen_port)
    sock.bind(listen_addr)
    print(f"Počúvam na {HOST}:{listen_port}")

    # Spustíme vlákno na príjem správ
    thread = threading.Thread(target=receive_messages, args= (sock,), daemon=True)
    thread.start()

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
