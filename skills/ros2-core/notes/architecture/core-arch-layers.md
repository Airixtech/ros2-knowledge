---
id: core-arch-layers
title: "Layered architecture, node roles, state management & bridges"
domain: core
area: architecture
distro: humble
tested: false
audience: dev
summary: "Layered robot stack (drivers→perception→planning→control→behavior→UI), single-responsibility nodes, lifecycle/FSM/BT, external bridges."
tags: [architecture, layers, behavior tree, FSM, foxglove, rosbridge]
see: ["[[core-arch-failure-rt]]", "[[core-composition]]", "[[core-lifecycle-concepts]]", "[[core-nav2-overview]]"]
requires: []
version_notes: []
---
# Layered architecture, node roles, state management & bridges

**TL;DR** Dependencies flow downward only. Each node has a single responsibility and a concrete name. Use lifecycle nodes for bring-up and BTs or FSMs for missions. Expose data to the outside through bridges (Foxglove, rosbridge).

## Layered architecture
```
UI / Monitoring    Foxglove, RViz2, PlotJuggler
Behavior           BT.CPP, YASMIN, SMACC2, plansys2        -- actions -->
Planning           MoveIt2, Nav2 planner_server            -- Path / JointTrajectory -->
Control            Nav2 controller_server, ros2_control    -- Twist / hw commands -->
Perception         SLAM, EKF, detection, PCL               <-- sensor_msgs
Drivers            ros2_control SystemInterface, camera drivers  <-- bytes
Hardware           sensors, actuators, MCU, FPGA
```
| Layer | Publishes | Consumes |
|---|---|---|
| Drivers | sensor_msgs, joint_states | commands |
| Perception | /map, /odometry/filtered, /detections | sensor_msgs |
| Planning | Path, trajectories | map, pose, goal |
| Control | cmd_vel, actuator refs | path, odom |
| Behavior | goals | state |
Needing data from two non-adjacent layers is a modeling smell.

## Responsibilities
Single Responsibility per node, named with a concrete noun (`LocalPlanner`, `BatteryMonitor`). Nav2 example: bt_navigator, planner_server, controller_server, behavior_server, smoother_server, waypoint_follower, map_server, amcl, lifecycle_manager ([[core-nav2-overview]]).

## State management
| Tool | Granularity | Best for |
|---|---|---|
| Lifecycle nodes | per node | deterministic bring-up of servers ([[core-lifecycle-concepts]]) |
| FSM (YASMIN, SMACC2) | mission | rigid, few states |
| Behavior Trees (BT.CPP) | mission | reactive, modular, reusable recovery subtrees |
| plansys2 (PDDL) | symbolic | combinatorial task planning |
Nav2 style: a BT orchestrator + lifecycle servers under lifecycle_manager.

## External integration
| Need | Bridge |
|---|---|
| Web dashboards (high BW) | `foxglove_bridge` (`ros2 launch foxglove_bridge foxglove_bridge_launch.xml port:=8765`) |
| Legacy web JS | rosbridge_suite + roslibjs |
| Recording | rosbag2 (MCAP) ([[core-bag-record]]) |
| IoT | MQTT bridge |
| Time series | InfluxDB/Prometheus via custom bridge |
Process boundaries and zero-copy: [[core-composition]]. Failures and real-time: [[core-arch-failure-rt]].
