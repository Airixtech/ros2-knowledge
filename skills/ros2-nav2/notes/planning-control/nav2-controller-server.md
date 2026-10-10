---
id: nav2-controller-server
title: "controller_server, progress checker and goal checker parameters"
domain: nav2
area: planning-control
distro: humble
tested: false
audience: dev
summary: "controller_server (local planner, cmd_vel): launch, server parameters with Humble defaults, SimpleProgressChecker and SimpleGoalChecker, available controllers."
tags: [controller_server, nav2_controller, controller_frequency, failure_tolerance, progress_checker, goal_checker, xy_goal_tolerance, cmd_vel, FollowPath]
see: ["[[nav2-dwb-controller]]", "[[nav2-local-costmap]]", "[[nav2-planner-server]]", "[[core-nav2-tuning]]", "[[core-nav2-overview]]"]
requires: [ros2-core]
version_notes:
  - "humble: defaults min_*_velocity_threshold 0.0001; failure_tolerance in seconds, default 0.0 — https://github.com/ros-navigation/navigation2/blob/humble/nav2_controller/src/controller_server.cpp (NAV2-V07)"
  - "humble: controllers DWB, RPP, MPPI, Rotation Shim, Graceful are released; TEB is not released for ROS 2 — http://packages.ros.org/ros2/ubuntu/dists/jammy/main/binary-amd64/Packages.gz (NAV2-V05)"
  - "jazzy: progress_checker_plugins (list) replaces progress_checker_plugin (Iron); default controller in nav2_params is MPPI — https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/migration_guides/Humble.md (NAV2-V18, NAV2-V32)"
  - "lyrical: cmd_vel is TwistStamped by default (Kilted) — https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/migration_guides/jazzy/Jazzy.md (NAV2-V26)"
---
# controller_server, progress checker and goal checker parameters

**TL;DR** The controller (ROS 1 "local planner") follows the global path a few meters ahead, avoids **dynamic** obstacles from the local costmap and **generates the wheel commands** on `cmd_vel`.

## Server config
Package `nav2_controller`, executable `controller_server` ([[nav2-path-planning-launch]]). Top of `config/controller.yaml` (DWB block: [[nav2-dwb-controller]]; local costmap: [[nav2-local-costmap]]):
```yaml
controller_server:
  ros__parameters:
    use_sim_time: True
    controller_frequency: 10.0
    min_x_velocity_threshold: 0.001
    min_y_velocity_threshold: 0.5
    min_theta_velocity_threshold: 0.001
    failure_tolerance: 0.3
    progress_checker_plugin: "progress_checker"
    goal_checker_plugins: ["general_goal_checker"]
    controller_plugins: ["FollowPath"]
    # Progress checker parameters
    progress_checker:
      plugin: "nav2_controller::SimpleProgressChecker"
      required_movement_radius: 0.5
      movement_time_allowance: 10.0
    # Goal checker parameters
    general_goal_checker:
      stateful: True
      plugin: "nav2_controller::SimpleGoalChecker"
      xy_goal_tolerance: 0.25
      yaw_goal_tolerance: 0.25
```

## Parameters (Humble code defaults)
| Parameter | Default | Meaning |
|---|---|---|
| `controller_frequency` | 20.0 Hz | rate of the control loop |
| `min_x_velocity_threshold` | 0.0001 m/s | odometry X velocity below this counts as 0.0 |
| `min_y_velocity_threshold` | 0.0001 m/s | same for Y |
| `min_theta_velocity_threshold` | 0.0001 rad/s | same for the angular velocity |
| `failure_tolerance` | 0.0 s | how long the controller plugin may fail before the `FollowPath` action fails; -1.0 = infinite, 0.0 = fail at once |
| `progress_checker_plugin`, `goal_checker_plugins`, `controller_plugins` | `"progress_checker"`, `["goal_checker"]`, `["FollowPath"]` | mapped plugin names |

- **Progress checker** (is the robot stuck?): `required_movement_radius` 0.5 m must be covered within `movement_time_allowance` 10.0 s.
- **Goal checker** (goal reached?): `xy_goal_tolerance` 0.25 m and `yaw_goal_tolerance` 0.25 rad; `stateful: True` keeps "xy reached" while rotating to the final heading.

Other Humble controllers (RPP, MPPI, Rotation Shim, Graceful; no TEB) and how to choose: [[core-nav2-tuning]].

## Pitfalls
- `controller_id` in the BT XML must match a name in `controller_plugins` (`FollowPath`).
- The robot "aborts" right after starting → `progress_checker` too strict for a slow robot, or `failure_tolerance: 0.0`.
