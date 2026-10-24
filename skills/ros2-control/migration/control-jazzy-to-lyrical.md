---
id: control-jazzy-to-lyrical
type: reference
owner: equipo-ros2
updated: 2026-10-24
review_by: 2027-04-22
source: manual
confidentiality: internal
title: "Jazzy → Kilted/Lyrical: removed export methods, set_state/get_command, CMake targets, new defaults"
domain: control
area: migration
distro: jazzy
tested: false
audience: dev
summary: "Port the course to Lyrical: export_state/command_interfaces and HardwareInfo on_init removed, set_state/get_command checklist, target_link_libraries, enforce_command_limits, JTC and broadcaster defaults."
tags: [lyrical, kilted, migration, export_state_interfaces, export_command_interfaces, set_state, get_state, set_command, get_command, joint_state_interfaces_, target_link_libraries, enforce_command_limits, goal_time, publish_dynamic_joint_states, forward_command_controller]
see: ["[[control-hw-template-export]]", "[[control-hw-template-activate-rw]]", "[[control-hw-package-build]]", "[[control-jtc-parameters]]", "[[control-urdf-tag]]", "[[control-humble-to-jazzy]]"]
requires: [ros2-core]
version_notes:
  - "lyrical: ros2_control 6.12.0 removed export_state_interfaces/export_command_interfaces, the HardwareInfo on_init and the Handle(prefix, name, double *) constructor — https://github.com/ros-controls/ros2_control/blob/master/doc/migration.rst (CONTROL-V19)"
  - "kilted: ament_target_dependencies deprecated; lyrical: removed (V09, CONTROL-V29)"
  - "kilted/lyrical: enforce_command_limits default true — https://github.com/ros-controls/ros2_control/blob/master/controller_manager/src/controller_manager_parameters.yaml (CONTROL-V22)"
  - "lyrical: JTC goal_time default 10.0, open_loop_control removed; publish_dynamic_joint_states default false; JointGroup*Controller packages not released — https://github.com/ros-controls/ros2_controllers/blob/master/doc/migration.rst (CONTROL-V07, CONTROL-V28, CONTROL-V34, CONTROL-V35)"
---
# Jazzy → Kilted/Lyrical: removed export methods, set_state/get_command, CMake targets, new defaults

**TL;DR** The course's hardware code compiles on Jazzy and Kilted with deprecated methods, and not on Lyrical (ros2_control 6.12.0): the export methods, the `HardwareInfo` form of `on_init()` and the interface constructor that takes a pointer are removed. Port the code to the framework's interfaces (possible since Jazzy) and to namespaced CMake targets, and check three changed defaults.

## Hardware interface: the official checklist (ros2_control migration guide, Kilted → Lyrical)
1. Mark the `export_state_interfaces()`/`export_command_interfaces()` overrides with `override` (the course already does): a method without it would compile and never be called.
2. Delete both overrides.
3. Make sure every interface they exported is listed in the URDF `<ros2_control>` tag ([[control-urdf-tag]]); others go to `export_unlisted_state_interface_descriptions()`/`export_unlisted_command_interface_descriptions()`.
4. In `read()`, replace writes to the state members (`hw_states_[i] = …`) with `set_state("<joint>/<interface>", value)`.
5. In `write()`, `on_activate()`, `on_deactivate()`, replace reads of the command members with `get_command<double>("<joint>/<interface>")`.
6. Delete `hw_states_`, `hw_commands_` and their `resize()` calls in `on_init()`.
7. Search the package for `export_state_interfaces`, `export_command_interfaces` and `&hw_`: nothing may remain.

Loops over the old vectors become loops over the framework's maps, keyed by the full interface name (`joint1/position`):
```cpp
for (const auto & [name, descr] : joint_state_interfaces_)
{
  set_state(name, 0.0);
}
```
The template's `on_configure()`, `on_activate()` and `read()` in this form: [[control-hw-template-activate-rw]] (official Jazzy demo, identical on Lyrical). `set_state()`/`set_command()` throw at run time if the value type does not match the interface: `set_state(name, 0)` (an `int`) throws on a `double` interface; write `0.0`. The Dynamixel code ports the same way: `joints_[i].state/command` become `set_state`/`get_command` calls per interface.

`on_init(const HardwareComponentInterfaceParams & params)` is the only signature (the course already uses it); `params.hardware_info` holds the `HardwareInfo`.

## CMake
`ament_target_dependencies` is deprecated in Kilted and removed in Lyrical: use `target_link_libraries(${PROJECT_NAME} PUBLIC hardware_interface::hardware_interface pluginlib::pluginlib rclcpp::rclcpp rclcpp_lifecycle::rclcpp_lifecycle)` and, for Dynamixel, `dynamixel_workbench_toolbox::dynamixel_workbench_toolbox` ([[control-hw-package-build]]).

## Changed defaults
| What | Jazzy | Kilted / Lyrical |
|---|---|---|
| controller_manager `enforce_command_limits` | `false` | `true`: commands are clamped to the URDF `<limit>` and the interface `min`/`max` (the course's ±1 vs 1.57 rad) |
| JTC `constraints.goal_time` | 0.0 = no limit | Lyrical: default 10.0; 0.0 = on time; negative = no limit ([[control-jtc-parameters]]) |
| JTC `open_loop_control` | deprecated | Lyrical: removed |
| joint_state_broadcaster `publish_dynamic_joint_states` | `true` | Lyrical: deprecated, default `false`: no `/dynamic_joint_states` |
| `JointGroupEffort/Position/VelocityController` | available | Lyrical: deprecated, packages not released: use `forward_command_controller/ForwardCommandController` with `interface_name` |

## Dynamixel
`dynamixel_hardware` (the code of the course) is not released for Lyrical; ROBOTIS's `dynamixel_hardware_interface` (1.5.1) is ([[control-dynamixel-sdk]]).

## Pitfalls
- A YAML that relied on `goal_time: 0.0` for "no timeout" aborts late goals on Lyrical: set `-1.0`.
- A hardware component that still exports its own pointers fails to compile on Lyrical, it does not fall back.
