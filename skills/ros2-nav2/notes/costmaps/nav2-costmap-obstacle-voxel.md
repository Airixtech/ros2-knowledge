---
id: nav2-costmap-obstacle-voxel
title: "Obstacle and voxel layer parameters"
domain: nav2
area: costmaps
distro: humble
tested: false
audience: dev
summary: "ObstacleLayer (2D laser) and VoxelLayer (3D point cloud) YAML, observation sources, marking/clearing, obstacle_max_range/raytrace_max_range with Humble defaults."
tags: [ObstacleLayer, VoxelLayer, observation_sources, marking, clearing, obstacle_max_range, raytrace_max_range, PointCloud2, LaserScan, z_voxels]
see: ["[[nav2-costmap-layers]]", "[[nav2-local-costmap]]", "[[nav2-global-costmap]]", "[[core-recipe-laserscan]]"]
requires: [ros2-core]
version_notes:
  - "humble: range params are obstacle_max_range/obstacle_min_range and raytrace_max_range/raytrace_min_range (obstacle_range/raytrace_range are ROS 1 names); source clearing default false — https://github.com/ros-navigation/navigation2/blob/humble/nav2_costmap_2d/plugins/obstacle_layer.cpp (NAV2-V09)"
  - "lyrical: relative source topics resolve in the robot namespace (Kilted) — https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/migration_guides/jazzy/Jazzy.md (NAV2-V25)"
---
# Obstacle and voxel layer parameters

**TL;DR** The obstacle layer marks and raytraces (clears) obstacles in 2D from laser scans; the voxel layer does it in 3D from point clouds and projects the result to the 2D costmap. Each sensor is an "observation source" with its own block.

## Obstacle layer (laser)
```yaml
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
Layer parameters (Humble defaults): `enabled` true · `observation_sources` "" (space-separated source names) · `footprint_clearing_enabled` true (clear cells under the footprint) · `max_obstacle_height` 2.0 / `min_obstacle_height` 0.0 (heights added to the grid) · `combination_method` 1 (how data enters the master costmap: 1 = maximum, 0 = overwrite).

Per observation source:
| Parameter | Default | Meaning |
|---|---|---|
| `topic` | `""` | topic of the data |
| `data_type` | `"LaserScan"` | `LaserScan` or `PointCloud2` |
| `marking` | true | the source marks obstacles |
| `clearing` | **false** | the source raytraces free space (clears) |
| `obstacle_max_range` / `obstacle_min_range` | 2.5 / 0.0 m | range to mark obstacles |
| `raytrace_max_range` / `raytrace_min_range` | 3.0 / 0.0 m | range to raytrace-clear obstacles |
| `max_obstacle_height` / `min_obstacle_height` | 2.0 / 0.0 m | height limits of returns |
| `inf_is_valid` | false | treat infinite laser returns as valid measurements to raycast |

## Voxel layer (3D point cloud)
```yaml
      voxel_layer:
        plugin: "nav2_costmap_2d::VoxelLayer"
        enabled: True
        footprint_clearing_enabled: true
        max_obstacle_height: 2.0
        publish_voxel_map: True
        origin_z: 0.0
        z_resolution: 0.05
        z_voxels: 16
        unknown_threshold: 15
        mark_threshold: 0
        observation_sources: pointcloud
        combination_method: 1
        pointcloud:  # no frame set, uses frame from message
          topic: /intel_realsense_r200_depth/points
          max_obstacle_height: 2.0
          min_obstacle_height: 0.0
          obstacle_max_range: 2.5
          obstacle_min_range: 0.0
          raytrace_max_range: 3.0
          raytrace_min_range: 0.0
          clearing: True
          marking: True
          data_type: "PointCloud2"
```
Voxel-specific (Humble defaults): `z_voxels` 10, `z_resolution` 0.2 m (height covered = z_voxels × z_resolution), `origin_z` 0.0, `unknown_threshold` 15, `mark_threshold` 0, `publish_voxel_map` false.

## Pitfalls
- `clearing` left at its default (false) → obstacles that moved away are never erased.
- `obstacle_max_range` > `raytrace_max_range` → marks that can never be cleared.
