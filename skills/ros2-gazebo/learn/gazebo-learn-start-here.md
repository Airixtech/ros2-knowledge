---
id: gazebo-learn-start-here
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "Course map: all units, packages, reading order (units 2, 3, 8 in ros2-urdf)"
domain: gazebo
area: learn
distro: jazzy
tested: false
audience: students
order: 1
summary: "URDF course map: units 1–8, box_bot packages and files per unit, prerequisites, reading order, running it on Humble with Fortress."
tags: [course, urdf course, box_bot, my_box_bot_description, my_box_bot_gazebo, units, prerequisites, reading order, humble, fortress]
see: ["[[urdf-learn-start-here]]", "[[gazebo-learn-unit4-sim]]", "[[gazebo-learn-unit5-moving]]", "[[gazebo-learn-unit6-sensors]]", "[[gazebo-learn-unit7-xacro]]", "[[gazebo-migration-fortress]]"]
requires: [ros2-core, ros2-urdf]
version_notes:
  - "jazzy: the course targets Jazzy + Gazebo Harmonic; on Humble use Fortress and the table of gazebo-migration-fortress (GZ-V45)"
---
# Course map: all units, packages, reading order (units 2, 3, 8 in ros2-urdf)

**TL;DR** The course takes a robot from a drawing to a simulation with physics, actuators and sensors, then cleans the model up with xacro and shows a CAD export. It practises on three robots: urdfbot (unit 2), box_bot (units 3–7) and a quadruped (unit 8).

## Units
| Unit | Topic | Note |
|---|---|---|
| 1 | why a robot model, outline | [[urdf-overview]] |
| 2 | URDF basics on urdfbot, RViz2 | [[urdf-learn-unit2-urdfbot]] |
| 3 | micro-project: box_bot | [[urdf-learn-unit3-box-bot]] |
| 4 | Gazebo Sim: world, collisions, inertia, spawn, friction | [[gazebo-learn-unit4-sim]] |
| 5 | moving: DiffDrive, bridge, ros2_control for a laser mount | [[gazebo-learn-unit5-moving]] |
| 6 | sensors: lidar, point cloud, cameras, IMU | [[gazebo-learn-unit6-sensors]] |
| 7 | xacro version of box_bot, two robots | [[gazebo-learn-unit7-xacro]] |
| 8 | CAD export with onshape-to-robot | [[urdf-learn-unit8-quadruped]] |

## Packages of box_bot
- `my_box_bot_description`: `urdf/` (one file per step: `box_bot_geometric.urdf` … `box_bot_final.urdf`, `box_bot.xacro`, `box_bot.gazebo.xacro`), `meshes/` (`cute_cube.dae`, `sensors/rplidar.dae`), `rviz/urdf_vis.rviz`, `launch/urdf_visualize_*.launch.py`, `config/controller_*.yaml`.
- `my_box_bot_gazebo`: `launch/start_world.launch.py`, `spawn_robot_description.launch.py`, `spawn_robot_ros2_*.launch.xml`, `control*.launch.py`; `worlds/box_bot_empty.world`; `models/`; `scripts/move_laser.py`.
- The course copies meshes and a `box_room` model from its own repositories, and has a separate final project: use your own meshes and models; the notes do not depend on them.

## Before starting
ROS 2 basics, Python, XML, a basic idea of forces and torques. Gazebo and the ROS packages of [[gazebo-sim-overview]]. Each terminal: `source ~/ros2_ws/install/setup.bash`; build after every change.

## On Humble
The course runs on Jazzy with Gazebo Harmonic. On Humble with Fortress almost everything works unchanged; read [[gazebo-migration-fortress]] first (the `<robot_param_node>` line for gz_ros2_control matters in unit 5).

## Reading order
Units in order; for each, the learn note first, then the technical notes it links. Course questions only: technical questions go straight to the area notes.
