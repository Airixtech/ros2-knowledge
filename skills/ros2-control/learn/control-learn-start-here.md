---
id: control-learn-start-here
type: reference
owner: equipo-ros2
updated: 2026-10-24
review_by: 2027-04-22
source: manual
confidentiality: internal
title: "ros2_control course map: eight units (this part: 1–5), requirements, reading order"
domain: control
area: learn
distro: jazzy
tested: false
audience: students
order: 1
summary: "ros2_control course map: units 1–8 (part 1 = units 1–5), packages, prerequisites, course workspace, reading order, running it on Humble."
tags: [course, ros2_control course, units, rrbot, my_robot_bringup, my_robot_hardware_interface, dynamixel_hardware_interface, prerequisites, reading order, humble]
see: ["[[control-learn-unit1-demo]]", "[[control-learn-unit2-setup]]", "[[control-learn-unit2-test]]", "[[control-learn-unit3-manager]]", "[[control-learn-unit4-template]]", "[[control-learn-unit5-dynamixel]]", "[[control-overview]]", "[[control-humble-to-jazzy]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: the course targets Jazzy with Gazebo Sim (Harmonic); its hardware code needs the Jazzy API, see control-humble-to-jazzy for Humble (CONTROL-V18)"
---
# ros2_control course map: eight units (this part: 1–5), requirements, reading order

**TL;DR** The course goes from configuring controllers for a simulated arm (rrbot, two rotary joints) to writing hardware interfaces for a template robot and for Dynamixel servos. Part 1 (these notes) covers units 1–5; units 6–8 are a later part.

## Units
| Unit | Topic | Notes |
|---|---|---|
| 1 | what control means, a demo with ready-made controllers | [[control-learn-unit1-demo]], [[control-overview]] |
| 2 | ros2_control for a simulated robot: bringup package, YAML, URDF tags, launch | [[control-learn-unit2-setup]], [[control-learn-unit2-test]] |
| 3 | the controller manager: states, CLI, services, spawner | [[control-learn-unit3-manager]] |
| 4 | a general method for a custom hardware interface (template) | [[control-learn-unit4-template]] |
| 5 | wrapping an SDK: hardware interface for Dynamixel servos | [[control-learn-unit5-dynamixel]] |
| 6 | the controllers of ros2_controllers, including advanced and task-specific ones | part 2 (not converted yet) |
| 7 | writing a minimal custom controller | part 2 |
| 8 | course project with a quadruped robot | part 2 |

The course text sometimes numbers units 6 and 7 as 5 and 6.

## Packages
- From the course repository (branch `jazzy`, link given in the course) in `~/ros2_ws/src`: the robot packages per unit (`rrbot_unit2`, `rrbot_unit3`, `rrbot_unit4`) and `joint_trajectory_demo`. The simulation (`rrbot_sim`, with its start script) is provided by the course platform.
- Written by you: `my_robot_bringup` (unit 2), `my_robot_hardware_interface` (unit 4), `dynamixel_hardware_interface` (unit 5; a ROBOTIS package has the same name, see [[control-dynamixel-sdk]]).
- After cloning or changing anything: `cd ~/ros2_ws && colcon build && source install/setup.bash`.

## Before starting
Experience with ROS 2, intermediate to advanced C++ and Linux. Recommended: the URDF and Gazebo Sim material of this repository (ros2-urdf and ros2-gazebo skills): this course does not explain how robot descriptions are built.

## On Humble
The course runs on Jazzy with Gazebo Sim. On Humble the YAML, URDF tags, CLI and launch files work with the marks of the notes, but the hardware interface code of units 4–5 must use the Humble API: [[control-humble-to-jazzy]]. Gazebo on Humble (Fortress): ros2-gazebo skill, `gazebo-migration-fortress`.

## Reading order
Units in order; for each, the learn note first, then the technical notes it links. Technical questions go straight to the area notes.
