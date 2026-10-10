---
id: nav2-path-planning-launch
title: "Path planning stack launch: planner, controller, behaviors, bt_navigator"
domain: nav2
area: planning-control
distro: humble
tested: false
audience: dev
summary: "pathplanner.launch.py: planner_server, controller_server, behavior_server, bt_navigator and lifecycle_manager_pathplanner on top of map_server + AMCL."
tags: [pathplanner.launch.py, planner_server, controller_server, behavior_server, bt_navigator, lifecycle_manager, path planning, Nav2 launch]
see: ["[[nav2-amcl-launch]]", "[[nav2-planner-server]]", "[[nav2-controller-server]]", "[[nav2-bt-navigator]]", "[[nav2-behavior-server]]", "[[core-nav2-overview]]"]
requires: [ros2-core]
version_notes:
  - "humble: Nav2's own navigation_launch.py also starts smoother_server, velocity_smoother and waypoint_follower (controller → cmd_vel_nav → velocity_smoother → cmd_vel); this minimal stack publishes cmd_vel from the controller — https://github.com/ros-navigation/navigation2/blob/humble/nav2_bringup/launch/navigation_launch.py (NAV2-V27)"
---
# Path planning stack launch: planner, controller, behaviors, bt_navigator

**TL;DR** Path planning needs a map and a localized robot first (`map_server` + `amcl`, [[nav2-amcl-launch]]). Then launch four servers and one lifecycle manager with a **different name** from the localization one.

## Nodes
`planner_server` (path, [[nav2-planner-server]]), `controller_server` (velocity commands, [[nav2-controller-server]]), `behavior_server` named `recoveries_server` (manages recovery actions in case of navigation failures, [[nav2-behavior-server]]), `bt_navigator` (high-level logic with behavior trees, [[nav2-bt-navigator]]) and a `nav2_lifecycle_manager` for the four.

## launch/pathplanner.launch.py (package `path_planner_server`)
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

    return LaunchDescription([
        Node(package='nav2_controller', executable='controller_server', name='controller_server',
             output='screen', parameters=[controller_yaml]),
        Node(package='nav2_planner', executable='planner_server', name='planner_server',
             output='screen', parameters=[planner_yaml]),
        Node(package='nav2_behaviors', executable='behavior_server', name='recoveries_server',
             parameters=[recovery_yaml], output='screen'),
        Node(package='nav2_bt_navigator', executable='bt_navigator', name='bt_navigator',
             output='screen', parameters=[bt_navigator_yaml]),
        Node(package='nav2_lifecycle_manager', executable='lifecycle_manager',
             name='lifecycle_manager_pathplanner', output='screen',
             parameters=[{'autostart': True},
                         {'node_names': ['planner_server', 'controller_server',
                                         'recoveries_server', 'bt_navigator']}])
    ])
```
The four YAML files go in `config/` and are installed from `setup.py`. Run order: localization launch → RViz → initial pose → `ros2 launch path_planner_server pathplanner.launch.py`.

## Check it in RViz
Add a `Path` display on `/plan` (Line Style **Billboards**, Line Width **0.05**), then click **Nav2 Goal** and a point on the map: a green line shows the path and the robot moves ([[nav2-rviz-displays]]).

## Pitfalls
- Two lifecycle managers with the same name → their services collide; give each a unique name ([[nav2-lifecycle-manager]]).
- `recovery.yaml` keyed `behavior_server:` while the node is `recoveries_server` → its parameters are ignored ([[nav2-behavior-server]]).
