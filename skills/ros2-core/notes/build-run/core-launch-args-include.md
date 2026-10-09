---
id: core-launch-args-include
title: "Launch arguments, includes, namespaces & conditions"
domain: core
area: build-run
distro: humble
tested: false
audience: dev
summary: "Launch args, YAML from share, GroupAction+PushRosNamespace, includes, IfCondition, OpaqueFunction."
tags: [DeclareLaunchArgument, LaunchConfiguration, IncludeLaunchDescription, PushRosNamespace, IfCondition]
see: ["[[core-launch-basics]]", "[[core-multi-robot-namespacing]]", "[[core-param-yaml-cli]]"]
requires: []
version_notes:
  - "jazzy: PushROSNamespace (Iron rename; old name = alias) — https://docs.ros.org/en/rolling/Releases/Release-Iron-Irwini.html (V15)"
---
# Launch arguments, includes, namespaces & conditions

**TL;DR** Declare every argument, read it with `LaunchConfiguration`, group per-robot actions under `GroupAction([PushRosNamespace(...), ...])` and gate optional nodes with `IfCondition`.

## Full pattern (args, YAML from share, include, namespace group, condition)
```python
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node, PushRosNamespace, SetParameter, SetRemap
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    pkg_share = FindPackageShare('my_pkg')
    use_sim_time = LaunchConfiguration('use_sim_time')
    robot_ns = LaunchConfiguration('robot_ns')
    params_file = LaunchConfiguration('params_file')

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        DeclareLaunchArgument('robot_ns', default_value='robot1'),
        DeclareLaunchArgument('with_rviz', default_value='true'),
        DeclareLaunchArgument('params_file',
            default_value=PathJoinSubstitution([pkg_share, 'config', 'params.yaml'])),
        SetParameter(name='use_sim_time', value=use_sim_time),   # applies to all following nodes
        GroupAction([
            PushRosNamespace(robot_ns),                 # must be first in the group
            SetRemap(src='/tf', dst='tf'),              # per-robot TF (multi-robot)
            SetRemap(src='/tf_static', dst='tf_static'),
            Node(package='my_pkg', executable='driver', parameters=[params_file]),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    PathJoinSubstitution([pkg_share, 'launch', 'robot.launch.py'])),
                launch_arguments={'use_sim_time': use_sim_time}.items()),
        ]),
        Node(package='rviz2', executable='rviz2',
             arguments=['-d', PathJoinSubstitution([pkg_share, 'rviz', 'view.rviz'])],
             condition=IfCondition(LaunchConfiguration('with_rviz'))),
    ])
```
- `PushRosNamespace` is the only name in Humble [changed in Jazzy: `PushROSNamespace`; old name kept as alias]. Other conditions: `UnlessCondition`.
- Values from `LaunchConfiguration` are lazy substitutions, not Python strings. For Python logic, wrap the code in `OpaqueFunction(function=fn)` and call `LaunchConfiguration('x').perform(context)`.
- `/tf` remaps: [[core-multi-robot-namespacing]] · global `use_sim_time`: [[core-time-timers]].

## Include with get_package_share_directory (eager alternative)
```python
import os
from ament_index_python.packages import get_package_share_directory
other = IncludeLaunchDescription(
    PythonLaunchDescriptionSource(os.path.join(
        get_package_share_directory('other_pkg'), 'launch', 'other.launch.py')),
    launch_arguments={'robot_name': 'robot1'}.items())
```

## Pitfalls
- Actions placed before `PushRosNamespace` in the group are not namespaced.
- `if LaunchConfiguration('x') == 'true':` compares an object and is always false. Use `IfCondition` or `OpaqueFunction`.
