---
id: nav2-recovery-flow
type: reference
owner: equipo-ros2
updated: 2026-10-10
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "How recoveries are triggered: progress checker, bt_navigator, behavior_server action servers"
domain: nav2
area: behavior-trees
distro: humble
tested: false
audience: dev
summary: "Recovery chain: progress checker fails FollowPath, RecoveryNode runs recoveries, behavior_server actions; Humble behavior_plugins, transform_tolerance."
tags: [recovery behaviors, recoveries, behavior_server, behavior_plugins, recovery_plugins, progress checker, Failed to make progress, spin, backup, wait, drive_on_heading, ros2 action list]
see: ["[[nav2-behavior-server]]", "[[nav2-bt-control-nodes]]", "[[nav2-bt-action-nodes]]", "[[nav2-controller-server]]", "[[nav2-goal-progress-checkers]]"]
requires: [ros2-core]
version_notes:
  - "humble: recovery_plugins → behavior_plugins (default spin, backup, drive_on_heading, wait), recoveries_server → behavior_server, nav2_recoveries → nav2_behaviors — https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/migration_guides/galactic/Galactic.md (NAV2-V48, NAV2-V31, NAV2-V03)"
  - "jazzy: behavior_server uses local_frame + global_frame and costmap/footprint topics per frame (Iron) — https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/migration_guides/Humble.md (NAV2-V02)"
---
# How recoveries are triggered

**TL;DR** The Nav2 **recovery behaviors** are activated automatically when the robot gets stuck, to try to recover. They are activated by the `bt_navigator` when a checker of the `controller_server` signals that the robot is not progressing to its goal. Each behavior plugin provides an **action server**, called by the behavior tree nodes that require it.

## The chain (Humble)
1. The `controller_server` detects that the robot is stuck: its progress checker fails ([[nav2-goal-progress-checkers]]), the server logs `Failed to make progress` and aborts the `FollowPath` action.
2. The `FollowPath` BT node returns FAILURE; the behavior tree XML (not a config file) decides what follows: the `RecoveryNode` runs its recovery branch ([[nav2-bt-control-nodes]]).
3. The recovery nodes (`Spin`, `BackUp`, `Wait`) call the action servers of the `behavior_server` (`recoveries_server` before Humble) ([[nav2-bt-action-nodes]]).

## Configuration
The recovery behaviors are configured in the `behavior_server` config file `recovery.yaml` (Humble-correct file and parameter table: [[nav2-behavior-server]]). The course file used Galactic keys:
```yaml
behavior_server:
  ros__parameters:
    costmap_topic: local_costmap/costmap_raw
    footprint_topic: local_costmap/published_footprint
    cycle_frequency: 10.0
    behavior_plugins: ["spin", "backup", "wait"]   # course: recovery_plugins (ignored in Humble)
    # ...
    transform_tolerance: 0.1                       # course: transform_timeout (not a Humble parameter)
```
- Parameters of the server itself: `costmap_topic`, `footprint_topic`, `cycle_frequency`.
- Conditions that apply to all the plugins (speed limits and frames): `global_frame`, `robot_base_frame`, `transform_tolerance`, `simulate_ahead_time`, `max_rotational_vel`, `min_rotational_vel`, `rotational_acc_lim`.

With `recovery_plugins` Humble ignores the list and loads its defaults: `spin`, `backup`, `drive_on_heading`, `wait`. The course says three plugins exist; Humble's `nav2_behaviors` has five:
1. `Spin`: rotation in place while the costmaps are updated. Useful when the robot sees the costmap around it filled with obstacles (which may exist in reality or not): it helps determine the obstacles that exist at present and increases the chances of finding a new path to the goal.
2. `BackUp`: linear motion of the robot for a certain distance.
3. `DriveOnHeading`: drive straight on the current heading for a distance.
4. `Wait`: stops the robot in place and waits for a certain amount of time (given in the action request).
5. `AssistedTeleop`: teleoperation with collision checking.

## How they work
Launch the navigation system and list the action servers:
```bash
ros2 action list
```
The course shows `/backup`, `/compute_path_through_poses`, `/compute_path_to_pose`, `/follow_path`, `/navigate_through_poses`, `/navigate_to_pose`, `/spin`, `/wait` (plus a non-Nav2 action of its environment). With Humble's defaults you also get `/drive_on_heading`.

## Pitfalls
- The YAML key must equal the launched node name (`behavior_server:` for a node named `behavior_server`) ([[nav2-behavior-server]]).
- Recoveries that never run: check the BT, not `recovery.yaml` — only the tree calls them.
