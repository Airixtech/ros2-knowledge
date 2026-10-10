---
id: nav2-jazzy-to-lyrical
title: "Jazzy → Lyrical changes (Nav2, includes Kilted)"
domain: nav2
area: migration
distro: lyrical
tested: false
audience: dev
summary: "Nav2 changes from Jazzy to Lyrical (Kilted included): TwistStamped cmd_vel default, namespace-ready params, map_topic in static_layer, Groot 2, nav2_ros_common."
tags: [migration, lyrical, kilted, Nav2, TwistStamped, namespaces, map_topic, Groot 2, nav2_ros_common, bond_heartbeat_period]
see: ["[[nav2-humble-to-jazzy]]", "[[nav2-migration-checklist]]", "[[core-jazzy-to-lyrical]]"]
requires: [ros2-core]
version_notes:
  - "sources: https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/migration_guides/jazzy/Jazzy.md · https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/migration_guides/kilted/Kilted.md"
---
# Jazzy → Lyrical changes (Nav2, includes Kilted)

**TL;DR** Kilted (non-LTS) and Lyrical change runtime behavior more than file syntax: `cmd_vel` becomes `TwistStamped`, configs become namespace-ready with relative topics, the costmap's global `map_topic` moves into the static layer, and Nav2 nodes move to `nav2_ros_common`. `NAV2-Vxx` = row in `reports/version_audit_nav2.md`.

| Area | Jazzy | Lyrical (Kilted unless noted) | Ref |
|---|---|---|---|
| cmd_vel | Twist (opt-in stamped) | **TwistStamped by default**; your base must subscribe to `TwistStamped`, or set `enable_stamped_cmd_vel: false` everywhere | NAV2-V26 |
| Namespaces | absolute topics in per-robot configs | relative topics join the robot namespace (`joinWithParentNamespace`); one `nav2_params.yaml` and one RViz config for single and multi-robot; `use_namespace` launch arg removed | NAV2-V25 |
| Costmap `map_topic` | costmap-level `map_topic` read by the static layer | removed: set `map_topic` inside `static_layer` | NAV2-V24 |
| Groot | — | Groot 2 live monitoring (`enable_groot_monitoring`, off by default) | NAV2-V10 |
| Lifecycle | `nav2_util::LifecycleNode` | `nav2::LifecycleNode` in `nav2_ros_common` (Lyrical); factories return Nav2 wrappers; custom plugins/servers need migration | NAV2-V40 |
| Bonds | `bond_heartbeat_period` 0.1 s | default 0.25 s, also set it in the lifecycle manager (Lyrical) | NAV2-V23 |
| New servers | docking | route server; following server and a collision monitor toggle (Lyrical) | NAV2-V27 |
| Inflation layer | — | refactored (OpenMP), custom inscribed radius, asymmetric inflation (Lyrical) | NAV2-V09 |
| Simple Commander | untyped methods | typed API, `getTaskError()`, `isTaskComplete(task)`; (Lyrical) `followWaypoints(poses, number_of_loops, goal_index)`, `followObjectByTopic`/`ByFrame`, `toggleCollisionMonitor` | NAV2-V57 |
| Action results | `error_code`, `error_msg` | named codes 9000–9003; (Lyrical) `GOAL_REJECTED`, `SEND_GOAL_FAILURE`, feedback tracking errors, `FollowWaypoints` `WaypointStatus[]` | NAV2-V58, NAV2-V59 |
| Costmap filters | keepout, speed, binary | keepout and speed zones in the default bringup, vector object server; (Lyrical) zone parameter filter | NAV2-V61 |
| Plugin API | `rclcpp_lifecycle` node, `setPlan()` | (Lyrical) `nav2::LifecycleNode`, `nav2::TransformBuffer`, `createPlan(…, viapoints, cancel_checker)`, `Controller::newPathReceived()` and `computeVelocityCommands(…, transformed_global_plan, global_goal)` | NAV2-V63 |
| Controller server | progress/goal checkers | (Lyrical) path handler plugin (`FeasiblePathHandler`), `AdaptiveToleranceGoalChecker`, `AxisGoalChecker` | NAV2-V67 |
| Regulated Pure Pursuit | — | (Lyrical) dynamic window (`use_dynamic_window`, velocity/acceleration limits), `min_distance_to_obstacle`; − `transform_tolerance`, `max_robot_pose_search_dist`, `stateful` | NAV2-V65 |
| CMake | `ament_target_dependencies()` | deprecated; removed in Lyrical: `target_link_libraries()` | NAV2-V68 |

Unchanged: AMCL parameters, the `navigate_to_pose` goal and `goal_pose`, map_saver_cli, cartographer_ros and SLAM Toolbox (both released for Lyrical).

Generic ROS 2 changes: [[core-jazzy-to-lyrical]]. Step-by-step: [[nav2-migration-checklist]].
