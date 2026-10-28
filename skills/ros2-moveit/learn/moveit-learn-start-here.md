---
id: moveit-learn-start-here
type: reference
owner: equipo-ros2
updated: 2026-10-28
review_by: 2027-04-26
source: manual
confidentiality: internal
title: "Manipulation course: start here (outline, prerequisites, robot, first demo)"
domain: moveit
area: learn
distro: humble
tested: false
audience: students
order: 1
summary: "Manipulation course map: UR3e and Robotiq gripper, MoveIt 2 package, C++ planning, Cartesian paths, perception, pick and place, first demo."
tags: [course, manipulation, learning path, UR3e, Robotiq 85, MoveIt 2, test_moveit_config, demo, prerequisites, units]
see: ["[[moveit-learn-unit2-3]]", "[[moveit-learn-unit4]]", "[[moveit-learn-unit5]]", "[[moveit-rviz-motion-planning]]", "[[moveit-architecture]]"]
requires: [ros2-core]
version_notes: []
---
# Manipulation course: start here

**TL;DR** In robotics, manipulation is a robot's ability to interact with objects in its environment: change or move them, e.g. pick an object up and put it somewhere else. This course gives the basic tools to understand and program it in ROS 2 with MoveIt 2 and a manipulator robot, a **UR3e** arm with a **Robotiq 85** gripper and a depth camera on the wrist, in simulation.

## What the course covers
- Set up a MoveIt 2 configuration package for a manipulator robot (unit 2).
- Use MoveIt 2 from C++ programs, with different types of motion planning (units 3 and 4).
- Use perception to find the coordinates of objects (unit 5).
- Build a pick-and-place task in ROS 2 (units 4 and 5).

| Unit | Topic | Notes |
|---|---|---|
| 1 | first demo: move the arm with MoveIt 2 in RViz2 | this note, [[moveit-rviz-motion-planning]] |
| 2 | MoveIt 2 package: Setup Assistant, fixes, RViz2 planning, architecture | [[moveit-learn-unit2-3]] |
| 3 | Move Group C++ interface: joint, pose, gripper, approach & retreat | [[moveit-learn-unit2-3]] |
| 4 | Cartesian paths, kinematics plugins, full pick & place | [[moveit-learn-unit4]] |
| 5 | perception with simple_grasping, object poses, pick & place with perception | [[moveit-learn-unit5]] |

## Prerequisites
ROS 2 basics in C++ (the ros2-cpp skill: nodes, topics, services, actions, ament_cmake; ros2-core), basic Linux, basic C++. The course's own prerequisite courses are linked on the course platform.

## First demo (unit 1)
After sourcing the workspace of the course simulation, start MoveIt 2 with a ready-made package, `test_moveit_config`:
```bash
ros2 launch test_moveit_config move_group.launch.py
```
In a second terminal, RViz2 with a predefined configuration:
```bash
ros2 launch test_moveit_config moveit_rviz.launch.py
```
After some seconds RViz2 shows the robot. Then:
1. Change the **Planning Group** from `gripper` to `ur_manipulator` (to command the arm joints).
2. Change the **Goal State**, e.g. to `home`: the scene shows the robot in that pose.
3. Click **Plan & Execute** in **Commands**: the robot first plans a trajectory to the goal state, then executes it.

Explore the MoveIt 2 RViz2 interface and send other goals. Details: [[moveit-rviz-motion-planning]].
