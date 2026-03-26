import socket
import struct
import json
import threading
import queue
import pygame
import random
import sys
import time

# ===================== PROTOKOL =====================
def send_message(sock: socket.socket, msg: dict):
    data = json.dumps(msg).encode("utf-8")
    length = struct.pack("!I", len(data))
    sock.sendall(length + data)

def recv_message(sock: socket.socket) -> dict | None:
    # 1. hlavička 4 bajty
    header = b""
    while len(header) < 4:
        chunk = sock.recv(4 - len(header))
        if not chunk:
            return None
        header += chunk
    length = struct.unpack("!I", header)[0]

    # 2. dáta presne 'length' bajtov
    data = b""
    while len(data) < length:
        chunk = sock.recv(length - len(data))
        if not chunk:
            return None
        data += chunk
    return json.loads(data.decode("utf-8"))
# ====================================================

GRID_SIZE = 4
CELL_SIZE = 50
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 900

BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
RED = (255, 0, 0)
GRAY = (180, 180, 180)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Server - Battleship (multiplayer)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)
    big_font = pygame.font.SysFont(None, 48)

    # ===================== GENEROVANIE LODÍ =====================
    ship_fleet = []          # list of sets: každá loď = set pozícií, ktoré ešte nie sú zasiahnuté
    occupied = set()         # pomocná množina pre kontrolu dotykov

    ship_specs = [(3, 1)]   # (dĺžka, počet lodí)

    for length, count in ship_specs:
        for _ in range(count):
            placed = False
            for attempt in range(1000):
                horizontal = random.choice([True, False])
                if horizontal:
                    x = random.randint(0, GRID_SIZE - length)
                    y = random.randint(0, GRID_SIZE - 1)
                    positions = [(x + i, y) for i in range(length)]
                else:
                    x = random.randint(0, GRID_SIZE - 1)
                    y = random.randint(0, GRID_SIZE - length)
                    positions = [(x, y + i) for i in range(length)]

                pos_set = set(positions)

                # 1. kontrola prekrývania
                if pos_set & occupied:
                    continue

                # 2. kontrola dotyku (ani vrcholy) – 8 susedov
                touches = False
                for px, py in positions:
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            if dx == 0 and dy == 0:
                                continue
                            nx, ny = px + dx, py + dy
                            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and (nx, ny) in occupied:
                                touches = True
                                break
                        if touches:
                            break
                    if touches:
                        break
                if touches:
                    continue

                # OK – umiestnime loď
                ship_fleet.append(pos_set.copy())
                occupied.update(pos_set)
                placed = True
                break

            if not placed:
                print(f"⚠️  Varovanie: Nepodarilo sa umiestniť {length}-políčkovú loď!")

    print(f"✅ Umiestnených {len(ship_fleet)} lodí (bez dotykov).")
    # ============================================================

    hit_cells = set()        # zasiahnuté políčka lodí
    miss_cells = set()       # minuté políčka (voda)
    players = {}             # socket → {"name": str, "score": int}
    message_queue = queue.Queue()

    # Server socket
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(("0.0.0.0", 12345))
    server_sock.listen(5)
    print("🚀 Server beží na 0.0.0.0:12345")

    def acceptor_loop():
        while True:
            try:
                client_sock, addr = server_sock.accept()
                print(f"✅ Pripojený klient: {addr}")
                threading.Thread(target=client_handler, args=(client_sock, message_queue), daemon=True).start()
            except:
                break

    def client_handler(client_sock, q):
        while True:
            msg = recv_message(client_sock)
            if msg is None:
                q.put((client_sock, {"type": "disconnect"}))
                break
            q.put((client_sock, msg))

    threading.Thread(target=acceptor_loop, daemon=True).start()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False

        # Spracovanie správ z queue
        while not message_queue.empty():
            try:
                sock, msg = message_queue.get_nowait()

                if msg.get("type") == "disconnect":
                    players.pop(sock, None)
                    sock.close()
                    continue

                if msg.get("type") != "guess":
                    continue

                player_name = msg.get("player", "Anonymous")
                x = msg.get("x")
                y = msg.get("y")

                if not (0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE):
                    send_message(sock, {"type": "error", "msg": "Neplatné súradnice!"})
                    continue

                # Pridáme hráča (ak ešte nie je) – zobrazí sa v zozname pripojených
                if sock not in players:
                    players[sock] = {
                        "name": player_name,
                        "score": 0,
                        "attempts": 0,
                        "last_shot_time": 0.0
                    }

                current_time = time.time()
                if current_time - players[sock]["last_shot_time"] < 2.0:
                    send_message(sock, {
                        "type": "error",
                        "msg": "Príliš rýchlo! Počkaj 2 sekundy medzi strelami."
                    })
                    continue

                # Aktualizácia času a počtu pokusov
                players[sock]["last_shot_time"] = current_time
                players[sock]["attempts"] += 1

                pos = (x, y)

                if pos in hit_cells or pos in miss_cells:
                    send_message(sock, {"type": "result", "hit": False, "msg": "Už si to skúšal!"})
                    continue

                # Spracovanie strely
                is_hit = False
                sunk = False
                for ship in ship_fleet:
                    if pos in ship:
                        is_hit = True
                        ship.remove(pos)
                        hit_cells.add(pos)
                        if len(ship) == 0:
                            sunk = True
                        break

                if not is_hit:
                    miss_cells.add(pos)

                # Odpoveď klientovi
                if is_hit:
                    score = players[sock]["score"]
                    if sunk:
                        players[sock]["score"] += 1
                        score = players[sock]["score"]
                        print(f"🔥 {player_name} POTOPIL loď na ({x},{y})! Skóre: {score}")
                    else:
                        print(f"🔥 {player_name} zasiahol ({x},{y})")
                    resp = {
                        "type": "result",
                        "hit": True,
                        "sunk": sunk,
                        "x": x,
                        "y": y,
                        "score": score
                    }
                else:
                    print(f"💧 {player_name} minul ({x},{y})")
                    resp = {
                        "type": "result",
                        "hit": False,
                        "sunk": False,
                        "x": x,
                        "y": y,
                        "score": players[sock]["score"]
                    }

                send_message(sock, resp)

            except:
                continue

        # ===================== KRESLENIE =====================
        screen.fill(BLACK)

        # Mriežka
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                rect = pygame.Rect(50 + x * CELL_SIZE, 50 + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pos = (x, y)

                if pos in hit_cells:
                    pygame.draw.rect(screen, RED, rect)
                    pygame.draw.line(screen, WHITE, rect.topleft, rect.bottomright, 4)
                    pygame.draw.line(screen, WHITE, rect.topright, rect.bottomleft, 4)
                elif pos in miss_cells:
                    pygame.draw.rect(screen, GRAY, rect)
                else:
                    pygame.draw.rect(screen, BLUE, rect)
                pygame.draw.rect(screen, WHITE, rect, 2)

        # Popisky osí
        for i in range(GRID_SIZE):
            txt = font.render(str(i), True, WHITE)
            screen.blit(txt, (50 + i * CELL_SIZE + 15, 20))      # stĺpce
            screen.blit(txt, (20, 50 + i * CELL_SIZE + 15))      # riadky

        # Panel s pripojenými hráčmi a skóre
        pygame.draw.rect(screen, (30, 30, 30), (900, 50, 280, 500))
        title = font.render("HRÁČI:", True, GREEN)
        screen.blit(title, (920, 70))

        y_pos = 110
        for data in players.values():
            txt = font.render(
                f"{data['name']}: {data['score']} (pokusy: {data['attempts']})",
                True, WHITE
            )
            screen.blit(txt, (920, y_pos))
            y_pos += 35

        # Stav hry
        if all(len(ship) == 0 for ship in ship_fleet):
            win_txt = big_font.render("VŠETKY LODE POTOPENÉ!", True, GREEN)
            screen.blit(win_txt, (280, 220))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    server_sock.close()
    sys.exit()

if __name__ == "__main__":
    main()