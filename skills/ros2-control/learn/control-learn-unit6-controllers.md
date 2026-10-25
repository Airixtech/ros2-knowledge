---
id: control-learn-unit6-controllers
type: reference
owner: equipo-ros2
updated: 2026-10-24
review_by: 2027-04-22
source: manual
confidentiality: internal
title: "Unit 6 exercises 6.2.1–6.6.1: rrbot_unit5 with each forward controller and JTC with joint_trajectory_publisher"
domain: control
area: learn
distro: jazzy
tested: false
audience: students
summary: "Unit 6 exercises 6.2.1–6.6.1: rrbot_unit5 ros2_control blocks per controller, YAML, build, spawn_rrbot, load/test/unload, joint_trajectory_publisher."
tags: [unit 6, exercise 6.2.1, exercise 6.3.1, exercise 6.4.1, exercise 6.5.1, exercise 6.6.1, rrbot_unit5, spawn_rrbot.launch.py, load_controller, set_controller_state, unload_controller, joint_trajectory_publisher, hands-on]
see: ["[[control-builtin-forward]]", "[[control-jtc-commands]]", "[[control-learn-unit6-diffbot]]", "[[control-cli-state-changes]]", "[[control-learn-unit7-custom]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: GazeboSimSystem has no acceleration interfaces; the exercises' acceleration lines are skipped — https://github.com/ros-controls/gz_ros2_control/blob/jazzy/gz_ros2_control/src/gz_system.cpp (CONTROL-V52)"
  - "kilted/lyrical: commands above min/max ±1 are clamped [verify] (CONTROL-V64); JointGroup* packages not released in Lyrical (CONTROL-V35)"
---
# Unit 6 exercises 6.2.1–6.6.1: rrbot_unit5 with each forward controller and JTC with joint_trajectory_publisher

**TL;DR** The unit tries each controller type of ros2_controllers on the two-joint `rrbot` in Gazebo Sim, then a differential drive robot ([[control-learn-unit6-diffbot]]). Every rrbot exercise repeats the same steps with another `<ros2_control>` block and YAML. The controllers themselves: [[control-builtin-forward]], [[control-jtc-commands]].

## Before you start
Start the course's empty Gazebo Sim world for unit 6 (the course platform provides the start script). The package is `rrbot_unit5` in `~/ros2_ws/src/ros2_control_course/unit5`; the robot description is `urdf/rrbot.xacro`.

## The steps of every rrbot exercise
1. Replace the `<ros2_control>` and `<gazebo>` tags in `rrbot.xacro` with the exercise's block (the earlier tags are no longer needed).
2. Create the exercise's YAML in `rrbot_unit5/config/`: `position_controller_config.yaml`, `effort_controller_config.yaml`, `velocity_controller_config.yaml`, `forward_command_controller_config.yaml` (contents: [[control-builtin-forward]]) or `joint_trajectory_controller_config.yaml`. Install the folder once, in `CMakeLists.txt`:
```cmake
install(
  DIRECTORY config urdf rviz
  DESTINATION share/${PROJECT_NAME}
)
```
3. Build and spawn (the launch file also starts `robot_state_publisher`):
```bash
cd ~/ros2_ws
colcon build --packages-select rrbot_unit5
source install/setup.bash
ros2 launch spawn_robot spawn_rrbot.launch.py
```
4. Load and start the controller and the broadcaster (it publishes `/joint_states`):
```bash
ros2 control load_controller --set-state active forward_position_controller
ros2 control load_controller --set-state active joint_state_broadcaster
```
```text
Successfully loaded controller forward_position_controller
Successfully loaded controller forward_position_controller into state active
```
5. Send commands (below), then stop and unload ([[control-cli-state-changes]]):
```bash
ros2 control set_controller_state forward_position_controller inactive
ros2 control unload_controller forward_position_controller
```
```text
Successfully deactivated forward_position_controller
Successfully unloaded controller forward_position_controller
```
6. Clean up: Ctrl+C in the terminal of `spawn_rrbot.launch.py`, and delete the robot model in Gazebo. Its gz_ros2_control plugin read the YAML when it was spawned, so a robot with a new configuration must be spawned again.

## Exercise 6.2.1: position_controllers
```xml
<ros2_control name="position_controllers_exercise" type="system">
  <hardware>
    <plugin>gz_ros2_control/GazeboSimSystem</plugin>
  </hardware>
  <joint name="joint1">
    <command_interface name="position">
      <param name="min">-1000</param>
      <param name="max">1000</param>
    </command_interface>
    <state_interface name="position"/>
    <state_interface name="velocity"/>
    <state_interface name="effort"/>
  </joint>
  <joint name="joint2">
    <command_interface name="position">
      <param name="min">-1000</param>
      <param name="max">1000</param>
    </command_interface>
    <state_interface name="position"/>
    <state_interface name="velocity"/>
    <state_interface name="effort"/>
  </joint>
</ros2_control>
<gazebo>
  <plugin filename="gz_ros2_control-system" name="gz_ros2_control::GazeboSimROS2ControlPlugin">
    <parameters>$(find rrbot_unit5)/config/position_controller_config.yaml</parameters>
  </plugin>
</gazebo>
```
Command: `ros2 topic pub /forward_position_controller/commands std_msgs/msg/Float64MultiArray "data: [2.55, 2.55]" -1`; the joints go to 2.55 rad.

## The other exercises: what changes in the block
- **6.3.1 effort_controllers**: `<ros2_control name="effort_controllers_exercise" type="system">`, `<command_interface name="effort">` with min/max ±1000, `<parameters>$(find rrbot_unit5)/config/effort_controller_config.yaml</parameters>`. Load `effort_controllers`; `data: [10.0, 4.0]` on `/effort_controllers/commands` moves the joints abruptly until they settle; `data: [0.0, 0.0]` removes the effort.
- **6.4.1 velocity_controllers**: `<ros2_control name="velocity_controller_exercise" type="system">`, `<command_interface name="velocity">` with `<param name="min">-1</param>` and `<param name="max">1</param>`, states position, velocity and `<state_interface name="acceleration"/>`, `<parameters>$(find rrbot_unit5)/config/velocity_controller_config.yaml</parameters>`. Load `forward_velocity_controller`; `data: [0.5, 0.5]` turns both joints at 0.5 rad/s, `data: [0.0, 0.0]` stops them.
- **6.5.1 forward_command_controller**: `<ros2_control name="forward_command_controllers_exercise" type="system">`; each joint has `<command_interface name="position">`, `"velocity"` and `<command_interface name="acceleration">`, all ±1, and states position, velocity, acceleration; `<parameters>$(find rrbot_unit5)/config/forward_command_controller_config.yaml</parameters>`. Load `forward_position_controller`; `data: [1.14, 1.14]` holds both joints there [changed in Kilted: 1.0, clamped by `max` [verify]].
- **6.6.1 joint_trajectory_controller**: `<ros2_control name="trajectory_controllers_exercise" type="system">`, interfaces as in 6.5.1, then `<!-- Gazebo ros2_control plugin -->` and `<parameters>$(find rrbot_unit5)/config/joint_trajectory_controller_config.yaml</parameters>`; the YAML is the trajectory block of [[control-controller-config]] named `position_trajectory_controller` ([[control-jtc-parameters]]). Load `position_trajectory_controller` and the broadcaster, then run the course's test program: `ros2 launch joint_trajectory_publisher joint_trajectory_publisher.launch.py`; the robot follows a sequence of positions.

GazeboSimSystem knows no `acceleration` interface: those lines are skipped without a message. Only one of the three command interfaces of 6.5.1 and 6.6.1 is used, the one the controller claims.

The last exercise, 6.7.1, drives a differential drive robot: [[control-learn-unit6-diffbot]].
