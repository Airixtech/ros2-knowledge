---
id: nav2-single-launch
title: "Single navigation launch file with one lifecycle manager"
domain: nav2
area: bringup
distro: humble
tested: false
audience: dev
summary: "navigation.launch.py: map_server, amcl, planner, controller, behaviors and bt_navigator managed by ONE lifecycle_manager, for a full navigation system."
tags: [navigation.launch.py, lifecycle_manager, single launch, map_server, amcl, planner_server, controller_server, bt_navigator]
see: ["[[nav2-lifecycle-manager]]", "[[nav2-amcl-launch]]", "[[nav2-path-planning-launch]]", "[[core-launch-args-include]]"]
requires: [ros2-core]
version_notes:
  - "humble: Nav2's bringup_launch.py does the same with includes (localization + navigation) and adds smoothers and waypoint_follower — https://github.com/ros-navigation/navigation2/blob/humble/nav2_bringup/launch/bringup_launch.py (NAV2-V27)"
  - "lyrical: controller publishes TwistStamped cmd_vel by default (Kilted) — https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/migration_guides/jazzy/Jazzy.md (NAV2-V26)"
---
# Single navigation launch file with one lifecycle manager

**TL;DR** For learning, localization and path planning had their own lifecycle managers, which also helps to find which node causes a problem. A real navigation system uses **one** `nav2_lifecycle_manager` for **all** navigation nodes, started from a single launch file.

## launch/navigation.launch.py (package `path_planner_server`)
```python
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    controller_yaml = os.path.join(get_package_share_directory('path_planner_server'), 'config', 'controller.yaml')
    bt_navigator_yaml = os.path.join(get_package_share_directory('path_planner_server'), 'config', 'bt_navigator.yaml')
    planner_yaml = os.path.join(get_package_share_directory('path_planner_server'), 'config', 'planner_server.yaml')
    recovery_yaml = os.path.join(get_package_share_directory('path_planner_server'), 'config', 'recovery.yaml')
    nav2_yaml = os.path.join(get_package_share_directory('localization_server'), 'config', 'amcl_config.yaml')
    map_file = os.path.join(get_package_share_directory('map_server'), 'config', 'turtlebot_area.yaml')

    return LaunchDescription([
        Node(package='nav2_map_server', executable='map_server', name='map_server', output='screen',
             parameters=[{'use_sim_time': True}, {'yaml_filename': map_file}]),
        Node(package='nav2_amcl', executable='amcl', name='amcl', output='screen',
             parameters=[nav2_yaml]),
        Node(package='nav2_controller', executable='controller_server', name='controller_server',
             output='screen', parameters=[controller_yaml]),
        Node(package='nav2_planner', executable='planner_server', name='planner_server',
             output='screen', parameters=[planner_yaml]),
        Node(package='nav2_behaviors', executable='behavior_server', name='recoveries_server',
             parameters=[recovery_yaml], output='screen'),
        Node(package='nav2_bt_navigator', executable='bt_navigator', name='bt_navigator',
             output='screen', parameters=[bt_navigator_yaml]),
        Node(package='nav2_lifecycle_manager', executable='lifecycle_manager', name='lifecycle_manager',
             output='screen',
             parameters=[{'autostart': True},
                         {'node_names': ['map_server', 'amcl', 'controller_server', 'planner_server',
                                         'recoveries_server', 'bt_navigator']}])
    ])
```
- Include every navigation node: `map_server`, localization (`amcl`), planner, controller, `bt_navigator` and the behavior server.
- One manager with a generic name (`lifecycle_manager`) manages them all, each with its config file.
- `recovery.yaml` must start with `recoveries_server:` to match the node name ([[nav2-behavior-server]]).

## Pitfalls
- Order in `node_names` matters: map and localization first, so the planner finds `map → odom` when it activates.
- Leaving the old per-unit launch files running as well → duplicate nodes with the same names.
