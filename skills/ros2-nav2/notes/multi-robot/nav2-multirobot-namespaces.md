---
id: nav2-multirobot-namespaces
type: reference
owner: equipo-ros2
updated: 2026-10-10
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "Multi-robot setup: namespaces for nodes, topics and frames"
domain: nav2
area: multi-robot
distro: humble
tested: false
audience: dev
summary: "Multi-robot prerequisite: a namespace per robot (tb3_0, tb3_1) for nodes, topics and frames; how to check them."
tags: [multi-robot, namespace, tb3_0, tb3_1, frames, ros2 node list, view_frames, TF tree]
see: ["[[core-multi-robot-namespacing]]", "[[nav2-multirobot-mapping]]", "[[nav2-multirobot-localization]]", "[[core-tf-basics]]"]
requires: [ros2-core]
version_notes:
  - "humble: view_frames writes frames_<YYYY-MM-DD_HH.MM.SS>.pdf (use -o frames for a fixed name) — https://github.com/ros2/geometry2/blob/humble/tf2_tools/tf2_tools/view_frames.py (NAV2-V15)"
  - "lyrical: Nav2 bringup and nav2_params.yaml are namespace-ready with relative topics (Kilted) — https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/migration_guides/jazzy/Jazzy.md (NAV2-V25)"
---
# Multi-robot setup: namespaces for nodes, topics and frames

**TL;DR** Identical robots publish the same `/cmd_vel`, the same `base_footprint` frame and run nodes with the same names, so navigation cannot tell them apart. Put each robot under a **namespace** (`tb3_0`, `tb3_1`) for its topics, frames and node names **before** configuring Nav2.

## Where namespaces are configured
- **Simulated robots**: in the URDF description and the Gazebo plugins.
- **Real robots**: in the bring-up provided by the vendor.
If the URDF, the plugins or the bring-up do not support namespaces, the robots are hard to boot in namespace mode. How to do it in ROS 2 (no `tf_prefix`): [[core-multi-robot-namespacing]]. In the course simulation two TurtleBot3 robots, `tb3_0` and `tb3_1`, are already namespaced.

## Check the node names
```bash
ros2 node list
```
```
/gazebo
/tb3_0/robot_state_publisher
/tb3_0/turtlebot3_diff_drive
/tb3_0/turtlebot3_imu
/tb3_0/turtlebot3_joint_state
/tb3_0/turtlebot3_laserscan
/tb3_1/robot_state_publisher
/tb3_1/turtlebot3_diff_drive
/tb3_1/turtlebot3_imu
/tb3_1/turtlebot3_joint_state
/tb3_1/turtlebot3_laserscan
```

## Check the topic names
```bash
ros2 topic list
```
```
/clock
/parameter_events
/performance_metrics
/rosout
/tb3_0/cmd_vel
/tb3_0/imu
/tb3_0/joint_states
/tb3_0/odom
/tb3_0/robot_description
/tb3_0/scan
/tb3_1/cmd_vel
/tb3_1/imu
/tb3_1/joint_states
/tb3_1/odom
/tb3_1/robot_description
/tb3_1/scan
/tf
/tf_static
```
Each robot has its own IMU, odom, scan, cmd_vel, robot description and joint states topics; `/tf` is shared and the frames are prefixed.

## Check the frame names
```bash
cd ~/ros2_ws/src; ros2 run tf2_tools view_frames
```
In Humble this writes `frames_<date>.pdf` in the current directory (add `-o frames` for `frames.pdf`). Before localization there are two independent trees:
```
tb3_0/odom → tb3_0/base_footprint → tb3_0/base_link → tb3_0/base_scan, wheels, imu
tb3_1/odom → tb3_1/base_footprint → tb3_1/base_link → …
```
After both AMCL nodes run, `map` becomes the common parent of `tb3_0/odom` and `tb3_1/odom` ([[nav2-multirobot-localization]]).

## Pitfalls
- A namespace in the launch file does not rename frames inside config files: frames must be edited by hand.
- A sensor plugin without namespace support publishes `/scan` for both robots → mixed data.
