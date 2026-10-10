---
id: nav2-mp400-costmaps
title: "Costmap configuration of the advanced course robot (Neobotix MP-400)"
domain: nav2
area: costmaps
distro: humble
tested: false
audience: dev
summary: "MP-400 warehouse robot costmaps: global costmap in planner_server.yaml (robot_radius 0.3), local costmap in controller.yaml (3x3 rolling, voxel layer, radius 0.4)."
tags: [MP-400, Neobotix, global_costmap, local_costmap, planner_server.yaml, controller.yaml, robot_radius, base_footprint, voxel_layer, obstacle_layer, inflation_layer, warehouse]
see: ["[[nav2-global-costmap]]", "[[nav2-local-costmap]]", "[[nav2-costmap-layers]]", "[[nav2-robot-footprint]]", "[[nav2-learn-adv-start-here]]"]
requires: [ros2-core]
version_notes:
  - "humble: same parameters as the TurtleBot3 configs of the intro course, with the MP-400's size and frames; code defaults in nav2-global-costmap — https://github.com/ros-navigation/navigation2/blob/humble/nav2_costmap_2d/src/costmap_2d_ros.cpp (NAV2-V09)"
---
# Costmap configuration of the advanced course robot (Neobotix MP-400)

**TL;DR** The advanced course runs Nav2 on the Neobotix MP-400 in a warehouse. Its costmaps follow the same structure as the TurtleBot3 ones ([[nav2-global-costmap]], [[nav2-local-costmap]]), with a bigger robot and other frames. These are the course files; the plugin examples copy and modify them.

## Global costmap (bottom of planner_server.yaml)
```yaml
global_costmap:
  global_costmap:
    ros__parameters:
      update_frequency: 1.0
      publish_frequency: 1.0
      global_frame: map
      robot_base_frame: base_footprint
      use_sim_time: True
      robot_radius: 0.3
      resolution: 0.05
      track_unknown_space: true
      plugins: ["static_layer", "obstacle_layer", "inflation_layer"]
      static_layer:
        plugin: "nav2_costmap_2d::StaticLayer"
        map_subscribe_transient_local: True
      inflation_layer:
        plugin: "nav2_costmap_2d::InflationLayer"
        cost_scaling_factor: 3.0
        inflation_radius: 0.55
      always_send_full_costmap: True
      obstacle_layer:
        plugin: "nav2_costmap_2d::ObstacleLayer"
        enabled: True
        observation_sources: scan
        scan:
          topic: /scan
          max_obstacle_height: 2.0
          clearing: True
          marking: True
          data_type: "LaserScan"
          raytrace_max_range: 3.0
          raytrace_min_range: 0.0
          obstacle_max_range: 2.5
          obstacle_min_range: 0.0
```

## Local costmap (bottom of controller.yaml)
```yaml
local_costmap:
  local_costmap:
    ros__parameters:
      update_frequency: 5.0
      publish_frequency: 2.0
      global_frame: odom
      robot_base_frame: base_footprint
      use_sim_time: True
      rolling_window: true
      width: 3
      height: 3
      resolution: 0.05
      robot_radius: 0.4
      plugins: ["voxel_layer", "inflation_layer"]
      inflation_layer:
        plugin: "nav2_costmap_2d::InflationLayer"
        cost_scaling_factor: 3.0
        inflation_radius: 0.55
      voxel_layer:
        plugin: "nav2_costmap_2d::VoxelLayer"
        enabled: True
        publish_voxel_map: True
        origin_z: 0.0
        z_resolution: 0.05
        z_voxels: 16
        max_obstacle_height: 2.0
        mark_threshold: 0
        observation_sources: scan
        scan:
          topic: /scan
          max_obstacle_height: 2.0
          clearing: True
          marking: True
          data_type: "LaserScan"
          raytrace_max_range: 3.0
          raytrace_min_range: 0.0
          obstacle_max_range: 2.5
          obstacle_min_range: 0.0
      static_layer:
        map_subscribe_transient_local: True
      always_send_full_costmap: True
```

## Variants in the course files
| File | Differences |
|---|---|
| `config/custom_costmap/planner_server.yaml`, `config/straightline_planner/planner_server.yaml` | `robot_base_frame: base_link`, `inflation_radius: 0.4` |
| `config/custom_costmap/controller.yaml` | local: `robot_base_frame: base_link`, `inflation_radius: 0.4`, a commented `footprint: '[ [0.65, 0.65], [0.65, -0.65], [-0.65, -0.65], [-0.65, 0.65] ]'` |
| `config/my_custom_crazy_costmap/` | global: `my_crazy_layer` instead of the inflation layer; local: only `voxel_layer` |

## Pitfalls
- The course mixes `base_link` and `base_footprint` between files: use the same `robot_base_frame` in both costmaps.
- `static_layer` in the local costmap is not in its `plugins` list, so those parameters are ignored.
