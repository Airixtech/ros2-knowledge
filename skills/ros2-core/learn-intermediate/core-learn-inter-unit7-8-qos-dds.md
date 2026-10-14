---
id: core-learn-inter-unit7-8-qos-dds
type: reference
owner: equipo-ros2
updated: 2026-10-14
review_by: 2027-04-12
source: manual
confidentiality: internal
title: "Intermediate Units 7-8: QoS and DDS exercises"
domain: core
area: learn-intermediate
distro: humble
tested: false
audience: students
summary: "Unit 7 exercises (QoS-tuned /scan subscriber, deadline scenarios) and Unit 8 examples (message-loss test per DDS implementation)."
tags: [course, unit 7, unit 8, qos_tests_pkg, dds_tests_pkg, subscriber_scan_qos, deadline exercise, Cyclone DDS, students]
see: ["[[core-qos-events]]", "[[core-qos-deadline]]", "[[core-dds-loss-test]]", "[[core-rmw-implementations]]"]
requires: []
version_notes: []
---
# Intermediate Units 7-8: QoS and DDS exercises

**TL;DR** Unit 7 builds `qos_tests_pkg` (one publisher/subscriber pair per QoS policy: [[core-qos-events]], [[core-qos-durability-demo]], [[core-qos-deadline]], [[core-qos-lifespan]], [[core-qos-liveliness]]) and replays a bag with other QoS ([[core-bag-play]]). Unit 8 compares DDS implementations with `dds_tests_pkg` ([[core-dds-loss-test]]).

## Package
```bash
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_python qos_tests_pkg --dependencies rclpy std_msgs
cd ~/ros2_ws/src/qos_tests_pkg
touch qos_tests_pkg/subscriber_custom_minimal_qos.py qos_tests_pkg/publisher_custom_minimal_qos.py
```
Each later example adds two files (`subscriber_durability.py` / `publisher_durability.py`, `…_deadline`, `…_lifespan`, `…_liveliness`) and their entry points; you may keep the earlier executables in `setup.py`.

## Exercise 7.1
A subscriber for `/scan`, `subscriber_scan_qos.py`, whose QoS you set completely:
- the middleware used by `/scan` is Cyclone DDS, and the QoS must be compatible with it (check with `ros2 topic info /scan --verbose`);
- set `history`, `reliability`, `lifespan`, `deadline`, `liveliness`, `liveliness_lease_duration` and `depth`.
QoS for services and actions is set the same way; the course does not cover it.

## Exercise 7.2: deadline scenarios
With `publisher_deadline_exe` and `subscriber_deadline_exe`:
1. the publisher misses its own deadline (deadline shorter than its publishing period);
2. the subscriber does not get messages in time (subscriber deadline shorter than the publisher's period, or than its pause);
3. incompatible QoS between them (see the compatibility rules).
Solutions and outputs: [[core-qos-deadline]].

## Unit 8 examples
- **8.1**: `dds_tests_pkg` with `publisher_dds.py` / `subscriber_dds.py` and a launch file each; run them with Cyclone DDS.
- **8.2**: set `timer_period = 0.0` to flood the topic and count the lost messages.
- **8.2.1**: repeat with Fast DDS and compare losses and pub-to-sub delay.
Code, commands and results: [[core-dds-loss-test]]. Before each run, check the daemon's RMW ([[core-ros2-daemon]]).

## Pitfalls
- Each shell needs the same `RMW_IMPLEMENTATION` export; the course sets Cyclone explicitly in these units.
- A subscriber QoS stricter than the sensor's (RELIABLE for a BEST_EFFORT `/scan`) receives nothing ([[core-qos-policies]]).
