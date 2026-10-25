---
id: core-launch-basics
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "Launch files: CLI, minimal template, install, recipes"
domain: core
area: build-run
distro: humble
tested: false
audience: dev
summary: "ros2 launch CLI, minimal Python launch file with params/remaps, installing launch files, process/timer recipes, anti-patterns."
tags: [launch, ros2 launch, Node, ExecuteProcess, TimerAction, emulate_tty]
see: ["[[core-launch-args-include]]", "[[core-robot-state-publisher]]", "[[core-param-yaml-cli]]", "[[core-pkg-ament-python]]"]
requires: []
version_notes:
  - "humble: Fortress uses 'ign gazebo'; 'gz sim' = Garden/Harmonic — https://github.com/gazebosim/ros_gz/blob/humble/ros_gz_sim/launch/gz_sim.launch.py.in (V20)"
---
# Launch files: CLI, minimal template, install, recipes

**TL;DR** `generate_launch_description()` returns a `LaunchDescription` of actions. The file must be installed (setup.py `data_files` / CMake `install(DIRECTORY launch ...)`) and the ws re-sourced.

## CLI
```bash
ros2 launch <pkg> <file.launch.py> [arg:=value ...]     # [TAB][TAB] lists launch files
ros2 launch my_pkg bringup.launch.py robot_name:=robot2 use_sim_time:=true
ros2 launch my_pkg bringup.launch.py --show-args          # declared args (-s, --show-arguments)
ros2 launch my_pkg bringup.launch.py --print              # print description, do not run
ros2 launch my_pkg bringup.launch.py --debug
ros2 launch my_pkg bringup.launch.py -a                   # --show-all-subprocesses-output: override each process's output setting
ros2 launch my_pkg bringup.launch.py --launch-prefix 'xterm -e gdb -ex run --args' --launch-prefix-filter '<regex>'  # prefix only matching executables
ros2 launch /abs/path/file.launch.py                      # without package
```

## Minimal template
```python
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='my_pkg',
            executable='my_node',          # entry point name (or script.py in ament_cmake)
            name='my_node',                # overrides node name
            namespace='robot1',            # optional
            output='screen',
            emulate_tty=True,              # colored logs
            parameters=[{'max_speed': 1.5, 'use_pid': True}, '/abs/path/params.yaml'],
            remappings=[('/cmd_vel', '/robot1/cmd_vel')],
            arguments=['--ros-args', '--log-level', 'info'],
        ),
    ])
```
Arguments, YAML from the share dir, includes, namespaces and conditions: [[core-launch-args-include]].
One launch file can start executables of one package or of several, C++ and Python alike; `executable=` is the CMake executable or the entry point, not the source file.

## Recipes
```python
# N robots in a loop
nodes = [Node(package='demo_nodes_cpp', executable='talker',
              namespace=f'robot{i}', name=f'talker_{i}') for i in range(3)]

# Arbitrary process (simulator, rosbag)
from launch.actions import ExecuteProcess
ExecuteProcess(cmd=['ros2', 'bag', 'record', '-a', '-o', 'auto_bag'], output='screen')
ExecuteProcess(cmd=['ign', 'gazebo', 'empty.sdf'], output='screen')   # Humble+Fortress; Garden/Harmonic: ['gz', 'sim', ...]

# Delay start
from launch.actions import TimerAction
TimerAction(period=5.0, actions=[Node(package='my_pkg', executable='late_node')])
```
Xacro → `robot_description`: [[core-robot-state-publisher]] · `Trace` action: [[core-debug-tools]] · portable Gazebo start (`ros_gz_sim` `gz_sim.launch.py gz_args:=empty.sdf`): [[core-gazebo-bridge]].

## Typical args in good launch files
`use_sim_time:=true` (sim/bags) · `namespace:=/robot1` · `use_rviz:=true` · `params_file:=...` · `robot_name:=...`

## Layout & install
```
my_pkg/launch/*.launch.py   my_pkg/config/*.yaml   my_pkg/rviz/*.rviz
```
setup.py: `(os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py'))` · CMake: `install(DIRECTORY launch config DESTINATION share/${PROJECT_NAME})` ([[core-pkg-ament-python]], [[core-pkg-ament-cmake]]).

## Anti-patterns
Hard-coded absolute paths/namespaces · undeclared args · monolithic launch (split + `IncludeLaunchDescription`) · `time.sleep` for ordering (use `TimerAction`/lifecycle/event handlers).
