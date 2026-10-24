---
id: control-cli-state-changes
type: reference
owner: equipo-ros2
updated: 2026-10-24
review_by: 2027-04-22
source: manual
confidentiality: internal
title: "ros2 control set_controller_state, load/unload_controller, switch_controllers"
domain: control
area: manager
distro: jazzy
tested: false
audience: dev
summary: "Change controller states from the CLI: set_controller_state inactive/active/unconfigured, load_controller --set-state, unload_controller, switch_controllers --activate/--deactivate."
tags: [ros2 control, set_controller_state, load_controller, unload_controller, switch_controllers, --set-state, --activate, --deactivate, cleanup, configure, activate, deactivate]
see: ["[[control-controller-lifecycle]]", "[[control-cli-list]]", "[[control-services-spawner]]", "[[control-learn-unit3-manager]]", "[[core-ros2-control-overview]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: messages 'Successfully configured/deactivated/activated <name>' (the course shows 'successfully started') — https://github.com/ros-controls/ros2_control/blob/jazzy/ros2controlcli/ros2controlcli/verb/set_controller_state.py (CONTROL-V09)"
  - "jazzy: set_controller_state accepts unconfigured (cleanup); humble: inactive and active only; unloading an active controller fails — https://github.com/ros-controls/ros2_control/blob/humble/ros2controlcli/ros2controlcli/verb/set_controller_state.py (CONTROL-V26)"
  - "jazzy: 'Successfully loaded controller X into state active' is load_controller --set-state — https://github.com/ros-controls/ros2_control/blob/jazzy/ros2controlcli/ros2controlcli/verb/load_controller.py (CONTROL-V41)"
  - "humble: switch_controllers prints only 'Successfully switched controllers'; --start/--stop removed in Jazzy (V62) — https://github.com/ros-controls/ros2_control/blob/humble/ros2controlcli/ros2controlcli/verb/switch_controllers.py (CONTROL-V43)"
---
# ros2 control set_controller_state, load/unload_controller, switch_controllers

**TL;DR** Every lifecycle transition of [[control-controller-lifecycle]] has a CLI command. Deactivate before unloading, and switch two controllers that share interfaces in one call.

## Commands and what they print
| Command | From → to | Message |
|---|---|---|
| `ros2 control load_controller joint_state_broadcaster` | — → unconfigured | `Successfully loaded controller joint_state_broadcaster` |
| `ros2 control load_controller --set-state active <name>` | — → inactive or active | `Successfully loaded controller <name> into state active` |
| `ros2 control set_controller_state <name> inactive` | unconfigured → inactive (configure) | `Successfully configured <name>` |
| `ros2 control set_controller_state <name> inactive` | active → inactive | `Successfully deactivated <name>` |
| `ros2 control set_controller_state <name> active` | inactive → active | `Successfully activated <name>` |
| `ros2 control set_controller_state <name> unconfigured` [≥Jazzy] | inactive → unconfigured (cleanup) | `successfully cleaned up <name>` |
| `ros2 control unload_controller <name>` | inactive or unconfigured → unloaded | `Successfully unloaded controller <name>` |

The course prints `successfully configured …` and `successfully started …`: messages of an older release. Any other start state is refused ("cannot activate … from its current state …").

## Walk-through (two loaded, active controllers)
```bash
ros2 control set_controller_state forward_position_controller inactive
ros2 control set_controller_state joint_state_broadcaster inactive
ros2 topic pub /forward_position_controller/commands std_msgs/msg/Float64MultiArray "data:
- -0.79
- -0.79" -1                                    # the robot does not move: the loop does not run it
ros2 control unload_controller forward_position_controller
ros2 control unload_controller joint_state_broadcaster
ros2 control list_controllers                  # No controllers are currently loaded!
ros2 control load_controller joint_state_broadcaster
ros2 control load_controller forward_position_controller      # both unconfigured, no topics
ros2 control set_controller_state joint_state_broadcaster inactive
ros2 control set_controller_state forward_position_controller inactive
ros2 control set_controller_state joint_state_broadcaster active
ros2 control set_controller_state forward_position_controller active
```
Publish again and the robot moves.

## Switching controllers
```bash
ros2 control switch_controllers --deactivate forward_position_controller --activate position_trajectory_controller
```
```text
Successfully switched controllers!
Deactivated controllers: [ forward_position_controller ]
Activated controllers: [ position_trajectory_controller ]
```
Both claim the same `position` interfaces, so they cannot be active at once; one call deactivates one and activates the other. [Humble: prints only `Successfully switched controllers`; `--start/--stop` are deprecated aliases there and removed in Jazzy].

## Pitfalls
- `unload_controller` on an active controller fails: "Could not unload controller with name '…' because it is still active". Deactivate first [≥Jazzy: `unload_controller --all-inactive` unloads every inactive one].
- [Humble: no `unconfigured` target: unload and load again to clean up].
- Activating the second controller of a pair that shares interfaces fails with a resource conflict: use `switch_controllers`.
