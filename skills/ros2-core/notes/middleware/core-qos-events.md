---
id: core-qos-events
type: reference
owner: equipo-ros2
updated: 2026-10-14
review_by: 2027-04-12
source: manual
confidentiality: internal
title: "QoS event callbacks: incompatible QoS, defaults, topic info --verbose"
domain: core
area: middleware
distro: humble
tested: false
audience: dev
summary: "Publisher/SubscriptionEventCallbacks for incompatible QoS, deadline and liveliness; QoS defaults; /scan QoS with topic info."
tags: [QoS events, PublisherEventCallbacks, SubscriptionEventCallbacks, incompatible_qos, last_policy_kind, qos_event, event_handler, topic info verbose, QoS defaults]
see: ["[[core-qos-events-demo]]", "[[core-qos-policies]]", "[[core-qos-deadline]]", "[[core-qos-liveliness]]"]
requires: []
version_notes:
  - "jazzy: import the callbacks from rclpy.event_handler (Iron); rclpy.qos_event warns (Jazzy, Kilted) and is removed in Lyrical — https://github.com/ros2/rclpy/blob/jazzy/rclpy/rclpy/event_handler.py (V86)"
  - "humble: Fast DDS (default RMW) also raises incompatible-QoS events — https://github.com/ros2/rmw_fastrtps/blob/humble/rmw_fastrtps_shared_cpp/src/custom_publisher_info.cpp (V87)"
  - "humble: liveliness default is SYSTEM_DEFAULT, durations 'default' — https://github.com/ros2/rmw/blob/humble/rmw/include/rmw/qos_profiles.h (V36)"
---
# QoS event callbacks: incompatible QoS, defaults, topic info --verbose

**TL;DR** QoS lets you choose, per publisher and subscriber, how reliable delivery must be: ROS 1 used TCP, which suits neither lossy networks (Wi-Fi) nor critical systems, while ROS 2 rides on DDS over UDP. Both ends must have **compatible** QoS or nothing flows ([[core-qos-policies]]). Pass `event_callbacks` to `create_publisher` / `create_subscription` to be told when it happens. The same callbacks report missed deadlines ([[core-qos-deadline]]) and liveliness changes ([[core-qos-liveliness]]). Test programs: [[core-qos-events-demo]].

## The callbacks
```python
from rclpy.qos_event import PublisherEventCallbacks, SubscriptionEventCallbacks   # Jazzy+: rclpy.event_handler

event_callbacks = PublisherEventCallbacks(incompatible_qos=self.incompatible_qos_clb)
self.publisher_ = self.create_publisher(msg_type=String, topic='/qos_test',
                                        qos_profile=qos_profile, event_callbacks=event_callbacks)
```
| Callback (publisher / subscription) | Fires when | Event fields |
|---|---|---|
| `incompatible_qos` | an endpoint with incompatible QoS is discovered | `last_policy_kind` (e.g. `RMW_QOS_POLICY_RELIABILITY`) |
| `deadline` | no message within the deadline ([[core-qos-deadline]]) | `total_count`, `total_count_change` |
| `liveliness` | publisher lost liveliness / subscription sees publishers appear or disappear ([[core-qos-liveliness]]) | publisher: `total_count`, `total_count_change`; subscription: `alive_count`, `not_alive_count`, `alive_count_change`, `not_alive_count_change` |

Event callbacks go through the executor like any callback: give them their own callback group when other callbacks block.

## What an incompatibility looks like
```text
[ERROR] [publisher_qos_obj]: A subscriber is asking for an INCOMPATIBLE QoS Triggered!
[ERROR] [publisher_qos_obj]: rmw_qos_policy_kind_t.RMW_QOS_POLICY_RELIABILITY
[WARN] [subscriber_qos_obj]: New publisher discovered on topic '/qos_test', offering incompatible QoS. No messages will be received from it. Last incompatible policy: RELIABILITY
```
Two things happen: the publisher's `incompatible_qos` callback fires, and the subscriber logs a warning naming the (last) incompatible policy: best-effort publisher, reliable subscriber. The course exported `RMW_IMPLEMENTATION=rmw_cyclonedds_cpp` in both shells because event support differs between DDS implementations; in Humble both Fast DDS and Cyclone DDS raise these events.

## Defaults and a real sensor
A publisher or subscriber created with only a depth gets: history KEEP_LAST, depth 10 (queue size), RELIABLE, VOLATILE, liveliness SYSTEM_DEFAULT; deadline, lifespan and lease duration "default", shown as 9223372036854775807 ns (infinite). Every QoS of a topic:
```bash
ros2 topic info /scan --verbose
```
```text
Node name: lidar_1
Topic type: sensor_msgs/msg/LaserScan
Endpoint type: PUBLISHER
QoS profile:
  Reliability: BEST_EFFORT
  Durability: VOLATILE
  Lifespan: 9223372036854775807 nanoseconds
  Deadline: 9223372036854775807 nanoseconds
  Liveliness: AUTOMATIC
  Liveliness lease duration: 9223372036854775807 nanoseconds
```
- BEST_EFFORT + VOLATILE is the usual sensor choice: a continuous flow where one or two lost messages and old data do not matter.
- AUTOMATIC liveliness: the publisher counts as alive while its node is running ([[core-qos-liveliness]]).
- Infinite deadline and lifespan: acceptable in simulation; a real sensor has a rate, so a deadline and a lifespan make sense ([[core-qos-deadline]], [[core-qos-lifespan]]).
All event types: [rclpy qos_event.py (humble)](https://github.com/ros2/rclpy/blob/humble/rclpy/rclpy/qos_event.py). Services and actions take the same QoS objects ([rclpy services](https://docs.ros2.org/foxy/api/rclpy/api/services.html), [actions](https://docs.ros2.org/foxy/api/rclpy/api/actions.html)).

## Pitfalls
- The event callback only reports the **last** incompatible policy: fix it and run again to find the next one.
- No event callback, no message: an incompatible subscriber only logs a warning and silently receives nothing.
