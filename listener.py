import socket

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
            print(f"!!! Nová správa od {addr[0]}:{addr[1]}: {message}\n", end='')
        except Exception as e:
            print("Chyba v príjme:", e)
            break
        except KeyboardInterrupt as e:
            print("Končím s počúvaním")
            break

def main():
    # Vytvorenie UDP socketu
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Nastavenie počúvania na danej adrese
    listen_addr = (HOST, PORT)
    sock.bind(listen_addr)
    print(f"Počúvam na {HOST}:{PORT}")

    # Prijímanie správ
    receive_messages(sock)

    # Ukončenie
    print("Vypínam server...")
    sock.close()

if __name__ == "__main__":
    main()
