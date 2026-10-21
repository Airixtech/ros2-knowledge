---
id: urdf-frames-rviz
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "Links as TF frames; RViz2 RobotModel and TF displays, Transient Local QoS"
domain: urdf
area: model
distro: humble
tested: false
audience: dev
summary: "Links as TF frames: fixed joints on /tf_static, movable on /tf; RViz2 Fixed Frame, RobotModel description topic, rqt_tf_tree."
tags: [tf, tf_static, frames, rviz2, robotmodel, description topic, transient local, fixed frame, marker scale, rqt_tf_tree, robot_state_publisher]
see: ["[[core-tf-basics]]", "[[core-robot-state-publisher]]", "[[urdf-joint-state-publisher]]", "[[urdf-description-package]]", "[[core-debug-tools]]"]
requires: [ros2-core]
version_notes:
  - "humble: robot_state_publisher sends fixed joints once on /tf_static (StaticTransformBroadcaster) and movable joints on /tf from /joint_states — https://github.com/ros/robot_state_publisher/blob/humble/src/robot_state_publisher.cpp (URDF-V03)"
  - "humble: /robot_description is published with QoS(1).transient_local(); RViz2 RobotModel subscribes Transient Local by default — https://github.com/ros2/rviz/blob/humble/rviz_default_plugins/src/rviz_default_plugins/displays/robot_model/robot_model_display.cpp (URDF-V16)"
  - "lyrical: robot_state_publisher can subscribe to the description instead (use_robot_description_topic) — https://github.com/ros/robot_state_publisher/blob/lyrical/src/robot_state_publisher.cpp (URDF-V16)"
---
# Links as TF frames; RViz2 RobotModel and TF displays, Transient Local QoS

**TL;DR** Every link has a TF frame named like the link. robot_state_publisher publishes the transforms between them: **fixed** joints once on `/tf_static`, **movable** joints on `/tf` whenever `/joint_states` arrives. RViz2 draws the model from `/robot_description` and places each link with TF.

## Who publishes what
| Topic | Content | Needs |
|---|---|---|
| `/robot_description` | URDF text (transient local: late subscribers still get it) | the `robot_description` parameter |
| `/tf_static` | fixed joints, sent once | — |
| `/tf` | continuous/revolute/prismatic joints | `/joint_states` ([[urdf-joint-state-publisher]]) |

- One link and no joint → there is no transform at all; RViz2 still draws that link if it is the Fixed Frame.
- A movable joint without a joint state → RViz2 RobotModel shows an error and draws the child link without position (white). Publish joint states and it appears.
- `ros2 topic info /tf --verbose` and `ros2 topic info /tf_static --verbose` show robot_state_publisher as publisher.

## RViz2 setup
1. `rviz2` → **Global Options › Fixed Frame**: type `base_link` (not in the drop-down until TF exists).
2. **Add › RobotModel** → Description Source `Topic`, Description Topic `/robot_description`; Reliability `Reliable`, Durability `Transient Local` (the default).
3. **Add › TF** → frames and axes; RobotModel **Alpha** `0.5` shows frames inside the shapes; TF **Marker Scale** `0.2`–`0.3` and **Show Names** off for small robots.
4. **File › Save Config As** `rviz/urdf_vis.rviz` and start with `rviz2 -d <file>` or from launch ([[urdf-description-package]]).

## Frame vs shape
A visual `<origin>` moves the shape, not the frame: with `<origin xyz="0 0 0.1"/>` in the head's visual, the box floats 0.1 m above the `head_link` axes ([[urdf-links]]). The frame position comes only from the joint `<origin>` ([[urdf-joints]]).

## Tree view
```bash
ros2 run rqt_tf_tree rqt_tf_tree       # graph of frames, broadcaster and rate
ros2 run tf2_tools view_frames         # same as a PDF (frames_<date>.pdf)
```
Tree of a URDF without running anything: `check_urdf` ([[core-xacro]]). TF tools in general: [[core-tf-basics]].

## Pitfalls
- Fixed joints missing in a TF echo of `/tf` → they are on `/tf_static`.
- Description Topic set to Volatile → RViz2 never gets the latched description and shows nothing.
- Fixed Frame `map` (RViz default) with only a robot model → "frame map does not exist"; use `base_link` (or `odom` once odometry publishes it).
