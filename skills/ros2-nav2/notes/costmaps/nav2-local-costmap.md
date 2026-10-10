---
id: nav2-local-costmap
title: "Local costmap: rolling window in controller.yaml"
domain: nav2
area: costmaps
distro: humble
tested: false
audience: dev
summary: "local_costmap YAML block appended to controller.yaml: rolling_window in odom, width/height, voxel layer from /scan, inflation; how the controller uses it."
tags: [local_costmap, controller.yaml, rolling_window, width, height, odom, VoxelLayer, dynamic obstacles]
see: ["[[nav2-costmap-concepts]]", "[[nav2-costmap-obstacle-voxel]]", "[[nav2-controller-server]]", "[[nav2-global-costmap]]"]
requires: [ros2-core]
version_notes:
  - "humble: same structure as the global costmap; defaults in costmap_2d_ros.cpp — https://github.com/ros-navigation/navigation2/blob/humble/nav2_costmap_2d/src/costmap_2d_ros.cpp (NAV2-V09)"
---
# Local costmap: rolling window in controller.yaml

**TL;DR** The local costmap is configured at the bottom of the controller's file, at the **first column**. It is a small window (`width` × `height` meters) that rolls with the robot in the `odom` frame and reacts fast to close obstacles.

## Block for controller.yaml
```yaml
local_costmap:
  local_costmap:
    ros__parameters:
      update_frequency: 5.0
      publish_frequency: 2.0
      global_frame: odom
      robot_base_frame: base_link
      use_sim_time: True
      rolling_window: true
      width: 1
      height: 1
      resolution: 0.05
      robot_radius: 0.15
      plugins: ["voxel_layer", "inflation_layer"]
      inflation_layer:
        plugin: "nav2_costmap_2d::InflationLayer"
        cost_scaling_factor: 3.0
        inflation_radius: 0.35
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
The local costmap has the same structure and parameters as the global one ([[nav2-global-costmap]]): it is a reduced, more dynamic version of it. The `static_layer` block is unused here because `static_layer` is not in `plugins`. The voxel layer with a 2D laser works like an obstacle layer ([[nav2-costmap-obstacle-voxel]]).

## Size and behavior
- `width` and `height` (meters) set the area around the robot that the sensors update. Here 1 × 1 m; Nav2's default config uses 3 × 3 m.
- `global_frame: odom` + `rolling_window: true`: the window follows the robot, so the controller avoids obstacles that are not on the map (e.g. a spawned gas bottle) while following the global plan ([[nav2-controller-server]]).
- In RViz, show `/local_costmap/costmap` with color scheme `costmap` ([[nav2-rviz-displays]]).

## Pitfalls
- A window smaller than the stopping distance at full speed → the robot sees obstacles too late.
- `global_frame: map` for the local costmap → it jumps every time AMCL corrects the pose.
- Block indented under `controller_server` → it is ignored and defaults are used.
