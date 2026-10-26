---
id: cpp-learn-inter-unit5-params
type: reference
owner: equipo-ros2
updated: 2026-10-26
review_by: 2027-04-24
source: manual
confidentiality: internal
title: "Intermediate C++ Unit 5: parameter_tests package, launch files with parameters, exercises 1-2"
domain: cpp
area: learn
distro: humble
tested: false
audience: students
order: 15
summary: "parameter_tests: CMake, CLI session, YAML dump and load, startup flags, launch files with parameters, exercises 1-2."
tags: [course, unit 5, parameter_tests, param_tests_node, param_tests_callback_node, ros2 param, params.yaml, config folder, --params-file, test_parameters.launch.py, get_laser_data, get_odom_data, students]
see: ["[[cpp-params-declare-get]]", "[[cpp-params-callback]]", "[[core-param-yaml-cli]]", "[[core-learn-inter-unit5-params]]", "[[cpp-topic-subscriber]]"]
requires: [ros2-core]
version_notes:
  - "course: ament_target_dependencies(param_vel_node …) for the target param_tests_node stops CMake ('the first argument must be a valid target name') — https://github.com/ament/ament_cmake/blob/humble/ament_cmake_target_dependencies/cmake/ament_target_dependencies.cmake (CPP-V55)"
  - "course: both test_parameters.launch.py files start executable='param_vel_node', which the package does not install (param_tests_node, param_tests_callback_node) — course CMakeLists (CPP-V56)"
  - "course: the YAML of the second launch file was dumped from /move_robot_node, but the launch names the node param_vel_node; a parameter file applies only to the node named by its top key (or a wildcard such as /**) — https://docs.ros.org/en/humble/How-To-Guides/Node-arguments.html (CPP-V86)"
---
# Intermediate C++ Unit 5: parameters

**TL;DR** Package `parameter_tests` holds the node of [[cpp-params-declare-get]] (`param_tests_node`, node name `move_robot_node`) and the validated one of [[cpp-params-callback]] (`param_tests_callback_node`, node name `param_vel_node`). The unit drives them from the CLI, dumps and loads a YAML file, sets values at startup, and writes launch files with parameters. CLI reference: [[core-param-yaml-cli]]; Python twin: [[core-learn-inter-unit5-params]].

## Package and CMake
```bash
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_cmake parameter_tests --dependencies rclcpp geometry_msgs
```
```cmake
add_executable(param_tests_node src/parameter_tests_node.cpp)
ament_target_dependencies(param_tests_node rclcpp geometry_msgs)   # CPP-V55: the course writes param_vel_node here

add_executable(param_tests_callback_node src/parameter_tests_callback.cpp)
ament_target_dependencies(param_tests_callback_node rclcpp geometry_msgs rcl_interfaces)

install(TARGETS
  param_tests_node
  param_tests_callback_node
  DESTINATION lib/${PROJECT_NAME})

install(DIRECTORY launch config
  DESTINATION share/${PROJECT_NAME})
```
The callback node and the `install(DIRECTORY …)` line come later (5.9, 5.10). Build: `cd ~/ros2_ws && colcon build --packages-select parameter_tests && source install/setup.bash`.

## CLI session (5.4–5.6)
```bash
ros2 run parameter_tests param_tests_node        # MoveRobot started | linear=0.00 angular=0.00 rate=1.00 Hz, once per second
ros2 param list                                  # every node and its parameters
ros2 param list /move_robot_node                 # angular_speed, linear_speed, publish_rate, qos_overrides./parameter_events.publisher.*, use_sim_time
ros2 param describe /move_robot_node angular_speed   # Type: double, Description: Angular speed of the robot in rad/s.
ros2 param get /move_robot_node angular_speed        # Double value is: 0.0
ros2 param set /move_robot_node angular_speed 0.5    # Set parameter successful
ros2 param set /move_robot_node angular_speed 0.0    # stop
```
With the first version of the node the log keeps `angular=0.00`: the value is read only in the constructor. The final version re-reads it in the timer and the rover turns at 0.5 rad/s.

```bash
mkdir ~/ros2_ws/src/parameter_tests/config
ros2 param dump /move_robot_node > ~/ros2_ws/src/parameter_tests/config/params.yaml
```
```yaml
/move_robot_node:
  ros__parameters:
    angular_speed: 0.5
    linear_speed: 0.0
    publish_rate: 1.0
    qos_overrides:
      /parameter_events:
        publisher:
          depth: 1000
          durability: volatile
          history: keep_last
          reliability: reliable
    use_sim_time: false
```
Edit it to the values to load, without the read-only `qos_overrides` block:
```yaml
/move_robot_node:
  ros__parameters:
    angular_speed: 1.0
    linear_speed: 0.5
    publish_rate: 1.0
    use_sim_time: false
```
```bash
ros2 param load /move_robot_node ~/ros2_ws/src/parameter_tests/config/params.yaml
#   Set parameter angular_speed successful … Set parameter linear_speed successful … publish_rate … use_sim_time
ros2 run parameter_tests param_tests_node --ros-args -p angular_speed:=1.5 -p linear_speed:=0.3 -p publish_rate:=0.5
ros2 run parameter_tests param_tests_node --ros-args --params-file ~/ros2_ws/src/parameter_tests/config/params.yaml
```
`config/` is the usual folder for parameter files in ROS 2 packages.

## Exercise 1
A new node with two boolean parameters, `get_laser_data` and `get_odom_data`, both `false` by default. When `true`, `get_laser_data` prints the laser value right in front of the robot and `get_odom_data` prints the robot's [X, Y]. Hints: the data comes from the topics `scan` and `odom` (subscriptions: [[cpp-topic-subscriber]]).

## Launch files with parameters (5.9)
`launch/test_parameters.launch.py`, values in the launch file:
```python
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='parameter_tests',
            executable='param_tests_node',   # CPP-V56: the course writes 'param_vel_node'
            name='param_vel_node',
            output='screen',
            emulate_tty=True,
            parameters=[
                {'angular_speed': 0.5},
                {'linear_speed': 0.5},
                {'publish_rate': 1.0}
            ]
        )
    ])
```
The same launch file with the YAML of `config/`:
```python
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    config_file = os.path.join(
        get_package_share_directory('parameter_tests'),
        'config',
        'params.yaml'
    )

    return LaunchDescription([
        Node(
            package='parameter_tests',
            executable='param_tests_node',   # CPP-V56
            name='param_vel_node',
            output='screen',
            emulate_tty=True,
            parameters=[config_file]
        )
    ])
```
`name='param_vel_node'` renames the node, but `params.yaml` starts with `/move_robot_node:`: its values are not applied and the node keeps its defaults (CPP-V86). Make the top key `/param_vel_node:` (or `/**:` for every node), or drop `name=`. Run: `ros2 launch parameter_tests test_parameters.launch.py`; parameters given at launch are startup values, not runtime changes.

## Exercise 2
A launch file that starts the node of Exercise 1.
