---
id: nav2-learn-adv-start-here
title: "Advanced Nav2 course: path, simulated warehouse and MP-400 robot"
domain: nav2
area: learn
distro: humble
tested: false
audience: students
summary: "Start here for the advanced Nav2 course: four units, warehouse world, Neobotix MP-400 robot, how to use the notes."
tags: [course, students, advanced course, start here, Nav2, warehouse, MP-400, Simple Commander, behavior trees, plugins, controller server]
see: ["[[nav2-learn-adv-unit1-features]]", "[[nav2-learn-start-here]]", "[[nav2-simple-commander]]", "[[nav2-plugins-overview]]"]
requires: [ros2-core]
order: 2
version_notes: []
---
# Advanced Nav2 course: path, simulated warehouse and MP-400 robot

**TL;DR** The advanced course builds on the introductory one ([[nav2-learn-start-here]]): ROS 2 Humble, Nav2, a simulated warehouse and an industrial mobile robot. Each unit note lists its exercises with the exact names; the technical notes hold the explanations and the code.

## Learning path
| Unit | Topic | Exercises | Main notes |
|---|---|---|---|
| 1 | New Nav2 features: Simple Commander API, waypoint following, keepout zones and speed-restricted zones | demos | [[nav2-learn-adv-unit1-features]] |
| 2 | Nav2 behaviors: behavior trees in `bt_navigator`, recoveries | E2.1 | [[nav2-learn-adv-unit2-behaviors]] |
| 3 | Plugins: default plugins, custom costmap, planner and controller plugins | Examples 3.1–3.3, EX.1, EX.2 | [[nav2-learn-adv-unit3-plugins]] |
| 4 | Controller server in depth: checkers, controllers, critics | E1.1 | [[nav2-learn-adv-unit4-controller]] |

## Unit 1 at a glance
Nav2 provides new features and tools that make creating robot applications easier. In Unit 1 you review the essential ones: basic Nav2 operations through the **Simple Commander API**, the Waypoint Follower and Task Executor plugins via **FollowWaypoints**, and Keepout Zones and speed-restricted zones. You then create a basic autonomous robotics demo in a simulated warehouse, where robots are often deployed.

## World and robot
- World: the AWS [Small Warehouse World](https://github.com/aws-robotics/aws-robomaker-small-warehouse-world).
- Robot: Neobotix's [MP-400](https://www.neobotix-robots.com/products/mobile-robots/mobile-robot-mp-400) mobile industrial robot.

## How to use these notes
- Read the unit note, try each exercise yourself, then compare with the linked technical note.
- Exercise names (packages, files, classes, plugin names) are exact.
- The course was written for Humble but copies some older (Foxy/Galactic) names; the technical notes use the Humble-correct form and cite the audit row (`NAV2-Vnn`).
