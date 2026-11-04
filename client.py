import socket

PROXY_HOST = "10.0.0.2"
PROXY_PORT = 8080

def send_request():

    print("\n===== PROXY CONTENT FILTERING SYSTEM =====")

    print("Available requests:")
    print("1. /news")
    print("2. /education")
    print("3. /sports")
    print("4. /shopping")
    print("5. /gambling")
    print("6. /malware")

    request = input("\nEnter request path: ").strip()

    client = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    try:

        client.connect((PROXY_HOST, PROXY_PORT))

        client.sendall(request.encode())

        response = client.recv(4096).decode()

        print("\n===== SERVER RESPONSE =====")
        print(response)

    except Exception as e:

        print("Connection error:", e)

    finally:

        client.close()

if __name__ == "__main__":
    send_request()
