---
id: core-robot-state-publisher
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "robot_state_publisher & xacro in launch"
domain: core
area: tools
distro: humble
tested: false
audience: dev
summary: "What robot_state_publisher publishes, running it from CLI, canonical xacro→robot_description launch with ParameterValue."
tags: [robot_state_publisher, robot_description, xacro, ParameterValue, joint_state_publisher_gui]
see: ["[[core-urdf-basics]]", "[[core-xacro]]", "[[core-launch-args-include]]", "[[core-ros2-control-overview]]"]
requires: []
version_notes:
  - "lyrical: robot_state_publisher can read robot_description from a topic — https://docs.ros.org/en/rolling/Releases/Release-Lyrical-Luth.html (V19)"
  - "jazzy: ros2_control's controller_manager reads /robot_description (topic) from RSP — https://github.com/ros-controls/ros2_control/blob/jazzy/doc/migration.rst (V60)"
---
# robot_state_publisher & xacro in launch

**TL;DR** RSP reads the `robot_description` parameter. It publishes `/robot_description` (latched), the fixed joints on `/tf_static`, and the movable joints (from `/joint_states`) on `/tf`. It does NOT publish `odom→base_link` or `map→odom`.

## CLI
```bash
ros2 run robot_state_publisher robot_state_publisher --ros-args -p robot_description:="$(xacro robot.urdf.xacro)"
ros2 run joint_state_publisher_gui joint_state_publisher_gui     # sliders for movable joints (no real HW)
```

## Launch (canonical)
```python
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    xacro_file = PathJoinSubstitution(
        [FindPackageShare('my_robot_description'), 'urdf', 'robot.urdf.xacro'])
    robot_description = ParameterValue(Command(['xacro ', xacro_file]), value_type=str)  # ParameterValue avoids YAML-parsing errors
    use_sim_time = LaunchConfiguration('use_sim_time')
    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        Node(package='robot_state_publisher', executable='robot_state_publisher',
             parameters=[{'robot_description': robot_description, 'use_sim_time': use_sim_time}]),
        Node(package='joint_state_publisher_gui', executable='joint_state_publisher_gui'),
        Node(package='rviz2', executable='rviz2'),
    ])
```
- Without `ParameterValue(..., value_type=str)`, launch tries to parse the URDF text as YAML and fails.
- Install the `urdf/`, `meshes/` and `rviz/` dirs in share ([[core-pkg-ament-python]]). For a plain URDF file, put `open(path).read()` in the param, or keep the same `Command(['xacro ', path])`: xacro passes a plain `.urdf` through, so one launch file serves both.
- Other consumers: ros2_control reads `robot_description` as a parameter in Humble and from this topic in Jazzy+ ([[core-ros2-control-overview]]).

## Pitfalls
- `joint_state_publisher_gui` together with a real `joint_state_broadcaster` → conflicting `/joint_states`.
- No `/joint_states` publisher → movable joints have no TF, and RViz shows those links at the origin with errors.
