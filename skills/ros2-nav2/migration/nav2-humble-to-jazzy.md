---
id: nav2-humble-to-jazzy
type: reference
owner: equipo-ros2
updated: 2026-10-10
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "Humble → Jazzy changes (Nav2)"
domain: nav2
area: migration
distro: jazzy
tested: false
audience: dev
summary: "Nav2 changes from Humble to Jazzy (incl. Iron): :: plugin names, BT.CPP 4.5, BT plugin list, behavior server frames, Gazebo."
tags: [migration, jazzy, iron, Nav2, BT.CPP 4, plugin names, progress_checker_plugins, behavior_server]
see: ["[[nav2-jazzy-to-lyrical]]", "[[nav2-migration-checklist]]", "[[core-humble-to-jazzy]]"]
requires: [ros2-core]
version_notes:
  - "sources: https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/migration_guides/Humble.md · https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/migration_guides/iron/Iron.md"
---
# Humble → Jazzy changes (Nav2)

**TL;DR** Jazzy's Nav2 (1.3.x) includes Iron's changes. The edits most course-style configs need are the `::` plugin names, BT XML for BehaviorTree.CPP 4.5, removing the BT plugin list, `progress_checker_plugins`, the behavior server's `local_frame`, and Gazebo Harmonic instead of Gazebo Classic. `NAV2-Vxx` = row in the repo's `reports/version_audit_nav2.md`.

| Area | Humble | Jazzy | Ref |
|---|---|---|---|
| Plugin names | mixed: `nav2_navfn_planner/NavfnPlanner`, `nav2_behaviors/Spin` | all `::`: `nav2_navfn_planner::NavfnPlanner`, `nav2_behaviors::Spin`; DWB stays `dwb_core::DWBLocalPlanner` | NAV2-V17 |
| Behavior trees | BT.CPP 3.8, `<root main_tree_to_execute=…>` | BT.CPP 4.5: `<root BTCPP_format="4" …>`, new SubTree syntax; custom control/decorator nodes handle `SKIPPED`; `SequenceStar` still accepted | NAV2-V20 |
| bt_navigator | `plugin_lib_names` lists every Nav2 BT library | Nav2 BT nodes load automatically, list only custom ones; `navigators` param; `$(find-pkg-share)` in param files | NAV2-V19, NAV2-V21 |
| controller_server | `progress_checker_plugin: "progress_checker"` | `progress_checker_plugins: ["progress_checker"]` | NAV2-V18 |
| Default controller | DWB in `nav2_params.yaml` | MPPI in `nav2_params.yaml` | NAV2-V32 |
| behavior_server | `global_frame` (default `odom`), `costmap_topic`, `footprint_topic` | `local_frame: odom` + `global_frame: map`; `local_/global_costmap_topic`, `local_/global_footprint_topic` | NAV2-V02 |
| Lifecycle | `bond_timeout` in the manager | + `bond_heartbeat_period` per node (0.1 s; ≤ 0 disables bonds) | NAV2-V23 |
| ManageLifecycleNodes | commands 0–4 | + `CONFIGURE = 5`, `CLEANUP = 6` | NAV2-V22 |
| cmd_vel | Twist | Twist, opt-in `enable_stamped_cmd_vel`; collision_monitor in the default chain | NAV2-V26, NAV2-V27 |
| Simulation | Gazebo Classic: `ros2 run gazebo_ros spawn_entity.py -entity … -database …` | Gazebo Harmonic: `ros2 run ros_gz_sim create …`; `gazebo_ros` not released | NAV2-V28 |
| Multi-robot bringup | `unique_/cloned_multi_tb3_simulation_launch.py` | renamed `unique_tb3_simulation_launch.py`, `cloned_tb3_simulation_launch.py` | NAV2-V25 |
| Map server launch | `yaml_filename` param | Nav2 launch files take a `map` argument that overrides it | NAV2-V36 |
| use_sim_time | set in every YAML | Nav2 launch files can set it for all nodes | NAV2-V30 |
| Simple Commander | `isTaskComplete()`, `getResult()` → `TaskResult`, clear*Costmap methods | + `driveOnHeading()`, docking, `followGpsWaypoints()`, `clearCostmapAroundRobot()` | NAV2-V57 |
| Action results | `NavigateToPose` result empty; `FollowWaypoints` `int32[] missed_waypoints` | `error_code` + `error_msg`; `FollowWaypoints` goal `number_of_loops`, `goal_index`, result `MissedWaypoint[]` | NAV2-V58, NAV2-V59 |
| waypoint_follower | `loop_rate`, `stop_on_failure`, task executor plugins | + `action_server_result_timeout`, `global_frame_id` | NAV2-V60 |
| Costmap filters | Keepout, Speed and Binary filters, `toggle_filter` | + `override_lethal_cost`, `lethal_override_cost` (KeepoutFilter) | NAV2-V61 |
| Plugin API | `GlobalPlanner::createPlan(start, goal)`; `Controller` without cancel | `createPlan(start, goal, cancel_checker)`; `Controller::cancel()`, `reset()` | NAV2-V63 |
| Regulated Pure Pursuit | `use_interpolation`, `max_allowed_time_to_collision_up_to_carrot` | + `use_fixed_curvature_lookahead`, `curvature_lookahead_dist`, `stateful`, cancel deceleration; − `use_interpolation` | NAV2-V65 |

Unchanged and safe to keep: AMCL parameters and topics, costmap layer parameters, NavFn parameters, DWB critics, map_saver_cli, cartographer_ros, the NavigateToPose goal and the `goal_pose` topic (its result gains error codes, NAV2-V58).

Generic ROS 2 changes (Ubuntu 24.04, rclpy, launch, tf2…): [[core-humble-to-jazzy]]. Step-by-step: [[nav2-migration-checklist]].
