---
id: control-services-spawner
type: reference
owner: equipo-ros2
updated: 2026-10-24
review_by: 2027-04-22
source: manual
confidentiality: internal
title: "controller_manager services, ListControllers response, and the spawner"
domain: control
area: manager
distro: jazzy
tested: false
audience: dev
summary: "/controller_manager services (load, configure, switch, unload, list…), ros2 service call ListControllers fields, spawner: load+configure+activate, already-loaded error, options."
tags: [controller_manager services, list_controllers service, controller_manager_msgs, ListControllers, ControllerState, switch_controller, load_controller, configure_controller, cleanup_controller, spawner, --inactive, --param-file, --controller-manager]
see: ["[[control-cli-list]]", "[[control-cli-state-changes]]", "[[control-bringup-sim-launch]]", "[[control-bringup-hardware-launch]]", "[[control-controller-lifecycle]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: + ~/cleanup_controller (since controller_manager 4.42.0), logger and type-description services; humble: none of them — https://github.com/ros-controls/ros2_control/blob/jazzy/controller_manager/src/controller_manager.cpp (CONTROL-V24)"
  - "jazzy: ControllerState has is_async, update_rate, exported_state_interfaces; humble: not — https://github.com/ros-controls/ros2_control/blob/jazzy/controller_manager_msgs/msg/ControllerState.msg (CONTROL-V25)"
  - "jazzy: the spawner prints 'Configured and activated <name>' and logs as spawner_<controller> (the course shows 'Configured and started') — https://github.com/ros-controls/ros2_control/blob/jazzy/controller_manager/controller_manager/spawner.py (CONTROL-V08)"
  - "jazzy: on an active controller the spawner prints 'Controller already loaded, skipping load_controller' and 'Failed to configure controller' (same on humble) (CONTROL-V42)"
---
# controller_manager services, ListControllers response, and the spawner

**TL;DR** Everything the CLI does goes through services of the `controller_manager` node; they are meant for programs (other nodes). The `spawner`, a Python script of the `controller_manager` package, uses them to load, configure and activate a controller in one command, which is why launch files use it.

## Services
```bash
ros2 service list | grep controller_manager
```
```text
/controller_manager/configure_controller
/controller_manager/describe_parameters
/controller_manager/get_logger_levels
/controller_manager/get_parameter_types
/controller_manager/get_parameters
/controller_manager/get_type_description
/controller_manager/list_controller_types
/controller_manager/list_controllers
/controller_manager/list_hardware_components
/controller_manager/list_hardware_interfaces
/controller_manager/list_parameters
/controller_manager/load_controller
/controller_manager/reload_controller_libraries
/controller_manager/set_hardware_component_state
/controller_manager/set_logger_levels
/controller_manager/set_parameters
/controller_manager/set_parameters_atomically
/controller_manager/switch_controller
/controller_manager/unload_controller
```
[≥Jazzy 4.42: also `/controller_manager/cleanup_controller`.] [Humble: no `cleanup_controller`, no `get/set_logger_levels`, no `get_type_description`]. Service types are in `controller_manager_msgs/srv`.

```bash
ros2 service call /controller_manager/list_controllers controller_manager_msgs/srv/ListControllers
```
```text
requester: making request: controller_manager_msgs.srv.ListControllers_Request()

response:
controller_manager_msgs.srv.ListControllers_Response(controller=[controller_manager_msgs.msg.ControllerState(name='forward_position_controller', state='active', type='forward_command_controller/ForwardCommandController', is_async=False, update_rate=10, claimed_interfaces=['joint1/position', 'joint2/position'], required_command_interfaces=['joint1/position', 'joint2/position'], required_state_interfaces=[], is_chainable=False, is_chained=False, exported_state_interfaces=[], reference_interfaces=[], chain_connections=[]), controller_manager_msgs.msg.ControllerState(name='joint_state_broadcaster', state='active', type='joint_state_broadcaster/JointStateBroadcaster', is_async=False, update_rate=10, claimed_interfaces=[], required_command_interfaces=[], required_state_interfaces=['joint1/effort', 'joint1/position', 'joint1/velocity', 'joint2/effort', 'joint2/position', 'joint2/velocity'], is_chainable=False, is_chained=False, exported_state_interfaces=[], reference_interfaces=[], chain_connections=[])])
```
The forward controller **claims** command interfaces; the broadcaster only **requires** state interfaces. [Humble: no `is_async`, `update_rate`, `exported_state_interfaces` fields].

## The spawner
```bash
ros2 run controller_manager spawner joint_state_broadcaster
```
On a controller that is already loaded and active:
```text
[WARN] [1764094248.964618067] [spawner_joint_state_broadcaster]: Controller already loaded, skipping load_controller
[ERROR] [1764094248.970169722] [spawner_joint_state_broadcaster]: Failed to configure controller
```
After `set_controller_state joint_state_broadcaster inactive` and `unload_controller joint_state_broadcaster`, the same command loads, configures and activates it:
```text
[INFO] [...] [spawner_joint_state_broadcaster]: Loaded joint_state_broadcaster
[INFO] [...] [spawner_joint_state_broadcaster]: Configured and activated joint_state_broadcaster
```
(The course prints `Configured and started` under a logger `spawner_my_controller_name`: an older release.) `list_controllers` then shows it `active`.

Useful options (Humble and Jazzy): several controller names in one call, `-c`/`--controller-manager <name>`, `-p`/`--param-file <yaml>`, `--inactive` (configure only), `--load-only`, `--activate-as-group`, `--unload-on-kill`, `--switch-timeout` [≥Jazzy: `--controller-ros-args`].

## Pitfalls
- With the default `--controller-manager-timeout 0` the spawner waits for the controller manager forever and warns "Could not contact service /controller_manager/…" every 10 s: no controller manager is running (robot not spawned, plugin or `ros2_control_node` failed). The order of spawners is still up to the launch file ([[control-bringup-sim-launch]]).
- `--inactive` for a second controller on the same interfaces ([[control-bringup-hardware-launch]]).
