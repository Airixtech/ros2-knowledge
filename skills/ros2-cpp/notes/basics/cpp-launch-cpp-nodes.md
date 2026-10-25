---
id: cpp-launch-cpp-nodes
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "Launch C++ executables: a launch file for two rover executables, install(DIRECTORY launch), ros2 launch, emulate_tty"
domain: cpp
area: basics
distro: humble
tested: false
audience: dev
summary: "Python launch file starting C++ executables (package, executable, output), install(DIRECTORY launch) in CMake, ros2 launch, emulate_tty, name= remap."
tags: [launch, launch.py, LaunchDescription, launch_ros.actions.Node, install DIRECTORY launch, ros2 launch, emulate_tty, two_rover_heartbeat.launch.py, name remap]
see: ["[[core-launch-basics]]", "[[cpp-pkg-cmake]]", "[[cpp-node-class]]", "[[core-ros-args]]"]
requires: [ros2-core]
version_notes:
  - "all: launch_ros Node(name=...) is passed to the process as -r __node:=<name> — https://github.com/ros2/launch_ros/blob/humble/launch_ros/launch_ros/actions/node.py"
---
# Launch C++ executables

**TL;DR** A launch file starts several executables with one command. For a C++ package: put `*.launch.py` in a `launch/` folder, add `install(DIRECTORY launch DESTINATION share/${PROJECT_NAME}/)` to CMakeLists, rebuild, and run `ros2 launch <package> <file>.launch.py`. Launch files are Python even when the nodes are C++ ([[core-launch-basics]]).

## `launch/two_rover_heartbeat.launch.py`
```python
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='mars_rover_systems',
            executable='heartbeat_executable',
            output='screen'),
        Node(
            package='mars_rover_systems',
            executable='heartbeat_executable2',
            output='screen')
    ])
```
- `package=`: the package that holds the program; `executable=`: the name given in `add_executable` of CMakeLists; `output='screen'`: print the program's output in the terminal.
- `emulate_tty=True` on a `Node` keeps the colors of the log levels (a `WARN` shows in yellow), as in a terminal.
- The executables can come from the same package or from different ones.

## CMakeLists.txt
```cmake
# Install launch files
install(DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}/)
```
The same `install(DIRECTORY …)` ships config folders too. Complete file: [[cpp-pkg-cmake]].

## Run
```bash
cd ~/ros2_ws && colcon build && source ~/ros2_ws/install/setup.bash
ros2 launch mars_rover_systems [TAB][TAB]     # lists the launch files (and the ros2 launch options)
ros2 launch mars_rover_systems two_rover_heartbeat.launch.py
```
```
[INFO] [launch]: All log files can be found below /home/user/.ros/log/2026-09-17-14-57-36-820426-1_xterm-17575
[INFO] [launch]: Default logging verbosity is set to INFO
[INFO] [heartbeat_executable-1]: process started with pid [17578]
[INFO] [heartbeat_executable2-2]: process started with pid [17580]
[heartbeat_executable2-2] [INFO] [1789657057.960491075] [mars_rover_2]: mars_rover_2 is alive...Time(nanoseconds=1789657057960487924, clock_type=ROS_TIME)
[heartbeat_executable-1] [INFO] [1789657057.962974359] [mars_rover_1]: mars_rover_1 is alive...Time(nanoseconds=1789657057962971320, clock_type=ROS_TIME)
```
Each line carries the process label (`<executable>-<n>`) and the node name; `ros2 node list` shows `/mars_rover_1` and `/mars_rover_2`. The TAB list also shows the options of `ros2 launch` (`--debug`, `--show-args`, `--launch-prefix`, `--noninteractive`, `--print-description`…).

## One executable, two node names
The course builds a second executable (`heartbeat2.cpp`) only to get another node name. One executable can be started twice instead: `name=` renames the node (launch passes `-r __node:=<name>`, [[core-ros-args]]):
```python
Node(package='mars_rover_systems', executable='heartbeat_executable', name='mars_rover_2', output='screen')
```

## Pitfalls
- A new or edited launch file is used only after `colcon build` (the installed copy runs), unless the workspace was built with `--symlink-install`.
- `executable=` must be the CMake executable name, not the `.cpp` file.
- No `install(DIRECTORY launch …)` → `ros2 launch` does not find the file.
