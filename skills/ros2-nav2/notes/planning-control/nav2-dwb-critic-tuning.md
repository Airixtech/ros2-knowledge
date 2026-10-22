---
id: nav2-dwb-critic-tuning
type: reference
owner: equipo-ros2
updated: 2026-10-21
review_by: 2027-04-19
source: manual
confidentiality: internal
title: "DWB critic tuning: PathAlign keeps the robot stuck behind an unmapped obstacle"
domain: nav2
area: planning-control
distro: humble
tested: false
audience: dev
summary: "Experiment: obstacle only in the local costmap; PathAlign holds DWB behind it, BaseObstacle stops it; without PathAlign it goes around."
tags: [DWB, critics, PathAlign, BaseObstacle, obstacle_layer, global costmap, local costmap, spawn_entity.py, construction_cone, critic tuning]
see: ["[[nav2-dwb-generators-critics]]", "[[nav2-dwb-controller]]", "[[nav2-mp400-costmaps]]", "[[nav2-global-costmap]]", "[[nav2-learn-adv-unit4-controller]]"]
requires: [ros2-core]
version_notes:
  - "humble: ros2 run gazebo_ros spawn_entity.py (Gazebo Classic); jazzy: gazebo_ros is not released, use ros2 run ros_gz_sim create — https://github.com/ros/rosdistro/blob/master/humble/distribution.yaml (NAV2-V28)"
  - "humble: modern Gazebo spawns with ros_gz_sim create -file <file or Fuel URL>; OpenRobotics/Construction Cone is on Gazebo Fuel (CC0) — https://github.com/gazebosim/ros_gz/blob/humble/ros_gz_sim/README.md (NAV2-V69)"
  - "humble: the outcome below is the course's observation in its simulation [verify] — https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/configuration_guide/controller_plugins/dwb_controller/trajectory_critics/path_align.md (NAV2-V66)"
---
# DWB critic tuning: PathAlign keeps the robot stuck behind an unmapped obstacle

**TL;DR** Critics decide what DWB prefers. With an obstacle that is only in the **local** costmap, a strong `PathAlign` keeps the robot on the global path, `BaseObstacle` prevents it from crashing, and the robot stops in front of the obstacle without avoiding it. Removing `PathAlign` lets it drive around [verify].

## The experiment
1. Configure the `global_costmap` **without** the `obstacle_layer` plugin (remove it from the configuration file): the global planner no longer considers newly detected obstacles.
2. Recompile, source and relaunch the navigation system. Provide an initial localization using RViz.
3. Spawn a cone in the simulation (Humble, Gazebo Classic):
   ```bash
   ros2 run gazebo_ros spawn_entity.py -entity construction_cone -database construction_cone -x -1
   ```
   Modern Gazebo (Humble + Fortress or Jazzy + Harmonic, only in a world started with `ros_gz_sim`): the cone is a Gazebo Fuel model (NAV2-V69; more: ros2-gazebo skill, `gazebo-spawn-urdf`):
   ```bash
   ros2 run ros_gz_sim create -name construction_cone -file 'https://fuel.gazebosim.org/1.0/OpenRobotics/models/Construction Cone' -x -1
   ```
4. Put the robot in front of the cone at approximately 1 meter and give a goal on the other side of the cone with RViz. The planned path goes over the cone: the planner does not consider the new obstacle.

The controller should take the cone into account and move around it, because the obstacle **is** in the local costmap. Instead, the robot stops in front of the obstacle without avoiding it.

## Why
The critic `PathAlign` forces the robot too much to follow the computed trajectory (whatever it is), so it goes straight. The critic `BaseObstacle` prevents the robot from crashing against the obstacle, but that does not solve the situation, and the robot cannot reach the goal. Critics of the course config: `["RotateToGoal", "Oscillation", "BaseObstacle", "GoalAlign", "PathAlign", "PathDist", "GoalDist"]` ([[nav2-dwb-controller]]).

## The change
1. Remove the `PathAlign` critic from the controller configuration:
   ```yaml
   critics: ["RotateToGoal", "Oscillation", "BaseObstacle", "GoalAlign", "PathDist", "GoalDist"]
   ```
2. Recompile, source and relaunch the navigation system.
3. Repeat the same situation: robot in front of the cone, goal on the other side. The robot now goes around the cone.

## Pitfalls
- Never remove `BaseObstacle` (or `ObstacleFootprint`) in this kind of tuning: they are the only collision checks of DWB ([[nav2-dwb-generators-critics]]).
- Restore the `obstacle_layer` in the global costmap after the experiment: without it, planned paths ignore new obstacles.
