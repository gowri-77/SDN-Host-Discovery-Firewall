# SDN Host Discovery and Firewall using Mininet and OS-Ken

## Problem Statement
The objective of this project is to implement a Software Defined Networking (SDN) solution that can:
- Discover hosts automatically in the network
- Maintain information about connected hosts
- Apply a firewall rule to block specific traffic
- Demonstrate interaction between controller and switches

---

## Tools Used
- Mininet
- OS-Ken (Ryu-based SDN controller)
- OpenFlow 1.3
- Ubuntu 24.04

---

## Implementation

### Host Discovery
The controller listens to Packet-In events from the switch. Whenever a new packet arrives, it extracts and stores:
- MAC address of the host
- Switch ID (DPID)
- Port number

This allows the controller to maintain a dynamic list of hosts in the network.

---

### Learning Switch Behavior
The controller works as a learning switch:
- If the destination is unknown, the packet is flooded
- If the destination is known, the packet is forwarded to the correct port
- Flow rules are installed in the switch to avoid repeated controller involvement

---

### Firewall Rule
A firewall rule is applied to block communication from host h1 to host h2.

This is implemented using an OpenFlow rule:
- Match: Source MAC (h1) and Destination MAC (h2)
- Action: Drop the packet

---

## Testing

### Allowed Traffic
Communication between h2 and h3 is successful.

### Blocked Traffic
Communication from h1 to h2 is blocked as expected.

---

## Flow Table Verification
The flow table of the switch can be checked using:
ovs-ofctl dump-flows s1

---

## Conclusion
This project demonstrates:
- Basic SDN concepts using Mininet
- Controller and switch communication through OpenFlow
- Dynamic host discovery
- Implementation of a simple firewall rule
