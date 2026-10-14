---
id: core-qos-policies
type: reference
owner: equipo-ros2
updated: 2026-10-14
review_by: 2027-04-12
source: manual
confidentiality: internal
title: "QoS policies, compatibility & preset profiles"
domain: core
area: middleware
distro: humble
tested: false
audience: dev
summary: "QoS policies and defaults, publisher/subscriber compatibility rules, preset profiles (sensor_data, services, parameters, system default)."
tags: [QoS, reliability, durability, BEST_EFFORT, TRANSIENT_LOCAL, qos_profile_sensor_data]
see: ["[[core-qos-usage]]", "[[core-topic-pub-sub-py]]", "[[core-debug-triage]]"]
requires: []
version_notes:
  - "humble: qos_profile_system_default sets every policy to SYSTEM_DEFAULT (not RELIABLE/VOLATILE/10) — https://github.com/ros2/rmw/blob/humble/rmw/include/rmw/qos_profiles.h (V35)"
  - "humble: default liveliness is SYSTEM_DEFAULT with lease \"default\" (not AUTOMATIC); deadline/lifespan \"default\" — https://github.com/ros2/rmw/blob/humble/rmw/include/rmw/qos_profiles.h (V36)"
  - "jazzy: warning printed for KEEP_LAST with depth 0 (Iron) — https://docs.ros.org/en/rolling/Releases/Release-Iron-Irwini.html (V34)"
---
# QoS policies, compatibility & preset profiles

**TL;DR** Incompatible publisher/subscriber QoS ⇒ **no communication and no error**. The publisher defines a topic's QoS. A BEST_EFFORT + VOLATILE subscriber connects to anything.

## Policies
| Policy | Values | Default |
|---|---|---|
| Reliability | `RELIABLE` (retransmit) / `BEST_EFFORT` (may drop) | RELIABLE |
| Durability | `VOLATILE` / `TRANSIENT_LOCAL` (late joiners get last N msgs = "latched") | VOLATILE |
| History | `KEEP_LAST` (+depth) / `KEEP_ALL` | KEEP_LAST |
| Depth | int queue size | 10 |
| Deadline / Lifespan | Duration | "default" (middleware usually treats it as infinite) |
| Liveliness | enum + lease duration | SYSTEM_DEFAULT (lease "default") |
Every non-duration policy also has a `SYSTEM_DEFAULT` value, meaning "use the middleware's default".

## Compatibility (Publisher → Subscriber)
| Pub | Sub | Match |
|---|---|---|
| RELIABLE | RELIABLE | yes |
| RELIABLE | BEST_EFFORT | yes |
| BEST_EFFORT | RELIABLE | **NO** |
| TRANSIENT_LOCAL | VOLATILE | yes (no history) |
| TRANSIENT_LOCAL | TRANSIENT_LOCAL | yes (latched) |
| VOLATILE | TRANSIENT_LOCAL | **NO** |
Rule: a BEST_EFFORT + VOLATILE subscriber connects to anything. The publisher defines the topic's QoS, so check it first.

Durations (deadline, liveliness lease): compatible when publisher ≤ subscriber, or when the subscriber is "default" (infinite); publisher "default" with a subscriber value → **NO**. Liveliness kind: MANUAL_BY_TOPIC publishers serve AUTOMATIC or MANUAL_BY_TOPIC subscribers; AUTOMATIC publisher + MANUAL_BY_TOPIC subscriber → **NO**. Source: [QoS compatibility (humble)](https://docs.ros.org/en/humble/Concepts/Intermediate/About-Quality-of-Service-Settings.html). Demos and events: [[core-qos-events]] · [[core-qos-durability-demo]] · [[core-qos-deadline]] · [[core-qos-lifespan]] · [[core-qos-liveliness]].

## Preset profiles (rclpy names / rclcpp classes)
| Python | C++ | Rel | Dur | Depth | Use |
|---|---|---|---|---|---|
| `qos_profile_sensor_data` | `SensorDataQoS()` | BEST_EFFORT | VOLATILE | 5 | lidar, camera, IMU |
| `qos_profile_services_default` | `ServicesQoS()` | RELIABLE | VOLATILE | 10 | services |
| `qos_profile_parameters` | `ParametersQoS()` | RELIABLE | VOLATILE | 1000 | params |
| `qos_profile_system_default` | `SystemDefaultsQoS()` | SYSTEM_DEFAULT | SYSTEM_DEFAULT | SYSTEM_DEFAULT | whatever the RMW decides (vendor-specific) |
Passing an int (e.g. `10`) = the default profile: KEEP_LAST depth 10, RELIABLE, VOLATILE.
How to use these in code, and per-data-type choices: [[core-qos-usage]].

## Pitfalls
- `qos_profile_system_default` is not "reliable/volatile/10". It defers every policy to the vendor, so behavior can change when you switch `RMW_IMPLEMENTATION`.
- KEEP_LAST with depth 0 makes no sense. The middleware substitutes a value (usually 1) [≥Jazzy: it prints a warning].
