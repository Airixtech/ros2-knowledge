---
id: nav2-cartographer-launch
type: reference
owner: equipo-ros2
updated: 2026-10-10
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "Launching cartographer_ros: cartographer_node + occupancy grid node"
domain: nav2
area: mapping
distro: humble
tested: false
audience: dev
summary: "cartographer.launch.py with cartographer_node (Lua config dir/basename) and cartographer_occupancy_grid_node (/map resolution, period); fixed topics."
tags: [cartographer_ros, cartographer_node, cartographer_occupancy_grid_node, launch, SLAM, configuration_basename]
see: ["[[nav2-cartographer-lua]]", "[[nav2-map-saver]]", "[[core-pkg-ament-python]]", "[[core-launch-basics]]", "[[core-ros-args]]"]
requires: [ros2-core]
version_notes:
  - "jazzy/lyrical: same executables and arguments (cartographer_ros ros2 fork released) — https://github.com/ros2/cartographer_ros/blob/ros2/cartographer_ros/CMakeLists.txt (NAV2-V37)"
---
# Launching cartographer_ros: cartographer_node + occupancy grid node

**TL;DR** Two nodes from `cartographer_ros`: `cartographer_node` (SLAM, reads a Lua file) and `cartographer_occupancy_grid_node` (turns submaps into `/map`). Pass the Lua location as arguments, not parameters.

## Node specs
| Node | Executable | Parameters | Arguments |
|---|---|---|---|
| `cartographer_node` | `cartographer_node` | `use_sim_time`: boolean, whether the node must synchronize its time with the simulation | `-configuration_directory` (the directory where to find the configuration files), `-configuration_basename` (config file name) |
| `occupancy_grid_node` | `cartographer_occupancy_grid_node` | `use_sim_time` | `-resolution` (meters per grid cell of the map), `-publish_period_sec` (how frequently, in seconds, the map is published in `/map`) |

## cartographer.launch.py (package `cartographer_slam`)
```python
import os
from launch import LaunchDescription
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node


def generate_launch_description():
    cartographer_config_dir = os.path.join(get_package_share_directory('cartographer_slam'), 'config')
    configuration_basename = 'cartographer.lua'

    return LaunchDescription([
        Node(
            package='cartographer_ros',
            executable='cartographer_node',
            name='cartographer_node',
            output='screen',
            parameters=[{'use_sim_time': True}],
            arguments=['-configuration_directory', cartographer_config_dir,
                       '-configuration_basename', configuration_basename]),
        Node(
            package='cartographer_ros',
            executable='cartographer_occupancy_grid_node',
            output='screen',
            name='occupancy_grid_node',
            parameters=[{'use_sim_time': True}],
            arguments=['-resolution', '0.05', '-publish_period_sec', '1.0']),
    ])
```
- `os.path.join` concatenates paths (module `os`); `get_package_share_directory` finds the installed share path of a package (module `ament_index_python.packages`).
- Install `launch/` and `config/` from `setup.py` (`data_files` with `glob`, plus `import os` and `from glob import glob`) ([[core-pkg-ament-python]]):
```python
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*')),
```

## Build and run
```bash
cd ~/ros2_ws                      # always build from the workspace root, never elsewhere
colcon build --packages-select cartographer_slam
source ~/ros2_ws/install/setup.bash
ros2 launch cartographer_slam cartographer.launch.py
ros2 run teleop_twist_keyboard teleop_twist_keyboard   # other terminal: drive around
```
Watch the map in RViz ([[nav2-rviz-displays]]).

## Fixed input topics
`cartographer_node` subscribes to `/scan`, `/odom` and `/imu`; these names **cannot be configured** in Lua. Other names → remap in the launch ([[core-ros-args]]).

## Pitfalls
- Lua changes only take effect after `colcon build` (the file is read from `install/…/share`).
