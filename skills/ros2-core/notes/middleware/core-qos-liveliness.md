---
id: core-qos-liveliness
type: reference
owner: equipo-ros2
updated: 2026-10-14
review_by: 2027-04-12
source: manual
confidentiality: internal
title: "Liveliness and lease duration: AUTOMATIC vs MANUAL_BY_TOPIC, assert_liveliness"
domain: core
area: middleware
distro: humble
tested: false
audience: dev
summary: "Liveliness kinds and lease duration, assert_liveliness(), liveliness event counts, test scenarios and results."
tags: [liveliness, lease duration, AUTOMATIC, MANUAL_BY_TOPIC, assert_liveliness, alive_count, not_alive_count, liveliness event]
see: ["[[core-qos-liveliness-demo]]", "[[core-qos-events]]", "[[core-qos-deadline]]", "[[core-qos-policies]]"]
requires: []
version_notes:
  - "humble: the lease duration applies to AUTOMATIC too (and to compatibility); DDS RMWs assert AUTOMATIC liveliness while the process runs — https://docs.ros.org/en/humble/Concepts/Intermediate/About-Quality-of-Service-Settings.html (V94)"
  - "jazzy: rclpy.qos_event -> rclpy.event_handler; removed in Lyrical — https://github.com/ros2/rclpy/blob/jazzy/rclpy/rclpy/event_handler.py (V86)"
---
# Liveliness and lease duration: AUTOMATIC vs MANUAL_BY_TOPIC, assert_liveliness

**TL;DR** Liveliness tells subscribers whether a publisher is still alive. The **lease duration** is the longest a publisher may stay silent before it counts as dead. `AUTOMATIC`: the middleware asserts it for every publisher of a running process. `MANUAL_BY_TOPIC`: publishing a message, or calling `publisher.assert_liveliness()`, renews it. Compatible if the publisher's lease ≤ the subscriber's, and a MANUAL_BY_TOPIC publisher serves an AUTOMATIC subscriber (not the reverse). Test programs: [[core-qos-liveliness-demo]].

## Manual assertion
```python
self.publisher_.assert_liveliness()     # MANUAL_BY_TOPIC: renew the lease without publishing
```
The demo publisher calls it from its own timer, in its own callback group:
- Three **mutually exclusive** groups, one per callback type (publish timer, alive timer, events): each callback never overlaps itself (a Reentrant group would let two `timer_callback` instances run at once), yet the three can run together.
- `MultiThreadedExecutor(num_threads=3)`: three threads for three parallel callbacks ([[core-exec-callback-groups]]).

## Scenarios
| Publisher | Subscriber | What happens |
|---|---|---|
| AUTOMATIC, lease 2000, publish 3000, no assert | AUTOMATIC, lease 1000 | incompatible (subscriber lease < publisher lease) |
| same | AUTOMATIC, lease 3000 | one event `alive_count=1, alive_count_change=1`; nothing during the pauses |
| MANUAL_BY_TOPIC, lease 2000, publish 1000, assert every 3000 | AUTOMATIC, lease 3000 | during the 5 s pause: `not_alive_count=1, alive_count_change=-1`; when publishing resumes: `alive_count=1, not_alive_count_change=-1` |
| MANUAL_BY_TOPIC, lease 2000, publish 4000, assert every 1000 | AUTOMATIC, lease 3000 | never lost: the 1 s assert covers the slow publisher and the pauses |

Stopping the publisher with Ctrl+C gives `alive_count=0, alive_count_change=-1` at once: a cleanly removed publisher is reported immediately, while a hung one is reported when the lease expires.
Publishing a message also counts as a liveliness assertion: "if I can talk with you, you know I am alive".

## Pitfalls
- The course concluded that the lease duration is only used with MANUAL_BY_TOPIC: in fact it applies to both kinds and to the compatibility check. With AUTOMATIC the DDS layer asserts liveliness for the whole process, so pauses in publishing never trigger it.
- `assert_liveliness()` from a timer in the **same** single-threaded executor as a blocking callback cannot run: give it its own group and enough threads, as above.
