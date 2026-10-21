---
id: urdf-learn-unit3-box-bot
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "Unit 3 micro-project: box_bot geometric and mesh versions"
domain: urdf
area: learn
distro: humble
tested: false
audience: students
summary: "Micro-project box_bot: empty base_link, chassis, two continuous wheels, yaw-roll-pitch caster chains; box_bot_geometric.urdf and the mesh version."
tags: [course, unit 3, micro-project, box_bot, my_box_bot_description, box_bot_geometric.urdf, caster wheel, continuous, cute_cube.dae]
see: ["[[urdf-learn-start-here]]", "[[urdf-links]]", "[[urdf-joints]]", "[[urdf-description-package]]", "[[urdf-joint-state-publisher]]"]
requires: [ros2-core]
version_notes:
  - "humble: the course's <joint_properties damping friction/> and <axis rpy> are ignored by the parser and left out here — https://github.com/ros/urdfdom/blob/humble/urdf_parser/src/joint.cpp (URDF-V02)"
  - "humble: the 'only difference' snippet gives the mesh visual box_bot_blue; the solution file has no material there, which keeps the mesh colors (URDF-V04, URDF-V07)"
---
# Unit 3 micro-project: box_bot geometric and mesh versions

**TL;DR** Build `box_bot`: a 0.1 m cube on an empty `base_link`, two motor wheels on continuous joints, and two caster wheels made of three continuous joints each (yaw → roll → pitch), because URDF has no spherical joint. Then replace the cube's visual with a mesh. This file is the base of units 4–7.

## Files
Package `my_box_bot_description` (ament_cmake, `urdf` + `xacro`, folders `launch rviz urdf meshes`, install rule with `meshes`; [[urdf-description-package]]). Copy `urdf_vis.rviz` from unit 2. Launch files `urdf_visualize_geometric.launch.py` and `urdf_visualize_meshes.launch.py` are the RViz launch file of [[urdf-description-package]] with `urdf_file = 'box_bot_geometric.urdf'` / `'box_bot_geometric_meshes.urdf'` and `package_description = "my_box_bot_description"`.

## box_bot_geometric.urdf
```xml
<?xml version="1.0"?>
<robot name="box_bot">
  <material name="red"><color rgba="1.0 0.0 0.0 1"/></material>
  <material name="green_light"><color rgba="0.0 1.0 0.0 1"/></material>
  <material name="green_dark"><color rgba="0.0 0.5 0.0 1"/></material>
  <material name="blue"><color rgba="0.0 0.0 1.0 1"/></material>
  <material name="black"><color rgba="0.0 0.0 0.0 1"/></material>
  <material name="white"><color rgba="1.0 1.0 1.0 1"/></material>
  <material name="box_bot_blue"><color rgba="0.088656 0.428691 0.491021 1"/></material>

  <link name="base_link"></link>  <!-- frame only -->

  <!-- Body -->
  <link name="chassis">
    <visual>
      <geometry><box size="0.1 0.1 0.1"/></geometry>
      <material name="box_bot_blue"/>
    </visual>
  </link>
  <joint name="base_link_joint" type="fixed">
    <origin rpy="0 0 0" xyz="0 0 0"/>
    <parent link="base_link"/>
    <child link="chassis"/>
  </joint>

  <!-- Wheel Left (Wheel Right: right_wheel, material white, joint_right_wheel at xyz="0 -0.05 -0.025") -->
  <link name="left_wheel">
    <visual>
      <origin rpy="0 1.5707 1.5707" xyz="0 0 0"/>
      <geometry><cylinder length="0.001" radius="0.035"/></geometry>
      <material name="black"/>
    </visual>
  </link>
  <joint name="joint_left_wheel" type="continuous">
    <origin rpy="0 0 0" xyz="0 0.05 -0.025"/>
    <child link="left_wheel"/>
    <parent link="chassis"/>
    <axis xyz="0 1 0"/>
    <limit effort="10000" velocity="1000"/>
  </joint>

  <!-- Caster Wheel Front (Back: back_* names, back_yaw_joint at xyz="-0.04 0 -0.05", back_pitch_link green_light) -->
  <link name="front_yaw_link">
    <visual>
      <origin rpy="0 1.5707 1.5707" xyz="0 0 0"/>
      <geometry><cylinder length="0.005" radius="0.010"/></geometry>
      <material name="blue"/>
    </visual>
  </link>
  <joint name="front_yaw_joint" type="continuous">
    <origin rpy="0 0 0" xyz="0.04 0 -0.05"/>
    <parent link="chassis"/>
    <child link="front_yaw_link"/>
    <axis xyz="0 0 1"/>
    <limit effort="1000.0" velocity="100.0"/>
    <dynamics damping="0.0" friction="0.1"/>
  </joint>
  <link name="front_roll_link">
    <visual>
      <origin rpy="0 1.5707 1.5707" xyz="0 0 0"/>
      <geometry><cylinder length="0.005" radius="0.010"/></geometry>
      <material name="red"/>
    </visual>
  </link>
  <joint name="front_roll_joint" type="continuous">
    <origin rpy="0 0 0" xyz="0 0 0"/>
    <parent link="front_yaw_link"/>
    <child link="front_roll_link"/>
    <axis xyz="1 0 0"/>
    <limit effort="1000.0" velocity="100.0"/>
    <dynamics damping="0.0" friction="0.1"/>
  </joint>
  <link name="front_pitch_link">
    <visual>
      <origin rpy="0 1.5707 1.5707" xyz="0 0 0"/>
      <geometry><sphere radius="0.010"/></geometry>
      <material name="green_dark"/>
    </visual>
  </link>
  <joint name="front_pitch_joint" type="continuous">
    <origin rpy="0 0 0" xyz="0 0 0"/>
    <parent link="front_roll_link"/>
    <child link="front_pitch_link"/>
    <axis xyz="0 1 0"/>
    <limit effort="1000.0" velocity="100.0"/>
    <dynamics damping="0.0" friction="0.1"/>
  </joint>
</robot>
```
Write out the right wheel and the back caster as the comments say (same elements, other names and positions). Link tree of the complete file (generated from the course solution):
```text
base_link
└── chassis  (fixed: base_link_joint)
    ├── left_wheel  (continuous: joint_left_wheel)
    ├── right_wheel  (continuous: joint_right_wheel)
    ├── front_yaw_link  (continuous: front_yaw_joint)
    │   └── front_roll_link  (continuous: front_roll_joint)
    │       └── front_pitch_link  (continuous: front_pitch_joint)
    └── back_yaw_link  (continuous: back_yaw_joint)
        └── back_roll_link  (continuous: back_roll_joint)
            └── back_pitch_link  (continuous: back_pitch_joint)
```
Run it with the GUI and move every slider: each wheel must spin about the axis perpendicular to it, and each caster chain must turn about z, x and y.

## Mesh version (box_bot_geometric_meshes.urdf)
Only the chassis visual changes (the `box_bot_blue` material goes away so the mesh keeps its own look):
```xml
<link name="chassis">
  <visual>
    <geometry><mesh filename="package://my_box_bot_description/meshes/cute_cube.dae" scale="0.1 0.1 0.1"/></geometry>
  </visual>
</link>
```
`filename` uses `package://`; `scale` 0.1 because the mesh is modelled 10 times too big. The course's mesh file also already has the smaller caster discs of unit 4 (`length="0.001" radius="0.0045000000000000005"` for the yaw and roll cylinders).

## Pitfalls
- A wheel spins about the wrong axis → its visual `rpy` only rotates the drawing; the motion axis is the joint's `<axis xyz="0 1 0"/>`.
- In RViz2, adjust the TF display (Marker Scale 0.2, Show Names off) and save the config with File › Save.
