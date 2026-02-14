import socket

# Konfigurácia
HOST = "0.0.0.0"  # počúva na všetkých rozhraniach
PORT = 55777  # ľubovoľný voľný port > 1024
BUFFER_SIZE = 1024

clients = set() # množina adries (IP, port) pripojených klientov

def broadcast(sock, bytes):
    """Pošle správu všetkým klientom"""
    for client_addr in list(clients):
        try:
            sock.sendto(bytes, client_addr)
        except Exception as e:
            print(e)

def receive_messages(sock):
    """Načítava nové správy a posiela ich všetkým klientom"""
    while True:
        try:
            # Prijatie správy (datagramu)
            data, addr = sock.recvfrom(BUFFER_SIZE)
            # Dekódovanie správy
            message = data.decode('utf-8')
            # Pridáme klienta do zoznamu
            clients.add(addr)
            # Správa, ktorú pošleme klientom
            message = f"[{addr[0]}:{addr[1]}] {message}"
            # Zalogujeme
            print(message)
            # Pošleme všetkým
            broadcast(sock, message.encode('utf-8'))
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