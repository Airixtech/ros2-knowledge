---
id: nav2-rpp-controller-params
title: "Regulated Pure Pursuit controller (nav2_regulated_pure_pursuit_controller) parameters"
domain: nav2
area: planning-control
distro: humble
tested: false
audience: dev
summary: "Nav2's RegulatedPurePursuitController as FollowPath: Humble parameters (lookahead, regulation, collision time, rotate to heading), other Humble controllers, Jazzy/Lyrical changes."
tags: [Regulated Pure Pursuit, RPP, nav2_regulated_pure_pursuit_controller, RegulatedPurePursuitController, desired_linear_vel, lookahead_dist, max_allowed_time_to_collision_up_to_carrot, use_rotate_to_heading, allow_reversing, TEB, MPPI]
see: ["[[nav2-controller-server]]", "[[nav2-goal-progress-checkers]]", "[[nav2-controller-plugin-rpp]]", "[[core-nav2-tuning]]"]
requires: [ros2-core]
version_notes:
  - "humble: controllers DWB, RPP, MPPI, Rotation Shim, Graceful (course: two, TEB 'still unavailable' — TEB is not released for ROS 2) — http://packages.ros.org/ros2/ubuntu/dists/jammy/main/binary-amd64/Packages.gz (NAV2-V05)"
  - "jazzy: + use_fixed_curvature_lookahead, curvature_lookahead_dist, stateful, cancel_deceleration; − use_interpolation; lyrical: dynamic window (use_dynamic_window, velocity/acceleration limits), − transform_tolerance, max_robot_pose_search_dist — https://github.com/ros-navigation/navigation2/tree/lyrical/nav2_regulated_pure_pursuit_controller/src (NAV2-V65)"
---
# Regulated Pure Pursuit controller parameters

**TL;DR** The **Regulated Pure Pursuit** controller is made for industrial applications where safety at speed matters. It regulates the linear velocity by the curvature of the path to help reduce overshoot at high speeds around blind corners, allowing much safer operation. It tracks a lookahead point on the path instead of sampling trajectories like DWB.

## FollowPath block (inside controller_server ros__parameters)
```yaml
    FollowPath:
      plugin: "nav2_regulated_pure_pursuit_controller::RegulatedPurePursuitController"
      desired_linear_vel: 0.5
      lookahead_dist: 0.6
      min_lookahead_dist: 0.3
      max_lookahead_dist: 0.9
      lookahead_time: 1.5
      rotate_to_heading_angular_vel: 1.8
      transform_tolerance: 0.1
      use_velocity_scaled_lookahead_dist: false
      min_approach_linear_velocity: 0.05
      max_allowed_time_to_collision_up_to_carrot: 1.0
      use_regulated_linear_velocity_scaling: true
      use_cost_regulated_linear_velocity_scaling: false
      regulated_linear_scaling_min_radius: 0.9
      regulated_linear_scaling_min_speed: 0.25
      use_rotate_to_heading: true
      allow_reversing: false
      rotate_to_heading_min_angle: 0.785
      max_angular_accel: 3.2
      max_robot_pose_search_dist: 10.0
      use_interpolation: false
```
| Group | Parameters | Meaning |
|---|---|---|
| Speed | `desired_linear_vel` | cruise speed (m/s) before regulation |
| Lookahead | `lookahead_dist`; with `use_velocity_scaled_lookahead_dist: true`: `lookahead_time`, bounded by `min_`/`max_lookahead_dist` | distance to the point on the path the robot steers to |
| Regulation | `use_regulated_linear_velocity_scaling`, `regulated_linear_scaling_min_radius`, `regulated_linear_scaling_min_speed`, `use_cost_regulated_linear_velocity_scaling` | slow down in tight turns and near obstacles |
| Approach | `min_approach_linear_velocity` | minimum speed while approaching the goal |
| Collision | `max_allowed_time_to_collision_up_to_carrot` | time (s) the current command is projected forward to check for collisions |
| Heading | `use_rotate_to_heading`, `rotate_to_heading_min_angle`, `rotate_to_heading_angular_vel`, `max_angular_accel` | rotate in place when the path heading differs too much |
| Path | `allow_reversing`, `max_robot_pose_search_dist`, `use_interpolation`, `transform_tolerance` | reversing, path search window, TF tolerance |

Humble parameter list and defaults: [RPP README (humble)](https://github.com/ros-navigation/navigation2/blob/humble/nav2_regulated_pure_pursuit_controller/README.md); current docs: [Regulated Pure Pursuit](https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/configuration_guide/controller_plugins/configuring_regulated_pp.md).

## Controllers in Humble
Controller plugins are responsible for computing the local plan: the velocities to the wheels to follow the path, considering the obstacles in close range. The course says only DWB and RPP exist and that **TEB** (for holonomic or car-like robots) is "announced but still unavailable". In Humble the released controllers are DWB, RPP, MPPI, Rotation Shim and Graceful; TEB is not released for any ROS 2 distro (NAV2-V05). [changed in Jazzy: Nav2's default config uses MPPI]

## Pitfalls
- Values copied from an older RPP (e.g. `max_allowed_time_to_collision`, `use_approach_linear_velocity_scaling`) are ignored in Humble ([[nav2-controller-plugin-config]]).
- Jazzy-only keys (`use_fixed_curvature_lookahead`, `stateful`) have no effect in Humble.
