---
id: control-hw-template-init
type: reference
owner: equipo-ros2
updated: 2026-10-24
review_by: 2027-04-22
source: manual
confidentiality: internal
title: "Template on_init (hardware parameters, the four interface checks) and on_configure"
domain: control
area: hardware
distro: jazzy
tested: false
audience: dev
summary: "RRBot template on_init: base on_init(params), hardware_parameters.at(), resize state/command vectors, four interface checks; on_configure resets values."
tags: [on_init, on_configure, HardwareComponentInterfaceParams, hardware_info, hardware_parameters, ComponentInfo, command_interfaces, state_interfaces, HW_IF_POSITION, RCLCPP_FATAL, CallbackReturn, quiet_NaN]
see: ["[[control-hw-template-header]]", "[[control-hw-template-export]]", "[[control-urdf-tag]]", "[[control-controller-lifecycle]]", "[[control-humble-to-jazzy]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: HardwareComponentInterface::on_init(params) is the same call as SystemInterface::on_init(params) of the official demo: it fills info_ and parses the interfaces — https://github.com/ros-controls/ros2_control/blob/jazzy/hardware_interface/src/hardware_component_interface.cpp (CONTROL-V39)"
  - "humble: on_init(const HardwareInfo & info) calling SystemInterface::on_init(info) — https://github.com/ros-controls/ros2_control_demos/blob/humble/example_1/hardware/rrbot.cpp (CONTROL-V18)"
  - "jazzy: the official demo resets values with set_state()/set_command() and logs with get_logger() — https://github.com/ros-controls/ros2_control_demos/blob/jazzy/example_1/hardware/rrbot.cpp (CONTROL-V19)"
  - "jazzy: guide: on_init initialises members and parameters, on_configure sets up the communication — https://github.com/ros-controls/ros2_control/blob/jazzy/hardware_interface/doc/writing_new_hardware_component.rst"
---
# Template on_init (hardware parameters, the four interface checks) and on_configure

**TL;DR** `on_init()` is called first: let the base class parse the `<ros2_control>` tag, read your parameters, size your storage and reject a URDF you cannot drive. `on_configure()` opens the communication so that states can be read; the template only waits and resets the values.

## on_init()
```cpp
CallbackReturn RRBotSystemPositionOnlyHardware::on_init(
  const hardware_interface::HardwareComponentInterfaceParams & params)
{
  if (hardware_interface::HardwareComponentInterface::on_init(params) !=
    CallbackReturn::SUCCESS)
  {
    return CallbackReturn::ERROR;
  }

  const auto & info = params.hardware_info;

  // START: This part here is for exemplary purposes - Please do not copy to
  // your production code
  hw_start_sec_ = std::stod(info.hardware_parameters.at("example_param_hw_start_duration_sec"));
  hw_stop_sec_ = std::stod(info.hardware_parameters.at("example_param_hw_stop_duration_sec"));
  hw_slowdown_ =
    std::stod(info.hardware_parameters.at("example_param_hw_slowdown"));
  // END: This part here is for exemplary purposes - Please do not copy to your
  // production code

  hw_states_.resize(info.joints.size(), std::numeric_limits<double>::quiet_NaN());
  hw_commands_.resize(info.joints.size(), std::numeric_limits<double>::quiet_NaN());

  for (const hardware_interface::ComponentInfo & joint : info.joints) {
    // RRBotSystemPositionOnly has exactly one state and command interface on
    // each joint
    if (joint.command_interfaces.size() != 1) {
      RCLCPP_FATAL(
        rclcpp::get_logger("RRBotSystemPositionOnlyHardware"),
        "Joint '%s' has %zu command interfaces found. 1 expected.",
        joint.name.c_str(), joint.command_interfaces.size());
      return CallbackReturn::ERROR;
    }

    if (joint.command_interfaces[0].name != hardware_interface::HW_IF_POSITION) {
      RCLCPP_FATAL(
        rclcpp::get_logger("RRBotSystemPositionOnlyHardware"),
        "Joint '%s' have %s command interfaces found. '%s' expected.",
        joint.name.c_str(), joint.command_interfaces[0].name.c_str(),
        hardware_interface::HW_IF_POSITION);
      return CallbackReturn::ERROR;
    }

    if (joint.state_interfaces.size() != 1) {
      RCLCPP_FATAL(
        rclcpp::get_logger("RRBotSystemPositionOnlyHardware"),
        "Joint '%s' has %zu state interface. 1 expected.",
        joint.name.c_str(), joint.state_interfaces.size());
      return CallbackReturn::ERROR;
    }

    if (joint.state_interfaces[0].name != hardware_interface::HW_IF_POSITION) {
      RCLCPP_FATAL(
        rclcpp::get_logger("RRBotSystemPositionOnlyHardware"),
        "Joint '%s' have %s state interface. '%s' expected.",
        joint.name.c_str(), joint.state_interfaces[0].name.c_str(),
        hardware_interface::HW_IF_POSITION);
      return CallbackReturn::ERROR;
    }
  }

  return CallbackReturn::SUCCESS;
}
```
- The base `on_init(params)` copies `params.hardware_info` (everything parsed from `<ros2_control>`) into the member `info_` and parses the interface descriptions; on failure return `ERROR`. The official demo calls `SystemInterface::on_init(params)`: the same function.
- `hardware_parameters` holds the `<param>` values of `<hardware>` as strings ([[control-urdf-tag]]): convert them (`std::stod`).
- States and commands start as `NaN` (no valid value read or sent yet); one entry per joint.
- The four optional checks: exactly one command interface, of type position; exactly one state interface, of type position. Any other URDF makes `on_init()` return `ERROR` and the component is not loaded.

## on_configure()
```cpp
CallbackReturn RRBotSystemPositionOnlyHardware::on_configure(
  const rclcpp_lifecycle::State & previous_state)
{
  // START: This part here is for exemplary purposes - Please do not copy to
  // your production code
  // prevent unused variable warning
  auto prev_state = previous_state;
  RCLCPP_INFO(
    rclcpp::get_logger("RRBotSystemPositionOnlyHardware"), "Configuring ...please wait...");

  for (int i = 0; i < hw_start_sec_; i++) {
    rclcpp::sleep_for(std::chrono::seconds(1));
    RCLCPP_INFO(
      rclcpp::get_logger("RRBotSystemPositionOnlyHardware"), "%.1f seconds left...",
      hw_start_sec_ - i);
  }
  // END: This part here is for exemplary purposes - Please do not copy to your
  // production code

  // reset values always when configuring hardware
  for (uint i = 0; i < hw_states_.size(); i++) {
    hw_states_[i] = 0;
    hw_commands_[i] = 0;
  }

  RCLCPP_INFO(rclcpp::get_logger("RRBotSystemPositionOnlyHardware"), "Successfully configured!");

  return CallbackReturn::SUCCESS;
}
```
With `example_param_hw_start_duration_sec` = 0.0 in the URDF the wait loop does not run. A real driver opens the port here. An unnamed parameter (`const rclcpp_lifecycle::State & /*previous_state*/`) avoids the unused warning without the copy.

## Versions
[Humble: `on_init(const hardware_interface::HardwareInfo & info)` and `hardware_interface::SystemInterface::on_init(info)`, then use `info_` ([[control-humble-to-jazzy]])]. [≥Jazzy: the official demo logs with the member `get_logger()` and resets with `set_state(name, 0.0)` / `set_command(name, 0.0)` over the interfaces the framework exported, instead of member vectors].

## Pitfalls
- `.at("…")` throws if the `<param>` is missing from the URDF: every parameter you read must be declared there.
- The official guide: `on_init()` initialises members and processes the parameters, `on_configure()` is where you usually set up the communication with the hardware (the Dynamixel code of [[control-dynamixel-init]] opens the port in `on_init()`, as its upstream package does).
