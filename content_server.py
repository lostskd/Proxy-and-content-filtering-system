import socket
import threading

HOST = "0.0.0.0"
PORT = 9000

CONTENT = {
    "/news": "Welcome to the News Service!",
    "/education": "Welcome to the Education Portal!",
    "/sports": "Welcome to the Sports Service!",
    "/shopping": "Welcome to the Shopping Service!",
    "/": "Welcome to the Content Server!"
}

def handle_client(conn, address):
    print(f"[SERVER] Connection from {address}")

    try:
        request = conn.recv(4096).decode().strip()

        print(f"[SERVER] Received: {request}")

        response = CONTENT.get(
            request,
            "404 - Content Not Found"
        )

        conn.sendall(response.encode())

    except Exception as e:
        print("[SERVER ERROR]", e)

    finally:
        conn.close()

def start_server():
    server = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    server.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    server.bind((HOST, PORT))
    server.listen(10)

    print(f"[SERVER] Running on port {PORT}")

    while True:
        conn, address = server.accept()

        thread = threading.Thread(
            target=handle_client,
            args=(conn, address)
        )

        thread.start()

if __name__ == "__main__":
    start_server()
