import io
import socket

import pygame

PORT = 5005
MAX_DATAGRAM_SIZE = 65507


def main():
    pygame.init()
    screen = pygame.display.set_mode((200, 200))
    clock = pygame.time.Clock()

    # UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', PORT))
    sock.settimeout(0.5)

    print(f"Listening on UDP port {PORT} (broadcast)…")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        try:
            data, addr = sock.recvfrom(MAX_DATAGRAM_SIZE)

            if not data:
                continue

            print(f"Received {len(data)} bytes from {addr}")

            try:
                # Load image directly from bytes
                file_like = io.BytesIO(data)
                surf = pygame.image.load(file_like).convert()

                # Create / update window size if needed
                w, h = surf.get_size()
                if screen is None or screen.get_size() != (w, h):
                    screen = pygame.display.set_mode((w, h))
                    pygame.display.set_caption("Received UDP Image")

                screen.blit(surf, (0, 0))
                pygame.display.flip()

                print(f"Displayed: {w}×{h}")

            except Exception as e:
                print("Cannot display image:", e)

        except TimeoutError:
            print(".", end="", flush=True)
            pass
        except BlockingIOError:
            pass  # no data ready
        except Exception as e:
            print("Socket error:", e)

        clock.tick(10)

    pygame.quit()
    sock.close()
    print("Exited.")


if __name__ == "__main__":
    main()
