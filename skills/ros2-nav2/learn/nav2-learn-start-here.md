---
id: nav2-learn-start-here
title: "Course path, requirements and robot (TurtleBot3 Burger)"
domain: nav2
area: learn
distro: humble
tested: false
audience: students
summary: "Start here for the Nav2 course: unit path (demo, mapping, localization, path planning, costmaps, multi-robot), prerequisites, TurtleBot3 Burger, credits."
tags: [course, students, start here, Nav2, TurtleBot3, learning path, requirements]
see: ["[[nav2-learn-demo]]", "[[nav2-architecture]]", "[[core-learn-start-here]]", "[[nav2-learn-course-project]]"]
requires: [ros2-core]
order: 1
version_notes: []
---
# Course path, requirements and robot (TurtleBot3 Burger)

**TL;DR** The course teaches ROS 2 Humble navigation with Nav2 in six units, on a simulated TurtleBot3 Burger, plus a course project on a real robot. Each unit note lists its exercises with the exact names; the technical notes hold the explanations and the code.

## Learning path
| Unit | Topic | Exercises | Main notes |
|---|---|---|---|
| 1 | Hands-on demo of Nav2 | demo | [[nav2-learn-demo]], [[nav2-architecture]] |
| 2 | How to build a map | 2.1–2.3 | [[nav2-learn-unit2-mapping]] |
| 3 | How to localize a robot | 3.1–3.5 | [[nav2-learn-unit3-localization]] |
| 4 | Path planning | 4.1–4.4 | [[nav2-learn-unit4-path-planning]] |
| 5 | Obstacle avoidance (costmaps) | 5.1–5.5 | [[nav2-learn-unit5-costmaps]] |
| 6 | Multi-robot navigation | 6.1–6.2 + planning + single launch | [[nav2-learn-unit6-multirobot]] |
| – | Course project (Sections I–IV) | after Units 2–5 | [[nav2-learn-course-project]] |

## Requirements
- Basic knowledge of **Python**.
- Basic knowledge of **Linux** (shell, files, sourcing).
- Basic knowledge of **ROS 2**: nodes, topics, services, actions, launch files, packages ([[core-learn-start-here]]).

## Robot: TurtleBot3 Burger
TurtleBot3 is a small, affordable, programmable, ROS-based mobile robot used in education, research, hobbies and product prototyping. Its goal is to reduce the size and price of the platform without sacrificing functionality and quality, while offering expandability. The Burger has a 360° LDS laser, odometry and an IMU; its frames are `base_footprint`, `base_link`, `base_scan`, `odom`. Specs: [ROBOTIS e-Manual](https://emanual.robotis.com/docs/en/platform/turtlebot3/overview/).

## Credits
This course builds on the Navigation2 community's work ([navigation2](https://github.com/ros-navigation/navigation2)), on [ROBOTIS](http://en.robotis.com/), the company behind TurtleBot3, and on the whole ROS 2 community.

## How to use these notes
- Read the unit note, try each exercise yourself, then compare with the linked technical note.
- Exercise names (packages, files, nodes) are exact: graders check them.
- Version marks (`[changed in Jazzy: …]`) tell you what differs if your computer runs another ROS 2 distribution.
