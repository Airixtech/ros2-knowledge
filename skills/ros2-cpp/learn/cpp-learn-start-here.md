---
id: cpp-learn-start-here
type: reference
owner: equipo-ros2
updated: 2026-10-26
review_by: 2027-04-24
source: manual
confidentiality: internal
title: "C++ basics course map: units 2-9, packages per unit, environment, the Python twin course"
domain: cpp
area: learn
distro: humble
tested: false
audience: students
order: 1
summary: "Learning path of the C++ basics course (Leo Mars rover, Humble): units 2-9, packages, notes, environment, Python twin."
tags: [course, learning path, Leo rover, Mars rover, C++, units, packages, environment, students]
see: ["[[core-learn-start-here]]", "[[cpp-learn-unit2-basics]]", "[[cpp-node-first-program]]", "[[cpp-pkg-cmake]]", "[[cpp-learn-inter-start-here]]"]
requires: [ros2-core]
version_notes: []
---
# C++ basics course map

**TL;DR** The C++ twin of the ROS 2 basics course in ros2-core: the same Leo Mars rover simulation on Humble, rewritten with `rclcpp` and `ament_cmake` packages, plus a unit on components (C++ only). The course environment (simulation workspace, sourcing, saved `~/.bashrc`) is described in [[core-learn-start-here]]. Unit 2 starts with the foundations: how ROS 2 programs are organized and launched (packages, launch files), first C++ programs, nodes and client libraries.

## Units, packages and notes
| Unit | Topic | Packages | Read |
|---|---|---|---|
| 2 | basics, packages, nodes, launch | `mars_rover_systems` | [[cpp-learn-unit2-basics]] · [[cpp-pkg-cmake]] · [[cpp-node-first-program]] · [[cpp-node-class]] · [[cpp-launch-cpp-nodes]] |
| 3 | topics, custom messages, quiz | `mars_rover_tasks`, `custom_interfaces`, `topics_quiz` | [[cpp-learn-unit3-topics]] · [[cpp-learn-unit3-quiz]] · [[cpp-topic-subscriber]] · [[cpp-topic-publisher]] · [[cpp-pub-sub-node]] · [[cpp-iface-use]] |
| 4 | services, custom srv, quiz | `mars_rover_tasks`, `custom_interfaces`, `services_quiz`, `services_quiz_srv` | [[cpp-learn-unit4-services]] · [[cpp-srv-server]] · [[cpp-srv-client]] · [[cpp-srv-custom]] |
| 5 | callbacks, single-threaded execution | `basics_ros2_multithreading` | [[cpp-learn-unit5-callbacks]] · [[cpp-callbacks-functions]] · [[cpp-exec-blocking]] |
| 6 | multithreading, callback groups | `basics_ros2_multithreading` | [[cpp-learn-unit6-multithreading]] · [[cpp-exec-callback-groups]] |
| 7 | actions, Nav2 client, quiz | `my_action_client`, `my_action_server`, `custom_interfaces`, `actions_quiz`, `actions_quiz_msg` | [[cpp-learn-unit7-actions]] · [[cpp-action-client]] · [[cpp-action-server]] |
| 8 | components | `rover_components` | [[cpp-learn-unit8-components]] · [[cpp-component-write]] |
| 9 | logs, RViz2, view_frames, ros2 doctor | `logs_test` | [[cpp-learn-unit9-debugging]] · [[cpp-logging]] |

## Course environment
- `source /opt/ros/humble/setup.bash` for the CLI; `source ~/ros2_ws/install/setup.bash` after each build, in every terminal. The simulation packages (`leo_description`) live in the course's simulation workspace, which must be sourced before building packages that use them ([[core-learn-start-here]]).
- The course ships extra files (the plant-detector AI class and model, a text-detection script) in a repository whose link is given in the course; the timing visualizations of units 5–6 are scripts of the course environment.
- A real robot project (parts I–III after units 3, 6 and 7) is done on the course platform.

## Python and C++
The same missions in Python: [[core-learn-unit2-basics]] and the following units of ros2-core. Choosing a language for a node, and mixing both in one robot: [[core-lang-choice]].

Next course: the intermediate course in C++ (launch formats, parameters, QoS, DDS, managed nodes), [[cpp-learn-inter-start-here]].
