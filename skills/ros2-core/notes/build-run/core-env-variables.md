---
id: core-env-variables
type: reference
owner: equipo-ros2
updated: 2026-10-14
review_by: 2027-04-12
source: manual
confidentiality: internal
title: "ROS environment variables (domain, discovery, RMW, logging)"
domain: core
area: build-run
distro: humble
tested: false
audience: dev
summary: "ROS_DOMAIN_ID, ROS_LOCALHOST_ONLY vs ROS_AUTOMATIC_DISCOVERY_RANGE, RMW_IMPLEMENTATION, logging vars, per-distro DDS."
tags: [ROS_DOMAIN_ID, ROS_LOCALHOST_ONLY, ROS_AUTOMATIC_DISCOVERY_RANGE, ROS_STATIC_PEERS, RMW_IMPLEMENTATION, RCUTILS]
see: ["[[core-env-sourcing]]", "[[core-multi-pc-dds]]", "[[core-debug-triage]]"]
requires: []
version_notes:
  - "humble: rmw_zenoh_cpp is also a binary package in Humble and Jazzy; Tier 1 only from Kilted — https://docs.ros.org/en/humble/Installation/RMW-Implementations/Non-DDS-Implementations/Working-with-Zenoh.html (V92)"
  - "jazzy: ROS_LOCALHOST_ONLY deprecated since Iron (still honored, warns); use ROS_AUTOMATIC_DISCOVERY_RANGE / ROS_STATIC_PEERS — https://docs.ros.org/en/rolling/Releases/Release-Iron-Irwini.html (V01)"
  - "lyrical: ROS_LOCALHOST_ONLY removed in Kilted (rcl#1169), no effect — https://docs.ros.org/en/rolling/Releases/Kilted-Kaiju-Complete-Changelog.html (V01)"
  - "lyrical: default RMW still rmw_fastrtps_cpp (Fast DDS 3.6); Kilted renamed fastrtps packages to fastdds; Zenoh Tier 1 — https://docs.ros.org/en/rolling/Releases/Release-Kilted-Kaiju.html (V03)"
---
# ROS environment variables

**TL;DR** Use the same `ROS_DOMAIN_ID` and `RMW_IMPLEMENTATION` on every terminal and host that must talk. In Humble, `ROS_LOCALHOST_ONLY=1` isolates a machine. From Iron on, `ROS_AUTOMATIC_DISCOVERY_RANGE` replaces it.

## Key variables
| Var | Purpose | Notes |
|---|---|---|
| `ROS_DISTRO` | current distro | must print `humble` after sourcing |
| `ROS_DOMAIN_ID` | DDS isolation | safe 0–101 on Linux (max 232); must match across peers |
| `ROS_LOCALHOST_ONLY=1` | no network traffic | disable for multi-PC. [changed in Jazzy: deprecated, still honored] [changed in Lyrical: removed in Kilted] |
| `RMW_IMPLEMENTATION` | DDS vendor | default `rmw_fastrtps_cpp`; `rmw_cyclonedds_cpp` lighter/recommended for Isaac Sim [verify: Isaac Sim docs now default to Fast DDS] |
| `RCUTILS_COLORIZED_OUTPUT=1` | colored console logs | |
| `RCUTILS_CONSOLE_OUTPUT_FORMAT` | log line format | e.g. `"[{severity} {time}] [{name}]: {message}"` |
| `ROS_DISCOVERY_SERVER` | FastDDS discovery server | see [[core-multi-pc-dds]] |

## Discovery range [≥Jazzy] (introduced in Iron)
```bash
export ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST   # SUBNET (default) | LOCALHOST | OFF | SYSTEM_DEFAULT
export ROS_STATIC_PEERS="192.168.1.10;192.168.1.11"   # ';'-separated extra peers (ignored if range is OFF)
```
- `SUBNET`: discover anything reachable by multicast. `LOCALHOST`: same machine only. `OFF`: no automatic discovery at all. `SYSTEM_DEFAULT`: leave the middleware settings untouched.
- Typical use: keep robots on `LOCALHOST`, and add one robot's IP to `ROS_STATIC_PEERS` in the terminal where RViz runs.
- In Humble, the only switch is `ROS_LOCALHOST_ONLY` (on/off). Static peers there need DDS XML ([[core-multi-pc-dds]]).

## Middleware per distro
| | Humble | Jazzy | Lyrical |
|---|---|---|---|
| Default RMW | `rmw_fastrtps_cpp` (Fast DDS 2.6) | same (2.14) | same (Fast DDS 3.6) |
| Cyclone DDS | 0.9.x | 0.10.x | 11.0.x |
| Zenoh (`rmw_zenoh_cpp`, needs `rmw_zenohd`) | binary 0.1.x | binary 0.2.x | Tier 1 (since Kilted) |

## Pitfalls
- Different `ROS_DOMAIN_ID` or RMW between terminals or hosts → nodes do not see each other, and nothing reports an error ([[core-debug-triage]]).
- In Jazzy, `ROS_LOCALHOST_ONLY=1` only prints a deprecation warning. Since Kilted it is silently ignored, so you may communicate over the network without realizing it.
- Fast DDS XML profile variable: `FASTRTPS_DEFAULT_PROFILES_FILE` [Humble] → `FASTDDS_DEFAULT_PROFILES_FILE` [≥Kilted].
