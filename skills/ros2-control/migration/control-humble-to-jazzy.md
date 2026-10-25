---
id: control-humble-to-jazzy
type: reference
owner: equipo-ros2
updated: 2026-10-24
review_by: 2027-04-22
source: manual
confidentiality: internal
title: "Humble vs Jazzy: hardware interface API, robot_description, CLI, controller parameters"
domain: control
area: migration
distro: jazzy
tested: false
audience: dev
order: 1
summary: "Run the course on Humble: on_init(HardwareInfo), robot_description parameter, CLI, JTC and diff_drive parameters, custom controller set_value/get_value, realtime_tools, Dynamixel."
tags: [humble, jazzy, migration, on_init, HardwareInfo, HardwareComponentInterfaceParams, robot_description, set_controller_state, cleanup_controller, state_publish_rate, enforce_command_limits, get_logger, porting]
see: ["[[control-hw-template-header]]", "[[control-hw-template-init]]", "[[control-bringup-hardware-launch]]", "[[control-cli-state-changes]]", "[[control-jtc-parameters]]", "[[control-diff-drive-controller]]", "[[control-custom-activate-update]]", "[[control-jazzy-to-lyrical]]", "[[core-ros2-control-overview]]"]
requires: [ros2-core]
version_notes:
  - "humble: on_init(const HardwareInfo & info) and SystemInterface::on_init(info), from the official humble demo — https://github.com/ros-controls/ros2_control_demos/blob/humble/example_1/hardware/rrbot.cpp (CONTROL-V18)"
  - "humble: no node per component, no get_logger()/get_clock() members — https://github.com/ros-controls/ros2_control/blob/humble/hardware_interface/include/hardware_interface/system_interface.hpp (CONTROL-V20)"
  - "humble: the controller manager needs robot_description as a parameter (V60, CONTROL-V23)"
  - "humble: CLI and services: no unconfigured state, no cleanup_controller, no logger or type-description services; ControllerState without is_async/update_rate (CONTROL-V24, CONTROL-V25, CONTROL-V26)"
  - "humble: void set_value and double get_value (the course appendix form) — https://github.com/ros-controls/ros2_control/blob/humble/hardware_interface/include/hardware_interface/handle.hpp (CONTROL-V74)"
  - "humble: realtime_tools 2.15 without RealtimeThreadSafeBox and try_publish — https://github.com/ros-controls/realtime_tools/blob/humble/include/realtime_tools/realtime_publisher.hpp (CONTROL-V73)"
  - "humble: diff_drive_controller use_stamped_vel (false = Twist on ~/cmd_vel_unstamped), has_*_limits default false — https://github.com/ros-controls/ros2_controllers/blob/humble/diff_drive_controller/src/diff_drive_controller_parameter.yaml (CONTROL-V67, CONTROL-V68)"
  - "humble: JTC also publishes ~/state; JointTrajectoryControllerState with desired/actual — https://github.com/ros-controls/ros2_controllers/blob/humble/joint_trajectory_controller/src/joint_trajectory_controller.cpp (CONTROL-V66)"
  - "humble: interface configurations ALL/INDIVIDUAL/NONE; controller nodes allow undeclared parameters; update() ERROR only logged; no introspection/activity/statistics topics — https://github.com/ros-controls/ros2_control/blob/humble/controller_interface/include/controller_interface/controller_interface_base.hpp (CONTROL-V76, CONTROL-V77, CONTROL-V71)"
---
# Humble vs Jazzy: hardware interface API, robot_description, CLI, controller parameters

**TL;DR** The course is written for Jazzy. On Humble the YAML, URDF tags, CLI and launch files work with small differences; the hardware interface code of units 4 and 5 needs the Humble `on_init()` signature, and the custom controller of unit 7 the older `set_value()`/`get_value()` lines. Every Humble form below comes from the official `humble` branches.

## Hardware interface (units 4 and 5)
The course's `on_init(const HardwareComponentInterfaceParams & params)` and its header `hardware_interface/types/hardware_component_interface_params.hpp` do not exist in Humble (ros2_control 2.54). Header:
```cpp
hardware_interface::CallbackReturn on_init(
  const hardware_interface::HardwareInfo & info) override;
```
Source, as in the official Humble demo (ros2_control_demos example_1, Apache-2.0):
```cpp
hardware_interface::CallbackReturn RRBotSystemPositionOnlyHardware::on_init(
  const hardware_interface::HardwareInfo & info)
{
  if (
    hardware_interface::SystemInterface::on_init(info) !=
    hardware_interface::CallbackReturn::SUCCESS)
  {
    return hardware_interface::CallbackReturn::ERROR;
  }
  // ... the rest uses info_ (the member), e.g. info_.hardware_parameters, info_.joints
  return hardware_interface::CallbackReturn::SUCCESS;
}
```
- Drop the `hardware_component_interface_params.hpp` include, and replace `params.hardware_info` with `info_` (the template's `const auto & info = params.hardware_info;` becomes `const auto & info = info_;`). The Dynamixel `on_init()` changes the same way.
- `export_state_interfaces()`/`export_command_interfaces()` with pointers into member vectors are the normal way in Humble: the course code stays as it is ([[control-hw-template-export]]).
- No `get_logger()`/`get_clock()` members and no node per component: log with `rclcpp::get_logger("…")`, as the course does.
- `HW_IF_*` constants: only position, velocity, acceleration and effort; write other interface names as strings.
- No `enforce_command_limits`: the controller manager does not clamp commands to `min`/`max` or URDF limits.

## Launch and description
- `ros2_control_node` takes `robot_description` as a **parameter**: the course's real-hardware launch already passes it ([[control-bringup-hardware-launch]]). Jazzy ignores it and reads the topic.
- In simulation, gz_ros2_control on Humble (with Fortress) reads the description parameter of the node `robot_state_publisher`: ros2-gazebo skill, `gazebo-migration-fortress`.

## CLI, services, spawner
- `set_controller_state` accepts only `inactive` and `active`: to clean up, unload and load again ([[control-cli-state-changes]]). `load_controller --set-state` also accepts `configured`.
- No `/controller_manager/cleanup_controller`, `get/set_logger_levels` or `get_type_description` services; `ListControllers` has no `is_async`, `update_rate`, `exported_state_interfaces` ([[control-services-spawner]]).
- `switch_controllers` prints only "Successfully switched controllers"; `--start`/`--stop` are deprecated aliases of `--activate`/`--deactivate`.
- Spawner: same main options; `--stopped` is an older name of `--inactive`; no `--controller-ros-args`.
- An inactive forward controller stores incoming commands without a warning and drops them on activation.

## Controller parameters
- JTC: `state_publish_rate` is a parameter (default 50.0); `open_loop_control` is not deprecated; `goal_time: 0.0` means no time limit, as in Jazzy ([[control-jtc-parameters]]). JTC also publishes the older `~/state`, and `JointTrajectoryControllerState` has `desired` and `actual` besides `reference`/`feedback`/`error`/`output` ([[control-jtc-commands]]).
- diff_drive_controller (units 6, [[control-diff-drive-controller]]): `use_stamped_vel` exists (default `true`). Keep it `true` to receive the course's TwistStamped on `~/cmd_vel`; with the course's `false` the controller listens to `geometry_msgs/msg/Twist` on `~/cmd_vel_unstamped`. `has_velocity_limits`/`has_acceleration_limits` default to `false`: the limits apply only with them set to `true`, as the course file does.

## Custom controller (unit 7)
- `set_value()` returns nothing and `get_optional()` does not exist: write the two lines of `update()` in the form of the course's appendix ([[control-custom-activate-update]]):
```cpp
      command_interfaces_[i].set_value((*current_command)->displacements[i]);
```
```cpp
    state_publisher_->msg_.set_point = command_interfaces_[0].get_value();
```
- realtime_tools 2.15: `RealtimeBuffer` and `RealtimePublisher` (`trylock()`, `msg_`, `unlockAndPublish()`) as in the course; include the `.hpp` headers (the `.h` ones print a deprecation message); no `RealtimeThreadSafeBox`, no `try_publish()`.
- Interface configuration types: `ALL`, `INDIVIDUAL`, `NONE` only ([[control-custom-interfaces]]).
- Controller nodes accept undeclared parameters and declare the YAML keys automatically; an `ERROR` from `update()` is only logged, the controller stays active ([[control-custom-init]]).
- No `/controller_manager/introspection_data/*`, `/activity` or `/statistics/*` topics.

## Dynamixel packages
`dynamixel_hardware` is not released for Humble; ROBOTIS's `dynamixel_hardware_interface` (1.5.0) is, and `ros-humble-dynamixel-sdk` and `ros-humble-dynamixel-workbench-toolbox` install the SDK ([[control-dynamixel-sdk]]).

## Pitfalls
- Mixing: a Jazzy example (`on_init(params)`, `set_state()`) does not compile on Humble; a Humble example compiles on Jazzy with deprecation warnings but not on Lyrical ([[control-jazzy-to-lyrical]]).
