---
id: nav2-amcl-params-filter
title: "AMCL filter parameters: particles, update thresholds, recovery, initial pose"
domain: nav2
area: localization
distro: humble
tested: false
audience: dev
summary: "AMCL overall filter parameters with Humble defaults: min/max_particles, update_min_d/a, resample_interval, transform_tolerance, recovery alphas, initial pose."
tags: [AMCL, min_particles, max_particles, update_min_d, update_min_a, recovery_alpha_slow, set_initial_pose, always_reset_initial_pose, save_pose_rate]
see: ["[[nav2-amcl-params-models]]", "[[nav2-amcl-launch]]", "[[nav2-initial-pose-config]]", "[[nav2-global-localization]]"]
requires: [ros2-core]
version_notes:
  - "humble: always_reset_initial_pose is a bool; save_pose_rate is declared but has no effect (the pose is not saved or reused) — https://github.com/ros-navigation/navigation2/blob/humble/nav2_amcl/src/amcl_node.cpp (NAV2-V08)"
  - "humble: defaults below read from the parameter declarations; same in Jazzy and Lyrical — https://github.com/ros-navigation/navigation2/blob/humble/nav2_amcl/src/amcl_node.cpp (NAV2-V33)"
---
# AMCL filter parameters: particles, update thresholds, recovery, initial pose

**TL;DR** AMCL parameters fall in three groups: overall filter (this note), laser model and odometry model ([[nav2-amcl-params-models]]). For the filter, tune the particle limits and the motion needed before an update.

## Overall filter parameters (Humble defaults)
| Parameter | Type, default | Meaning |
|---|---|---|
| `min_particles` | int, 500 | minimum allowed number of particles |
| `max_particles` | int, 2000 | maximum allowed number of particles |
| `update_min_d` | double, 0.25 m | translational movement required before performing a filter update |
| `update_min_a` | double, 0.2 rad | rotational movement required before performing a filter update |
| `resample_interval` | int, 1 | number of filter updates required before re-sampling |
| `transform_tolerance` | double, 1.0 s | time with which to post-date the published transform, i.e. how long it is valid into the future |
| `recovery_alpha_slow` | double, 0.0 (disabled) | exponential decay rate of the slow average weight filter, used to decide when to recover by adding random poses; a good value might be 0.001 |
| `recovery_alpha_fast` | double, 0.0 (disabled) | decay rate of the fast average weight filter for the same decision; a good value might be 0.1 |
| `pf_err`, `pf_z` | double, 0.05 / 0.99 | KLD-sampling error and quantile: how many particles are needed |
| `set_initial_pose` | bool, false | set the initial pose from the `initial_pose` parameters instead of waiting for an `initialpose` message |
| `initial_pose` | `x`, `y`, `z`, `yaw`, all 0.0 | initial pose of the robot base frame in the global frame (meters, radians) |
| `always_reset_initial_pose` | **bool**, false | on reset, require an initial pose from the topic or from `initial_pose` (with `set_initial_pose: true`); by default AMCL reuses the last known pose |
| `save_pose_rate` | double, 0.5 Hz | ROS 1 option (store the last pose for later runs). In Humble it is declared but **does nothing** |
| `scan_topic`, `map_topic` | string, `scan` / `map` | input topics (relative: they get the node namespace) |
| `first_map_only` | bool, false | ignore map updates after the first map |

Initial pose from the file: [[nav2-initial-pose-config]].

## Tuning hints
- More particles = more robust and more CPU; global localization needs tens of thousands ([[nav2-global-localization]]).
- Smaller `update_min_d` / `update_min_a` = more frequent updates (more CPU, faster correction).

## Pitfalls
- Expecting AMCL to remember the last pose after a restart: `save_pose_rate` does nothing in Humble; use `set_initial_pose` or publish the pose ([[nav2-initial-pose-publisher]]).
- `transform_tolerance` too large hides TF delays instead of fixing them.
