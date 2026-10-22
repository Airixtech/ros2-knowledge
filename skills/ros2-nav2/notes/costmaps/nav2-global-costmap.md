---
id: nav2-global-costmap
type: reference
owner: equipo-ros2
updated: 2026-10-21
review_by: 2027-04-19
source: manual
confidentiality: internal
title: "Global costmap: config in planner_server.yaml and general parameters"
domain: nav2
area: costmaps
distro: humble
tested: false
audience: dev
summary: "global_costmap YAML block (static + inflation layers) appended to planner_server.yaml, general costmap parameters with Humble defaults, the static-only experiment."
tags: [global_costmap, planner_server.yaml, update_frequency, publish_frequency, robot_radius, resolution, track_unknown_space, always_send_full_costmap]
see: ["[[nav2-costmap-layers]]", "[[nav2-costmap-concepts]]", "[[nav2-planner-server]]", "[[nav2-robot-footprint]]"]
requires: [ros2-core]
version_notes:
  - "humble: code defaults always_send_full_costmap false, resolution 0.1, robot_radius 0.1, update_frequency 5.0, width/height 5 — https://github.com/ros-navigation/navigation2/blob/humble/nav2_costmap_2d/src/costmap_2d_ros.cpp (NAV2-V09)"
  - "jazzy: gazebo_ros (Gazebo Classic) is not released; spawn with ros_gz_sim create — https://github.com/ros/rosdistro/blob/master/jazzy/distribution.yaml (NAV2-V28)"
  - "humble: modern Gazebo spawns with ros_gz_sim create -name -file <file or Fuel URL> -x -y (same flags in jazzy and lyrical) — https://github.com/gazebosim/ros_gz/blob/humble/ros_gz_sim/src/create.cpp (NAV2-V69)"
---
# Global costmap: config in planner_server.yaml and general parameters

**TL;DR** The global costmap is configured in the same file as the planner. Append this block at the **first column** of `planner_server.yaml`: two nested `global_costmap:` keys (namespace and node name).

## Block for planner_server.yaml
```yaml
global_costmap:
  global_costmap:
    ros__parameters:
      update_frequency: 1.0
      publish_frequency: 1.0
      global_frame: map
      robot_base_frame: base_link
      use_sim_time: True
      robot_radius: 0.15
      resolution: 0.05
      track_unknown_space: true
      plugins: ["static_layer", "inflation_layer"]
      static_layer:
        plugin: "nav2_costmap_2d::StaticLayer"
        map_subscribe_transient_local: True
      inflation_layer:
        plugin: "nav2_costmap_2d::InflationLayer"
        cost_scaling_factor: 3.0
        inflation_radius: 0.35
      always_send_full_costmap: True
```
Rebuild, launch the planning stack (it also needs `map_server` and AMCL), and add an RViz Map display for `/global_costmap/costmap` ([[nav2-rviz-displays]]). Map obstacles appear expanded in shades of grey: the robot cannot move that close; light-grey areas are what the planner uses.

## General parameters (Humble code defaults)
| Parameter | Default | Meaning |
|---|---|---|
| `global_frame` | `map` | reference frame |
| `robot_base_frame` | `base_link` | robot base frame |
| `update_frequency` | 5.0 Hz | costmap update frequency |
| `publish_frequency` | 1.0 Hz | frequency to publish the costmap to its topic |
| `resolution` | 0.1 | meters per costmap cell |
| `width`, `height` | 5 (int, m) | costmap size (used by rolling costmaps) |
| `robot_radius` | 0.1 m | robot radius, used if no `footprint` is given ([[nav2-robot-footprint]]) |
| `plugins` | `["static_layer", "obstacle_layer", "inflation_layer"]` | mapped layer names; each needs a `plugin` type ([[nav2-costmap-layers]]) |
| `track_unknown_space` | false | keep unknown cells as unknown instead of free |
| `always_send_full_costmap` | false | send the full costmap every update instead of partial updates |
| `transform_tolerance` | 0.3 s | TF tolerance |

## Static-only experiment (why you need an obstacle layer)
Spawn an object that is not on the map (Gazebo Classic, Humble):
```bash
ros2 run gazebo_ros spawn_entity.py -entity gas_bottle3 -database gas_bottle -x -0.6 -y -0.3
```
[changed in Jazzy: `ros2 run ros_gz_sim create` (no Gazebo Classic)]. Modern Gazebo (Humble + Fortress or Jazzy + Harmonic, only in a world started with `ros_gz_sim`): `ros2 run ros_gz_sim create -name gas_bottle3 -file <model_folder>/model.sdf -x -0.6 -y -0.3`; Gazebo Fuel has no model of that name, so use your own model or any Fuel model URL (NAV2-V69; spawning and resource paths: ros2-gazebo skill, `gazebo-spawn-urdf`). The laser sees the gas bottle, but this costmap does not include it, so the path crosses it and the robot crashes: **the object is not taken into account**. Fix: add the `obstacle_layer` ([[nav2-costmap-layers]]). Conversely, anything in the map is an obstacle for the planner **even if it is no longer there**.

## Pitfalls
- Wrong indentation (the block not at column 0, or inside `planner_server`) → the costmap silently uses defaults.
