import socket
import time
import csv
import statistics

# Mininet host addresses
CONTENT_SERVER = "10.0.0.3"
CONTENT_PORT = 9000

PROXY_SERVER = "10.0.0.2"
PROXY_PORT = 8080

REQUEST = "/news"
BLOCKED_REQUEST = "/gambling"
ITERATIONS = 30

def send_request(host, port, path):
    """Send one TCP request and measure its response time."""
    start = time.perf_counter()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.settimeout(5)
        client.connect((host, port))
        client.sendall(path.encode())

        response = b""
        while True:
            data = client.recv(4096)
            if not data:
                break
            response += data

    elapsed = (time.perf_counter() - start) * 1000
    return response.decode(errors="replace"), elapsed

def benchmark(name, host, port):
    times = []

    print(f"\nTesting {name}...")

    for i in range(ITERATIONS):
        response, elapsed = send_request(host, port, REQUEST)
        times.append(elapsed)

    total_time = sum(times) / 1000
    average = statistics.mean(times)
    minimum = min(times)
    maximum = max(times)
    throughput = ITERATIONS / total_time

    print(f"Requests completed: {ITERATIONS}")
    print(f"Average response time: {average:.3f} ms")
    print(f"Minimum response time: {minimum:.3f} ms")
    print(f"Maximum response time: {maximum:.3f} ms")
    print(f"Throughput: {throughput:.2f} requests/second")

    return {
        "Method": name,
        "Requests": ITERATIONS,
        "Average_ms": round(average, 3),
        "Minimum_ms": round(minimum, 3),
        "Maximum_ms": round(maximum, 3),
        "Throughput_req_sec": round(throughput, 2)
    }

if __name__ == "__main__":
    print("===== PROXY PERFORMANCE EVALUATION =====")

    results = []

    results.append(
        benchmark("Direct Server", CONTENT_SERVER, CONTENT_PORT)
    )

    results.append(
        benchmark("Through Proxy", PROXY_SERVER, PROXY_PORT)
    )

    print("\nTesting content filtering...")
    response, elapsed = send_request(
        PROXY_SERVER, PROXY_PORT, BLOCKED_REQUEST
    )

    if "403" in response or "FORBIDDEN" in response.upper():
        filtering_result = "PASS - Blocked request rejected"
    else:
        filtering_result = "FAIL - Blocked request was not rejected"

    print(filtering_result)
    print(f"Filtering response time: {elapsed:.3f} ms")

    with open("performance_results.csv", "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    print("\nResults saved to performance_results.csv")
    print("===== EVALUATION COMPLETE =====")
