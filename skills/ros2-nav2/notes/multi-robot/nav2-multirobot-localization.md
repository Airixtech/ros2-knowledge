---
id: nav2-multirobot-localization
title: "Multi-robot AMCL: namespaced nodes, per-robot config, bond_timeout"
domain: nav2
area: multi-robot
distro: humble
tested: false
audience: dev
summary: "multi_localization.launch.py: one map_server, one amcl per namespace with its own YAML (frames, scan_topic, map_topic /map), lifecycle manager with full names."
tags: [multi-robot, AMCL, namespace, tb3_0/amcl, multi_localization.launch.py, map_topic, scan_topic, bond_timeout, topic_name, frame_id]
see: ["[[nav2-amcl-launch]]", "[[nav2-multirobot-namespaces]]", "[[nav2-multirobot-rviz]]", "[[nav2-lifecycle-manager]]"]
requires: [ros2-core]
version_notes:
  - "humble: flat YAML keys like tb3_0/amcl: are valid (rcl adds the leading '/') — https://github.com/ros2/rcl/blob/humble/rcl_yaml_param_parser/src/parse.c (NAV2-V39)"
  - "humble: bond_timeout 0.0 disables bonds (no crash detection); why the course needs it is [verify] — https://github.com/ros-navigation/navigation2/blob/humble/nav2_lifecycle_manager/src/lifecycle_manager.cpp (NAV2-V23)"
---
# Multi-robot AMCL: namespaced nodes, per-robot config, bond_timeout

**TL;DR** One `map_server` for everybody and one `amcl` per robot, launched with `namespace='tb3_0'`. The namespace renames the node (`/tb3_0/amcl`), its topics and services, but **not the frames in its config file**: give each robot its own YAML.

## Step 1. Namespaced amcl nodes
```python
Node(namespace='tb3_0', package='nav2_amcl', executable='amcl', name='amcl', output='screen', parameters=[tb3_0_config]),
```
A namespace is a unique identifier below which all the robot's topics, TF frames and sensor data live; it is used massively in swarms of identical robots. The node above is named `tb3_0/amcl`, not `amcl`.

## Step 2. One config per robot
Copy `amcl_config.yaml` ([[nav2-amcl-launch]]) to `tb3_0_amcl_config.yaml` and `tb3_1_amcl_config.yaml` and change:
1. The first line: the **full node name**.
2. Every frame gets the namespace, except `global_frame_id`: there is a single global frame (the map) for all robots.
3. Topics are renamed by the launch namespace; frames are not.
4. Force `map_topic` to `/map`: without the `/` it becomes `tb3_0/map`, which no map server publishes.
```yaml
tb3_0/amcl:
  ros__parameters:
    # … all keys of amcl_config.yaml, with these values:
    base_frame_id: "tb3_0/base_footprint"
    odom_frame_id: "tb3_0/odom"
    global_frame_id: "map"
    scan_topic: "/tb3_0/scan"
    map_topic: "/map"
    set_initial_pose: true
    initial_pose:
      x: 0.0
      y: 0.0
      yaw: 0.0
```
`tb3_1` is identical with `tb3_1/…` frames, `/tb3_1/scan` and its own start pose (`y: -0.5`). Activate `set_initial_pose` only when you have a proper initial pose.

## Step 3–4. Lifecycle manager and map server
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
- The map server gets explicit `topic_name` and `frame_id` (both `map`) and the clean two-robot map.

## Step 5. Run
Build, source and `ros2 launch localization_server multi_localization.launch.py`: both AMCL nodes wait for their initial pose. Set them in RViz ([[nav2-multirobot-rviz]]). Then `ros2 run tf2_tools view_frames`: each AMCL publishes `map → tb3_X/odom`, joining both trees under `map`.

## Pitfalls
- Simulated robots **drift**: relaunch the simulation before the 2D Pose Estimate, or the start poses are off.
- `map_topic: map` (relative) → AMCL waits forever for `/tb3_0/map`.
