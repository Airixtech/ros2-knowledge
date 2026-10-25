---
id: control-builtin-forward
type: reference
owner: equipo-ros2
updated: 2026-10-24
review_by: 2027-04-22
source: manual
confidentiality: internal
title: "Built-in controllers; the forward family: JointGroupPosition/Effort/Velocity, ForwardCommandController, /commands"
domain: control
area: controllers
distro: jazzy
tested: false
audience: dev
summary: "ros2_controllers types; forward family (JointGroupPosition/Effort/VelocityController, ForwardCommandController interface_name) forwards Float64MultiArray on ~/commands unchanged."
tags: [ros2_controllers, position_controllers, JointGroupPositionController, effort_controllers, JointGroupEffortController, velocity_controllers, JointGroupVelocityController, forward_command_controller, ForwardCommandController, MultiInterfaceForwardCommandController, interface_name, commands, Float64MultiArray]
see: ["[[control-controller-config]]", "[[control-urdf-tag]]", "[[control-jtc-commands]]", "[[control-diff-drive-controller]]", "[[control-learn-unit6-controllers]]", "[[control-jazzy-to-lyrical]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: ros2_controllers has many more types than the course's six (steering, admittance, gpio, gripper, mecanum, PID, broadcasters…) — https://github.com/ros-controls/ros2_controllers/tree/jazzy (CONTROL-V62)"
  - "jazzy: JointGroup* controllers and ForwardCommandController forward ~/commands unchanged; MultiInterfaceForwardCommandController for one joint with several interfaces — https://github.com/ros-controls/ros2_controllers/blob/jazzy/forward_command_controller/forward_command_plugin.xml (CONTROL-V63)"
  - "jazzy: JointGroupEffortController reads only joints (interface fixed to effort); the course's command_interfaces/state_interfaces keys are ignored — https://github.com/ros-controls/ros2_controllers/blob/jazzy/effort_controllers/src/joint_group_effort_controller.cpp (CONTROL-V51)"
  - "jazzy: GazeboSimSystem exports only position, velocity and effort; acceleration interfaces are skipped — https://github.com/ros-controls/gz_ros2_control/blob/jazzy/gz_ros2_control/src/gz_system.cpp (CONTROL-V52)"
  - "kilted/lyrical: min/max of a command interface clamp only with enforce_command_limits true, the default there; jazzy default false — https://github.com/ros-controls/ros2_control/blob/master/controller_manager/src/controller_manager_parameters.yaml (CONTROL-V64, CONTROL-V22)"
  - "lyrical: position_controllers, velocity_controllers and effort_controllers are not released; use ForwardCommandController with interface_name — https://github.com/ros-controls/ros2_controllers/blob/master/doc/migration.rst (CONTROL-V35)"
---
# Built-in controllers; the forward family: JointGroupPosition/Effort/Velocity, ForwardCommandController, /commands

**TL;DR** The **ros2_controllers** repository (separate from the ros2_control framework) ships ready-made controllers. The simplest family subscribes to `~/commands` and writes the values **unchanged** to one command interface per joint. Use it when the control loop runs in the hardware (for example the servo's internal PID) or in a simulation that executes position commands perfectly.

## Which controller
The course names six: `position_controllers`, `effort_controllers`, `velocity_controllers`, `forward_command_controller` (this note), `joint_trajectory_controller` ([[control-jtc-commands]]) and `diff_drive_controller` ([[control-diff-drive-controller]]). The repository has many more (steering, admittance, GPIO, gripper, mecanum, PID and the broadcasters): list the installed ones with `ros2 control list_controller_types`, and see the up-to-date list in the official repository, github.com/ros-controls/ros2_controllers (branch of your distro).

| `type` | Command interface | Parameters |
|---|---|---|
| `position_controllers/JointGroupPositionController` | `position` | `joints` |
| `velocity_controllers/JointGroupVelocityController` | `velocity` | `joints` |
| `effort_controllers/JointGroupEffortController` | `effort` | `joints` |
| `forward_command_controller/ForwardCommandController` | the one named by `interface_name` | `joints`, `interface_name` |
| `forward_command_controller/MultiInterfaceForwardCommandController` | several interfaces of one joint | `joint`, `interface_names` |

The three JointGroup types are ForwardCommandController with `interface_name` fixed. [changed in Lyrical: their packages are not released; write `type: forward_command_controller/ForwardCommandController` and `interface_name: position` (or `velocity`, `effort`)].

## config/position_controller_config.yaml
```yaml
# Controller manager configuration
controller_manager:
  ros__parameters:
    update_rate: 50  # Hz

    # Declare controller name and type
    forward_position_controller:
      type: position_controllers/JointGroupPositionController
    joint_state_broadcaster:
      type: joint_state_broadcaster/JointStateBroadcaster

# Controller properties and joints to use
forward_position_controller:
  ros__parameters:
    joints:
      - joint1
      - joint2
```
The course's other files are the same with these lines changed:
- `effort_controller_config.yaml`: controller `effort_controllers` (the course names it like the package), `type: effort_controllers/JointGroupEffortController`. The course also gives it `command_interfaces: [effort]` and `state_interfaces: [position, velocity, effort]`: not parameters of this controller, ignored.
- `velocity_controller_config.yaml`: `forward_velocity_controller`, `type: velocity_controllers/JointGroupVelocityController`.
- `forward_command_controller_config.yaml`: `forward_position_controller`, `type: forward_command_controller/ForwardCommandController`, and under its `ros__parameters` the line `interface_name: position`. The name can be any interface the hardware exports, so a forward controller also drives custom interfaces.

## The URDF side
Each joint in `<ros2_control>` needs a `<command_interface>` with the name the controller claims, for example `<command_interface name="position">` ([[control-urdf-tag]]; the blocks of the course exercises: [[control-learn-unit6-controllers]]). With `gz_ros2_control/GazeboSimSystem` only `position`, `velocity` and `effort` exist: interfaces with other names (the course adds `acceleration`) are skipped without a message.

## Commands
`~/commands` takes `std_msgs/msg/Float64MultiArray`, one value per joint in the order of `joints`, in SI units (rad, rad/s, N·m for revolute joints):
```bash
ros2 topic pub /forward_position_controller/commands std_msgs/msg/Float64MultiArray "data:
- 2.55
- 2.55" -1
```
The joints move to the commanded value and stay there; an effort command (`/effort_controllers/commands`, `data: [10.0, 4.0]`) moves them abruptly and then holds the efforts until you send `0.0`.

## Pitfalls
- Wrong number of values → "command size (…) does not match number of interfaces (…)", nothing is written. Commands while inactive → "Can't accept new commands. Controller is not active."; NaN or infinite values → "Non-finite value received. Dropping message".
- Two forward controllers on the same interfaces cannot be active together: switch them ([[control-cli-state-changes]]).
- `min`/`max` of the command interface do not limit these commands on Jazzy unless the controller manager has `enforce_command_limits: true` [changed in Kilted: default `true`, so 1.14 rad with `max` 1 becomes 1.0 [verify]] ([[control-urdf-tag]]).
