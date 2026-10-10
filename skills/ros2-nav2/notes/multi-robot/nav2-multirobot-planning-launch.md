---
id: nav2-multirobot-planning-launch
title: "Multi-robot path planning launch and lifecycle manager"
domain: nav2
area: multi-robot
distro: humble
tested: false
audience: dev
summary: "multi_pathplanner.launch.py: planner, controller, behaviors, bt_navigator per namespace; one lifecycle manager with full node names."
tags: [multi-robot, multi_pathplanner.launch.py, namespace, lifecycle_manager, node_names, bond_timeout, goal_pose, Nav2 multi-robot]
see: ["[[nav2-path-planning-launch]]", "[[nav2-multirobot-planner-controller-config]]", "[[nav2-multirobot-bt-behavior-config]]", "[[nav2-multirobot-rviz]]"]
requires: [ros2-core]
version_notes:
  - "humble: nav2_bringup ships unique_multi_tb3_simulation_launch.py and cloned_multi_tb3_simulation_launch.py (one Nav2 stack and lifecycle manager per namespace); Kilted made params and RViz namespace-ready — https://github.com/ros-navigation/navigation2/tree/humble/nav2_bringup/launch (NAV2-V25)"
  - "humble: bond_timeout 0.0 disables bonds — https://github.com/ros-navigation/navigation2/blob/humble/nav2_lifecycle_manager/src/lifecycle_manager.cpp (NAV2-V23)"
---
# Multi-robot path planning launch and lifecycle manager

**TL;DR** Launch two of each path planning node (`planner_server`, `controller_server`, `recoveries_server`, `bt_navigator`), each with `namespace=` and its own config, and one lifecycle manager that lists all of them by **full name**.

## launch/multi_pathplanner.launch.py
Same nodes as [[nav2-path-planning-launch]], built in a loop (the course writes the eight `Node(...)` out one by one; the result is identical):
```python
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

ROBOTS = ['tb3_0', 'tb3_1']


def generate_launch_description():
    config = os.path.join(get_package_share_directory('path_planner_server'), 'config')
    nodes, managed = [], []
    for ns in ROBOTS:
        nodes += [
            Node(namespace=ns, package='nav2_controller', executable='controller_server',
                 name='controller_server', output='screen',
                 parameters=[os.path.join(config, f'{ns}_controller.yaml')]),
            Node(namespace=ns, package='nav2_planner', executable='planner_server',
                 name='planner_server', output='screen',
                 parameters=[os.path.join(config, f'{ns}_planner_server.yaml')]),
            Node(namespace=ns, package='nav2_behaviors', executable='behavior_server',
                 name='recoveries_server', output='screen',
                 parameters=[os.path.join(config, f'{ns}_recovery.yaml')]),
            Node(namespace=ns, package='nav2_bt_navigator', executable='bt_navigator',
                 name='bt_navigator', output='screen',
                 parameters=[os.path.join(config, f'{ns}_bt_navigator.yaml')]),
        ]
        managed += [f'{ns}/controller_server', f'{ns}/planner_server',
                    f'{ns}/recoveries_server', f'{ns}/bt_navigator']
    nodes.append(Node(package='nav2_lifecycle_manager', executable='lifecycle_manager',
                      name='lifecycle_manager', output='screen',
                      parameters=[{'autostart': True}, {'bond_timeout': 0.0},
                                  {'node_names': managed}]))
    return LaunchDescription(nodes)
```
Nodes become `tb3_0/planner_server`…; frames are edited per robot ([[nav2-multirobot-planner-controller-config]], [[nav2-multirobot-bt-behavior-config]]). `bond_timeout: 0.0` (course workaround) disables crash detection.

## Run
```bash
cd ~/ros2_ws
source install/setup.bash
colcon build
source install/setup.bash
ros2 launch localization_server multi_localization.launch.py      # terminal 1
ros2 launch path_planner_server multi_pathplanner.launch.py       # terminal 2
```
Final message telling you that everything launched correctly:
```
[lifecycle_manager-9] [INFO] [1701423537.147284432] [lifecycle_manager]: Managed nodes are active
```
 Then RViz ([[nav2-multirobot-rviz]]): set the **2D Goal Pose** tool topic to `/tb3_0/goal_pose`, send a goal, then `/tb3_1/goal_pose` for the other robot. Each robot avoids static and dynamic obstacles, including the other robot.

## Pitfalls
- A short name in `node_names` (`planner_server` instead of `tb3_0/planner_server`) → that node never activates.
