---
id: urdf-learn-start-here
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "Course map for units 2, 3 and 8 (units 4-7 live in ros2-gazebo)"
domain: urdf
area: learn
distro: humble
tested: false
audience: students
order: 1
summary: "URDF course map: three robots (urdfbot, box_bot, quadruped), packages, prerequisites, reading order; units 4–7 (Gazebo, xacro) in the ros2-gazebo skill."
tags: [course, urdf, urdfbot, box_bot, quadruped, prerequisites, reading order]
see: ["[[urdf-learn-unit2-urdfbot]]", "[[urdf-learn-unit3-box-bot]]", "[[urdf-learn-unit8-quadruped]]", "[[urdf-overview]]"]
requires: [ros2-core]
version_notes: []
---
# Course map for units 2, 3 and 8 (units 4-7 live in ros2-gazebo)

**TL;DR** The course goes from a robot drawing to a simulated robot with physics, actuators and sensors, practising on three robots. This skill holds the description units (2, 3, 8); the simulation and xacro units (4–7) and the full course map are in the ros2-gazebo skill.

## Units
| Unit | Topic | Robot / package | Notes |
|---|---|---|---|
| 1 | why URDF, outline | — | [[urdf-overview]] |
| 2 | links, joints, TF, materials, meshes, special joint elements, launch with RViz2 | `urdfbot_description` | [[urdf-learn-unit2-urdfbot]] |
| 3 | micro-project: a two-wheeled robot with caster wheels, then a mesh body | `my_box_bot_description` | [[urdf-learn-unit3-box-bot]] |
| 4–7 | Gazebo Sim, moving joints, sensors, xacro, two robots | `my_box_bot_gazebo` | ros2-gazebo skill (course map there) |
| 8 | export a CAD assembly with onshape-to-robot | `quadruped_description` | [[urdf-learn-unit8-quadruped]] |

## Before starting
- ROS 2 basics (packages, launch files, topics), Python, how XML files work, a basic idea of forces and torques.
- A workspace `~/ros2_ws` with `src/`; build with colcon and source `install/setup.bash` in every terminal.
- Meshes: the course ships its own DAE files (body, head, limbs, claws, a cube with a face, a lidar). Use any DAE/STL meshes of your own with the same file names, or keep the primitive shapes.

## Reading order
1. Concepts: [[urdf-overview]] → [[urdf-links]] → [[urdf-joints]] → [[urdf-frames-rviz]].
2. Tools: [[urdf-description-package]] → [[urdf-joint-state-publisher]] → [[urdf-joint-extras]].
3. Exercises: unit 2, then unit 3. Unit 8 needs only units 2–3.
