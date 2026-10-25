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
summary: "Port the course to Lyrical: export methods removed, set_state/get_command checklist, target_link_libraries, realtime_tools try_publish, diff_drive limits, changed defaults."
tags: [lyrical, kilted, migration, export_state_interfaces, export_command_interfaces, set_state, get_state, set_command, get_command, joint_state_interfaces_, target_link_libraries, enforce_command_limits, goal_time, publish_dynamic_joint_states, forward_command_controller]
see: ["[[control-hw-template-export]]", "[[control-hw-template-activate-rw]]", "[[control-hw-package-build]]", "[[control-jtc-parameters]]", "[[control-urdf-tag]]", "[[control-custom-configure]]", "[[control-custom-package-build]]", "[[control-diff-drive-controller]]", "[[control-humble-to-jazzy]]"]
requires: [ros2-core]
version_notes:
  - "lyrical: ros2_control 6.12.0 removed export_state_interfaces/export_command_interfaces, the HardwareInfo on_init and the Handle(prefix, name, double *) constructor — https://github.com/ros-controls/ros2_control/blob/master/doc/migration.rst (CONTROL-V19)"
  - "kilted: ament_target_dependencies deprecated; lyrical: removed (V09, CONTROL-V29)"
  - "kilted/lyrical: enforce_command_limits default true — https://github.com/ros-controls/ros2_control/blob/master/controller_manager/src/controller_manager_parameters.yaml (CONTROL-V22)"
  - "lyrical: JTC goal_time default 10.0, open_loop_control removed; publish_dynamic_joint_states default false; JointGroup*Controller packages not released — https://github.com/ros-controls/ros2_controllers/blob/master/doc/migration.rst (CONTROL-V07, CONTROL-V28, CONTROL-V34, CONTROL-V35)"
  - "kilted: realtime_tools .h headers removed, RealtimePublisher members deprecated; lyrical: removed, RealtimeBuffer deprecated — https://github.com/ros-controls/realtime_tools/blob/master/realtime_tools/CHANGELOG.rst (CONTROL-V73)"
  - "kilted: double get_value() removed — https://github.com/ros-controls/ros2_control/blob/kilted/hardware_interface/include/hardware_interface/handle.hpp (CONTROL-V74)"
  - "kilted: diff_drive has_*_limits removed (jerk 0.0 becomes a real limit [verify]); lyrical: publish_rate removed — https://github.com/ros-controls/ros2_controllers/blob/kilted/doc/migration.rst (CONTROL-V68, CONTROL-V69)"
  - "lyrical: RealtimeThreadSafeBox pattern as in example_7 — https://github.com/ros-controls/ros2_control_demos/blob/master/example_7/controller/r6bot_controller.cpp (CONTROL-V56)"
---
# Jazzy → Kilted/Lyrical: removed export methods, set_state/get_command, CMake targets, new defaults

**TL;DR** The course's hardware code compiles on Jazzy and Kilted with deprecated methods, and not on Lyrical (ros2_control 6.12.0); its custom controller (unit 7) stops compiling on Kilted (realtime_tools `.h` headers) and needs `try_publish()` on Lyrical. In the hardware code the export methods, the `HardwareInfo` form of `on_init()` and the interface constructor that takes a pointer are removed. Port the code to the framework's interfaces (possible since Jazzy) and to namespaced CMake targets, and check three changed defaults.

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

## Custom controller (unit 7)
- realtime_tools: [changed in Kilted: `realtime_buffer.h`/`realtime_publisher.h` removed, include the `.hpp` headers; `RealtimePublisher::msg_`, `lock()`, `unlock()`, `trylock()`, `unlockAndPublish()` deprecated]. [changed in Lyrical (5.4.0): those members removed, the constructor that wraps an existing publisher deprecated, `RealtimeBuffer` deprecated]. The appendix's `get_value()` does not compile from Kilted on ([[control-custom-activate-update]]).
- The state publisher in the Lyrical form: the controller keeps its own message and hands it to `try_publish()`; `s_publisher_` is no longer needed [verify build]:
```cpp
// header: members
std::unique_ptr<ControllerStatePublisher> state_publisher_;
ControllerStateMsg state_msg_;

// on_configure()
state_publisher_ = std::make_unique<ControllerStatePublisher>(
    get_node(), "~/state", rclcpp::SystemDefaultsQoS());
state_msg_.header.frame_id = joint_names_[0];

// update()
state_msg_.header.stamp = time;
state_msg_.set_point = command_interfaces_[0].get_optional().value_or(
    std::numeric_limits<double>::quiet_NaN());
state_publisher_->try_publish(state_msg_);
```
- The command buffer with `RealtimeThreadSafeBox` (available since Jazzy; the pattern of the official ros2_control_demos example_7) [verify build]:
```cpp
// header: members
realtime_tools::RealtimeThreadSafeBox<ControllerCommandMsg> input_command_;
ControllerCommandMsg last_command_;

// subscriber callback and on_activate(): store a copy
input_command_.set(*msg);

// update(): take the newest message when the box is free, keep the last one otherwise
auto new_command = input_command_.try_get();
if (new_command.has_value()) {
  last_command_ = new_command.value();
}
```
  The loop then reads `last_command_.displacements[i]`.
- CMake: `target_link_libraries` with the targets of `controller_interface`, `hardware_interface`, `pluginlib`, `rclcpp`, `rclcpp_lifecycle`, `realtime_tools` and `${control_msgs_TARGETS}` ([[control-custom-package-build]]).

## diff_drive_controller (unit 6)
[changed in Kilted: `has_velocity_limits`, `has_acceleration_limits`, `has_jerk_limits` and `min_acceleration` removed: an unset limit (NaN) means no limit. The course's `max_jerk: 0.0` and `min_jerk: 0.0` then are a jerk limit of 0 and the robot never accelerates [verify]: delete those lines]. [changed in Lyrical: `publish_rate` removed]. The wheel `min`/`max` of ±1 rad/s now clamp the commands (`enforce_command_limits`) ([[control-diff-drive-controller]]).

## Dynamixel
`dynamixel_hardware` (the code of the course) is not released for Lyrical; ROBOTIS's `dynamixel_hardware_interface` (1.5.1) is ([[control-dynamixel-sdk]]).

## Pitfalls
- A YAML that relied on `goal_time: 0.0` for "no timeout" aborts late goals on Lyrical: set `-1.0`.
- A hardware component that still exports its own pointers fails to compile on Lyrical, it does not fall back.
