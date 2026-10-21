---
id: urdf-overview
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "What a URDF is for, file structure, units, description to RViz/simulator workflow"
domain: urdf
area: model
distro: humble
tested: false
audience: dev
summary: "URDF purpose (TF, RViz, navigation, manipulation, simulation), robot/link/joint structure, SI units, robot_description to robot_state_publisher, RViz2 and Gazebo."
tags: [urdf, robot model, robot_description, link, joint, units, xml, rviz2, gazebo, workflow]
see: ["[[core-urdf-basics]]", "[[urdf-links]]", "[[urdf-joints]]", "[[urdf-description-package]]", "[[urdf-frames-rviz]]", "[[core-robot-state-publisher]]"]
requires: [ros2-core]
version_notes:
  - "lyrical: urdfdom 6.0 adds the capsule geometry for <robot version=\"1.1\"> — https://github.com/ros/urdfdom/blob/lyrical/urdf_parser/src/link.cpp (URDF-V14)"
---
# What a URDF is for, file structure, units, description to RViz/simulator workflow

**TL;DR** A URDF (Unified Robot Description Format) is one XML file that describes a robot as rigid **links** connected by **joints**, with their shapes, colors, masses and limits. ROS 2 tools read it from the `robot_description` parameter/topic: robot_state_publisher turns it into TF, RViz2 draws it, and a simulator spawns it. Minimal example and common pitfalls: [[core-urdf-basics]].

## Why a robot needs a model
- **Describe a real robot to ROS:** TF publishing, navigation and manipulation need to know where each part and each sensor is (a camera on the head, a lidar on top).
- **Simulate a robot:** spawn it in Gazebo Sim to test robots you do not have, robots not built yet (iterate on the design before manufacturing), or tests too risky for real hardware.

## What a URDF contains
| Element | Holds |
|---|---|
| `<robot name>` | the root element; exactly one tree of links |
| `<link>` | a rigid body: `visual`, `collision`, `inertial` ([[urdf-links]]) |
| `<joint>` | parent link, child link, pose, axis, type, limits ([[urdf-joints]]) |
| `<material>` | named colors or textures for visuals |
| `<gazebo>`, `<ros2_control>` | simulator and controller extensions (ros2-gazebo skill) |

Sensors and actuators are links and joints plus those extensions. All values are SI units: **meters**, **radians**, **kilograms** (inertia in kg·m²).

## Skeleton
```xml
<?xml version="1.0"?>
<robot name="urdfbot">
  <link name="base_link">
    <visual>
      <geometry><box size="0.1 0.1 0.1"/></geometry>
    </visual>
  </link>
</robot>
```

## Workflow
```text
urdf/robot.urdf (or .xacro) ──xacro──▶ robot_description parameter
robot_state_publisher ──▶ /robot_description (transient local) + /tf_static (fixed joints)
/joint_states (GUI, drivers, simulator) ──▶ robot_state_publisher ──▶ /tf (movable joints)
RViz2 RobotModel reads /robot_description · Gazebo spawns it from the same topic
```
Package layout and launch files: [[urdf-description-package]]. How links become TF frames in RViz2: [[urdf-frames-rviz]]. Macros instead of copy-paste: [[urdf-xacro-workflow]].

## Pitfalls
- Editor without XML syntax highlighting → unbalanced tags go unnoticed; validate with `check_urdf` ([[urdf-joint-extras]]).
- A visual model (no `collision`/`inertial`) is enough for RViz, not for a simulator ([[urdf-inertia]]).
- Degrees instead of radians in `rpy` or limits: the model loads but is wrong.
