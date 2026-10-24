---
id: gazebo-ros2-control-controllers
type: reference
owner: equipo-ros2
updated: 2026-10-24
review_by: 2027-04-22
source: manual
confidentiality: internal
title: "Controller YAML (JTC, JointGroupVelocity, broadcaster) and spawners in launch"
domain: gazebo
area: control
distro: jazzy
tested: false
audience: dev
summary: "controller_manager YAML: update_rate, joint_trajectory_controller, JointGroupVelocityController, joint_state_broadcaster; spawner nodes in launch; launch chain; exec_depend packages."
tags: [controller_manager, update_rate, joint_trajectory_controller, JointTrajectoryController, velocity_controllers, JointGroupVelocityController, joint_state_broadcaster, spawner, controller yaml, ros2_controllers]
see: ["[[gazebo-ros2-control-urdf]]", "[[control-controller-config]]", "[[control-services-spawner]]", "[[core-ros2-control-overview]]", "[[gazebo-jtc-action-client]]", "[[gazebo-velocity-control]]", "[[core-pkg-dependencies]]"]
requires: [ros2-core, ros2-urdf, ros2-control]
version_notes:
  - "humble/fortress: interface_name is not a JointTrajectoryController parameter (ignored); JTC uses joints, command_interfaces, state_interfaces — https://github.com/ros-controls/ros2_controllers/blob/humble/joint_trajectory_controller/src/joint_trajectory_controller_parameters.yaml (GZ-V06)"
  - "humble/fortress: JointGroupVelocityController takes joints only (interface_name is set to velocity by the controller) — https://github.com/ros-controls/ros2_controllers/blob/jazzy/forward_command_controller/src/forward_command_controller_parameters.yaml (GZ-V07)"
  - "jazzy/harmonic: controllers are run-time dependencies: <exec_depend> in package.xml, not CMake (GZ-V08)"
  - "lyrical/jetty: no velocity_controllers package (JointGroupVelocityController deprecated); use forward_command_controller/ForwardCommandController with interface_name: velocity — https://github.com/ros-controls/ros2_controllers/blob/master/doc/migration.rst (GZ-V59)"
  - "jazzy/harmonic: spawner takes several controller names, -c, -p/--param-file, --inactive (GZ-V32) — https://github.com/ros-controls/ros2_control/blob/jazzy/controller_manager/controller_manager/spawner.py"
---
# Controller YAML (JTC, JointGroupVelocity, broadcaster) and spawners in launch

**TL;DR** The YAML named in `<parameters>` ([[gazebo-ros2-control-urdf]]) configures the controller_manager (`update_rate`, which controllers exist and their types) and each controller. Controllers are not started by the YAML: a `spawner` node per controller loads and activates it.

## config/controller_position_velocity.yaml
```yaml
controller_manager:
  ros__parameters:
    update_rate: 100  # Hz
    joint_trajectory_controller:
      type: joint_trajectory_controller/JointTrajectoryController
    velocity_controller:
      type: velocity_controllers/JointGroupVelocityController
    joint_state_broadcaster:
      type: joint_state_broadcaster/JointStateBroadcaster

joint_trajectory_controller:
  ros__parameters:
    joints:
      - laser_scan_link_joint
    command_interfaces:
      - position
    state_interfaces:
      - position
      - velocity

velocity_controller:
  ros__parameters:
    joints:
      - laser_scan_model_link_joint
```
- The course's first file (`controller_position.yaml`) is the same without `velocity_controller`.
- The course also writes `interface_name: position` under the trajectory controller and `interface_name`/`command_interfaces`/`state_interfaces` under the velocity controller: JTC has no `interface_name`, and the velocity controller fixes its interface to `velocity` and reads only `joints`. They are ignored and left out here.
- [changed in Lyrical + Jetty: no `velocity_controllers` package; declare `velocity_controller` with `type: forward_command_controller/ForwardCommandController` and `interface_name: velocity`].
- The `command_interfaces`/`state_interfaces` of JTC must exist in the URDF `<ros2_control>` joint.

## launch/control_position_velocity.launch.py
```python
#!/usr/bin/python3
# -*- coding: utf-8 -*-
from launch_ros.actions import Node
from launch import LaunchDescription


# this is the function launch system will look for
def generate_launch_description():
    spawn_controller = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster"],
        output="screen",
    )
    spawn_controller_traj = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_trajectory_controller"],
        output="screen",
    )
    spawn_controller_velocity = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["velocity_controller"],
        output="screen",
    )

    # create and return launch description object
    return LaunchDescription([spawn_controller, spawn_controller_traj, spawn_controller_velocity])
```
`control.launch.py` (position only) has the first two spawners. One spawner can also take several names: `arguments=["joint_state_broadcaster", "joint_trajectory_controller"]`.

## Launch chain
```xml
<?xml version='1.0' ?>
<launch>
  <!-- Publish URDF file in robot_description topic -->
  <include file="$(find-pkg-share my_box_bot_description)/launch/urdf_visualize_control_velocity.launch.py"/>
  <!-- Read robot_description and spawn in gazebo running sim -->
  <include file="$(find-pkg-share my_box_bot_gazebo)/launch/spawn_robot_description.launch.py"/>
  <!-- Load the controllers -->
  <include file="$(find-pkg-share my_box_bot_gazebo)/launch/control_position_velocity.launch.py"/>
</launch>
```
Check with `ros2 control list_controllers` (all `active`) and `ros2 control list_hardware_interfaces` ([[core-ros2-control-overview]]; states and CLI in detail: [[control-cli-list]], spawner options: [[control-services-spawner]]).

## Dependencies
The controllers are plugins loaded at run time. Declare them in `package.xml` (`<exec_depend>joint_trajectory_controller</exec_depend>`, `velocity_controllers`, `joint_state_broadcaster`, `controller_manager`, `gz_ros2_control`) and install them: `sudo apt install ros-jazzy-ros2-controllers ros-jazzy-gz-ros2-control`.

## Pitfalls
- Spawner logs "Could not contact service /controller_manager/…" → the robot is not spawned yet, or the gz_ros2_control plugin failed (see the Gazebo log).
- `type` misspelled or package not installed → "Loader for controller '…' (type '…') not found."
- A joint listed in two controllers that claim the same interface → the second fails to activate.
