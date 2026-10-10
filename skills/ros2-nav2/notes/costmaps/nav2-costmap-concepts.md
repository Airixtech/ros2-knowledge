---
id: nav2-costmap-concepts
title: "Costmap 2D: global vs local costmaps"
domain: nav2
area: costmaps
distro: humble
tested: false
audience: dev
summary: "nav2_costmap_2d cell costs (free, inflated, lethal, unknown); global costmap for the planner, rolling local costmap for the controller."
tags: [costmap, nav2_costmap_2d, global_costmap, local_costmap, LETHAL_OBSTACLE, inflation, rolling_window]
see: ["[[nav2-global-costmap]]", "[[nav2-local-costmap]]", "[[nav2-costmap-layers]]", "[[core-nav2-tuning]]"]
requires: [ros2-core]
version_notes:
  - "humble: cost values FREE_SPACE 0, INSCRIBED_INFLATED_OBSTACLE 253, LETHAL_OBSTACLE 254, NO_INFORMATION 255; same in Jazzy and Lyrical — https://github.com/ros-navigation/navigation2/blob/humble/nav2_costmap_2d/include/nav2_costmap_2d/cost_values.hpp"
---
# Costmap 2D: global vs local costmaps

**TL;DR** A costmap is a 2D grid where each cell holds the cost of the robot being there. Nav2 keeps two: the **global costmap** (whole map, for the planner) and the **local costmap** (small rolling window around the robot, for the controller).

## What a costmap is
A Costmap is a 2D representation of robot-sensed obstacles on a grid map:
- Each grid cell contains information about the obstacles detected by the sensors (and those in the static map).
- The cost of a cell can be unknown, free, occupied or inflated.
- Different colors in RViz show how likely the robot is to collide with an obstacle there.
- Controllers, planners and recovery behaviors use this information to compute their tasks safely and efficiently.

| Cost | Value | Meaning |
|---|---|---|
| `FREE_SPACE` | 0 | free |
| 1–252 | | inflated: closer to an obstacle = higher cost |
| `INSCRIBED_INFLATED_OBSTACLE` | 253 | the robot center here means a collision |
| `LETHAL_OBSTACLE` | 254 | obstacle |
| `NO_INFORMATION` | 255 | unknown |

## Global vs local
1. **Global costmap**: generated from the obstacles in the static map. The `planner` uses it to generate the long-term path ([[nav2-global-costmap]]).
2. **Local costmap**: created from new obstacles detected by the robot in a small area around it. The `controller` uses it to generate the short-term path and avoid dynamic obstacles ([[nav2-local-costmap]]).

| | Global costmap | Local costmap |
|---|---|---|
| Avoids | known obstacles on the map | dynamic obstacles that are not on the map |
| Covers | the entire map | a small area around the robot |
| Moves | static over the map (`global_frame: map`) | rolls over the global costmap as the robot moves (`rolling_window: true`, `global_frame: odom`) |
| Lives in | `planner_server` (`/global_costmap/costmap`) | `controller_server` (`/local_costmap/costmap`) |

Both are built from layers (static, obstacle, voxel, inflation): [[nav2-costmap-layers]]. Visualize them with an RViz Map display, color scheme `costmap` ([[nav2-rviz-displays]]). Choosing values (update rates, inflation): [[core-nav2-tuning]].

## Pitfalls
- A path through an object you can see in the laser → that costmap has no obstacle (or voxel) layer for the sensor.
- An obstacle that is gone but still blocks paths → it is in the static map: edit the map ([[nav2-map-saver]]).
