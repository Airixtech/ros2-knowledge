---
id: nav2-rviz-displays
type: reference
owner: equipo-ros2
updated: 2026-10-10
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "RViz2 for Nav2: map, scan, particles, pose estimate, path, costmaps"
domain: nav2
area: bringup
distro: humble
tested: false
audience: dev
summary: "RViz2 displays and QoS for Nav2: Map, LaserScan, TF, RobotModel, ParticleCloud, 2D Pose Estimate, Nav2 Goal, Path, costmaps."
tags: [RViz2, Map display, LaserScan, QoS, ParticleCloud, PoseWithCovariance, 2D Pose Estimate, Nav2 Goal, Path, costmap display]
see: ["[[core-qos-usage]]", "[[core-debug-tools]]", "[[nav2-amcl-launch]]", "[[nav2-path-planning-launch]]", "[[nav2-multirobot-rviz]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: the Nav2 RViz config uses relative topics so the RViz namespace applies (Kilted); new Nav2 panel features — https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/migration_guides/jazzy/Jazzy.md (NAV2-V25)"
---
# RViz2 for Nav2: map, scan, particles, pose estimate, path, costmaps

**TL;DR** Start `rviz2`, set Fixed Frame `map`, add displays with **Add** (or the **By topic** tab) and fix their QoS: maps are Transient Local, laser scans are Best Effort. Save each setup with **File → Save Config As**.

## Mapping
| Display | Topic | Settings |
|---|---|---|
| `Map` | `/map` | Durability **Transient Local** (the map is latched); otherwise you see nothing |
| `TF` | | frames of the robot |
| `LaserScan` | `/scan` | Reliability **Best Effort** (instead of Reliable) for the scan to show |
In the map, grey pixels are free space, black pixels occupied space and transparent areas unknown. Save the config as `mapper_rviz_config.rviz` in `ros2_ws/src`. QoS background: [[core-qos-usage]].

## Localization
Add `Map`, `TF`, `RobotModel` (Description Topic `/robot_description`, published by `robot_state_publisher`), `LaserScan` (shows how well the estimate matches the map), `PoseWithCovariance` (`/amcl_pose`, the localization status) and `ParticleCloud` (`/particle_cloud`; this display does not appear under **By topic**, add it by type).
1. Click **2D Pose Estimate**, then click on the map at the robot's real position and drag to its orientation.
2. AMCL starts publishing `map → odom`: the robot and its frames appear. Hide all frames except `map`, `odom` and `base_footprint`: the arrow from the robot to `map` is the transform AMCL publishes.
3. The laser should roughly match the map drawing: the localization is correct.
4. Drive with `ros2 run teleop_twist_keyboard teleop_twist_keyboard`: the particles concentrate on the most likely location.
Save as `localization_rviz_config`.

## Path planning and costmaps
| Display | Topic | Settings |
|---|---|---|
| `Path` | `/plan` | Line Style **Billboards**, Line Width **0.05** |
| `Map` (global costmap) | `/global_costmap/costmap` | Color Scheme `map` |
| `Map` (local costmap) | `/local_costmap/costmap` | Color Scheme `costmap` |
Send a goal with **Nav2 Goal** (Nav2 RViz plugin) or RViz's **2D Goal Pose** (publishes `/goal_pose`): a green line is the planned path. **Publish Point** publishes `/clicked_point` and prints the coordinates in the RViz terminal. Save as `pathplanning_rviz_config`.

## Pitfalls
- Robot model invisible → wrong Description Topic, or no `map → odom` yet (set the initial pose).
- Particles never shown → the ParticleCloud display needs the Nav2 RViz plugins (`nav2_rviz_plugins`).
- Several robots: one display per robot and namespaced tool topics ([[nav2-multirobot-rviz]]).
