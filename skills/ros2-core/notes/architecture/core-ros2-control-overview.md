---
id: core-ros2-control-overview
type: reference
owner: equipo-ros2
updated: 2026-10-09
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "ros2_control: controllers, YAML, CLI, mock hardware"
domain: core
area: architecture
distro: humble
tested: false
audience: dev
summary: "controller_manager config, common controllers, ros2 control CLI, mock_components for CI, robot_description source Humble vs Jazzy."
tags: [ros2_control, controller_manager, joint_trajectory_controller, diff_drive_controller, mock_components, ros2 control]
see: ["[[core-moveit2-overview]]", "[[core-robot-state-publisher]]", "[[core-time-timers]]"]
requires: []
version_notes:
  - "jazzy: controller_manager subscribes to /robot_description; the robot_description parameter is no longer supported — https://github.com/ros-controls/ros2_control/blob/jazzy/doc/migration.rst (V60)"
  - "jazzy: switch_controllers --start/--stop removed (deprecated aliases in Humble); adds --activate-asap, --best-effort — https://github.com/ros-controls/ros2_control/blob/jazzy/ros2controlcli/ros2controlcli/verb/switch_controllers.py (V62)"
---
# ros2_control: controllers, YAML, CLI, mock hardware

**TL;DR** `controller_manager` loads hardware interfaces (System/Actuator/Sensor) and controllers, which are lifecycle plugins. Always run `joint_state_broadcaster`. In Humble the URDF reaches the controller manager as the `robot_description` **parameter**; in Jazzy+ it comes from the `/robot_description` **topic**.

## Config
```yaml
controller_manager:
  ros__parameters:
    update_rate: 500
    joint_state_broadcaster: {type: joint_state_broadcaster/JointStateBroadcaster}
    arm_controller: {type: joint_trajectory_controller/JointTrajectoryController}
arm_controller:
  ros__parameters:
    joints: [joint_1, joint_2, joint_3, joint_4, joint_5, joint_6]
    command_interfaces: [position]
    state_interfaces: [position, velocity]
```
Controllers: joint_state_broadcaster (always) · joint_trajectory_controller (MoveIt, FollowJointTrajectory) · forward_position_controller (Servo) · diff_drive_controller · admittance_controller.
`robot_description`: [Humble] passed as a parameter to `ros2_control_node` [changed in Jazzy: the CM subscribes to `/robot_description`, published by robot_state_publisher ([[core-robot-state-publisher]]); parameter support removed].

## CLI
```bash
ros2 control list_controllers
ros2 control list_hardware_interfaces
ros2 control switch_controllers --activate arm_controller --deactivate forward_position_controller
```
[Humble] `--start/--stop` are deprecated aliases [changed in Jazzy: removed; `--activate-asap`, `--best-effort` added].

## Mock hardware (CI without HW)
```xml
<ros2_control name="MockBot" type="system">
  <hardware><plugin>mock_components/GenericSystem</plugin></hardware>
  <joint name="joint1"><command_interface name="position"/><state_interface name="position"/></joint>
</ros2_control>
```
Same packages, different launch + YAML for real and sim ([[core-time-timers]]).

## Pitfalls
- Never run joint_state_publisher_gui alongside joint_state_broadcaster.
- With multiple controller managers in Jazzy+, remap `/robot_description` per manager.
