---
id: nav2-multirobot-localization
type: reference
owner: equipo-ros2
updated: 2026-10-10
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "Multi-robot localization launch: namespaced AMCL nodes, shared map server, bond_timeout"
domain: nav2
area: multi-robot
distro: humble
tested: false
audience: dev
summary: "multi_localization.launch.py: one map_server, one namespaced amcl per robot, lifecycle manager with full node names and bond_timeout."
tags: [multi-robot, AMCL, namespace, tb3_0/amcl, multi_localization.launch.py, map_topic, scan_topic, bond_timeout, topic_name, frame_id]
see: ["[[nav2-multirobot-amcl-config]]", "[[nav2-amcl-launch]]", "[[nav2-multirobot-namespaces]]", "[[nav2-multirobot-rviz]]", "[[nav2-lifecycle-manager]]"]
requires: [ros2-core]
version_notes:
  - "humble: bond_timeout 0.0 disables bonds (no crash detection); why the course needs it is [verify] — https://github.com/ros-navigation/navigation2/blob/humble/nav2_lifecycle_manager/src/lifecycle_manager.cpp (NAV2-V23)"
---
# Multi-robot localization launch: namespaced AMCL nodes, shared map server, bond_timeout

**TL;DR** One `map_server` for everybody and one `amcl` per robot, launched with `namespace='tb3_0'` / `'tb3_1'` and its own YAML ([[nav2-multirobot-amcl-config]]). A namespace is a unique identifier below which all the topics, TF frames and sensor data of a robot live; it is used massively in swarms of identical robots. The node is then named `tb3_0/amcl`, not `amcl`.

## launch/multi_localization.launch.py (package `localization_server`)
```python
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    tb3_0_nav2_yaml = os.path.join(get_package_share_directory('localization_server'), 'config', 'tb3_0_amcl_config.yaml')
    tb3_1_nav2_yaml = os.path.join(get_package_share_directory('localization_server'), 'config', 'tb3_1_amcl_config.yaml')
    map_file = os.path.join(get_package_share_directory('map_server'), 'config', 'turtlebot_area_two_robots_clean.yaml')

    return LaunchDescription([
        Node(package='nav2_map_server', executable='map_server', name='map_server', output='screen',
             parameters=[{'use_sim_time': True}, {'topic_name': "map"}, {'frame_id': "map"}, {'yaml_filename': map_file}]),
        Node(namespace='tb3_0', package='nav2_amcl', executable='amcl', name='amcl', output='screen', parameters=[tb3_0_nav2_yaml]),
        Node(namespace='tb3_1', package='nav2_amcl', executable='amcl', name='amcl', output='screen', parameters=[tb3_1_nav2_yaml]),
        Node(package='nav2_lifecycle_manager', executable='lifecycle_manager', name='lifecycle_manager_localization',
             output='screen',
             parameters=[{'use_sim_time': True}, {'autostart': True}, {'bond_timeout': 0.0},
                         {'node_names': ['map_server', 'tb3_0/amcl', 'tb3_1/amcl']}])
    ])
```
- `node_names` needs the **full names** with namespaces.
- `{'bond_timeout': 0.0}` was added in the course to prevent launch errors; it disables the bonds, so crashes are no longer detected ([[nav2-lifecycle-manager]]).
- The map server gets explicit `topic_name` and `frame_id` (both `map`) and `map_file` points to the clean two-robot map.

## Run
Build, source, `ros2 launch localization_server multi_localization.launch.py`: both AMCL nodes wait for their initial pose; set them in RViz ([[nav2-multirobot-rviz]]). `ros2 run tf2_tools view_frames` then shows `map → tb3_0/odom` and `map → tb3_1/odom`.

## Pitfalls
- Simulated robots **drift**: relaunch the simulation before the 2D Pose Estimate, or the start poses are off.
