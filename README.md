# Proxy and Content Filtering System

## 1. Project Overview

This project implements a Proxy and Content Filtering System using Python, Mininet, Open vSwitch and an SDN controller.

The system monitors client requests, applies content filtering policies, forwards permitted requests to a content server and blocks restricted requests.

## 2. Objectives

- Implement a proxy server for handling client requests.
- Apply content filtering using configurable policies.
- Block requests containing restricted keywords and paths.
- Maintain access logs of allowed and blocked requests.
- Create a software-defined network using Mininet and Open vSwitch.
- Use an SDN controller for network forwarding.
- Evaluate direct and proxy-based communication performance.

## 3. System Architecture

The network consists of three Mininet hosts:

- h1: Client (10.0.0.1)
- h2: Proxy Server (10.0.0.2)
- h3: Content Server (10.0.0.3)

An Open vSwitch connects the hosts and communicates with the remote SDN controller.

## 4. Technologies Used

- Python 3
- Mininet
- Open vSwitch
- OS-Ken SDN Controller
- OpenFlow 1.3
- JSON
- CSV

## 5. Project Files

| File | Description |
|---|---|
| client.py | Sends requests to the proxy |
| proxy_server.py | Receives, filters and forwards requests |
| content_server.py | Provides content to permitted requests |
| policy_manager.py | Loads and evaluates filtering policies |
| policies.json | Stores blocked keywords and paths |
| sdn_controller.py | Implements SDN-based MAC learning and forwarding |
| topology.py | Defines the Mininet network topology |
| performance.py | Measures response time and throughput |
| performance_results.csv | Stores performance measurements |
| logs/access_logs.csv | Records client requests and filtering decisions |
| test_cases.md | Documents project testing |

## 6. Content Filtering Policies

The system uses policies.json.

Blocked keywords:
- gambling
- malware
- adult
- phishing

Blocked paths:
- /blocked
- /malware

Default action: ALLOW

Requests matching a blocked keyword or path are rejected with a 403 Forbidden response.

## 7. Installation and Setup

Activate the Python virtual environment:

    source .venv/bin/activate

Install the required Python dependencies if they are not already installed.

Mininet, Open vSwitch and OS-Ken must also be available on the system.

## 8. Execution

### Terminal 1: Start the SDN Controller

    cd ~/Desktop/Proxy_Content_Filtering
    source .venv/bin/activate
    osken-manager sdn_controller.py --ofp-tcp-listen-port 6653

### Terminal 2: Start Mininet

    cd ~/Desktop/Proxy_Content_Filtering
    sudo mn --custom topology.py --topo proxytopo --controller=remote,ip=127.0.0.1,port=6653 --switch ovs,protocols=OpenFlow13

### Inside Mininet: Start the Content Server

    h3 python3 -u /home/sathvik/Desktop/Proxy_Content_Filtering/content_server.py

### Inside Mininet: Start the Proxy Server

    h2 python3 -u /home/sathvik/Desktop/Proxy_Content_Filtering/proxy_server.py

### Inside Mininet: Run the Client

    h1 python3 /home/sathvik/Desktop/Proxy_Content_Filtering/client.py

Enter a request path when prompted, such as /news or /gambling.

## 9. Performance Evaluation

Run the performance evaluation from the Mininet client:

    h1 python3 /home/sathvik/Desktop/Proxy_Content_Filtering/performance.py

The program compares direct server communication with communication through the proxy using average, minimum and maximum response times and throughput.

Results are saved in performance_results.csv.

## 10. Expected Behaviour

- Permitted requests are forwarded to the content server.
- Restricted requests are blocked by the proxy.
- Access decisions are recorded in the CSV access log.
- The SDN controller manages switch forwarding through OpenFlow.

## 11. Conclusion

The project demonstrates application-level content filtering through a Python proxy and SDN-based network forwarding using Mininet, Open vSwitch and OS-Ken. Performance measurements provide a comparison between direct and proxy-based communication.
DYNAMIC SDN INTEGRATION

The project integrates the proxy application with the SDN controller
using a shared access log.

When a client requests blocked content:

1. The proxy identifies the blocked request.
2. The proxy returns HTTP 403 Forbidden.
3. The request is recorded in access_logs.csv.
4. The SDN controller monitors the access log.
5. The controller identifies the blocked client's IP address.
6. The controller installs an OpenFlow DROP rule in Open vSwitch.

The DROP rule uses priority 100 and blocks IPv4 traffic from the
identified client for 60 seconds.

After 60 seconds, the rule automatically expires, allowing the
client to communicate with the network again.

This demonstrates dynamic application-to-SDN integration.

AUTOMATIC RECOVERY TEST

A blocked client was successfully isolated using an OpenFlow DROP
rule. After the 60-second timeout, the rule disappeared from the
switch flow table and normal network communication was restored.
