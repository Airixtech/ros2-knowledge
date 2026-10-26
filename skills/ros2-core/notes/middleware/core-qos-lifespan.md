---
id: core-qos-lifespan
type: reference
owner: equipo-ros2
updated: 2026-10-26
review_by: 2027-04-24
source: manual
confidentiality: internal
title: "Lifespan: message expiry"
domain: core
area: middleware
distro: humble
tested: false
audience: dev
summary: "QoS lifespan: messages older than the duration are dropped and never delivered; what the age test shows."
tags: [lifespan, QoS lifespan, message age, stale data, expiry, TRANSIENT_LOCAL, RELIABLE]
see: ["[[core-qos-lifespan-demo]]", "[[core-qos-durability]]", "[[core-qos-policies]]", "[[core-time-timers]]"]
requires: []
version_notes:
  - "all: lifespan applies whatever the durability; it matters most when old samples are stored (transient_local) — https://docs.ros.org/en/humble/Concepts/Intermediate/About-Quality-of-Service-Settings.html (V95)"
  - "jazzy: rclpy.qos_event -> rclpy.event_handler; removed in Lyrical — https://github.com/ros2/rclpy/blob/jazzy/rclpy/rclpy/event_handler.py (V86)"
---
# Lifespan: message expiry

**TL;DR** `lifespan` is the maximum time between publishing and receiving a message: older messages are silently dropped, as if they never arrived. It matters for sensor data (laser, camera), where late data is useless. The **publisher's** lifespan decides; the DDS layer drops the message before the subscriber callback. The demo uses RELIABLE + TRANSIENT_LOCAL so a stored message waits for a late subscriber, and the subscriber prints its age. Test programs: [[core-qos-lifespan-demo]].

## Scenarios
Publisher `-lifespan 20.0`, subscriber `-lifespan 1.0` started 10 s later:
```text
[INFO] [1644949766.033457458] [subscriber_qos_obj]: Message Age =10.363516569137573
```
- Publisher lifespan 20 s: a subscriber started 10 s later still receives the stored message. The subscriber's own lifespan (1.0) changes nothing.
- Start the subscriber **first**, then `-lifespan 0.001`: the message still arrives (the logged age, 0.02 s, includes the time the callback spent logging), because delivery took less than 1 ms.
- `-lifespan 0.00001`: the message expires before delivery and the subscriber callback never runs.

## Pitfalls
- The age is measured with `self.get_clock().now()` on both sides: fine on one machine, misleading across computers with unsynchronized clocks.
- With VOLATILE + BEST_EFFORT, messages are delivered at once or not at all, so a lifespan rarely drops anything visible.
- Lifespan takes no part in the compatibility check (the Humble QoS page lists reliability, durability, deadline, liveliness and lease duration): a subscriber cannot "require" messages valid for a minimum time, as the C++ course claims (CPP-V71).
