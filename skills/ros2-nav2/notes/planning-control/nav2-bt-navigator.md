---
id: nav2-bt-navigator
title: "bt_navigator: role, launch and parameters"
domain: nav2
area: planning-control
distro: humble
tested: false
audience: dev
summary: "bt_navigator coordinates planner, controller and recoveries through a behavior tree; launch, parameters (default_nav_to_pose_bt_xml, bt_loop_duration…), XML path."
tags: [bt_navigator, nav2_bt_navigator, NavigateToPose, behavior tree, default_nav_to_pose_bt_xml, bt_loop_duration, default_server_timeout, plugin_lib_names, Groot]
see: ["[[nav2-behavior-tree-xml]]", "[[nav2-bt-plugin-libs]]", "[[nav2-planner-server]]", "[[nav2-controller-server]]", "[[nav2-behavior-server]]"]
requires: [ros2-core]
version_notes:
  - "humble: no substitutions in param files, so default_nav_to_pose_bt_xml needs an absolute path; jazzy: $(find-pkg-share pkg)/… is allowed — https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/migration_guides/iron/Iron.md (NAV2-V21)"
  - "humble: live Groot monitoring was removed (enable_groot_monitoring has no effect); lyrical: Groot 2 monitoring, off by default (Kilted) — https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/migration_guides/galactic/Galactic.md (NAV2-V10)"
  - "jazzy: BT.CPP 4.5 and a navigators parameter; plugin_lib_names only for custom nodes — https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/migration_guides/iron/Iron.md (NAV2-V19, NAV2-V20)"
---
# bt_navigator: role, launch and parameters

**TL;DR** `bt_navigator` is the navigation coordinator: it asks the planner for a path, calls the controller to follow it and triggers recovery behaviors, all as defined by a **behavior tree XML** ([[nav2-behavior-tree-xml]]). It serves the `navigate_to_pose` and `navigate_through_poses` actions and listens to `goal_pose`.

Official definition: *the BT Navigator implements the NavigateToPose task interface. It is a Behavior Tree-based implementation of navigation that is intended to allow for flexibility in the navigation task and provide a way to easily specify complex robot behaviors, including recovery.*

## Launch
```python
        Node(package='nav2_bt_navigator', executable='bt_navigator', name='bt_navigator',
             output='screen', parameters=[bt_navigator_yaml]),
```
The complete `bt_navigator.yaml` of the course (with the Humble `plugin_lib_names` list): [[nav2-bt-plugin-libs]].

## Parameters
| Parameter | Default | Meaning |
|---|---|---|
| `default_nav_to_pose_bt_xml` | Nav2's `navigate_to_pose_w_replanning_and_recovery.xml` | full path to the BT XML used to navigate to a pose |
| `default_nav_through_poses_bt_xml` | Nav2's default | full path to the BT XML used to navigate through poses |
| `bt_loop_duration` | 10 ms | duration of each BT iteration (tick) |
| `default_server_timeout` | 20 ms | how long BT action nodes wait for their servers |
| `global_frame` | `map` | global reference frame |
| `robot_base_frame` | `base_link` | robot base frame |
| `odom_topic` | `odom` | odometry topic (used for the robot speed) |
| `plugin_lib_names` | all Nav2 BT libraries | BT node shared libraries to load |
| `transform_tolerance` | 0.1 s | TF tolerance |

## Avoid absolute paths in Humble
Humble cannot use `$(find-pkg-share …)` in a param file. Instead of `/home/user/ros2_ws/src/…/behavior.xml`, install the XML and pass the path from the launch file (later parameters override the YAML):
```python
bt_xml = os.path.join(get_package_share_directory('path_planner_server'), 'config', 'behavior.xml')
Node(package='nav2_bt_navigator', executable='bt_navigator', name='bt_navigator', output='screen',
     parameters=[bt_navigator_yaml, {'default_nav_to_pose_bt_xml': bt_xml}])
```

## Pitfalls
- XML path that does not exist → bt_navigator fails to configure and the lifecycle manager aborts the startup.
- A BT node used in the XML but missing from `plugin_lib_names` → "node not registered" error ([[nav2-bt-plugin-libs]]).
- Customizing behavior trees in depth: [Nav2 behavior trees](https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/getting_started/nav2_behavior_trees/index.md).
