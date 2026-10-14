---
id: nav2-map-concepts
type: reference
owner: equipo-ros2
updated: 2026-10-10
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "Occupancy grid maps and SLAM (Cartographer, SLAM Toolbox)"
domain: nav2
area: mapping
distro: humble
tested: false
audience: dev
summary: "What a ROS occupancy grid map is, what you need to build one (LIDAR, odometry), SLAM, Cartographer vs SLAM Toolbox."
tags: [map, occupancy grid, SLAM, cartographer_ros, slam_toolbox, LIDAR, odometry]
see: ["[[nav2-cartographer-launch]]", "[[nav2-map-saver]]", "[[core-tf-basics]]"]
requires: [ros2-core]
version_notes:
  - "humble/jazzy/lyrical: cartographer_ros (ros2 fork) and slam_toolbox are released for all three; Nav2 bringup's slam_launch.py uses SLAM Toolbox — https://github.com/ros/rosdistro/blob/master/humble/distribution.yaml (NAV2-V29)"
---
# Occupancy grid maps and SLAM (Cartographer, SLAM Toolbox)

**TL;DR** A Nav2 map is an occupancy grid: each cell is free, occupied or unknown. You build it once with SLAM (robot with LIDAR + odometry driving around), save it, and then serve it for localization and planning.

## What a map is used for
A map is a representation of the environment in which the robot operates. The robot relies on a map to:
- **Localize itself** within the environment ([[nav2-map-server]] feeds AMCL).
- **Plan trajectories** to navigate safely from one point to another.

In ROS, a map is typically an **occupancy grid map** (`nav_msgs/OccupancyGrid` on `/map`), where each cell contains values that indicate whether an area is free, occupied by an obstacle, or unknown.

## What is required to build a map
- **A robot equipped with:**
  - **LIDAR** for detecting obstacles and measuring distances (`/scan`).
  - **Odometry** to track the robot's movement (`/odom` and the `odom → base_footprint` transform).
- **An environment** for the robot to explore and map (drive it around with teleop).

## SLAM
SLAM (Simultaneous Localization and Mapping) builds a map of an unknown environment **while simultaneously determining the robot's own location** within it, so the robot can explore without prior knowledge of its surroundings. Widely used SLAM solutions in ROS 2:
- **Cartographer** (`cartographer_ros`): used in this course for its simplicity and reliability. Real-time 2D and 3D SLAM for various platforms and sensor setups, developed by Google (also used for Google Street View building interiors). `cartographer_ros` is the ROS-compatible wrapper: use the pre-built packages and only configure them for your robot ([[nav2-cartographer-launch]], [[nav2-cartographer-lua]]).
- **SLAM Toolbox** (SLAM-Toolbox, `slam_toolbox`): the SLAM used by Nav2's own `slam_launch.py`; also has a localization mode.

| Package | Humble | Jazzy | Lyrical |
|---|---|---|---|
| `ros-<distro>-cartographer-ros` | ✓ | ✓ | ✓ |
| `ros-<distro>-slam-toolbox` | ✓ | ✓ | ✓ |

Docs: [Cartographer](https://opensource.google/projects/cartographer), [cartographer_ros](https://google-cartographer-ros.readthedocs.io/en/latest/).

## Pitfalls
- No odometry TF (`odom → base_footprint`) → SLAM cannot place scans; check the TF tree first ([[core-tf-basics]]).
- Mapping with `use_sim_time` mismatched between the simulator and the SLAM nodes → TF extrapolation errors ([[core-time-timers]]).
- Moving or temporary objects (people, other robots) end up in the map as obstacles; clean the map image afterwards ([[nav2-map-saver]]).
