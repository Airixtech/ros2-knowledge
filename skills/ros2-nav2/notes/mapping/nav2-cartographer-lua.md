---
id: nav2-cartographer-lua
type: reference
owner: equipo-ros2
updated: 2026-10-10
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "cartographer.lua for a 2D robot (TurtleBot3)"
domain: nav2
area: mapping
distro: humble
tested: false
audience: dev
summary: "Complete cartographer.lua for 2D mapping: frames, odometry, one laser, TRAJECTORY_BUILDER_2D ranges, scan matching, POSE_GRAPH scores."
tags: [cartographer.lua, TRAJECTORY_BUILDER_2D, MAP_BUILDER, POSE_GRAPH, tracking_frame, published_frame, min_range, max_range]
see: ["[[nav2-cartographer-options]]", "[[nav2-cartographer-launch]]", "[[core-tf-basics]]"]
requires: [ros2-core]
version_notes:
  - "humble: the sampling key is fixed_frame_pose_sampling_ratio (the cartographer_ros docs say fixed_frame_sampling_ratio) — https://github.com/ros2/cartographer_ros/blob/ros2/cartographer_ros/src/trajectory_options.cpp (NAV2-V12)"
---
# cartographer.lua for a 2D robot (TurtleBot3)

**TL;DR** Put this file in `config/` of your package. The robot already publishes `odom → base_footprint`, so Cartographer tracks `base_footprint`, publishes `map → odom` and does not provide its own odom frame.

## config/cartographer.lua
```lua
include "map_builder.lua"
include "trajectory_builder.lua"

options = {
  map_builder = MAP_BUILDER,
  trajectory_builder = TRAJECTORY_BUILDER,
  map_frame = "map",
  tracking_frame = "base_footprint",
  published_frame = "odom",
  odom_frame = "odom",
  provide_odom_frame = false,
  publish_frame_projected_to_2d = true,
  use_odometry = true,
  use_nav_sat = false,
  use_landmarks = false,
  num_laser_scans = 1,
  num_multi_echo_laser_scans = 0,
  num_subdivisions_per_laser_scan = 1,
  num_point_clouds = 0,
  lookup_transform_timeout_sec = 0.2,
  submap_publish_period_sec = 0.3,
  pose_publish_period_sec = 5e-3,
  trajectory_publish_period_sec = 30e-3,
  rangefinder_sampling_ratio = 1.,
  odometry_sampling_ratio = 1.,
  fixed_frame_pose_sampling_ratio = 1.,
  imu_sampling_ratio = 1.,
  landmarks_sampling_ratio = 1.,
}

MAP_BUILDER.use_trajectory_builder_2d = true

TRAJECTORY_BUILDER_2D.min_range = 0.12
TRAJECTORY_BUILDER_2D.max_range = 3.5
TRAJECTORY_BUILDER_2D.missing_data_ray_length = 3.0
TRAJECTORY_BUILDER_2D.use_imu_data = false
TRAJECTORY_BUILDER_2D.use_online_correlative_scan_matching = true
TRAJECTORY_BUILDER_2D.motion_filter.max_angle_radians = math.rad(0.1)

POSE_GRAPH.constraint_builder.min_score = 0.65
POSE_GRAPH.constraint_builder.global_localization_min_score = 0.7

-- POSE_GRAPH.optimize_every_n_nodes = 0

return options
```
Every key of `options` must be present: Cartographer refuses to start if one is missing. Meaning of each option: [[nav2-cartographer-options]].

## TRAJECTORY_BUILDER parameters
| Parameter | Meaning |
|---|---|
| `TRAJECTORY_BUILDER_2D.min_range` | minimum measured distance taken into account to build the map |
| `TRAJECTORY_BUILDER_2D.max_range` | maximum measured distance taken into account to build the map |
| `TRAJECTORY_BUILDER_2D.missing_data_ray_length` | distance used for a lost laser ray (no return) |
| `TRAJECTORY_BUILDER_2D.use_imu_data` | whether or not to use the IMU (2D mapping works without it) |

`min_range 0.12` / `max_range 3.5` match the TurtleBot3 LDS laser; adapt them to your sensor and to where the robot works. The `config` folder of the course package holds this robot's file: modify the parameters there for your robot.

## Adapting to another robot
- `tracking_frame`: the frame SLAM tracks; with an IMU it must be at the IMU position (it may be rotated). Common: `base_link` or `base_footprint`.
- Your driver publishes no odometry TF → `provide_odom_frame = true` and `published_frame = "base_footprint"`.
- Several robots: prefix the frames (`tb3_0/base_footprint`, `tb3_0/odom`) — see [[nav2-multirobot-mapping]].

## Pitfalls
- A frame name that does not exist in TF → `lookup_transform_timeout_sec` warnings and an empty map.
- `use_odometry = true` without `/odom` → Cartographer waits forever for odometry.
