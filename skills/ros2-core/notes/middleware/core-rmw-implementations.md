---
id: core-rmw-implementations
type: reference
owner: equipo-ros2
updated: 2026-10-26
review_by: 2027-04-24
source: manual
confidentiality: internal
title: "RMW implementations in Humble and switching with RMW_IMPLEMENTATION"
domain: core
area: middleware
distro: humble
tested: false
audience: dev
summary: "Fast DDS (default), Cyclone DDS, Connext, Zenoh in Humble: install, switch with RMW_IMPLEMENTATION, verify with doctor and the daemon."
tags: [RMW_IMPLEMENTATION, rmw_fastrtps_cpp, rmw_cyclonedds_cpp, rmw_connextdds, rmw_zenoh_cpp, Fast DDS, Cyclone DDS, Connext, iceoryx, zenoh, ros2 doctor]
see: ["[[core-dds-overview]]", "[[core-ros2-daemon]]", "[[core-env-variables]]", "[[core-dds-loss-test]]"]
requires: []
version_notes:
  - "humble: default is Fast DDS; apt installs only Fast DDS (Cyclone needs ros-humble-rmw-cyclonedds-cpp) — https://docs.ros.org/en/humble/Concepts/Intermediate/About-Different-Middleware-Vendors.html (V88)"
  - "humble: ros2 doctor --report shows the RMW of its own shell, so an export is visible — https://github.com/ros2/ros2cli/blob/humble/ros2doctor/ros2doctor/api/rmw.py (V89)"
  - "humble: Connext from the ROS repo is free for non-commercial, research and academic use (no 30-day limit) — https://docs.ros.org/en/humble/Installation/RMW-Implementations/DDS-Implementations/Working-with-RTI-Connext-DDS.html (V90)"
  - "humble: rmw_zenoh_cpp binary in Humble (0.1.x) and Jazzy (0.2.x); Tier 1 from Kilted; needs the rmw_zenohd router — https://docs.ros.org/en/humble/Installation/RMW-Implementations/Non-DDS-Implementations/Working-with-Zenoh.html (V92)"
  - "humble: Cyclone 'better for Nav2' is Humble-era community advice; current Nav2 docs give no RMW recommendation [verify] — https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/tuning_guide.md (V93)"
---
# RMW implementations in Humble and switching with RMW_IMPLEMENTATION

**TL;DR** Humble's default RMW is **Fast DDS** (`rmw_fastrtps_cpp`, Apache 2), the only one apt installs with ROS 2. Others install as extra packages and are selected per shell with `export RMW_IMPLEMENTATION=…`; after switching, restart the ros2 daemon ([[core-ros2-daemon]]). Variables and defaults per distro: [[core-env-variables]].

## Which middleware is running
```bash
cd ~/ros2_ws
source install/setup.bash
ros2 doctor --report            # section "RMW MIDDLEWARE": middleware name : rmw_fastrtps_cpp
```
`ros2 doctor` reports the RMW of the shell where it runs, so after an `export` it shows the new one.

## Implementations in Humble
| RMW | Vendor, license | Install |
|---|---|---|
| `rmw_fastrtps_cpp` [default] | eProsima Fast DDS, Apache 2 | installed with ROS 2 (`ros-humble-rmw-fastrtps-cpp`) |
| `rmw_cyclonedds_cpp` | Eclipse Cyclone DDS, EPL 2.0 | `sudo apt install ros-humble-rmw-cyclonedds-cpp` |
| `rmw_connextdds` | RTI Connext, commercial; free for prototyping, research, non-commercial and academic use | `sudo apt install ros-humble-rmw-connextdds` |
| `rmw_gurumdds_cpp` | GurumDDS, commercial | `ros-humble-rmw-gurumdds-cpp` plus GurumDDS itself (separate) |
| `rmw_zenoh_cpp` (not DDS) | Zenoh | `sudo apt install ros-humble-rmw-zenoh-cpp`, then run the router `ros2 run rmw_zenoh_cpp rmw_zenohd` |

If Fast DDS is not installed, the first RMW in alphabetical order becomes the default. Reference: [middleware vendors (humble)](https://docs.ros.org/en/humble/Concepts/Intermediate/About-Different-Middleware-Vendors.html).
```bash
sudo apt update
sudo apt install ros-humble-rmw-cyclonedds-cpp -y
```

## Switch
```bash
# FastDDS
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
# CycloneDDS
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
# ConnextDDS
export RMW_IMPLEMENTATION=rmw_connextdds
```
Export it in every shell of the system (or in `~/.bashrc`), then restart the daemon and check it:
```bash
ros2 daemon stop
ros2 daemon start
ps faux | grep "rmw-implementation"     # ... --rmw-implementation rmw_cyclonedds_cpp
```
Quick test: `ros2 run demo_nodes_py talker` and `ros2 run demo_nodes_py listener` in two shells with the same export. Measuring losses and latency per RMW: [[core-dds-loss-test]].

## Why choose one or another
- Most users notice no difference. Reasons to switch: existing Cyclone DDS applications outside ROS 2, vendor-specific QoS or XML settings, performance on your network ([eProsima's own benchmark](https://www.eprosima.com/index.php/resources-all/performance/fast-dds-vs-cyclone-dds-performance) favors Fast DDS).
- In Humble both Fast DDS and Cyclone DDS raise the QoS events (incompatible QoS, deadline, liveliness) ([[core-qos-events]]).
- In the Humble era many Nav2, MoveIt and RMF users reported fewer problems with Cyclone DDS [verify on your robot].
- Cyclone side projects: **Eclipse iceoryx** passes pointers instead of copies (zero-copy shared memory, built for the camera loads of autonomous cars) and **Eclipse Zenoh** bridges DDS systems over Wi-Fi and the Internet, where DDS discovery struggles ([Zenoh–ROS 2 integration](https://zenoh.io/blog/2021-04-28-ros2-integration/)). Zenoh now also has its own RMW (table above).

## Pitfalls
- Mixed exports (one shell Fast DDS, another Cyclone) mostly work but not in every case: keep one RMW per system.
- A daemon started with the old RMW makes `ros2 topic list` show nothing or fail.
