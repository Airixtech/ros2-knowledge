---
id: urdf-learn-unit2-urdfbot
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "Unit 2 exercises: urdfbot links, joints, meshes, mimic claws"
domain: urdf
area: learn
distro: humble
tested: false
audience: students
summary: "Unit 2 on urdfbot: link, head joint, visual offset, joint types, materials, meshes, arm with mimic claws; final urdfbot_simple.urdf."
tags: [course, unit 2, urdfbot, urdfbot_simple.urdf, head_link, mimic, claw, joint_state_publisher_gui, exercise 2.7.1]
see: ["[[urdf-learn-start-here]]", "[[urdf-links]]", "[[urdf-joints]]", "[[urdf-joint-extras]]", "[[urdf-description-package]]", "[[urdf-frames-rviz]]"]
requires: [ros2-core]
version_notes:
  - "humble: a URDF material would replace the mesh colors in RViz2, so the mesh visuals carry no <material> — https://github.com/ros2/rviz/blob/humble/rviz_default_plugins/src/rviz_default_plugins/robot/robot_link.cpp (URDF-V04)"
---
# Unit 2 exercises: urdfbot links, joints, meshes, mimic claws

**TL;DR** One file, `urdfbot_description/urdf/urdfbot_simple.urdf`, grows step by step. Package, `CMakeLists.txt` and launch files: [[urdf-description-package]]. Each run: `colcon build --packages-select urdfbot_description && source install/setup.bash`, `ros2 launch urdfbot_description urdf_visualize.launch.py`, `rviz2 -d ~/ros2_ws/src/urdfbot_description/rviz/urdf_vis.rviz`, and `ros2 run joint_state_publisher_gui joint_state_publisher_gui` once joints move.

## Steps (only what changes)
1. **One link** `base_link` with a 0.1 m box: the skeleton of [[urdf-overview]]. Set up RViz2 and save `rviz/urdf_vis.rviz` ([[urdf-frames-rviz]]).
2. **Second link** `head_link` (same box) on a fixed joint:
   ```xml
   <joint name="base_link_to_head_link_joint" type="fixed">
     <origin rpy="0 0 0" xyz="0 0 0.11"/>
     <parent link="base_link"/>
     <child link="head_link"/>
   </joint>
   ```
   Two red boxes and two frames (the launch log prints "got segment base_link" and "got segment head_link"); `ros2 run rqt_tf_tree rqt_tf_tree` shows the tree.
3. **Visual offset**: `<origin rpy="0 0 0" xyz="0 0 0.1"/>` inside the head's `<visual>`: the box moves, the frame does not.
4. **Joint types** (exercise 2.7.1): make the joint `continuous` with `<axis xyz="0 0 1"/>` (then try `1 0 0`: it turns about the head's x), then `revolute` ±1.57 rad and `prismatic` ±0.1 m; the solution lines are the revolute and prismatic rows of [[urdf-joints]]. Keep the revolute version.
5. **Materials**: `white` body, `blue` head, defined as in [[urdf-links]].
6. **Meshes**: copy your meshes to `meshes/` and add `meshes` to the install rule. The body and head visuals become meshes, the head offset goes back to `0 0 0` (the head mesh has its own offset) and the joint moves down to `xyz="0 0 0.07"`; the materials are dropped so the meshes keep their colors.
7. **Right arm**: `upper_arm_r_link` (joint `rpy="-1.57 0 0"`, axis z of the arm), `lower_arm_r_link` (axis x) and two claws. In RViz2 set TF Marker Scale to 0.3.
8. **mimic**: before it, both claws have their own slider and the same `lower="-0.7" upper="0.7"` limits. With `<mimic>` claw B follows claw A with one slider, and the course sets B's now unused limits to `0.0`. Try `offset="-0.8"` and `multiplier="0.1"`; remove the follower's `<limit>` and `check_urdf` fails ([[urdf-joint-extras]]).

## Final urdfbot_simple.urdf
```xml
<?xml version="1.0"?>
<robot name="urdfbot">
  <link name="base_link">
    <visual>
      <geometry><mesh filename="package://urdfbot_description/meshes/urdfbot_body.dae" scale="0.1 0.1 0.1"/></geometry>
    </visual>
  </link>
  <link name="head_link">
    <visual>
      <origin rpy="0 0 0" xyz="0 0 0"/>
      <geometry><mesh filename="package://urdfbot_description/meshes/urdfbot_head.dae" scale="0.1 0.1 0.1"/></geometry>
    </visual>
  </link>
  <joint name="base_link_to_head_link_joint" type="revolute">
    <origin xyz="0 0 0.07" rpy="0 0 0"/>
    <parent link="base_link"/>
    <child link="head_link"/>
    <axis xyz="0 0 1"/>
    <limit effort="100" velocity="1.0" lower="-1.57" upper="1.57"/>
  </joint>

  <!-- Right Arm -->
  <link name="upper_arm_r_link">
    <visual>
      <origin rpy="0 0 0" xyz="0 0 0"/>
      <geometry><mesh filename="package://urdfbot_description/meshes/urdfbot_limb.dae" scale="0.1 0.1 0.1"/></geometry>
    </visual>
  </link>
  <joint name="base_link_to_upper_arm_r_link_joint" type="revolute">
    <origin xyz="0 -0.03272 0.0279895" rpy="-1.57 0 0"/>
    <parent link="base_link"/>
    <child link="upper_arm_r_link"/>
    <axis xyz="0 0 1"/>
    <limit effort="100" velocity="1.0" lower="-1.0" upper="1.0"/>
  </joint>
  <link name="lower_arm_r_link">
    <visual>
      <origin rpy="0 0 0" xyz="0 0 0"/>
      <geometry><mesh filename="package://urdfbot_description/meshes/urdfbot_limb.dae" scale="0.1 0.1 0.1"/></geometry>
    </visual>
  </link>
  <joint name="upper_arm_r_link_to_lower_arm_r_link_joint" type="revolute">
    <origin xyz="0 0 -0.0568" rpy="0 0 0"/>
    <parent link="upper_arm_r_link"/>
    <child link="lower_arm_r_link"/>
    <axis xyz="1 0 0"/>
    <limit effort="100" velocity="1.0" lower="-1.0" upper="1.0"/>
  </joint>
  <link name="claw_a_r_link">
    <visual>
      <origin rpy="0 0 0" xyz="0 0 0"/>
      <geometry><mesh filename="package://urdfbot_description/meshes/urdfbot_claw.dae" scale="0.1 0.1 0.1"/></geometry>
    </visual>
  </link>
  <joint name="upper_arm_r_link_to_claw_a_r_link_joint" type="revolute">
    <origin xyz="0 0 -0.065" rpy="-1.57 0 -1.57"/>
    <parent link="lower_arm_r_link"/>
    <child link="claw_a_r_link"/>
    <axis xyz="0 0 1"/>
    <limit effort="100" velocity="1.0" lower="-0.7" upper="0.7"/>
  </joint>
  <link name="claw_b_r_link">
    <visual>
      <origin rpy="0 0 0" xyz="0 0 0"/>
      <geometry><mesh filename="package://urdfbot_description/meshes/urdfbot_claw.dae" scale="0.1 0.1 0.1"/></geometry>
    </visual>
  </link>
  <joint name="upper_arm_r_link_to_claw_b_r_link_joint" type="revolute">
    <origin xyz="0 0 -0.065" rpy="-1.57 0 1.57"/>
    <parent link="lower_arm_r_link"/>
    <child link="claw_b_r_link"/>
    <axis xyz="0 0 1"/>
    <limit effort="100" velocity="1.0" lower="0.0" upper="0.0"/>
    <mimic joint="upper_arm_r_link_to_claw_a_r_link_joint" multiplier="1.0" offset="0.0"/>
  </joint>
</robot>
```

Link tree (generated from the file above):
```text
base_link
├── head_link  (revolute: base_link_to_head_link_joint)
└── upper_arm_r_link  (revolute: base_link_to_upper_arm_r_link_joint)
    └── lower_arm_r_link  (revolute: upper_arm_r_link_to_lower_arm_r_link_joint)
        ├── claw_a_r_link  (revolute: upper_arm_r_link_to_claw_a_r_link_joint)
        └── claw_b_r_link  (revolute: upper_arm_r_link_to_claw_b_r_link_joint)
```
The claw joints are named `upper_arm_…` although their parent is `lower_arm_r_link`: keep the names as they are, the launch files and exercises use them.

## Pitfalls
- Head moves about the wrong axis → `<axis>` is in the head's frame, the joint `<origin>` in the body's ([[urdf-joints]]).
- Mesh visible but too big → `scale` missing; mesh not found → `meshes` missing from the install rule.
