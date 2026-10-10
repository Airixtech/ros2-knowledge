---
id: nav2-map-server
title: "Serving a saved map: map_server + lifecycle manager launch"
domain: nav2
area: mapping
distro: humble
tested: false
audience: dev
summary: "nav2_map_server.launch.py: map_server (yaml_filename, use_sim_time, topic_name, frame_id) activated by a lifecycle_manager; /map QoS."
tags: [map_server, nav2_map_server, yaml_filename, lifecycle_manager, launch, /map, transient_local]
see: ["[[nav2-map-saver]]", "[[nav2-lifecycle-manager]]", "[[nav2-amcl-launch]]", "[[core-qos-usage]]", "[[core-pkg-ament-python]]"]
requires: [ros2-core]
version_notes:
  - "humble: map_server params yaml_filename, topic_name ('map'), frame_id ('map'); /map is published RELIABLE + TRANSIENT_LOCAL — https://github.com/ros-navigation/navigation2/blob/humble/nav2_map_server/src/map_server/map_server.cpp (NAV2-V36)"
  - "jazzy: Nav2's own launch files take the map path from a 'map' launch argument that overrides yaml_filename (Iron); a custom launch like this one is unchanged — https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/migration_guides/Humble.md (NAV2-V36)"
---
# Serving a saved map: map_server + lifecycle manager launch

**TL;DR** After saving the map you no longer need Cartographer. `map_server` loads the `.yaml` and publishes `/map` for AMCL and the planner. It is a lifecycle node, so it publishes nothing until a `lifecycle_manager` activates it.

## Node specs
| Node | Package / executable | Parameters |
|---|---|---|
| `map_server` | `nav2_map_server` / `map_server` | `use_sim_time` (boolean: whether it must synchronize its time with the simulation), `yaml_filename` (**complete path** to the map `.yaml`); optional `topic_name` and `frame_id` (both default `map`) |
| `lifecycle_manager_mapper` | `nav2_lifecycle_manager` / `lifecycle_manager` | `use_sim_time`, `autostart` (configure + activate at launch), `node_names` (nodes it manages; here only `map_server`) |

## launch/nav2_map_server.launch.py (package `map_server`, map files in its `config/`)
```python
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    map_file = os.path.join(get_package_share_directory('map_server'), 'config', 'turtlebot_area.yaml')

    return LaunchDescription([
        Node(
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            output='screen',
            parameters=[{'use_sim_time': True},
                        {'yaml_filename': map_file}]),
        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_mapper',
            output='screen',
            parameters=[{'use_sim_time': True},
                        {'autostart': True},
                        {'node_names': ['map_server']}])
    ])
```
Install `launch/` and `config/` in `setup.py` as for Cartographer ([[core-pkg-ament-python]]), build, source, then:
```bash
ros2 launch map_server nav2_map_server.launch.py
```

## Visualize
RViz Map display on `/map` with Durability **Transient Local** (the map is published once, latched) ([[core-qos-usage]], [[nav2-rviz-displays]]).

## Pitfalls
- Relative `yaml_filename` → "Failed to load map"; build the absolute path with `get_package_share_directory`.
- Map files copied into `src/…/config` but not rebuilt → the installed copy is old or missing.
- Forgot the lifecycle manager (or `autostart: False`) → the node stays `unconfigured` and `/map` never appears ([[nav2-lifecycle-manager]]).
