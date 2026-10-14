---
id: core-learn-inter-unit9-lifecycle
type: reference
owner: equipo-ros2
updated: 2026-10-14
review_by: 2027-04-12
source: manual
confidentiality: internal
title: "Intermediate Unit 9: managed node exercise"
domain: core
area: learn-intermediate
distro: humble
tested: false
audience: students
summary: "Unit 9 exercise 9.1 (shutdown service in the lifecycle manager) and the Nav2 part: pause and resume a navigation system."
tags: [course, unit 9, managed_scan, lifecycle manager, shutdown_managed_node, Empty, nav2_lifecycle_manager, manage_nodes, students]
see: ["[[core-lifecycle-manager-client]]", "[[core-lifecycle-services-cli]]", "[[core-lifecycle-cpp-node]]", "[[core-lifecycle-concepts]]"]
requires: []
version_notes:
  - "humble: managed nodes exist in Python too (rclpy.lifecycle); the course used C++ only — https://github.com/ros2/rclpy/tree/humble/rclpy/rclpy/lifecycle (V98)"
---
# Intermediate Unit 9: managed node exercise

**TL;DR** Unit 9 builds the C++ package `managed_scan`: a managed laser node ([[core-lifecycle-cpp-node]]), driven by hand ([[core-lifecycle-services-cli]]) and by an own manager ([[core-lifecycle-manager-client]]). Exercise 9.1 extends the manager; the last part applies the idea to Nav2.

## Exercise 9.1
Modify the lifecycle manager example:
1. Add a service server that receives an `Empty` message (`std_srvs/srv/Empty`), named `shutdown_managed_node`.
2. When it is called, transition the managed node from `active` to `finalized`.
Relaunch: `managed_scan_node` goes to `active` by itself thanks to the manager and publishes on `managed_scan`; call `shutdown_managed_node` from a terminal and watch the node reach `finalized` and the topic stop.

## Managed nodes in Nav2
This part needs the packages of the Nav2 course. Download them from that course with the IDE, upload them to this course's `~/ros2_ws/src`, build and source. Then:
```bash
ros2 launch path_planner navigation.launch.py
ros2 service list | grep lifecycle
```
Set the initial pose in RViz2. `/lifecycle_manager/manage_nodes` (`nav2_msgs/srv/ManageLifecycleNodes`) pauses (`command: 1`) and resumes (`command: 2`) the whole navigation stack. Everything about that service and the Nav2 lifecycle manager is in the `ros2-nav2` skill (notes `nav2-lifecycle-manager` and `nav2-lifecycle-manage-nodes`).

## Pitfalls
- The node names in the course launch file use `recoveries_server`; in Humble's Nav2 that server is `behavior_server` (see the Nav2 notes).
- `finalized` cannot be undone: restart the process to use the node again.
