# Test Cases – Proxy and Content Filtering System

## 1. Objective

To verify the functionality of the proxy server, content filtering policies, SDN network connectivity, access logging and performance evaluation.

## 2. Test Environment

- Operating System: Ubuntu 26.04 LTS
- Python: 3.14.4
- Mininet: 2.3.0
- Open vSwitch: 3.7.1
- SDN Controller: OS-Ken 4.1.1
- OpenFlow Version: 1.3

## 3. Functional Test Cases

| Test ID | Test Description | Input | Expected Result | Observed Result |
|---|---|---|---|---|
| TC01 | Test permitted request | /news | Request allowed | PASS |
| TC02 | Test blocked keyword | /gambling | Request blocked with 403 | PASS |
| TC03 | Test malware filtering | /malware | Request blocked | PASS |
| TC04 | Test education request | /education | Request allowed | PASS |
| TC05 | Test phishing filtering | /phishing | Request blocked | PASS |
| TC06 | Test access logging | Client requests | Request details recorded | PASS |
| TC07 | Test network connectivity | Mininet pingall | All hosts reachable | PASS |
| TC08 | Test SDN controller connection | OpenFlow 1.3 switch | Controller connected | PASS |
| TC09 | Test flow-rule installation | OpenFlow flow table | Forwarding rules installed | PASS |
| TC10 | Test performance evaluation | 30 requests per method | Metrics generated and saved | PASS |

Note: TC03, TC04 and TC05 were verified using the policy manager. TC01, TC02 and TC06 were also tested through the proxy.

## 4. Network Connectivity Results

The Mininet pingall command completed with:

0% packet loss (6/6 packets received).

This confirms connectivity between the three hosts.

## 5. SDN Controller Results

The OpenFlow switch successfully connected to the OS-Ken controller on port 6653.

The flow table displayed:
- Priority 0 table-miss rule forwarding unmatched packets to the controller.
- Priority 1 rules for learned MAC-address forwarding.

## 6. Content Filtering Results

The proxy successfully allowed the /news request and blocked the /gambling request.

The access log recorded the client IP, request path, filtering decision and processing time.

## 7. Performance Evaluation

Thirty requests were tested for each communication method.

| Metric | Direct Server | Through Proxy |
|---|---:|---:|
| Requests | 30 | 30 |
| Average Response Time (ms) | 0.245 | 0.632 |
| Minimum Response Time (ms) | 0.074 | 0.169 |
| Maximum Response Time (ms) | 0.972 | 2.810 |
| Throughput (requests/second) | 4083.25 | 1581.04 |

The proxy introduces additional processing overhead because requests are inspected before being forwarded.

## 8. Conclusion

The tested system successfully demonstrated proxy-based content filtering, request logging, Mininet network connectivity, SDN controller connectivity and performance evaluation.

The functional tests confirmed that permitted requests were allowed and restricted requests were blocked.
TC11: Dynamic SDN Blocking

Objective: Verify that the SDN controller detects blocked requests.

Procedure:
1. Start the SDN controller and Mininet.
2. Send a /gambling request from client h1.
3. Verify that the proxy returns 403 Forbidden.
4. Check the controller terminal for the blocked client's IP.

Expected Result:
The controller detects the blocked event and installs a temporary
OpenFlow DROP rule with priority 100 for client 10.0.0.1.

Actual Result: PASS


TC12: Automatic Recovery

Objective: Verify automatic removal of temporary SDN blocking.

Procedure:
1. Trigger a blocked request from h1.
2. Verify the priority-100 DROP rule using ovs-ofctl.
3. Wait for the 60-second hard timeout.
4. Check the switch flow table again.
5. Send an allowed /news request.

Expected Result:
The temporary DROP rule expires automatically and normal
communication is restored.

Actual Result: PASS
