---
id: nav2-bt-plugin-libs
type: reference
owner: equipo-ros2
updated: 2026-10-10
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "plugin_lib_names: BT node libraries in Humble"
domain: nav2
area: behavior-trees
distro: humble
tested: false
audience: dev
summary: "Course bt_navigator.yaml with the Humble plugin_lib_names list of Nav2 BT libraries; when to list them; Jazzy change."
tags: [bt_navigator.yaml, plugin_lib_names, BT nodes, nav2_behavior_tree, behavior tree plugins]
see: ["[[nav2-bt-navigator]]", "[[nav2-behavior-tree-xml]]"]
requires: [ros2-core]
version_notes:
  - "humble: all 44 libraries below exist; Humble's built-in default list has 49 — https://github.com/ros-navigation/navigation2/blob/humble/nav2_bt_navigator/src/bt_navigator.cpp (NAV2-V19)"
  - "jazzy: plugin_lib_names implicitly includes all Nav2 BT nodes; list only your own plugins — https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/migration_guides/iron/Iron.md (NAV2-V19)"
---
# plugin_lib_names: BT node libraries in Humble

**TL;DR** In Humble, `plugin_lib_names` lists the shared libraries that provide the BT nodes used by your XML. If you omit the parameter, Humble loads its built-in list of all Nav2 BT nodes; if you set it, every node your XML uses must be in your list. [changed in Jazzy: Nav2 nodes are always loaded; list only custom plugins]

## config/bt_navigator.yaml (course)
```yaml
bt_navigator:
  ros__parameters:
    use_sim_time: True
    global_frame: map
    robot_base_frame: base_link
    odom_topic: /odom
    bt_loop_duration: 10
    default_server_timeout: 20
    default_nav_to_pose_bt_xml: "/home/user/ros2_ws/src/path_planner_server/config/behavior.xml"
    plugin_lib_names:
    - nav2_compute_path_to_pose_action_bt_node
    - nav2_compute_path_through_poses_action_bt_node
    - nav2_smooth_path_action_bt_node
    - nav2_follow_path_action_bt_node
    - nav2_spin_action_bt_node
    - nav2_wait_action_bt_node
    - nav2_back_up_action_bt_node
    - nav2_drive_on_heading_bt_node
    - nav2_clear_costmap_service_bt_node
    - nav2_is_stuck_condition_bt_node
    - nav2_goal_reached_condition_bt_node
    - nav2_goal_updated_condition_bt_node
    - nav2_globally_updated_goal_condition_bt_node
    - nav2_is_path_valid_condition_bt_node
    - nav2_initial_pose_received_condition_bt_node
    - nav2_reinitialize_global_localization_service_bt_node
    - nav2_rate_controller_bt_node
    - nav2_distance_controller_bt_node
    - nav2_speed_controller_bt_node
    - nav2_truncate_path_action_bt_node
    - nav2_truncate_path_local_action_bt_node
    - nav2_goal_updater_node_bt_node
    - nav2_recovery_node_bt_node
    - nav2_pipeline_sequence_bt_node
    - nav2_round_robin_node_bt_node
    - nav2_transform_available_condition_bt_node
    - nav2_time_expired_condition_bt_node
    - nav2_path_expiring_timer_condition
    - nav2_distance_traveled_condition_bt_node
    - nav2_single_trigger_bt_node
    - nav2_goal_updated_controller_bt_node
    - nav2_is_battery_low_condition_bt_node
    - nav2_navigate_through_poses_action_bt_node
    - nav2_navigate_to_pose_action_bt_node
    - nav2_remove_passed_goals_action_bt_node
    - nav2_planner_selector_bt_node
    - nav2_controller_selector_bt_node
    - nav2_goal_checker_selector_bt_node
    - nav2_controller_cancel_bt_node
    - nav2_path_longer_on_approach_bt_node
    - nav2_wait_cancel_bt_node
    - nav2_spin_cancel_bt_node
    - nav2_back_up_cancel_bt_node
    - nav2_drive_on_heading_cancel_bt_node
```
- Library names follow the node: `ComputePathToPose` → `nav2_compute_path_to_pose_action_bt_node`, `ClearEntireCostmap` → `nav2_clear_costmap_service_bt_node`, `RecoveryNode` → `nav2_recovery_node_bt_node`.
- The absolute XML path is how the course does it; prefer passing it from the launch file ([[nav2-bt-navigator]]).

## Pitfalls
- An XML node whose library is missing from the list → "node not registered" when bt_navigator configures.
- Copying this list into a Jazzy (or later) config → remove it: the Nav2 libraries load automatically there.
