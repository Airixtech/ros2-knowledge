---
id: core-qos-durability
type: reference
owner: equipo-ros2
updated: 2026-10-14
review_by: 2027-04-12
source: manual
confidentiality: internal
title: "Durability: transient_local for late subscribers"
domain: core
area: middleware
distro: humble
tested: false
audience: dev
summary: "QoS durability: TRANSIENT_LOCAL keeps the last depth messages for late subscribers, VOLATILE keeps nothing; ros2 topic echo flags."
tags: [durability, TRANSIENT_LOCAL, VOLATILE, latched topic, late joiner, robot_description, topic echo qos-durability]
see: ["[[core-qos-durability-demo]]", "[[core-qos-policies]]", "[[core-qos-usage]]", "[[core-qos-lifespan]]"]
requires: []
version_notes:
  - "humble: without QoS flags ros2 topic echo adapts reliability and durability to the publishers; with any flag the rest comes from sensor_data — https://github.com/ros2/ros2cli/blob/humble/ros2topic/ros2topic/verb/echo.py (V96)"
  - "jazzy: rclpy.qos_event -> rclpy.event_handler; removed in Lyrical — https://github.com/ros2/rclpy/blob/jazzy/rclpy/rclpy/event_handler.py (V86)"
---
# Durability: transient_local for late subscribers

**TL;DR** Durability decides whether a message stays available for subscribers that join **after** it was published. `TRANSIENT_LOCAL`: the publisher keeps its last `depth` messages for late joiners (how `robot_description`, `/map` or `/tf_static` work). `VOLATILE`: nothing is kept. A late subscriber gets the old message only if **both** sides use `TRANSIENT_LOCAL` ([[core-qos-policies]]). Test programs: [[core-qos-durability-demo]].

## Late subscriber test
A publisher sends **one** message with TRANSIENT_LOCAL and keeps spinning; a subscriber started 25 s later with TRANSIENT_LOCAL still prints it:
```text
transient_local
[INFO] [1644605352.435077445] [subscriber_qos_obj]: Data Received =1644605326,985073117
```
From the terminal:
```bash
ros2 topic echo --qos-durability transient_local --qos-reliability reliable /qos_test
```
[Humble] `ros2 topic echo /qos_test` without QoS flags also works: echo copies the reliability and durability of the publishers. Once you pass a flag, the policies you omit come from the `sensor_data` preset (best effort), which is why the course had to add `--qos-reliability reliable`.

## Pitfalls
- A VOLATILE subscriber connects to a TRANSIENT_LOCAL publisher but receives only new messages; a TRANSIENT_LOCAL subscriber with a VOLATILE publisher is incompatible.
- `depth` is how many old messages a late joiner can get: depth 1 = only the last one.
