---
id: nav2-multirobot-bt-behavior-config
title: "Per-robot bt_navigator and behavior_server YAML, Groot port collision"
domain: nav2
area: multi-robot
distro: humble
tested: false
audience: dev
summary: "Per-robot bt_navigator.yaml and recovery.yaml: namespaced node keys, tb3_0 frames, odom_topic, XML path; the Groot setting and the behavior_server key bug."
tags: [multi-robot, bt_navigator, behavior_server, recoveries_server, tb3_0_bt_navigator.yaml, tb3_0_recovery.yaml, odom_topic, enable_groot_monitoring]
see: ["[[nav2-bt-navigator]]", "[[nav2-bt-plugin-libs]]", "[[nav2-behavior-server]]", "[[nav2-multirobot-planning-launch]]"]
requires: [ros2-core]
version_notes:
  - "humble: odom_topic tb3_0/odom inside namespace tb3_0 resolves to /tb3_0/tb3_0/odom — https://github.com/ros-navigation/navigation2/blob/humble/nav2_bt_navigator/src/bt_navigator.cpp (NAV2-V11)"
  - "humble: no live Groot monitoring, so enable_groot_monitoring has no effect; lyrical: Groot 2 monitoring off by default (Kilted); jazzy release [verify] — https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/migration_guides/galactic/Galactic.md (NAV2-V10)"
  - "humble: YAML key tb3_0/behavior_server: does not match node tb3_0/recoveries_server, so the file is ignored — https://github.com/ros-navigation/navigation2/blob/humble/nav2_behaviors/src/behavior_server.cpp (NAV2-V01)"
---
# Per-robot bt_navigator and behavior_server YAML, Groot port collision

**TL;DR** Same rules as the other per-robot files ([[nav2-multirobot-planner-controller-config]]): full node name as first key, namespaced frames. Two course details need fixes in Humble: the behavior server key and `odom_topic`.

## tb3_0_bt_navigator.yaml
```yaml
tb3_0/bt_navigator:
  ros__parameters:
    use_sim_time: True
    global_frame: map
    robot_base_frame: tb3_0/base_link
    odom_topic: odom                 # course: tb3_0/odom → /tb3_0/tb3_0/odom
    bt_loop_duration: 10
    default_server_timeout: 20
    default_nav_to_pose_bt_xml: "/home/user/ros2_ws/src/path_planner_server/config/behavior.xml"
    enable_groot_monitoring: false   # course setting; no effect in Humble
    plugin_lib_names:
    - nav2_compute_path_to_pose_action_bt_node
    # … the same list as the single-robot file ([[nav2-bt-plugin-libs]])
```
- `default_nav_to_pose_bt_xml` must be an **absolute path** in Humble (adapt it to your folders) or be passed from the launch file ([[nav2-bt-navigator]]). Both robots can use the same `behavior.xml`.
- Groot: the course disables Groot monitoring because two `bt_navigator`s would collide on the same Groot (ZMQ) port, as reported in navigation2 issue 2386. That happened in Galactic: Humble has no live Groot monitoring, so the parameter (missing from the official docs) does nothing.

## tb3_0_recovery.yaml
```yaml
tb3_0/recoveries_server:          # course: tb3_0/behavior_server: (ignored, see below)
  ros__parameters:
    costmap_topic: local_costmap/costmap_raw
    footprint_topic: local_costmap/published_footprint
    cycle_frequency: 10.0
    behavior_plugins: ["spin", "backup", "wait"]
    spin:
      plugin: "nav2_behaviors/Spin"
    backup:
      plugin: "nav2_behaviors/BackUp"
    wait:
      plugin: "nav2_behaviors/Wait"
    global_frame: tb3_0/odom
    robot_base_frame: tb3_0/base_link
    transform_tolerance: 0.1        # course: transform_timeout
    use_sim_time: true
    simulate_ahead_time: 2.0
    max_rotational_vel: 1.0
    min_rotational_vel: 0.4
    rotational_acc_lim: 3.2
```
With the course key `tb3_0/behavior_server:` the node `tb3_0/recoveries_server` ignores the file and keeps the default frames `odom` and `base_link`, which do not exist for namespaced robots: spin and backup fail their TF lookups ([[nav2-behavior-server]]).

## Pitfalls
- Relative topics inside a namespaced node must not repeat the namespace (`odom`, not `tb3_0/odom`).
