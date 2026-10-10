---
id: nav2-amcl-launch
title: "Launching AMCL: map_server + amcl + lifecycle manager, amcl_config.yaml"
domain: nav2
area: localization
distro: humble
tested: false
audience: dev
summary: "localization.launch.py (map_server, amcl, lifecycle_manager_localization) and a complete amcl_config.yaml for a differential robot."
tags: [AMCL, nav2_amcl, amcl_config.yaml, localization.launch.py, lifecycle_manager, map_server, DifferentialMotionModel]
see: ["[[nav2-amcl-concepts]]", "[[nav2-amcl-params-filter]]", "[[nav2-map-server]]", "[[nav2-initial-pose-config]]", "[[core-param-yaml-cli]]"]
requires: [ros2-core]
version_notes:
  - "humble: robot_model_type takes plugin names (nav2_amcl::DifferentialMotionModel / nav2_amcl::OmniMotionModel) — https://github.com/ros-navigation/navigation2/blob/humble/nav2_amcl/src/amcl_node.cpp (NAV2-V08)"
---
# Launching AMCL: map_server + amcl + lifecycle manager, amcl_config.yaml

**TL;DR** Three nodes: `map_server`, `amcl` (pkg `nav2_amcl`, one YAML with all its parameters) and a `lifecycle_manager` that activates both.

## launch/localization.launch.py (package `localization_server`)
```python
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    nav2_yaml = os.path.join(get_package_share_directory('localization_server'), 'config', 'amcl_config.yaml')
    map_file = os.path.join(get_package_share_directory('map_server'), 'config', 'turtlebot_area.yaml')

    return LaunchDescription([
        Node(package='nav2_map_server', executable='map_server', name='map_server', output='screen',
             parameters=[{'use_sim_time': True}, {'yaml_filename': map_file}]),
        Node(package='nav2_amcl', executable='amcl', name='amcl', output='screen',
             parameters=[nav2_yaml]),
        Node(package='nav2_lifecycle_manager', executable='lifecycle_manager',
             name='lifecycle_manager_localization', output='screen',
             parameters=[{'use_sim_time': True}, {'autostart': True},
                         {'node_names': ['map_server', 'amcl']}])
    ])
```

## config/amcl_config.yaml
```yaml
amcl:
  ros__parameters:
    use_sim_time: True
    alpha1: 0.2
    alpha2: 0.2
    alpha3: 0.2
    alpha4: 0.2
    alpha5: 0.2
    base_frame_id: "base_footprint"
    beam_skip_distance: 0.5
    beam_skip_error_threshold: 0.9
    beam_skip_threshold: 0.3
    do_beamskip: false
    global_frame_id: "map"
    lambda_short: 0.1
    laser_likelihood_max_dist: 2.0
    laser_max_range: 100.0
    laser_min_range: -1.0
    laser_model_type: "likelihood_field"
    max_beams: 60
    max_particles: 8000
    min_particles: 200
    odom_frame_id: "odom"
    pf_err: 0.05
    pf_z: 0.99
    recovery_alpha_fast: 0.0
    recovery_alpha_slow: 0.0
    resample_interval: 1
    robot_model_type: "nav2_amcl::DifferentialMotionModel"
    save_pose_rate: 0.5
    sigma_hit: 0.2
    tf_broadcast: true
    transform_tolerance: 1.0
    update_min_a: 0.2
    update_min_d: 0.25
    z_hit: 0.5
    z_max: 0.05
    z_rand: 0.5
    z_short: 0.05
```
Keys: [[nav2-amcl-params-filter]], [[nav2-amcl-params-models]]. Install `config/` and `launch/` in `setup.py`, then `colcon build --packages-select localization_server`, source, and `ros2 launch localization_server localization.launch.py`.

## Expected output
```
[amcl-2] [WARN] [1632242660.692356589] [amcl]: AMCL cannot publish a pose or update the transform. Please set the initial pose...
```
This message is correct: AMCL waits until somebody gives the initial pose, then tracks the robot as it moves. Provide it from RViz ([[nav2-rviz-displays]]), the config file ([[nav2-initial-pose-config]]) or a node ([[nav2-initial-pose-publisher]]).

## Pitfalls
- The YAML top key must equal the node name (`amcl:`), or the file is silently ignored ([[core-param-yaml-cli]]).
- `base_frame_id` must exist in your TF tree (`base_footprint` on TurtleBot3).
