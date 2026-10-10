---
id: nav2-migration-checklist
title: "Nav2 migration checklist: porting a Humble course setup"
domain: nav2
area: migration
distro: humble
tested: false
audience: dev
summary: "Step-by-step checklist to port this course's Nav2 packages (YAML, BT XML, launch, simulation) from Humble to Jazzy or Lyrical, plus Humble fixes."
tags: [migration, checklist, Nav2, Humble, Jazzy, Lyrical, YAML, BT XML, launch]
see: ["[[nav2-humble-to-jazzy]]", "[[nav2-jazzy-to-lyrical]]", "[[core-migration-checklist]]"]
requires: [ros2-core]
version_notes: []
---
# Nav2 migration checklist: porting a Humble course setup

**TL;DR** First fix what is wrong even in Humble, then apply the Jazzy changes, then the Lyrical ones. Test after each block: `colcon build`, launch, check `Managed nodes are active`, set the initial pose, send a goal.

## 0. Fix in Humble first (course configs)
- [ ] Behavior server YAML key = launched node name (`recoveries_server:` / `tb3_0/recoveries_server:`) (NAV2-V01, [[nav2-behavior-server]]).
- [ ] Behavior server: `global_frame: odom`, `transform_tolerance` (not `transform_timeout`), no `local_frame` (NAV2-V02).
- [ ] AMCL `robot_model_type: "nav2_amcl::DifferentialMotionModel"` (NAV2-V08).
- [ ] Multi-robot: `odom_topic: odom` in bt_navigator (NAV2-V11); drop `cmd_vel_topic` and `enable_groot_monitoring` (no effect, NAV2-V41, NAV2-V10).
- [ ] Goals from code: heading in the orientation quaternion (NAV2-V14).

## 1. Humble → Jazzy ([[nav2-humble-to-jazzy]])
- [ ] Ubuntu 24.04 and generic ROS 2 changes ([[core-migration-checklist]]).
- [ ] Plugin names to `::` in planner, behavior and navigator configs (NAV2-V17).
- [ ] `progress_checker_plugin` → `progress_checker_plugins: [...]` (NAV2-V18).
- [ ] Remove the Nav2 entries of `plugin_lib_names`; keep only custom BT plugins (NAV2-V19).
- [ ] BT XML: `<root BTCPP_format="4" main_tree_to_execute="MainTree">`; run BehaviorTree.CPP's `convert_v3_to_v4.py`; check SubTrees (NAV2-V20).
- [ ] Optionally replace absolute XML paths with `$(find-pkg-share pkg)/…` in the param file (NAV2-V21).
- [ ] Behavior server: `local_frame: odom`, `global_frame: map` and the local/global costmap topics (NAV2-V02).
- [ ] Simulation: Gazebo Harmonic, `ros_gz_sim create` instead of `spawn_entity.py`, bridge the topics ([[core-gazebo-bridge]], NAV2-V28).

## 2. Jazzy → Lyrical ([[nav2-jazzy-to-lyrical]])
- [ ] Robot base subscribes to `TwistStamped` on `cmd_vel`, or set `enable_stamped_cmd_vel: false` in every Nav2 node that publishes or subscribes velocity (NAV2-V26).
- [ ] Move a costmap-level `map_topic` into `static_layer` (NAV2-V24).
- [ ] Multi-robot: switch per-robot absolute topics to relative ones and use one params file with launch namespaces (NAV2-V25).
- [ ] Custom C++ plugins or servers: migrate to `nav2::LifecycleNode` / `nav2_ros_common` factories (NAV2-V40).
- [ ] Remove explicit `bond_heartbeat_period: 0.1` or set the new default 0.25 (NAV2-V23).

## Verify
- [ ] `ros2 param get /bt_navigator default_nav_to_pose_bt_xml` points to an existing file.
- [ ] `ros2 topic info /cmd_vel -v`: publisher and subscriber agree on the message type.
- [ ] Recoveries actually spin/back up when the robot is blocked (proves the behavior server YAML loads).
