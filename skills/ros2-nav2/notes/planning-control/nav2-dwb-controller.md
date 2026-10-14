---
id: nav2-dwb-controller
type: reference
owner: equipo-ros2
updated: 2026-10-10
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "DWB controller parameters and critics"
domain: nav2
area: planning-control
distro: humble
tested: false
audience: dev
summary: "DWBLocalPlanner FollowPath block: velocity/acceleration limits, trajectory sampling, goal tolerance, critics (BaseObstacle, PathAlign, GoalDist…) and their scales."
tags: [DWB, DWBLocalPlanner, dwb_core, FollowPath, critics, max_vel_x, max_vel_theta, acc_lim_x, sim_time, BaseObstacle, RotateToGoal]
see: ["[[nav2-controller-server]]", "[[nav2-robot-footprint]]", "[[core-nav2-tuning]]"]
requires: [ros2-core]
version_notes:
  - "jazzy/lyrical: DWB keeps the class name dwb_core::DWBLocalPlanner; Nav2's default config switched to MPPI — https://github.com/ros-navigation/navigation2/blob/jazzy/nav2_bringup/params/nav2_params.yaml (NAV2-V32)"
---
# DWB controller parameters and critics

**TL;DR** DWB is the default controller of Nav2 in Humble: a rewrite and extension of ROS 1's `dwa_local_planner`, hence `DWBLocalPlanner`. It samples velocity commands, simulates each trajectory for `sim_time` seconds and scores it with **critics**; the best one is sent to `cmd_vel`.

## FollowPath block (inside controller_server ros__parameters)
```yaml
    FollowPath:
      plugin: "dwb_core::DWBLocalPlanner"
      debug_trajectory_details: True
      trajectory_generator_name: "dwb_plugins::StandardTrajectoryGenerator"   # default; set in the advanced course (ASCII quotes, NAV2-V54)
      min_vel_x: 0.0
      min_vel_y: 0.0
      max_vel_x: 0.26
      max_vel_y: 0.0
      max_vel_theta: 1.0
      min_speed_xy: 0.0
      max_speed_xy: 0.26
      min_speed_theta: 0.0
      acc_lim_x: 2.5
      acc_lim_y: 0.0
      acc_lim_theta: 3.2
      decel_lim_x: -2.5
      decel_lim_y: 0.0
      decel_lim_theta: -3.2
      vx_samples: 20
      vy_samples: 5
      vtheta_samples: 20
      sim_time: 1.7
      linear_granularity: 0.05
      angular_granularity: 0.025
      transform_tolerance: 0.2
      xy_goal_tolerance: 0.25
      trans_stopped_velocity: 0.25
      short_circuit_trajectory_evaluation: True
      stateful: True
      critics: ["RotateToGoal", "Oscillation", "BaseObstacle", "GoalAlign", "PathAlign", "PathDist", "GoalDist"]
      BaseObstacle.scale: 0.02
      PathAlign.scale: 32.0
      PathAlign.forward_point_distance: 0.1
      GoalAlign.scale: 24.0
      GoalAlign.forward_point_distance: 0.1
      PathDist.scale: 32.0
      GoalDist.scale: 24.0
      RotateToGoal.scale: 32.0
      RotateToGoal.slowing_factor: 5.0
      RotateToGoal.lookahead_time: -1.0
```

## The most important parameters
- **Velocity and acceleration limits** for each axis (`max_vel_x`, `max_vel_theta`, `acc_lim_*`, `decel_lim_*`): how fast and how sharply the robot moves. 0.26 m/s and 1.0 rad/s are TurtleBot3 Burger limits. `min_vel_x: 0.0` forbids driving backwards.
- `xy_goal_tolerance` (0.25 m): how much position error is accepted at the goal.
- Sampling: `vx_samples`, `vy_samples`, `vtheta_samples` (more = better choice, more CPU); `sim_time` (how far ahead each trajectory is simulated).

## Critics
Critics are plugins that score each candidate trajectory against one constraint; `<Critic>.scale` weights it:
| Critic | Prefers trajectories that… |
|---|---|
| `BaseObstacle` | avoid high costmap costs at the robot center (use with `robot_radius`) |
| `ObstacleFootprint` | avoid costs anywhere under the footprint (use with `footprint`, [[nav2-robot-footprint]]) |
| `PathAlign`, `PathDist` | stay aligned with and close to the global path |
| `GoalAlign`, `GoalDist` | head towards and get closer to the goal |
| `RotateToGoal` | rotate in place to the goal heading once in xy tolerance |
| `Oscillation` | do not oscillate back and forth |

Trajectory generators and the full list of critics: [[nav2-dwb-generators-critics]]; [DWB docs](https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/configuration_guide/controller_plugins/dwb_controller/index.md).

## Pitfalls
- DWB needs tuning for each robot and is not meant for Ackermann robots ([[core-nav2-tuning]]).
- Limits above what the base can do → the robot lags the plan and the progress checker aborts.
