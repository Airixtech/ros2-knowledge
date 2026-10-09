---
id: core-multi-pc-dds
title: "Multi-PC discovery, domain strategy & DDS tuning"
domain: core
area: architecture
distro: humble
tested: false
audience: dev
summary: "Multi-host checklist, multicast test, static peers, Fast DDS discovery server (correct Humble flags), domain_bridge, Cyclone XML, kernel buffers."
tags: [multi-PC, discovery server, fastdds, Cyclone DDS, domain_bridge, sysctl, ROS_STATIC_PEERS]
see: ["[[core-env-variables]]", "[[core-multi-robot-namespacing]]", "[[core-debug-triage]]", "[[core-testing-ci-docker]]"]
requires: []
version_notes:
  - "humble: fastdds discovery uses --udp-address/-l and --udp-port/-p (no --ip-address/--port) — https://github.com/eProsima/Fast-DDS/blob/2.6.x/tools/fds/server.h (V61)"
  - "jazzy: ROS_LOCALHOST_ONLY deprecated (removed in Kilted); ROS_STATIC_PEERS env var for peers (Iron) — https://docs.ros.org/en/rolling/Releases/Release-Iron-Irwini.html (V01, V70)"
---
# Multi-PC discovery, domain strategy & DDS tuning

**TL;DR** Use the same `ROS_DOMAIN_ID` and RMW everywhere, with localhost-only off and UDP open. When multicast fails (Wi-Fi), use static peers or a Fast DDS discovery server. Large messages need bigger kernel buffers.

## Multi-PC basics
Same `ROS_DOMAIN_ID` and RMW on all hosts · `ROS_LOCALHOST_ONLY` unset [≥Jazzy: `ROS_AUTOMATIC_DISCOVERY_RANGE=SUBNET`] · same subnet, firewall open for UDP · test with `ros2 multicast receive` (host A) + `ros2 multicast send` (host B) · no hard-coded IPs in code.
Multicast is unreliable on Wi-Fi and many switches. Alternatives:
- Static peers in Cyclone or Fast DDS XML for small LANs. [≥Jazzy: `ROS_STATIC_PEERS="ip1;ip2"`, RMW-agnostic ([[core-env-variables]])]
- Fast DDS Discovery Server (fleets):
```bash
fastdds discovery --server-id 0 --udp-address 192.168.1.10 --udp-port 11811   # server host (short: -i 0 -l IP -p PORT)
export ROS_DISCOVERY_SERVER="192.168.1.10:11811"                              # every client
```
On Humble (Fast DDS 2.6), the options are `--udp-address`/`--udp-port`; `--ip-address`/`--port` do not exist. Fast DDS 3 (Kilted+) CLI [verify].

## Domain strategy
`ROS_DOMAIN_ID` 0–101 is safe (Linux max 232). Small fleet: 1 domain + namespaces (easy map sharing). Large fleet: 1 domain per robot + `domain_bridge`:
```yaml
topics:
  /robot1/odom: {type: nav_msgs/msg/Odometry, from_domain: 11, to_domain: 30}
```
```bash
ros2 run domain_bridge domain_bridge bridge.yaml
```
Plan domains at project start. Fleet management: Open-RMF (dispatcher, task planner, per-vendor fleet adapters with Easy Full Control recommended, traffic schedule, traffic editor, rmf-web).

## DDS selection & tuning
`rmw_fastrtps_cpp` (Humble default) or `rmw_cyclonedds_cpp` (`export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp`; used by Autoware, Isaac Sim).
```xml
<!-- cyclonedds.xml ; export CYCLONEDDS_URI=file:///path/cyclonedds.xml -->
<CycloneDDS><Domain id="any">
  <General>
    <Interfaces><NetworkInterface name="eth0"/></Interfaces>
    <AllowMulticast>default</AllowMulticast>
    <MaxMessageSize>65500B</MaxMessageSize>
  </General>
  <Internal><SocketReceiveBufferSize min="10MB"/></Internal>
  <Discovery><Peers><Peer address="192.168.1.10"/><Peer address="192.168.1.11"/></Peers></Discovery>
</Domain></CycloneDDS>
```
Kernel settings (large msgs: PointCloud2 and images are silently lost without them):
```bash
sudo sysctl -w net.core.rmem_max=2147483647
sudo sysctl -w net.ipv4.ipfrag_time=3
sudo sysctl -w net.ipv4.ipfrag_high_thresh=134217728
```
Debug: `ros2 doctor --report` · `ros2 topic hz|bw|info -v` · Wireshark filter `rtps`. Cyclone versions: 0.9 (Humble), 0.10 (Jazzy), 11.0 (Lyrical): check the XML on upgrade [verify].
