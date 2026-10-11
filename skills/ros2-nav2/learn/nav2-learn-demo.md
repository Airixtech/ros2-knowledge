---
id: nav2-learn-demo
type: reference
owner: equipo-ros2
updated: 2026-10-10
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "Unit 1 demo: run the Nav2 demo and send goals in RViz"
domain: nav2
area: learn
distro: humble
tested: false
audience: students
summary: "Unit 1: clone the course files, build, launch nav2_demo.launch.py, set the initial pose, send Nav2 goals in RViz."
tags: [course, students, unit 1, demo, nav2_course, nav2_demo.launch.py, 2D Pose Estimate, Nav2 Goal, RViz]
see: ["[[nav2-learn-start-here]]", "[[nav2-architecture]]", "[[nav2-rviz-displays]]"]
requires: [ros2-core]
version_notes: []
---
# Unit 1 demo: run the Nav2 demo and send goals in RViz

**TL;DR** First contact with Nav2: run a ready-made navigation system, localize the robot and send it goals with the mouse. The rest of the course explains each piece so you can apply it to your own robots.

## 1. Get the course files and build
Clone the course repository (link given in the course) into your workspace, then source Humble and build:
```bash
cd ~/ros2_ws/src
git clone <course repository URL>
```
```bash
source /opt/ros/humble/setup.bash
cd ~/ros2_ws
colcon build
source install/setup.bash
```

## 2. Run the demo
```bash
ros2 launch nav2_course nav2_demo.launch.py
```
RViz opens automatically. If it does not appear (or you close it), open the graphical tools window of your environment to see it.

## 3. Localize the robot
1. Click **2D Pose Estimate** in RViz.
2. Click on the map at the robot's position in the simulation and drag in the direction it faces.
3. After a few seconds the map changes: it shows the robot's location and the navigation costmaps (Unit 5 explains them).

## 4. Send goals
1. Click **Nav2 Goal** in the RViz toolbar.
2. Click on the map where the robot's journey should end: the robot starts moving.
Now you can move the robot in the simulation by sending goals through RViz.

## What is behind it
Map server, AMCL, planner, controller, behavior server and bt_navigator, all started by a lifecycle manager ([[nav2-architecture]]). RViz displays and tools: [[nav2-rviz-displays]].

## Tips
- No map or robot in RViz → check the Fixed Frame (`map`) and that the launch finished without errors.
- The robot does not move after a goal → set the initial pose first.
