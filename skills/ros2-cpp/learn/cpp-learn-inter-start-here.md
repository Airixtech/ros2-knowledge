---
id: cpp-learn-inter-start-here
type: reference
owner: equipo-ros2
updated: 2026-10-26
review_by: 2027-04-24
source: manual
confidentiality: internal
title: "Intermediate ROS 2 course in C++: start here (units, packages, notes, the demo, Python twin)"
domain: cpp
area: learn
distro: humble
tested: false
audience: students
order: 11
summary: "Learning path of the intermediate C++ course (Mars rover, Humble): units 1, 3-5, 7-9, packages, notes, parameter demo, Python twin."
tags: [course, learning path, intermediate, Mars rover, C++, units, packages, mars_rover_demo, params_demo_node, students]
see: ["[[core-learn-inter-start-here]]", "[[cpp-learn-start-here]]", "[[cpp-learn-inter-unit3-launch]]", "[[cpp-params-declare-get]]", "[[cpp-qos-profile]]", "[[cpp-lifecycle-param-node]]"]
requires: [ros2-core]
version_notes: []
---
# Intermediate ROS 2 course in C++: start here

**TL;DR** The C++ twin of the intermediate course in ros2-core, on the same simulated Mars rover (Humble): launch files in Python, XML and YAML, parameters, QoS, DDS and managed nodes, with every node written in `rclcpp` and built with `ament_cmake`. It assumes the C++ basics course ([[cpp-learn-start-here]]). Threading and callback management, announced in the course outline, are taught there (units 5–6: [[cpp-exec-callback-groups]]).

## Units, packages and notes
| Unit | Topic | Packages | Read |
|---|---|---|---|
| 1 | demo: moving the rover with parameters | `mars_rover_demo` | this note |
| 3 | nested launch files, launch arguments | `launch_tests_pkg`, `launch_args_example_pkg` | [[cpp-learn-inter-unit3-launch]] · [[cpp-learn-inter-unit3-args]] · [[core-launch-args-include]] · [[core-launch-substitutions]] |
| 4 | launch files in Python, XML and YAML | `launch_tests_pkg` | [[cpp-learn-inter-unit4-launch]] · [[core-launch-xml-yaml]] |
| 5 | parameters, CLI, YAML, validation callback | `parameter_tests` | [[cpp-learn-inter-unit5-params]] · [[cpp-params-declare-get]] · [[cpp-params-callback]] · [[core-param-yaml-cli]] |
| 7 | QoS: compatibility, durability, deadline, lifespan, liveliness, bags | `qos_tests_pkg` | [[cpp-learn-inter-unit7-qos]] · [[cpp-qos-profile]] · [[cpp-qos-events-demo]] · [[core-qos-policies]] |
| 8 | DDS, RMW implementations, the ros2 daemon | `dds_tests_pkg` | [[cpp-learn-inter-unit8-dds]] · [[cpp-dds-loss-test]] · [[core-rmw-implementations]] |
| 9 | managed nodes, own lifecycle manager, Nav2 | `managed_node_tests` | [[cpp-learn-inter-unit9-lifecycle]] · [[cpp-lifecycle-param-node]] · [[core-lifecycle-services-cli]] |

## The demo (unit 1)
The course's demo package `mars_rover_demo` (its repository link is given in the course) is cloned into `~/ros2_ws/src`, built and sourced:
```bash
ros2 launch mars_rover_demo demo_parameters.launch.py
ros2 param set /params_demo_node angular_speed 0.5     # Set parameter successful
ros2 param set /params_demo_node angular_speed 0.0     # stop turning
ros2 param set /params_demo_node linear_speed 0.1
```
The node logs `[params_demo_node]: MoveRobot started | linear=0.00 angular=0.50 rate=1.00 Hz` and the rover rotates at 0.5 rad/s. No velocity command was typed: the node itself publishes on `/cmd_vel` from a timer, using the current parameter values, the program of [[cpp-params-declare-get]].

## Python and C++
The same course in Python: [[core-learn-inter-start-here]] (its unit 9 was already C++; that program is [[cpp-lifecycle-node]]). Choosing a language per node: [[core-lang-choice]].
