---
id: control-bringup-hardware-launch
type: reference
owner: equipo-ros2
updated: 2026-10-24
review_by: 2027-04-22
source: manual
confidentiality: internal
title: "Launch for real hardware: ros2_control_node with description and controller YAML, spawners, RViz2"
domain: control
area: setup
distro: jazzy
tested: false
audience: dev
summary: "bring_up_on_hardware.launch.py: ros2_control_node with robot_description and controller YAML, spawners (trajectory controller --inactive), robot_state_publisher, RViz2."
tags: [ros2_control_node, controller_manager, real hardware, bring_up_on_hardware.launch.py, xacro.process_file, robot_description, spawner, --inactive, robot_state_publisher, rviz2, controller_configuration.yaml]
see: ["[[control-bringup-sim-launch]]", "[[control-urdf-tag]]", "[[control-controller-config]]", "[[control-services-spawner]]", "[[control-learn-unit4-template]]", "[[control-dynamixel-plugin-urdf-launch]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: the course spawns joint_trajectory_controller, which its YAML calls position_trajectory_controller: that spawner fails; spawn it with --inactive — https://github.com/ros-controls/ros2_control/blob/jazzy/controller_manager/src/controller_manager.cpp (CONTROL-V01)"
  - "jazzy: the controller manager ignores the robot_description parameter and reads /robot_description from robot_state_publisher; humble: the parameter is required — https://github.com/ros-controls/ros2_control_demos/blob/jazzy/example_1/bringup/launch/rrbot.launch.py (CONTROL-V23)"
---
# Launch for real hardware: ros2_control_node with description and controller YAML, spawners, RViz2

**TL;DR** Without Gazebo nobody starts the controller manager or reads the `<gazebo>` block, so launch `ros2_control_node` yourself and give it the controller YAML. RViz2 shows the robot from the joint states the broadcaster publishes.

## launch/bring_up_on_hardware.launch.py (template package)
```python
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
import xacro


def generate_launch_description():
    robot_model_file = "rrbot.xacro"
    package_name = "rrbot_unit3"

    rviz_config = os.path.join(get_package_share_directory("rrbot_unit3"), "rviz", "unit3.rviz")
    robot_description = os.path.join(get_package_share_directory(package_name), "urdf", robot_model_file)
    robot_description_config = xacro.process_file(robot_description)

    controller_config = os.path.join(
        get_package_share_directory("my_robot_hardware_interface"), "config", "controller_configuration.yaml"
    )

    return LaunchDescription([
        Node(
            package="controller_manager",
            executable="ros2_control_node",
            parameters=[{"robot_description": robot_description_config.toxml()}, controller_config],
            output={
                "stdout": "screen",
                "stderr": "screen",
            },
        ),
        Node(
            package="controller_manager",
            executable="spawner",
            arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"],
        ),
        Node(
            package="controller_manager",
            executable="spawner",
            arguments=["forward_position_controller", "-c", "/controller_manager"],
        ),
        Node(
            package="controller_manager",
            executable="spawner",
            arguments=["position_trajectory_controller", "-c", "/controller_manager", "--inactive"],
        ),
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            name="robot_state_publisher",
            parameters=[{"robot_description": robot_description_config.toxml()}],
            output="screen"
        ),
        Node(
            package="rviz2",
            executable="rviz2",
            name="rviz2",
            arguments=["-d", rviz_config],
            output={
                "stdout": "screen",
                "stderr": "log",
            },
        )
    ])
```
- The course's file spawns `joint_trajectory_controller`, a name its YAML ([[control-controller-config]], copy of units 4–5) does not define: the controller manager logs "The 'type' param was not defined for 'joint_trajectory_controller'." and only that spawner fails. Here it uses the YAML's name and `--inactive` (configured, not activated), because it claims the same `position` interfaces as `forward_position_controller`; switch to it when needed ([[control-cli-state-changes]]).
- The course also sets an unused variable `robot_name = "rrbot"` (left out).
- The Dynamixel unit uses the same file with `rrbot_unit4`, `unit4.rviz`, the YAML of `dynamixel_hardware_interface` and no trajectory spawner ([[control-dynamixel-plugin-urdf-launch]]).

## What is different from simulation
- `ros2_control_node` runs the controller manager and loads the hardware plugin named in `<ros2_control>` ([[control-urdf-tag]]); the controller YAML is a parameters file of this node. The `<gazebo>` block of the URDF is ignored.
- `robot_description`: [Humble] given as a parameter of `ros2_control_node`, as here [changed in Jazzy: the controller manager ignores that parameter and waits for the `/robot_description` topic of `robot_state_publisher`; the file still works because `robot_state_publisher` is launched. The official Jazzy demo passes only `update_rate` to `ros2_control_node`].
- `xacro.process_file(path).toxml()` is the short form of the parse/process steps of the simulation launch.
- The package must install `launch` and `config` (`install(DIRECTORY launch config DESTINATION share/${PROJECT_NAME}/)`, [[control-hw-package-build]]).

## Pitfalls
- Robot not shown in RViz2 → the broadcaster is not active, or the RViz2 fixed frame does not exist.
- Two controllers on the same interfaces started active → the second fails to activate: start the extra one with `--inactive`.
- On Jazzy, a controller manager without `robot_state_publisher` waits for `/robot_description` and never loads the hardware.
