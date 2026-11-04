import socket
import threading
import json
import csv
import os
import time
from policy_manager import is_allowed

HOST = "0.0.0.0"
PORT = 8080

CONTENT_SERVER = "10.0.0.3"
CONTENT_PORT = 9000

POLICY_FILE = "policies.json"
LOG_FILE = "logs/access_logs.csv"


def log_request(client, request, decision, duration):
    new_file = not os.path.exists(LOG_FILE)

    with open(LOG_FILE, "a", newline="") as file:
        writer = csv.writer(file)

        if new_file:
            writer.writerow([
                "Client",
                "Request",
                "Decision",
                "Time_ms"
            ])

        writer.writerow([
            client,
            request,
            decision,
            round(duration * 1000, 3)
        ])

def forward_request(request):
    server = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    server.settimeout(5)

    try:
        server.connect((CONTENT_SERVER, CONTENT_PORT))
        server.sendall(request.encode())

        response = server.recv(4096).decode()

        return response

    finally:
        server.close()

def handle_client(conn, address):
    start_time = time.perf_counter()

    try:
        request = conn.recv(4096).decode().strip()

        print(f"[PROXY] Request from {address}: {request}")

        if not request:
            return

        if is_allowed(request):

            response = forward_request(request)

            decision = "ALLOWED"

            print("[PROXY] Request allowed")

        else:

            response = "403 FORBIDDEN: Request blocked by proxy"

            decision = "BLOCKED"

            print("[PROXY] Request blocked")

        conn.sendall(response.encode())

        duration = time.perf_counter() - start_time

        log_request(
            address[0],
            request,
            decision,
            duration
        )

    except Exception as e:
        print("[PROXY ERROR]", e)

        try:
            conn.sendall(b"500 Internal Proxy Error")
        except OSError:
            pass

    finally:
        conn.close()

def start_proxy():

    os.makedirs("logs", exist_ok=True)

    proxy = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    proxy.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    proxy.bind((HOST, PORT))
    proxy.listen(20)

    print(f"[PROXY] Listening on port {PORT}")

    while True:

        conn, address = proxy.accept()

        thread = threading.Thread(
            target=handle_client,
            args=(conn, address),
            daemon=True
        )

        thread.start()

if __name__ == "__main__":
    start_proxy()
