---
id: nav2-cartographer-options
title: "Cartographer ROS options: frames, sensors, publish periods, sampling"
domain: nav2
area: mapping
distro: humble
tested: false
audience: dev
summary: "Reference of cartographer_ros top-level Lua options: map/tracking/published/odom frames, laser and point cloud counts, publish periods, sampling ratios."
tags: [cartographer_ros, options, map_frame, tracking_frame, published_frame, provide_odom_frame, num_laser_scans, sampling_ratio]
see: ["[[nav2-cartographer-lua]]", "[[nav2-cartographer-launch]]", "[[core-tf-basics]]"]
requires: [ros2-core]
version_notes:
  - "humble: the Lua key is fixed_frame_pose_sampling_ratio, not fixed_frame_sampling_ratio as in the cartographer_ros docs — https://github.com/ros2/cartographer_ros/blob/ros2/cartographer_ros/src/trajectory_options.cpp (NAV2-V12)"
---
# Cartographer ROS options: frames, sensors, publish periods, sampling

**TL;DR** These are the ROS integration top-level options of `cartographer_ros`; **all** of them must be specified in the Lua file. Configure frames first, then the sensor counts; the rest rarely changes.

## 1. General
| Option | Meaning |
|---|---|
| `map_frame` | ROS frame for publishing sub-maps, the parent frame of poses; usually `map` |
| `tracking_frame` | frame tracked by SLAM. With an IMU it should be at the IMU position (it may be rotated). Common: `base_link` or `base_footprint` |
| `published_frame` | child frame for publishing poses. E.g. `odom` if another part of the system supplies `odom` (then the pose of `odom` in `map_frame` is published); otherwise `base_link` |
| `odom_frame` | only used if `provide_odom_frame` is true: frame between `published_frame` and `map_frame` for the local (non-loop-closed) SLAM result; usually `odom` |
| `provide_odom_frame` | if enabled, the local, non-loop-closed, continuous pose is published as `odom_frame` in `map_frame` |
| `use_odometry` | if enabled, subscribes to `nav_msgs/Odometry` on topic `odom`; odometry must be provided and is included in SLAM |
| `use_nav_sat` | if enabled, subscribes to `sensor_msgs/NavSatFix` on topic `fix`; used in global SLAM |

## 2. Laser and range sensors
| Option | Meaning |
|---|---|
| `num_laser_scans` | number of `sensor_msgs/LaserScan` topics: `scan` for one scanner, `scan_1`, `scan_2`, … for several |
| `num_multi_echo_laser_scans` | number of `sensor_msgs/MultiEchoLaserScan` topics: `echoes`, or `echoes_1`, `echoes_2`, … |
| `num_subdivisions_per_laser_scan` | point clouds each received (multi-echo) scan is split into; subdividing lets scans acquired while moving be unwarped (a trajectory builder option accumulates them back for scan matching) |
| `num_point_clouds` | number of `sensor_msgs/PointCloud2` topics: `points2`, or `points2_1`, `points2_2`, … |

## 3. Timing and sampling
| Option | Meaning |
|---|---|
| `lookup_transform_timeout_sec` | timeout (s) for looking up transforms with tf2 |
| `submap_publish_period_sec` | interval in seconds to publish the submap poses, e.g. 0.3 seconds |
| `pose_publish_period_sec` | interval in seconds to publish poses, e.g. 5e-3 for a frequency of 200 Hz |
| `trajectory_publish_period_sec` | interval in seconds to publish the trajectory markers, e.g. 30e-3 for 30 milliseconds |
| `rangefinder_sampling_ratio` | fixed ratio sampling for range finder messages |
| `odometry_sampling_ratio` | fixed ratio sampling for odometry messages |
| `fixed_frame_pose_sampling_ratio` | fixed ratio sampling for fixed frame messages |
| `imu_sampling_ratio` | fixed ratio sampling for IMU messages |
| `landmarks_sampling_ratio` | fixed ratio sampling for landmark messages |

Topic names (`scan`, `odom`, `imu`, `fix`, `echoes`, `points2`) are fixed by Cartographer: remap them in the launch file ([[nav2-cartographer-launch]]).

## Pitfalls
- `published_frame = "odom"` while also `provide_odom_frame = true` → two publishers of `odom` and a broken TF tree.
- Sampling ratios < 1 drop data: lower them only for very high-rate sensors.
