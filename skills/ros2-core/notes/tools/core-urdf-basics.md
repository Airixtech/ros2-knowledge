---
id: core-urdf-basics
type: reference
owner: equipo-ros2
updated: 2026-10-09
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "URDF links, joints & pitfalls"
domain: core
area: tools
distro: humble
tested: false
audience: dev
summary: "Minimal URDF with visual/collision/inertial, joint types and limits, origin semantics, meshes, common simulation pitfalls."
tags: [URDF, link, joint, inertial, collision, continuous, revolute]
see: ["[[core-xacro]]", "[[core-robot-state-publisher]]", "[[core-tf-basics]]"]
requires: []
version_notes:
  - "lyrical: URDF improvements and RSP can read robot_description from a topic — https://docs.ros.org/en/rolling/Releases/Release-Lyrical-Luth.html (V19)"
---
# URDF links, joints & pitfalls

**TL;DR** A URDF is links (visual, collision, inertial) connected by joints. `<origin>` is the child frame's pose in the parent frame. Revolute and prismatic joints need `<limit>`, and every simulated link needs `<inertial>`.

## Minimal URDF
```xml
<?xml version="1.0"?>
<robot name="my_robot">
  <link name="base_link">
    <visual>
      <geometry><box size="0.5 0.3 0.1"/></geometry>
      <material name="blue"><color rgba="0 0 1 1"/></material>
    </visual>
    <collision><geometry><box size="0.5 0.3 0.1"/></geometry></collision>
    <inertial>
      <mass value="1.0"/>
      <inertia ixx="0.1" ixy="0" ixz="0" iyy="0.1" iyz="0" izz="0.1"/>
    </inertial>
  </link>

  <link name="wheel_left">
    <visual><geometry><cylinder radius="0.05" length="0.02"/></geometry></visual>
  </link>

  <joint name="base_to_wheel_left" type="continuous">
    <parent link="base_link"/>
    <child link="wheel_left"/>
    <origin xyz="0 0.17 0" rpy="-1.5708 0 0"/>
    <axis xyz="0 0 1"/>
  </joint>
</robot>
```
- Joint types: `fixed` (no motion) · `revolute` (rotation; `<limit lower upper effort velocity/>` is mandatory) · `continuous` (wheels) · `prismatic` (linear, needs a limit) · `floating` (6 DOF) · `planar`.
- `<origin xyz rpy>` = the child frame's pose in the parent frame. Collision: simple primitives or low-poly meshes. Visual may be detailed (DAE/STL via `package://pkg/meshes/x.dae`).
- Macros and arguments: [[core-xacro]]. Publishing TF from the model: [[core-robot-state-publisher]].

## Pitfalls
- `joint_state_publisher_gui` together with a real `joint_state_broadcaster` → conflicting `/joint_states`.
- A missing `<inertial>` makes Gazebo ignore or drop links, and unrealistic inertia makes the sim unstable.
- Sensor extrinsics belong in the URDF, not in ad-hoc `static_transform_publisher` calls.
