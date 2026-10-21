---
id: urdf-joints
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "Joint elements: parent/child, origin vs axis frames, limit, joint types"
domain: urdf
area: model
distro: humble
tested: false
audience: dev
summary: "URDF joint: parent/child, origin in the parent frame, axis in the child frame, fixed/continuous/revolute/prismatic/floating/planar, <limit> lower/upper/effort/velocity."
tags: [joint, parent, child, origin, axis, rpy, fixed, continuous, revolute, prismatic, floating, planar, limit, effort, velocity, lower, upper]
see: ["[[urdf-links]]", "[[urdf-joint-extras]]", "[[urdf-joint-state-publisher]]", "[[urdf-frames-rviz]]", "[[core-tf-broadcaster]]"]
requires: [ros2-core]
version_notes:
  - "humble: <joint_properties> does not exist (ignored); damping and friction go in <dynamics>; <axis> has only xyz — https://github.com/ros/urdfdom/blob/humble/urdf_parser/src/joint.cpp (URDF-V02)"
  - "humble: <limit> effort and velocity are required attributes; lower/upper default 0 — https://github.com/ros/urdfdom/blob/humble/urdf_parser/src/joint.cpp (URDF-V05, URDF-V27)"
  - "humble: planar becomes a fixed joint in kdl_parser, robot_state_publisher skips floating joints, joint_state_publisher gives neither a slider — https://github.com/ros/kdl_parser/blob/humble/kdl_parser/src/kdl_parser.cpp (URDF-V21)"
---
# Joint elements: parent/child, origin vs axis frames, limit, joint types

**TL;DR** A joint connects a **parent** link to a **child** link. `<origin>` places the child (joint) frame in the **parent** frame; `<axis>` is expressed in the **child** frame. The type decides how the child moves; `revolute` and `prismatic` need a `<limit>`.

## A fixed joint (welded)
```xml
<joint name="base_link_to_head_link_joint" type="fixed">
  <origin xyz="0 0 0.11" rpy="0 0 0"/>   <!-- head_link frame 0.11 m above base_link -->
  <parent link="base_link"/>
  <child link="head_link"/>
</joint>
```
The links form one tree: a single root (here `base_link`, every other link hangs from it), unique link and joint names.

## Moving joints
```xml
<joint name="base_link_to_head_link_joint" type="continuous">
  <origin xyz="0 0 0.11" rpy="0 0 0"/>
  <parent link="base_link"/>
  <child link="head_link"/>
  <axis xyz="0 0 1"/>                   <!-- z of head_link, not of base_link -->
</joint>
```
| Type | Motion | `<limit>` |
|---|---|---|
| `fixed` | none | — |
| `continuous` | rotation about `axis`, no position limit (wheels) | optional (`effort`, `velocity`) |
| `revolute` | rotation between `lower` and `upper` (rad) | required: `<limit effort="100" velocity="1.0" lower="-1.57" upper="1.57"/>` |
| `prismatic` | translation along `axis` (m) | required: `<limit effort="100" velocity="0.1" lower="-0.1" upper="0.1"/>` |
| `floating`, `planar` | 6 DOF / motion in a plane | parsed, but not usable with the ROS 2 tools (below) |

`<limit>`: `lower`/`upper` (rad or m, default 0; omit for continuous), `effort` (N or N·m) and `velocity` (rad/s or m/s) are **required** attributes. They are not "simulation only": the parser rejects a revolute/prismatic joint without them, and controllers and planners read them.

## Frames rule
- **Origin** (translation + `rpy` orientation) → measured in the **parent** frame.
- **Axis** → in the **child** frame. Example: an arm joint with `rpy="-1.57 0 0"` and `<axis xyz="0 0 1"/>` rotates about the arm's own z, which points along the parent's +y (a roll of −90° maps z onto +y).
- See it: TF display in RViz2 plus the joint sliders of [[urdf-joint-state-publisher]].

## floating and planar
urdfdom parses them, but `kdl_parser` turns `planar` into a fixed joint (warning) and robot_state_publisher publishes no TF for `floating`; joint_state_publisher gives neither a slider. Model a planar base as a chain of `prismatic` + `continuous` joints, and publish a moving base as `odom → base_link` from odometry ([[core-tf-broadcaster]]).

## Pitfalls
- `<joint_properties damping friction/>` (found in old examples) is silently ignored: use `<dynamics>` ([[urdf-joint-extras]]). `<axis rpy="…">` is ignored too: only `xyz` counts.
- Revolute without `<limit>` → "Joint [x] is of type REVOLUTE but it does not specify limits" and the model fails to load.
- Axis given in the parent's terms → the link turns about the wrong direction.
