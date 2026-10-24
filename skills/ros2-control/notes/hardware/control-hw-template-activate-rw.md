---
id: control-hw-template-activate-rw
type: reference
owner: equipo-ros2
updated: 2026-10-24
review_by: 2027-04-22
source: manual
confidentiality: internal
title: "Template on_activate, on_deactivate, read (simulated movement), write"
domain: control
area: hardware
distro: jazzy
tested: false
audience: dev
summary: "RRBot template on_activate (command = state), on_deactivate (graceful stop), read (state += error/slowdown), write (log commands); Jazzy set_state/get_command form."
tags: [on_activate, on_deactivate, read, write, return_type, hw_slowdown_, hw_stop_sec_, RCLCPP_INFO_THROTTLE, set_state, get_state, get_command, joint_state_interfaces_]
see: ["[[control-hw-template-export]]", "[[control-hw-template-init]]", "[[control-hw-interface-concept]]", "[[control-overview]]", "[[control-learn-unit4-template]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: official demo read() with get_state()/get_command()/set_state() and RCLCPP_INFO_THROTTLE, Apache-2.0 — https://github.com/ros-controls/ros2_control_demos/blob/jazzy/example_1/hardware/rrbot.cpp (CONTROL-V19)"
  - "jazzy: ERROR from read()/write() calls on_error(); SUCCESS → unconfigured, otherwise finalized — https://github.com/ros-controls/ros2_control/blob/jazzy/hardware_interface/doc/handling_errors_during_read_write.rst"
---
# Template on_activate, on_deactivate, read (simulated movement), write

**TL;DR** `on_activate()` powers the hardware up and makes the command equal to the state (no jump at start); `on_deactivate()` stops it cleanly; in every control cycle `read()` fills the states before the controllers run and `write()` sends their commands. The template only logs and simulates a slow joint: put your driver calls in these bodies.

## on_activate() and on_deactivate()
```cpp
CallbackReturn RRBotSystemPositionOnlyHardware::on_activate(
  const rclcpp_lifecycle::State & /*previous_state*/)
{
  // START: This part here is for exemplary purposes - Please do not copy it to your production code
  RCLCPP_INFO(rclcpp::get_logger("RRBotSystemPositionOnlyHardware"), "Activating ...please wait...");

  for (int i = 0; i < hw_start_sec_; i++)
  {
    rclcpp::sleep_for(std::chrono::seconds(1));
    RCLCPP_INFO(
      rclcpp::get_logger("RRBotSystemPositionOnlyHardware"), "%.1f seconds left...",
      hw_start_sec_ - i);
  }
  // END: This part here is for exemplary purposes - Please do not copy to your production code

  // command and state should be equal when starting
  for (uint i = 0; i < hw_states_.size(); i++)
  {
    hw_commands_[i] = hw_states_[i];
  }

  RCLCPP_INFO(rclcpp::get_logger("RRBotSystemPositionOnlyHardware"), "Successfully activated!");

  return CallbackReturn::SUCCESS;
}

CallbackReturn RRBotSystemPositionOnlyHardware::on_deactivate(
  const rclcpp_lifecycle::State & /*previous_state*/)
{
  // START: This part here is for exemplary purposes - Please do not copy to your production code
  RCLCPP_INFO(rclcpp::get_logger("RRBotSystemPositionOnlyHardware"), "Deactivating ...please wait...");

  for (int i = 0; i < hw_stop_sec_; i++)
  {
    rclcpp::sleep_for(std::chrono::seconds(1));
    RCLCPP_INFO(
      rclcpp::get_logger("RRBotSystemPositionOnlyHardware"), "%.1f seconds left...",
      hw_stop_sec_ - i);
  }

  RCLCPP_INFO(rclcpp::get_logger("RRBotSystemPositionOnlyHardware"), "Successfully deactivated!");
  // END: This part here is for exemplary purposes - Please do not copy to your production code

  return CallbackReturn::SUCCESS;
}
```
With the URDF of the course (`example_param_hw_stop_duration_sec` = 3.0) deactivating takes 3 s.

## read() and write()
```cpp
hardware_interface::return_type
RRBotSystemPositionOnlyHardware::read(
  const rclcpp::Time & /*time*/, const rclcpp::Duration & /*period*/)
{
  RCLCPP_INFO(rclcpp::get_logger("RRBotSystemPositionOnlyHardware"), "Reading...");

  for (uint i = 0; i < hw_states_.size(); i++) {
    // Simulate RRBot's movement
    hw_states_[i] =
      hw_states_[i] + (hw_commands_[i] - hw_states_[i]) / hw_slowdown_;
    RCLCPP_INFO(
      rclcpp::get_logger("RRBotSystemPositionOnlyHardware"),
      "Got state %.5f for joint %d!", hw_states_[i], i);
  }
  RCLCPP_INFO(rclcpp::get_logger("RRBotSystemPositionOnlyHardware"), "Joints successfully read!");

  return hardware_interface::return_type::OK;
}

hardware_interface::return_type
RRBotSystemPositionOnlyHardware::write(
  const rclcpp::Time & /*time*/, const rclcpp::Duration & /*period*/)
{
  RCLCPP_INFO(rclcpp::get_logger("RRBotSystemPositionOnlyHardware"), "Writing...");

  for (uint i = 0; i < hw_commands_.size(); i++) {
    // Simulate sending commands to the hardware
    RCLCPP_INFO(
      rclcpp::get_logger("RRBotSystemPositionOnlyHardware"),
      "Got command %.5f for joint %d!", hw_commands_[i], i);
  }
  RCLCPP_INFO(rclcpp::get_logger("RRBotSystemPositionOnlyHardware"), "Joints successfully written!");

  return hardware_interface::return_type::OK;
}
```
`read()` moves each state a fraction `1 / hw_slowdown_` (here 1/10) of the remaining error towards the command, every cycle; the console shows these logs while the loop runs.

## [≥Jazzy] the same read() with the framework's interfaces
From the official Jazzy demo (ros2_control_demos example_1, Apache-2.0):
```cpp
for (const auto & [name, descr] : joint_state_interfaces_)
{
  // Simulate RRBot's movement
  auto new_value = get_state(name) + (get_command(name) - get_state(name)) / hw_slowdown_;
  set_state(name, new_value);
}
```
It logs with `RCLCPP_INFO_THROTTLE(get_logger(), *get_clock(), 500, …)` instead of every cycle.

## Pitfalls
- Logging in `read()`/`write()` without throttling floods the console at the loop rate (and costs time in a real-time loop).
- `read()`/`write()` returning `ERROR` calls the component's `on_error()`: on `SUCCESS` it goes back to unconfigured, otherwise it ends finalized and only reloading the plugin recovers it (official docs, "Handling of Errors During read() and write() Calls"). Return `ERROR` only for real failures.
