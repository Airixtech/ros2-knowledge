---
id: core-launch-substitutions
type: reference
owner: equipo-ros2
updated: 2026-10-14
review_by: 2027-04-12
source: manual
confidentiality: internal
title: "Launch substitutions: LaunchConfiguration, TextSubstitution, PathJoinSubstitution, LogInfo"
domain: core
area: build-run
distro: humble
tested: false
audience: dev
summary: "Required vs optional launch arguments, LogInfo, TextSubstitution, launch CLI common to Python/XML/YAML, a main launch with namespace."
tags: [DeclareLaunchArgument, LaunchConfiguration, TextSubstitution, PathJoinSubstitution, FindPackageShare, LogInfo, launch_arguments, show-args, GroupAction]
see: ["[[core-launch-args-include]]", "[[core-launch-xml-yaml]]", "[[core-launch-node-arguments]]", "[[core-learn-inter-unit4-launch-formats]]"]
requires: []
version_notes:
  - "humble: ros2 run takes values only with flags: --ros-args -p name:=value (a bare name:=value raises UnknownROSArgsError) — https://github.com/ros2/rcl/blob/humble/rcl/src/rcl/arguments.c (V83)"
  - "all: IncludeLaunchDescription also accepts a plain path; the file type is picked by extension — https://github.com/ros2/launch/blob/humble/launch/launch/actions/include_launch_description.py (V104)"
  - "jazzy: PushRosNamespace renamed PushROSNamespace (Iron), old name kept as alias — https://docs.ros.org/en/rolling/Releases/Release-Iron-Irwini.html (V15)"
---
# Launch substitutions: LaunchConfiguration, TextSubstitution, PathJoinSubstitution, LogInfo

**TL;DR** Launch values are *substitutions*: they are resolved when the launch runs, not when Python reads the file. An argument with `default_value` is optional; without it, it is **required**. Print resolved values with `LogInfo`. Every format (Python, XML, YAML) is started and parametrized the same way. Includes, conditions and YAML params: [[core-launch-args-include]].

## Same CLI for every format
```bash
ros2 launch <package_name> <launch_file_name>
ros2 launch <path_to_launch_file>
ros2 launch <package_name> <launch_file_name> argument1:=WHATEVER_VALUE
ros2 launch <package_name> <launch_file_name> --show-args      # list the arguments
ros2 run <package_name> <executable_name> --ros-args -p param1:=WHATEVER_VALUE   # a node: -p for parameters
```

## Required and optional arguments, LogInfo
```python
import launch


def generate_launch_description():
    return launch.LaunchDescription([
        launch.actions.DeclareLaunchArgument('extra_msg', default_value='hello world'),
        launch.actions.DeclareLaunchArgument('important_msg'),
        launch.actions.LogInfo(msg=launch.substitutions.LaunchConfiguration('extra_msg')),
        launch.actions.LogInfo(msg=launch.substitutions.LaunchConfiguration('important_msg')),
    ])
```
```bash
ros2 launch launch_args_example_pkg start_with_arguments_dummy.launch.py extra_msg:="ROS2 is Great!" important_msg:="Execute Order 66"
```
```text
[INFO] [launch]: Default logging verbosity is set to INFO
[INFO] [launch.user]: ROS2 is Great!
[INFO] [launch.user]: Execute Order 66
```
Without `important_msg:=…` the launch stops and reports the missing argument. `LogInfo(msg=str(rviz_config_dir))` also prints plain Python values, for example the path of the RViz config a launch file loads.

## A main launch: args, includes, namespace
```python
import os
from ament_index_python import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription
from launch.actions import GroupAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import TextSubstitution
from launch_ros.actions import Node
from launch_ros.actions import PushRosNamespace


def generate_launch_description():

    package_description = "launch_tests_pkg"

    # args that can be set from the command line or a default will be used
    # TextSubstitution(text="0.0") will only evaluate that in execution time.
    turning_speed_arg = DeclareLaunchArgument(
        "turning_speed", default_value=TextSubstitution(text="0.2")
    )
    forward_speed_arg = DeclareLaunchArgument(
        "forward_speed", default_value="0.1"
    )
    rviz_config_file_name_arg = DeclareLaunchArgument(
        "rviz_config_file_name", default_value=TextSubstitution(text="launch_part.rviz")
    )
    custom_namespace_arg = DeclareLaunchArgument(
        "custom_namespace", default_value=TextSubstitution(text="mazinger")
    )

    turning_speed_f = LaunchConfiguration('turning_speed')
    forward_speed_f = LaunchConfiguration('forward_speed')
    rviz_config_file_name_f = LaunchConfiguration('rviz_config_file_name')
    custom_namespace_f = LaunchConfiguration('custom_namespace')

    # include another launch file
    # use items because you need to pass a list with a key-value structure
    # [(key1,value_x),(key2,value_y),...]
    start_rviz_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare(package_description),
                'launch',
                'start_rviz_with_arguments.launch.py'
            ])
        ]),
        launch_arguments={
            'rviz_config_file_name': rviz_config_file_name_f}.items()
    )

    # include another launch file in the chatter_ns namespace
    move_robot_with_namespace_launch = GroupAction(
        actions=[
            # push-ros-namespace to set namespace of included nodes
            PushRosNamespace(custom_namespace_f),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource([
                    PathJoinSubstitution([
                        FindPackageShare(package_description),
                        'launch',
                        'move_with_arguments.launch.py'
                    ])
                ]),
                launch_arguments={'turning_speed': turning_speed_f,
                                  'forward_speed': forward_speed_f}.items()),
        ],
    )

    return LaunchDescription([
        turning_speed_arg,
        forward_speed_arg,
        rviz_config_file_name_arg,
        custom_namespace_arg,
        start_rviz_launch,
        move_robot_with_namespace_launch,
    ])
```
The two included files and the node: [[core-learn-inter-unit4-launch-formats]]. The same launch in XML and YAML: [[core-launch-xml-yaml]].
- `TextSubstitution(text="0.2")` is resolved at launch time; a plain string `"0.1"` works the same.
- `LaunchConfiguration('turning_speed')` is the **future** value of the argument: never use it in Python operations (`+`, `if`); keep it inside substitutions.
- `PathJoinSubstitution([FindPackageShare(pkg), 'launch', file])` is the substitution form of `os.path.join(get_package_share_directory(pkg), 'launch', file)`. [all] `IncludeLaunchDescription(PathJoinSubstitution([...]))` works without the source wrapper.
- `launch_arguments` takes key–value pairs: pass the dictionary's `.items()`.
- `GroupAction` holds includes and other actions; `PushRosNamespace` puts every node of the group in the namespace.
- To install launch files of every format: `(os.path.join('share', package_name, 'launch'), glob('launch/*'))` in `setup.py`.

Further reading: [Using substitutions (humble)](https://docs.ros.org/en/humble/Tutorials/Intermediate/Launch/Using-Substitutions.html) · [Launch file formats (humble)](https://docs.ros.org/en/humble/How-To-Guides/Launch-file-different-formats.html).

## Pitfalls
- Values in `Node(arguments=[...])` must be strings or substitutions: a Python float fails ([[core-launch-node-arguments]]).
- `ros2 run … --ros-args argument1:=VALUE` (without `-p`) is not a parameter: the node fails with `UnknownROSArgsError`.
