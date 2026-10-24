---
id: control-controller-lifecycle
type: reference
owner: equipo-ros2
updated: 2026-10-24
review_by: 2027-04-22
source: manual
confidentiality: internal
title: "Controller states and transitions: unconfigured, inactive, active, finalized"
domain: control
area: framework
distro: jazzy
tested: false
audience: dev
summary: "Controller lifecycle in ros2_control: states unconfigured/inactive/active/finalized, on_configure…on_error, SUCCESS/FAILURE/ERROR, what each state allows."
tags: [lifecycle, controller state, unconfigured, inactive, active, finalized, on_configure, on_activate, on_deactivate, on_cleanup, on_shutdown, on_error, CallbackReturn]
see: ["[[control-overview]]", "[[control-cli-state-changes]]", "[[control-cli-list]]", "[[control-services-spawner]]", "[[control-hw-template-init]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: callbacks return SUCCESS, FAILURE or ERROR; ERROR leads to ErrorProcessing and on_error — https://github.com/ros2/rclcpp/blob/jazzy/rclcpp_lifecycle/include/rclcpp_lifecycle/node_interfaces/lifecycle_node_interface.hpp (CONTROL-V15)"
  - "jazzy: the course's state diagram matches the lifecycle design except ErrorProcessing, added here — https://github.com/ros2/design/blob/gh-pages/articles/node_lifecycle.md (CONTROL-V33)"
  - "jazzy: publishers and subscribers of joint_state_broadcaster and the forward controllers are created in on_configure — https://github.com/ros-controls/ros2_controllers/blob/jazzy/joint_state_broadcaster/src/joint_state_broadcaster.cpp (CONTROL-V03)"
  - "jazzy: an inactive forward controller logs 'Can't accept new commands. Controller is not active.'; humble: it stores them without a log and drops them at activation — https://github.com/ros-controls/ros2_controllers/blob/jazzy/forward_command_controller/src/forward_controllers_base.cpp (CONTROL-V27)"
---
# Controller states and transitions: unconfigured, inactive, active, finalized

**TL;DR** Every controller and broadcaster is a lifecycle node. The controller manager stores its state and triggers its transitions, so it can make sure the hardware is ready before commands are accepted, and restart or switch controllers online. A controller moves the robot only when it is **active**.

## States and transitions
```mermaid
stateDiagram-v2
    [*] --> unconfigured
    unconfigured --> inactive: on_configure SUCCESS
    unconfigured --> unconfigured: on_configure FAILURE
    inactive --> active: on_activate SUCCESS
    inactive --> inactive: on_activate FAILURE
    active --> inactive: on_deactivate SUCCESS
    inactive --> unconfigured: on_cleanup SUCCESS
    unconfigured --> finalized: on_shutdown SUCCESS
    inactive --> finalized: on_shutdown SUCCESS
    active --> finalized: on_shutdown SUCCESS
    finalized --> [*]
```
- Six transition callbacks: `on_configure`, `on_cleanup`, `on_activate`, `on_deactivate`, `on_shutdown`, `on_error`.
- Each callback returns `SUCCESS`, `FAILURE` or `ERROR` (`CallbackReturn`), and the controller manager reads the result to decide the new state. `ERROR` (or an exception) is not drawn above: it goes to the transition state `ErrorProcessing`, which calls `on_error`.

## What each state allows
| State | How you get there | What you see |
|---|---|---|
| unconfigured | `load_controller` | no topics of the controller yet: publishers and subscribers are created in `on_configure` (no `/dynamic_joint_states`, no `/forward_position_controller/commands`) |
| inactive | configure, or deactivate an active one | topics exist, but the controller manager does not call its `update()`: commands do not reach the joints [≥Jazzy: the forward controller logs "Can't accept new commands. Controller is not active."]; a broadcaster does not publish |
| active | activate | `update()` runs every control cycle: a controller moves the joints, a broadcaster publishes |
| finalized | shutdown (when the controller is destroyed) | nothing: the controller is gone |

Check the state with `ros2 control list_controllers` ([[control-cli-list]]); change it from the CLI, the services or the spawner ([[control-cli-state-changes]], [[control-services-spawner]]).

## Pitfalls
- Robot ignores commands, no error → the controller is `inactive`, or the topic exists only because it was configured: check `list_controllers`.
- A topic you expect is missing → the controller is still `unconfigured` (loaded, not configured).
- If you do not know the states, you cannot tell which situation caused an error, or you may not notice a problem at all: look at the state first when debugging.
