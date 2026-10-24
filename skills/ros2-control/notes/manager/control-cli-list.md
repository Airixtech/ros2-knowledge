---
id: control-cli-list
type: reference
owner: equipo-ros2
updated: 2026-10-24
review_by: 2027-04-22
source: manual
confidentiality: internal
title: "ros2 control list_controller_types and list_controllers: what each state looks like"
domain: control
area: manager
distro: jazzy
tested: false
audience: dev
summary: "ros2 control list_controller_types, list_controllers output (name, type, state; -v), list_hardware_interfaces/components; which topics exist in each controller state."
tags: [ros2 control, list_controller_types, list_controllers, list_hardware_interfaces, list_hardware_components, controller state, active, inactive, unconfigured, diagnostics, ros2controlcli]
see: ["[[control-cli-state-changes]]", "[[control-controller-lifecycle]]", "[[control-services-spawner]]", "[[control-controller-config]]", "[[core-ros2-control-overview]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: list_controllers prints three columns (name, type, state), like Humble; the name[type] state lines of the course's hardware units come from an older release — https://github.com/ros-controls/ros2_control/blob/jazzy/ros2controlcli/ros2controlcli/verb/list_controllers.py (CONTROL-V10)"
  - "lyrical: joint_state_broadcaster does not publish /dynamic_joint_states unless publish_dynamic_joint_states is set — https://github.com/ros-controls/ros2_controllers/blob/master/doc/migration.rst (CONTROL-V34)"
  - "lyrical: JointGroupEffort/Position/VelocityController deprecated, no effort/position/velocity_controllers packages released — https://github.com/ros/rosdistro/blob/master/lyrical/distribution.yaml (CONTROL-V35)"
---
# ros2 control list_controller_types and list_controllers: what each state looks like

**TL;DR** The `ros2 control` verbs are a diagnostic tool: `list_controller_types` shows what can be loaded, `list_controllers` shows what is loaded and in which state. Look there first when the robot does not move.

## What can be loaded
```bash
ros2 control list_controller_types
```
```text
diff_drive_controller/DiffDriveController                              controller_interface::ControllerInterface
effort_controllers/JointGroupEffortController                          controller_interface::ControllerInterface
force_torque_sensor_broadcaster/ForceTorqueSensorBroadcaster           controller_interface::ControllerInterface
forward_command_controller/ForwardCommandController                    controller_interface::ControllerInterface
imu_sensor_broadcaster/IMUSensorBroadcaster                            controller_interface::ControllerInterface
joint_state_broadcaster/JointStateBroadcaster                          controller_interface::ControllerInterface
joint_trajectory_controller/JointTrajectoryController                  controller_interface::ControllerInterface
position_controllers/JointGroupPositionController                      controller_interface::ControllerInterface
velocity_controllers/JointGroupVelocityController                      controller_interface::ControllerInterface
```
The list depends on the controller packages installed (part of the course machine's list). These names are the `type` values of the YAML ([[control-controller-config]]). [changed in Lyrical: the `JointGroup…Controller` types are replaced by `forward_command_controller/ForwardCommandController` with `interface_name`; their packages are not released].

## What is loaded, per state
```bash
ros2 control list_controllers
```
```text
joint_state_broadcaster      joint_state_broadcaster/JointStateBroadcaster        active
forward_position_controller  forward_command_controller/ForwardCommandController  active
```
| `list_controllers` state | Topics of the course's two controllers |
|---|---|
| `active` | `/joint_states`, `/dynamic_joint_states`, `/forward_position_controller/commands`: the broadcaster publishes and the controller moves the joints |
| `inactive` | the same topics exist, but nothing is published or executed |
| `unconfigured` (after `load_controller`) | none of them: they are created in `on_configure` |
| nothing loaded | `No controllers are currently loaded!` |

The course's hardware units show an older format (`forward_position_controller[forward_command_controller/ForwardCommandController] active`); Humble and Jazzy print the columns above. `-v` (`--verbose`) adds the claimed and required interfaces [≥Jazzy: and `update_rate`, `is_async`]; `--claimed-interfaces`, `--required-state-interfaces`, `--required-command-interfaces` print only those.

## Hardware side
`ros2 control list_hardware_components` prints each component of `<ros2_control>` with its name, type, plugin name, lifecycle state and its command interfaces (`[available]`, `[claimed]`) and state interfaces; `ros2 control list_hardware_interfaces` prints all command and state interfaces. Use them to check that the interfaces a controller needs exist.

## Pitfalls
- A controller not in the list → it was never loaded (spawner failed: read its log, [[control-services-spawner]]).
- `unconfigured` and no topic → configure it ([[control-cli-state-changes]]); `inactive` → activate it.
- [changed in Lyrical: `/dynamic_joint_states` is off by default (`publish_dynamic_joint_states`)]: do not use it as a sign that the broadcaster runs.
