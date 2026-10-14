---
id: core-dds-overview
type: reference
owner: equipo-ros2
updated: 2026-10-14
review_by: 2027-04-12
source: manual
confidentiality: internal
title: "DDS and ROS 2: what DDS provides, the rmw layer"
domain: core
area: middleware
distro: humble
tested: false
audience: dev
summary: "What DDS is, how ROS 2 builds on it (rmw layer) and its foundations: data centricity, QoS, discovery, security."
tags: [DDS, RTPS, middleware, rmw, data centricity, discovery, QoS, security, SROS2, TCPROS]
see: ["[[core-rmw-implementations]]", "[[core-qos-policies]]", "[[core-multi-pc-dds]]", "[[core-ros2-daemon]]"]
requires: []
version_notes:
  - "humble: default RMW is Fast DDS (rmw_fastrtps_cpp); Cyclone was Galactic's default — https://docs.ros.org/en/humble/Concepts/Intermediate/About-Different-Middleware-Vendors.html (V88)"
---
# DDS and ROS 2: what DDS provides, the rmw layer

**TL;DR** The Data Distribution Service (DDS) is a publish–subscribe middleware **standard** (OMG) for high-performance data exchange: low-latency connectivity, flexible reliability, scalable architectures. It is used well beyond robotics (military, air-traffic control, autonomous vehicles, medical devices). ROS 2 is an ecosystem built on top of DDS/RTPS: it adds robotics data types, tools and ready-made QoS profiles, and hides most DDS details. ROS 1 used custom protocols (TCPROS) and a central master instead.

## How ROS 2 uses DDS
- Discovery is **distributed**: no `roscore`; nodes find each other through the DDS discovery protocol ([[core-ros2-daemon]] for its cost on the CLI).
- Each vendor implementation is wrapped by a "ROS middleware interface" (**rmw**) package. The rmw API sits between the client libraries (rclcpp, rclpy) and the vendor, so ROS 2 can support several implementations, each with its own platforms, languages, performance, memory footprint, dependencies and license. Choosing and switching: [[core-rmw-implementations]].

## The four foundations
1. **Data centricity**: publishers, subscribers and participants (nodes) decide how data moves with minimum impact and latency. DDS stops sending a topic nobody reads, avoids useless copies when several apps read the same data, and cleans or keeps old data as the publisher specifies.
2. **QoS**: how data is shared is configurable: reliability (must every sample arrive, how many losses are acceptable), system health (alert if a publisher misses its 0.1 s period, vital for safety-critical systems), security. DDS also keeps each endpoint's QoS to check compatibility ([[core-qos-policies]], [[core-qos-events]]).
3. **Dynamic discovery**: plug and play. DDS tracks every node, the types it publishes and subscribes and their QoS, so nodes can start and stop without disturbing the rest.
4. **Security**: authentication, access control and data integrity (encryption); in ROS 2 through SROS2 ([security tutorials (humble)](https://docs.ros.org/en/humble/Tutorials/Advanced/Security/Introducing-ros2-security.html)).

## Pitfalls
- "DDS = ROS 2" is wrong: two machines can run the same DDS and still fail to talk because of the ROS domain, the RMW choice or incompatible QoS ([[core-multi-pc-dds]]).
- Different RMW implementations interoperate only partly: use the same `RMW_IMPLEMENTATION` on every machine of one system.
