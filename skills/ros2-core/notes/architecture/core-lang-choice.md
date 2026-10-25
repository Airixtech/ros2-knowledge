---
id: core-lang-choice
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "Choosing and combining rclpy and rclcpp: client library layers, C++-only features, mixed-language systems"
domain: core
area: architecture
distro: humble
tested: false
audience: dev
summary: "rclpy vs rclcpp per node: common rcl core, shared messages, Python prototypes and tools, C++ efficiency, plugins, components; mixing both."
tags: [rclpy, rclcpp, client library, rcl, language choice, Python, C++, mixed-language, pluginlib, composition, intra-process, prototyping, rclc, rclrs]
see: ["[[core-composition]]", "[[core-pkg-ament-cmake]]", "[[core-iface-package]]", "[[core-arch-layers]]", "[[core-node-skeleton]]"]
requires: []
version_notes:
  - "all: rclcpp and rclpy are maintained by the core team and both build on the C library rcl; nodes in different client libraries share messages through the generated code; community libraries include rclc (C), rclrs (Rust), Java/Android, .NET, Node.js — https://docs.ros.org/en/humble/Concepts/Basic/About-Client-Libraries.html (CPP-V42)"
  - "all: pluginlib is a C++ library; composition is rclcpp_components (no Python container in rclpy, Humble to Lyrical); zero-copy intra-process needs std::unique_ptr messages in rclcpp — https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Pluginlib.html, https://docs.ros.org/en/humble/Tutorials/Demos/Intra-Process-Communication.html (CPP-V43)"
  - "all: the Rust crate ros2-client is a community library on RustDDS, not on rcl; the official page lists rclrs — https://crates.io/crates/ros2-client (CPP-V41)"
---
# Choosing and combining rclpy and rclcpp

**TL;DR** Choose the language **per node**, not per robot: nodes written with `rclpy` (Python) and `rclcpp` (C++) talk to each other with no extra work, because both client libraries sit on the same C core (`rcl`) and every interface generates code for both. Python suits prototypes, scripts, tests, visualization tools and Python-only libraries; C++ suits efficiency-critical nodes and is required for plugins of C++ frameworks (pluginlib), components and zero-copy intra-process transport. C++ details: the ros2-cpp skill.

## How the layers fit
- Client library = the API you write nodes with (nodes, topics, services, actions, parameters, time, logging, threading model, intra-process).
- `rcl` (C) implements the language-neutral behaviour (names, namespaces, parameters…) once; `rclcpp` and `rclpy` wrap it, so behaviour stays consistent and fixes reach both. Language-specific parts, such as the threading model of `spin`, live in each library.
- `rclpy` converts Python message objects to C messages at the `rcl` boundary; in one process it avoids that conversion where it can.
- Maintained by the ROS 2 core team: `rclcpp`, `rclpy`. Community: `rclc` (C, used by micro-ROS), `rclrs` (Rust, ros2-rust), JVM/Android, .NET/C#, Node.js (`rclnodejs`), Flutter/Dart, Ada.

## Decision guide
| Need | Use |
|---|---|
| Fast iteration, prototypes, test and debug tools, visualization | `rclpy` (the official docs give visualization tools as an example) |
| A library that exists only (or best) in Python: ML frameworks, data analysis | `rclpy` |
| Efficiency: high-rate sensor processing, tight loops, low latency | `rclcpp` |
| A plugin for a C++ framework: Nav2 planners, controllers and costmap layers, ros2_control controllers and hardware interfaces, RViz displays (loaded with pluginlib); BehaviorTree.CPP nodes (BT.CPP's own plugin libraries) | `rclcpp` |
| Several nodes in one process loaded at run time (components), zero-copy with `std::unique_ptr` | `rclcpp` ([[core-composition]]) |
| Team skills, existing code base, community examples for the hardware | whichever the team and the ecosystem support best |

## Combining both in one robot
- Split the system into nodes by responsibility ([[core-arch-layers]]); each node can use its own language.
- Keep message, service and action definitions in one interface package (an `ament_cmake` package, usable from both languages, [[core-iface-package]]).
- One launch file starts Python and C++ nodes alike; a single `ament_cmake` package can hold C++ executables and Python scripts ([[core-pkg-ament-cmake]]).
- Prototype a node in Python and port it to C++ when it becomes a bottleneck: if the topic names, types and parameters stay the same, the rest of the system does not change.

## Pitfalls
- Python node in a high-rate data path (images, point clouds at full rate) → measure before deciding; message conversion and the interpreter cost CPU.
- Expecting Python components or Python plugins for pluginlib-based frameworks → they do not exist; write that part in C++.
- Two interface packages with the same fields are different types: both languages must use the same package.
