---
id: gazebo-learn-unit4-sim
type: reference
owner: equipo-ros2
updated: 2026-10-21
review_by: 2027-04-19
source: manual
confidentiality: internal
title: "Unit 4: box_bot_gazebo package, world, complete physical box_bot, spawn"
domain: gazebo
area: learn
distro: jazzy
tested: false
audience: students
summary: "Unit 4: my_box_bot_gazebo package, empty world and box_room, collisions and inertias per link, smaller casters, spawn files, wheel friction blocks."
tags: [course, unit 4, my_box_bot_gazebo, box_bot_empty.world, box_bot_meshes_collisions_inertias.urdf, box_bot_physical_properties.urdf, spawn_robot_ros2.launch.xml, inertia, friction]
see: ["[[gazebo-learn-start-here]]", "[[urdf-learn-unit3-box-bot]]", "[[gazebo-start-sim]]", "[[gazebo-world-sdf]]", "[[gazebo-spawn-urdf]]", "[[gazebo-urdf-sim-tags]]", "[[urdf-inertia]]"]
requires: [ros2-core, ros2-urdf]
version_notes:
  - "humble/fortress: box izz = m(x²+y²)/12; the course's formula printed x²+z² (its values are right) (URDF-V01)"
  - "humble/fortress: right_wheel uses material green, which the file never defines (URDF-V07)"
  - "jazzy/harmonic: mu/mu2 are two friction directions, kp stiffness, kd damping (GZ-V01, GZ-V02)"
---
# Unit 4: box_bot_gazebo package, world, complete physical box_bot, spawn

**TL;DR** Start from `box_bot_geometric_meshes.urdf` of unit 3 ([[urdf-learn-unit3-box-bot]]) and add what a simulator needs, step by step. Only the parts that change are shown; the technical notes hold the complete launch and world files.

## 1. Gazebo package and world
- Package `my_box_bot_gazebo` with `launch/ worlds/ models/` and `start_world.launch.py` ([[gazebo-start-sim]]). The course copies a `box_room` model into `models/` from its own repository; use any model folder of your own.
- World `worlds/box_bot_empty.world` ([[gazebo-world-sdf]]); then add the `<include>` of `model://box_room` and relaunch. Return to the empty world afterwards.
- `ros2 launch my_box_bot_gazebo start_world.launch.py` (stop it with Ctrl+C before the next run).

## 2. Collisions and inertias (exercise 4.2)
Copy the mesh URDF to `box_bot_meshes_collisions_inertias.urdf` and give every link a `<collision>` and an `<inertial>` ([[urdf-inertia]]). The chassis collision is the bounding box of the mesh (read its dimensions in a 3D tool such as Blender: 1 m modelled × scale 0.1 = 0.1 m). One block per link type:
```xml
<!-- chassis (add after the mesh visual) -->
<collision><geometry><box size="0.1 0.1 0.1"/></geometry></collision>
<inertial>
  <mass value="0.5"/>
  <origin rpy="0 0 0" xyz="0 0 0"/>
  <inertia ixx="0.0008333333333333335" ixy="0" ixz="0" iyy="0.0008333333333333335" iyz="0" izz="0.0008333333333333335"/>
</inertial>

<!-- left_wheel, right_wheel: same origin as the visual -->
<collision>
  <origin rpy="0 1.5707 1.5707" xyz="0 0 0"/>
  <geometry><cylinder length="0.001" radius="0.035"/></geometry>
</collision>
<inertial>
  <origin rpy="0 1.5707 1.5707" xyz="0 0 0"/>
  <mass value="0.05"/>
  <inertia ixx="1.531666666666667e-05" ixy="0" ixz="0" iyy="1.531666666666667e-05" iyz="0" izz="3.0625000000000006e-05"/>
</inertial>

<!-- front/back yaw and roll links: smaller discs (visual and collision) -->
<cylinder length="0.001" radius="0.0045000000000000005"/>
<!-- their inertial: same origin, mass 0.001 -->
<inertia ixx="5.145833333333334e-09" ixy="0" ixz="0" iyy="5.145833333333334e-09" iyz="0" izz="1.0125000000000003e-08"/>

<!-- front/back pitch spheres (radius 0.010): mass 0.001 -->
<inertia ixx="4e-08" ixy="0" ixz="0" iyy="4e-08" iyz="0" izz="4e-08"/>
```
- The caster discs of unit 3 (`length="0.005" radius="0.010"`) would touch the ground and block the casters: shrink them as above; keep them visible to see the caster structure.
- The course computes the values with its own calculator (example with 0.2 kg); the file uses 0.5 kg for the chassis. The formulas give the same numbers ([[urdf-inertia]]).
- Wheel colors in this file: left `red`, right `green`. Define `green` (it is not in the file) or use `yellow` as the next units do.

## 3. Spawn
New files: `my_box_bot_gazebo/launch/spawn_robot_description.launch.py`, `my_box_bot_gazebo/launch/spawn_robot_ros2.launch.xml`, `my_box_bot_description/launch/urdf_visualize_meshes_collisions_inertias.launch.py` (the RViz launch file with the new URDF). Contents: [[gazebo-spawn-urdf]]. Add the description package paths to `start_world.launch.py` (the version in [[gazebo-start-sim]]).
```bash
# Terminal 1
cd ~/ros2_ws && colcon build && source install/setup.bash
ros2 launch my_box_bot_gazebo start_world.launch.py
# Terminal 2
cd ~/ros2_ws && colcon build --symlink-install --packages-select my_box_bot_gazebo my_box_bot_description
source install/setup.bash
ros2 launch my_box_bot_gazebo spawn_robot_ros2.launch.xml
```
In RViz2 the links behind non-fixed joints have no TF yet: in simulation the joint states come from the simulator, added in unit 5.

## 4. Physical properties
`box_bot_physical_properties.urdf` = the previous file plus one `<gazebo reference>` friction block per contact link ([[gazebo-urdf-sim-tags]]): `left_wheel` and `right_wheel` mu = mu2 = 10, `front_pitch_link` and `back_pitch_link` mu = mu2 = 0.5, all with kp = kd = 1e7. Wheel colors from now on: left `red`, right `yellow`, defined as `<material name="yellow"><color rgba="1.0 1.0 0.0 1"/></material>`. Launch with `spawn_robot_ros2_physical.launch.xml` and `urdf_visualize_physical.launch.py`, the same two-include pattern. The robot looks the same; the friction matters once it moves.
