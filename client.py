import socket
import threading

# Konfigurácia
PORT = 55777
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
            print(f"{message}")
        except Exception as e:
            print("Chyba v príjme:", e)
            break
        except KeyboardInterrupt as e:
            print("Končím s počúvaním")
            break

def send_messages(sock, addr, nick):
    """Posiela správy načítané z konzoly"""
    while True:
        try:
            message = input()
            full_message = f"{nick}: {message}"
            bytes = full_message.encode('utf-8')
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

    # Prihlásenie na server
    host = input("Zadaj IP adresu servera: ")
    server_addr = (host, PORT)
    nick = input("Zadaj svoju prezývku: ").strip() or "Fero"

    # Najprv pošlem HELLO, aby sa automaticky priradil port
    sock.sendto(f"Práve sa pripojil: {nick}".encode('utf-8'), server_addr)

    # Spustíme vlákno na prijímanie správ
    thread = threading.Thread(target=receive_messages, args= (sock,), daemon=True)
    thread.start()

    ## Posielaj správy
    send_messages(sock, server_addr, nick)

    print("Vypínam klienta...")
    sock.close()

if __name__ == "__main__":
    main()