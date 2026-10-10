---
id: core-nav2-overview
title: "Nav2 architecture, cmd_vel chain & rates"
domain: core
area: architecture
distro: humble
tested: false
audience: dev
summary: "Nav2 servers under lifecycle_manager, cmd_vel chain in Humble vs Jazzy, TwistStamped change, TF and topic rates/QoS, new servers per distro."
tags: [Nav2, bt_navigator, velocity_smoother, collision_monitor, cmd_vel, TwistStamped]
see: ["[[core-nav2-tuning]]", "[[core-nav2-python-client]]", "[[core-tf-basics]]", "[[core-lifecycle-concepts]]"]
requires: []
version_notes:
  - "humble: default bringup chain controller->cmd_vel_nav->velocity_smoother->cmd_vel; collision_monitor in bringup from Jazzy — https://github.com/ros-navigation/navigation2/blob/humble/nav2_bringup/launch/navigation_launch.py (V48)"
  - "lyrical: TwistStamped default (Kilted); route + following servers — https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/migration_guides/jazzy/Jazzy.md (V54, V55)"
---
# Nav2 architecture, cmd_vel chain & rates

**TL;DR** `bt_navigator` drives the planner, controller, behavior and smoother servers, all of them lifecycle nodes under `lifecycle_manager`. In Humble's default bringup, `cmd_vel` only passes through the velocity smoother. Per-server configuration, costmaps, behavior trees and multi-robot setups: skill ros2-nav2.

## Architecture
- `bt_navigator` (NavigateToPose / NavigateThroughPoses BT, ~10 Hz) → `planner_server`, `controller_server`, `behavior_server`, `smoother_server`, `waypoint_follower`; global + local `nav2_costmap_2d`. All are lifecycle nodes under `lifecycle_manager` ([[core-lifecycle-concepts]]).
- Cmd chain [Humble default bringup]: controller → `/cmd_vel_nav` → velocity_smoother → `/cmd_vel`. Collision Monitor exists in Humble (later backport) but is not in the default bringup.
- [changed in Jazzy: controller → `/cmd_vel_nav` → velocity_smoother → `cmd_vel_smoothed` → collision_monitor → `/cmd_vel`; `enable_stamped_cmd_vel` option (default false); docking server]
- [changed in Lyrical: `cmd_vel` is `TwistStamped` by default (since Kilted; disable with `enable_stamped_cmd_vel: false`); route server, following server, Nav2 lifecycle-node refactor]

## Rates & QoS
| Transform | Publisher | Rate |
|---|---|---|
| map→odom | AMCL / SLAM Toolbox | ~10 Hz |
| odom→base_link | odom driver / EKF | 50–100 Hz |
| base_link→sensors | robot_state_publisher | static |

| Topic | Rate | QoS |
|---|---|---|
| /cmd_vel | 10–20 Hz | RELIABLE |
| /odom | 50–100 Hz | RELIABLE |
| /scan | 10–40 Hz | BEST_EFFORT |
| /imu/data | 100–200 Hz | BEST_EFFORT |
| /map, /tf_static | latched | RELIABLE + TRANSIENT_LOCAL |

Tuning (costmaps, planners, controllers, BT, AMCL): [[core-nav2-tuning]]. Sending goals from code: [[core-nav2-python-client]].

## Pitfalls
- A robot base that subscribes to `Twist` stops moving under Kilted+ Nav2 defaults (`TwistStamped`) with no error.
- Teleop or other nodes publishing `/cmd_vel` directly bypass the smoother (and the collision monitor in Jazzy+).
