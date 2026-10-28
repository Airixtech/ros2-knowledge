---
id: moveit-scene-grasp-boxes
type: reference
owner: equipo-ros2
updated: 2026-10-28
review_by: 2027-04-26
source: manual
confidentiality: internal
title: "Objects to grasp in simulation: grasp_box.urdf, grasp_box2.urdf and spawning them in Gazebo"
domain: moveit
area: planning
distro: humble
tested: false
audience: dev
summary: "grasp_box.urdf (0.04x0.04x0.08 m, 0.5 kg, corrected inertia), grasp_box2 (0.1 m cube); spawn with ros_gz_sim create -file -name -x -y -z."
tags: [grasp_box.urdf, grasp_box2.urdf, box inertia, ixx, izz, ros_gz_sim create, spawn, gazebo reference, mu1, mu2, kp, kd, Gazebo/Red, material, pick and place, simulation]
see: ["[[moveit-approach-retreat]]", "[[moveit-pick-and-place]]", "[[moveit-find-objects-action]]", "[[urdf-inertia]]", "[[urdf-links]]"]
requires: [ros2-core, ros2-urdf]
version_notes:
  - "humble: box inertia ixx = m(y²+z²)/12, iyy = m(x²+z²)/12, izz = m(x²+y²)/12; the course gives both boxes 0.000133333 (a 0.04 m cube) — https://docs.ros.org/en/humble/Tutorials/Intermediate/URDF/Adding-Physical-and-Collision-Properties-to-a-URDF-Model.html (MOVEIT-V06)"
  - "humble/fortress: spawn_entity.py is not a ros_gz tool; ros2 run ros_gz_sim create -file <path> -name <name> -x -y -z (same flags jazzy/harmonic, lyrical/jetty) — https://github.com/gazebosim/ros_gz/blob/jazzy/ros_gz_sim/src/create.cpp (MOVEIT-V33)"
  - "jazzy/harmonic: <material>Gazebo/Red</material> is read from an internal gazebo.material with a warning — https://github.com/gazebosim/gz-sim/blob/gz-sim8/src/SdfEntityCreator.cc (MOVEIT-V34)"
  - "humble/fortress: gz-sim 6 has no lookup for Gazebo/* names: which color is shown [verify] — https://github.com/gazebosim/gz-sim/blob/ign-gazebo6/src/SdfEntityCreator.cc (MOVEIT-V34)"
---
# Objects to grasp: two boxes and how to spawn them

**TL;DR** The pick-and-place exercises use a red box (0.04 × 0.04 × 0.08 m, 0.5 kg); the multi-object exercise adds a blue 0.1 m cube. Write the URDF, then spawn it in the running Gazebo with `ros_gz_sim create` at the position the exercise gives.

## `~/ros2_ws/src/grasp_box.urdf`
```xml
<robot name="grasp_box">
    <!-- Colours for RViz for geometric elements -->
    <material name="blue"><color rgba="0 0 0.8 1"/></material>
    <material name="red"><color rgba="0.8 0 0 1"/></material>
    <material name="green"><color rgba="0 0.8 0 1"/></material>
    <material name="grey"><color rgba="0.75 0.75 0.75 1"/></material>
    <material name="white"><color rgba="1.0 1.0 1.0 1"/></material>
    <material name="black"><color rgba="0 0 0 1"/></material>

    <!-- * * * Link Definitions * * * -->
    <link name="grasp_box_base_link">
        <inertial>
            <origin xyz="0 0 0" rpy="0 0 0"/>
            <mass value="0.5" />
            <!-- MOVEIT-V06: box 0.04 x 0.04 x 0.08 m, 0.5 kg; the course gives 0.000133333333333 for all three -->
            <inertia ixx="0.000333333333333" ixy="0.0" ixz="0.0" iyy="0.000333333333333" iyz="0.0" izz="0.000133333333333"/>
        </inertial>
        <collision>
            <origin xyz="0 0 0" rpy="0 0 0"/>
            <geometry>
                <box size="0.04 0.04 0.08"/>
            </geometry>
        </collision>
        <visual>
            <origin rpy="0.0 0 0" xyz="0 0 0"/>
            <geometry>
                <box size="0.04 0.04 0.08"/>
            </geometry>
            <material name="red"/>
        </visual>
    </link>

    <gazebo reference="grasp_box_base_link">
        <kp>100000.0</kp>
        <kd>100.0</kd>
        <mu1>0.25</mu1>
        <mu2>0.25</mu2>
        <!-- MOVEIT-V34: a Gazebo/* material name; Harmonic translates it with a warning, Fortress [verify] -->
        <material>Gazebo/Red</material>
    </gazebo>
</robot>
```
`kp`/`kd` (contact stiffness and damping) and `mu1`/`mu2` (friction) are the short `<gazebo reference>` tags, explained in the ros2-gazebo skill (note `gazebo-urdf-sim-tags`). For a portable color, drop `<material>Gazebo/Red</material>` (Gazebo then uses the URDF color) or use an `ambient`/`diffuse` block as shown there (MOVEIT-V34). Inertia formulas: [[urdf-inertia]].

## `~/ros2_ws/src/grasp_box2.urdf` (exercise 5.3): changes
Same file with: link `grasp_box2_base_link` (also in `<gazebo reference="grasp_box2_base_link">`), `<box size="0.1 0.1 0.1"/>` in collision and visual, `<material name="blue"/>`, `<material>Gazebo/Blue</material>`, and the inertia of a 0.1 m cube of 0.5 kg: `ixx = iyy = izz = 0.000833333333333` (the course: 0.000133333333333, MOVEIT-V06). The robot name stays `grasp_box`.

## Spawn into the running simulation
The course spawns with `spawn_entity.py` of its simulator; in Gazebo Sim the tool is `ros_gz_sim create` (same flags on Humble + Fortress, Jazzy + Harmonic and Lyrical + Jetty; ros2-gazebo note `gazebo-spawn-urdf`, MOVEIT-V33):
```bash
# approach & retreat (3.10) and pick & place (4.5): next to the arm
ros2 run ros_gz_sim create -file ~/ros2_ws/src/grasp_box.urdf -name grasp_box -x 0.34 -y 0.13 -z 0.1
# perception (5.3): in front of the arm, under the wrist camera
ros2 run ros_gz_sim create -file ~/ros2_ws/src/grasp_box.urdf -name grasp_box -x 0.5 -y 0.13 -z 0.1
# second object (5.7)
ros2 run ros_gz_sim create -file ~/ros2_ws/src/grasp_box2.urdf -name grasp_box2 -x 0.3 -y 0.13 -z 0.1
```

## Pitfalls
- A second spawn with the same `-name` is refused ("Entity named [grasp_box] already exists and [allow_renaming] is false. Entity not spawned."); use another `-name` or the `-allow_renaming` flag of `create` (gz-sim 8 `UserCommands.cc`).
- The pick poses of the programs (x 0.343, y 0.132) are written for the box at (0.34, 0.13): move the box and they miss it; with perception the pose comes from the camera ([[moveit-cpp-get-object-pose]]).
