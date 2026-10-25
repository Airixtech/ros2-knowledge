---
id: control-learn-unit8-project
type: reference
owner: equipo-ros2
updated: 2026-10-24
review_by: 2027-04-22
source: manual
confidentiality: internal
title: "Unit 8 project: Solo 8 quadruped on a stand, starter model files and joint names, tasks, test script"
domain: control
area: learn
distro: jazzy
tested: false
audience: students
summary: "Unit 8 project: Solo 8 quadruped on a stand, starter xacro files, joint names, spawn_solo, six tasks, push-ups test."
tags: [unit 8, course project, Solo 8, quadruped, Open Dynamic Robot Initiative, robot_properties_solo, odri_solo_quadruped.urdf.xacro, solo_quadruped.urdf.xacro, solo_system_quadruped.ros2_control.xacro, spawn_solo.launch.py, joint_trajectory_solo_push-ups.launch.py, HFE, KFE]
see: ["[[control-learn-unit8-solution]]", "[[control-jtc-commands]]", "[[control-builtin-forward]]", "[[control-urdf-tag]]", "[[control-learn-start-here]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: Solo facts (24 cm standing height, just over 2 kg, 3D-printed, Solo 8/12) agree with the 2020 NYU announcement — https://engineering.nyu.edu/news/open-source-low-cost-quadruped-robot-makes-sophisticated-robotics-available-all (CONTROL-V79)"
  - "jazzy: model from robot_properties_solo (BSD-3-Clause); its comment with an internal upstream address is left out — https://github.com/open-dynamic-robot-initiative/robot_properties_solo/blob/master/src/robot_properties_solo/resources/xacro/solo8.urdf.xacro (CONTROL-V80)"
  - "jazzy: the text names the package solo_description, the xacro $(find) odri_solo_quadruped_bringup [verify] (CONTROL-V61); ${prefix}base_link works only with prefix=\"\" (CONTROL-V82)"
---
# Unit 8 project: Solo 8 quadruped on a stand, starter model files and joint names, tasks, test script

**TL;DR** Apply the course to a robot with eight joints: add ros2_control to a quadruped, choose the right controller and start it, so that a test script makes the robot do push-ups. A robot stand holds the robot, so it cannot tip over while you test.

## The robot
Solo is a small open-source quadruped: about 24 cm standing height and just over 2 kg; apart from electronics and actuators all structural parts are 3D printed, which makes it cheap and easy to build for teaching and research. Solo 8 has two actuated joints per leg; Solo 12 has three per leg and can also step sideways. Hardware and software come from the Open Dynamic Robot Initiative (github.com/open-dynamic-robot-initiative).

## Simulation
Source the course's simulation workspace and your workspace, then start the world with the stand (packages provided by the course platform):
```bash
source ~/ros2_ws/install/setup.bash
ros2 launch unit6_simulation simulation_launch.py
```
Place the robot on the stand; the launch file also starts `robot_state_publisher`:
```bash
source ~/ros2_ws/install/setup.bash
ros2 launch spawn_solo spawn_solo.launch.py
```
After every change of the model, delete the robot in Gazebo and spawn it again.

## Starter model (`~/ros2_ws/src/ros2_control_course/unit6`)
The text names the package `solo_description`; the files' `$(find)` use `odri_solo_quadruped_bringup`: the package that `$(find)` names must be installed [verify]. The main file, `description/odri_solo_quadruped.urdf.xacro`:
```xml
<?xml version="1.0"?>
<!-- Quadruped robot  -->
<!--
Copied and modified from https://github.com/open-dynamic-robot-initiative/robot_properties_solo
-->
<robot xmlns:xacro="http://www.ros.org/wiki/xacro" name="quadruped_robot">

  <!-- Import solo macro -->
  <xacro:include filename="$(find odri_solo_quadruped_bringup)/description/solo/solo_quadruped.urdf.xacro" />

  <!-- Import solo ros2_control description -->
  <xacro:include filename="$(find odri_solo_quadruped_bringup)/description/solo/solo_system_quadruped.ros2_control.xacro" />

  <!-- Used for fixing robot -->
  <link name="world"/>
  <!-- or set as parent podest -->

  <xacro:solo_quadruped parent="world" prefix="">
    <origin xyz="0 0 0.35" rpy="0 0 0" />
  </xacro:solo_quadruped>

  <xacro:solo_system_quadruped name="SoloSystemQuadruped" />

</robot>
```
`solo_quadruped.urdf.xacro` defines the macro `solo_quadruped`: a fixed joint to the parent (`world`), the body and four calls of the `leg` macro of `leg.xacro` (not shown in the course):
```xml
<?xml version="1.0" ?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro">
  <xacro:macro name="solo_quadruped" params="parent prefix *origin">
    <xacro:property name="color_name" value="grey" />
    <xacro:property name="color" value="0.8 0.8 0.8" />
    <xacro:property name="opacity" value="1.0" />
    <xacro:property name="mesh_ext" value="stl" />

    <joint name="${prefix}base_joint" type="fixed">
      <xacro:insert_block name="origin" />
      <parent link="${parent}"/>
      <child link="${prefix}base_link" />
    </joint>

    <link name="base_link">
      <!-- BASE LINK INERTIAL -->
      <inertial>
        <origin xyz="0 0 0" rpy="0 0 0" />
        <mass value="1.43315091"/>
        <!-- The base is extremely symmetrical. -->
        <inertia ixx="0.00578574" ixy="0.0" ixz="0.0" iyy="0.01938108" iyz="0.0" izz="0.02476124" />
      </inertial>
      <!-- BASE LINK VISUAL -->
      <visual>
        <origin xyz="0 0 0" rpy="0 0 0" />
        <geometry>
          <mesh filename="package://odri_solo_quadruped_bringup/description/solo/meshes/${mesh_ext}/with_foot/solo_body.${mesh_ext}"/>
        </geometry>
        <material name="${color_name}">
          <color rgba="${color} ${opacity}"/>
        </material>
      </visual>
    </link> <!-- END BASE LINK -->

    <!-- Include the legs -->
    <xacro:include filename="$(find odri_solo_quadruped_bringup)/description/solo/leg.xacro"/>

    <!-- Include the front left leg -->
    <xacro:leg prefix="FL" is_front="true" is_right="false" has_side_motion="false"
               mesh_ext="${mesh_ext}" color_name="${color_name}" color="${color}" opacity="${opacity}"/>
    <!-- Include the front right leg -->
    <xacro:leg prefix="FR" is_front="true" is_right="true" has_side_motion="false"
               mesh_ext="${mesh_ext}" color_name="${color_name}" color="${color}" opacity="${opacity}"/>
    <!-- Include the hind left leg -->
    <xacro:leg prefix="HL" is_front="false" is_right="false" has_side_motion="false"
               mesh_ext="${mesh_ext}" color_name="${color_name}" color="${color}" opacity="${opacity}"/>
    <!-- Include the hind right leg -->
    <xacro:leg prefix="HR" is_front="false" is_right="true" has_side_motion="false"
               mesh_ext="${mesh_ext}" color_name="${color_name}" color="${color}" opacity="${opacity}"/>
  </xacro:macro>
</robot>
```
The joint's child is `${prefix}base_link`, the link is `base_link`: this works only with `prefix=""`, as used. `solo_system_quadruped.ros2_control.xacro` is the file you fill in; it starts empty:
```xml
<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro"></robot>
```

## Joint names
| Leg | Hip (base to upper leg) | Knee (upper to lower leg) |
|---|---|---|
| front left | `FL_HFE` | `FL_KFE` |
| front right | `FR_HFE` | `FR_KFE` |
| hind left | `HL_HFE` | `HL_KFE` |
| hind right | `HR_HFE` | `HR_KFE` |

## Tasks
1. Create a new package for your code.
2. Choose the controller from the included ones (position, effort, velocity, forward command, joint trajectory, diff drive) for the motion the test asks for.
3. Update the robot description in the starter package.
4. Connect the simulated robot with ros2_control (Gazebo integration).
5. Write the controller configuration, with a broadcaster for the joint states.
6. Write a launch file that starts the controllers and makes them active.

## Test
The program must build and run; then:
```bash
ros2 launch joint_trajectory_publisher joint_trajectory_solo_push-ups.launch.py
```
It publishes on `/position_trajectory_controller/joint_trajectory`: your controller must listen on that topic, or the joints do not move. When it works, the legs retract and extend (push-ups). Rebuild and source after every change, also of config files. The solution: [[control-learn-unit8-solution]].
