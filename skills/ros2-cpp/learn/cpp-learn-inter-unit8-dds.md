---
id: cpp-learn-inter-unit8-dds
type: reference
owner: equipo-ros2
updated: 2026-10-26
review_by: 2027-04-24
source: manual
confidentiality: internal
title: "Intermediate C++ Unit 8: dds_tests_pkg runs, forcing message loss, Fast DDS vs Cyclone DDS, the daemon warning"
domain: cpp
area: learn
distro: humble
tested: false
audience: students
order: 17
summary: "Check the middleware, switch RMW, loss test 8.1, 0 ms overload 8.2, Fast DDS vs Cyclone DDS 8.2.1, daemon restarts."
tags: [course, unit 8, dds_tests_pkg, RMW_IMPLEMENTATION, rmw_fastrtps_cpp, rmw_cyclonedds_cpp, ros2 doctor --report, demo_nodes_py, ros2 daemon stop, message loss, students]
see: ["[[cpp-dds-loss-test]]", "[[core-dds-overview]]", "[[core-rmw-implementations]]", "[[core-ros2-daemon]]", "[[core-learn-inter-unit7-8-qos-dds]]"]
requires: [ros2-core]
version_notes: []
---
# Intermediate C++ Unit 8: DDS in practice

**TL;DR** Unit 8 explains DDS and the RMW layer ([[core-dds-overview]]), checks which middleware runs, switches it with `RMW_IMPLEMENTATION` ([[core-rmw-implementations]]) and runs the C++ message-loss test of [[cpp-dds-loss-test]] with Fast DDS and Cyclone DDS. Python twin: [[core-learn-inter-unit7-8-qos-dds]].

## Steps
1. **Current middleware**: `source /opt/ros/humble/setup.bash`, then `ros2 doctor --report`; the `RMW MIDDLEWARE` section shows `middleware name : rmw_fastrtps_cpp` (Humble's default).
2. **Switch**: `export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp`, then `ros2 run demo_nodes_py talker` in one terminal and `ros2 run demo_nodes_py listener` in another (same export): `Publishing: "Hello World: 0"` … `I heard: [Hello World: 0]` …; `ros2 doctor --report | grep middleware` → `middleware name : rmw_cyclonedds_cpp`. Then the same with `rmw_fastrtps_cpp`. For most users nothing visible changes; implementations differ in performance, supported QoS features and events, discovery and tooling.
3. **Example 8.1**: create `dds_tests_pkg`, the two programs, the two launch files and the CMake of [[cpp-dds-loss-test]]; build, then start the subscriber (`ros2 launch dds_tests_pkg subscriber_dds.launch.py`) and the publisher (`ros2 launch dds_tests_pkg publisher_dds.launch.py`). The subscriber prints the message status (`MESSAGE OK` / `MESSAGE LOST`), the total of lost messages and the publication-to-reception delay in nanoseconds.
4. **Example 8.2, forcing losses**: set the publisher's timer to `0ms`, rebuild, relaunch both. Losses depend on the machine: fewer cores, more losses.
5. **Example 8.2.1**: repeat with `export RMW_IMPLEMENTATION=rmw_fastrtps_cpp` and then `rmw_cyclonedds_cpp` before `ros2 run dds_tests_pkg subscriber_dds_exe` and `ros2 run dds_tests_pkg publisher_dds_exe`. Both lose messages when overloaded; which one does better depends on hardware, load and network.

## Warning: the daemon keeps its middleware
Nodes use the `RMW_IMPLEMENTATION` of the terminal that starts them, but CLI tools ask the ros2 daemon, which keeps the middleware it started with. If `ros2 node list`, `ros2 topic list` or `ros2 doctor` look inconsistent after a switch, run `ros2 daemon stop`; the next CLI command starts it again with the current value. `ps faux | grep "rmw-implementation"` shows the daemon's middleware ([[core-ros2-daemon]]).
