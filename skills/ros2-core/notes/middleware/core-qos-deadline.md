---
id: core-qos-deadline
type: reference
owner: equipo-ros2
updated: 2026-10-14
review_by: 2027-04-12
source: manual
confidentiality: internal
title: "Deadline: missed-deadline events and compatibility"
domain: core
area: middleware
distro: humble
tested: false
audience: dev
summary: "QoS deadline: maximum time between messages, deadline events on publisher and subscriber, compatibility, test scenarios."
tags: [deadline, QoS deadline, deadline event, offered deadline missed, requested deadline missed, Duration, cmd_vel]
see: ["[[core-qos-deadline-demo]]", "[[core-qos-events]]", "[[core-qos-policies]]", "[[core-exec-callback-groups]]"]
requires: []
version_notes:
  - "jazzy: rclpy.qos_event -> rclpy.event_handler; removed in Lyrical — https://github.com/ros2/rclpy/blob/jazzy/rclpy/rclpy/event_handler.py (V86)"
---
# Deadline: missed-deadline events and compatibility

**TL;DR** `deadline` is the expected maximum time between two messages of a topic. When it passes without a message, the publisher's and the subscriber's `deadline` event callbacks fire: useful for commands that must be regular (`cmd_vel`, obstacle detection). Compatible only if the publisher's deadline ≤ the subscriber's ([[core-qos-policies]]). Test programs: [[core-qos-deadline-demo]] (a publisher that sends one message per second and pauses 2 s every few messages).

## Scenarios
| Publisher `-deadline` | Subscriber `-deadline` | Result |
|---|---|---|
| 10.0 | 10.0 | works: both deadlines are longer than the period (1 s) and than the pause (2 s) |
| 0.99 | — | publisher deadline event every second: even 0.99 s is shorter than its 1 s period |
| 1.0 | — | publisher event during the pause phase |
| 1.2 | 1.8 | events on both sides only during the 2 s pause |
| 1.5 | 1.0 | **incompatible** (publisher deadline > subscriber's): `RMW_QOS_POLICY_DEADLINE` in both incompatible-QoS callbacks; the publisher keeps publishing, the subscriber receives nothing |
```text
deadline==Duration(nanoseconds=990000000)
[ERROR] [1644945025.239750790] [publisher_qos_obj]: PUBLISHER:::  Deadline Triggered!
```
The subscriber's deadline only counts while a matched publisher exists: with no publisher running, nothing fires.

## Pitfalls
- The pause runs `time.sleep()` inside the timer callback of a single-threaded executor, so the publisher's deadline callback waits until the timer callback returns: with `-deadline 1.0` it is reported after ~2 s. Put event callbacks in their own callback group with a `MultiThreadedExecutor` ([[core-qos-liveliness]], [[core-exec-callback-groups]]).
- A deadline that the publisher cannot meet by design (shorter than its period) fires forever: set it from the real rate plus a margin.
