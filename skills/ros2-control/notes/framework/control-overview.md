---
id: control-overview
type: reference
owner: equipo-ros2
updated: 2026-10-24
review_by: 2027-04-22
source: manual
confidentiality: internal
title: "ros2_control architecture: controller manager, resource manager, hardware components, controllers"
domain: control
area: framework
distro: jazzy
tested: false
audience: dev
order: 1
summary: "Why robots need control loops; ros2_control architecture: controller manager, resource manager, hardware components, controllers, command/state interfaces."
tags: [ros2_control, controller_manager, resource manager, hardware component, controller, command interface, state interface, architecture, control loop, ros2_controllers]
see: ["[[control-controller-lifecycle]]", "[[control-hw-interface-concept]]", "[[control-controller-config]]", "[[control-urdf-tag]]", "[[control-cli-list]]", "[[core-ros2-control-overview]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: controller manager, resource manager and component types as in the official getting-started page — https://github.com/ros-controls/control.ros.org/blob/jazzy/doc/getting_started/getting_started.rst (CONTROL-V21)"
  - "jazzy: an access conflict is per command interface, not per joint — https://github.com/ros-controls/ros2_control/blob/jazzy/controller_manager/src/controller_manager.cpp (CONTROL-V17)"
---
# ros2_control architecture: controller manager, resource manager, hardware components, controllers

**TL;DR** A motor told to go to a position does not end exactly there: robot dynamics, manufacturing tolerances, signal distortion, friction and payload get in the way, so every joint needs a control algorithm. ros2_control runs many of them in one loop. The **controller manager** loads controllers and, through the **resource manager**, hardware components (both are plugins), and connects them by named **command** and **state interfaces** such as `joint1/position`.

## The architecture
```text
High-level application layer: <your_cool_app>      3rd party: MoveIt 2, Nav2
        |
ros2_control & friends
  Controller management (controller manager)
     arm_controller [▲ ●]   status_broadcaster [~]   base_controller [●]
     tool_controller [▲]    <cool_controller> [✱]
        |  command and state interfaces
  Resource management (resource manager)
     Simulation HW interface [▲ ● ■]  <-> robot simulator on a desktop computer
     Arm HW interface        [▲ ● ~]  <-> robot arm
     Base HW interface       [● ◆ ✱]  <-> mobile base (platform, rover)
     Tool HW interface       [▲ ✱]    <-> end effector (gripper or tool)
```
Legend: `▲ ● ■ ◆ ~ ✱` are six interface kinds (the original figure draws them as a green triangle, red circle, blue square, purple diamond, yellow wavy connector and blue gear/star icon). A controller connects to the hardware that offers the interfaces it needs; a broadcaster only reads. Redrawn after the architecture figure of the ros2_control documentation (source: https://github.com/ros-controls/control.ros.org; Denis Štogl, Bence Magyar; CC-BY).

## The parts
- **Controller manager** (`controller_manager` node, started by `ros2_control_node` or by the simulator plugin): loads, configures, activates, deactivates and unloads controllers ([[control-controller-lifecycle]]), matches the interfaces a controller requires with the ones the hardware provides, and runs the loop at `update_rate`: read all hardware components, update all active controllers, write all hardware components. It is the user entry point through ROS services and the `ros2 control` CLI ([[control-services-spawner]], [[control-cli-list]]).
- **Resource manager**: loads the hardware components with pluginlib, manages their lifecycle and their state and command interfaces; its `read()`/`write()` talk to the components in each loop.
- **Hardware components** (System, Actuator, Sensor): your code that talks to the drivers ([[control-hw-interface-concept]]). They are declared in the URDF `<ros2_control>` tag ([[control-urdf-tag]]).
- **Controllers** and broadcasters: plugins derived from `controller_interface::ControllerInterface`, configured in YAML ([[control-controller-config]]). Common ones come in `ros2_controllers` (`joint_state_broadcaster`, `forward_command_controller`, `joint_trajectory_controller`, `diff_drive_controller`…).

## What the controller manager guarantees
- Only controllers of a type that is installed and exported can be loaded.
- Hardware is initialised before commands are accepted; controllers can be restarted and switched online.
- Topics and services are provided by the controllers to send commands and read state.
- Two controllers cannot claim the same **command interface**: the second one fails with "Resource conflict for controller '…'. Command interface '…' is already claimed." State interfaces can be read by any number of controllers.

## Pitfalls
- "The motor will go where I send it" is the assumption ros2_control exists to remove: always close the loop through a state interface.
- Two controllers that claim the same command interfaces (a forward position controller and a trajectory controller on `joint1/position`) cannot be active together: switch from one to the other ([[control-cli-state-changes]]).
