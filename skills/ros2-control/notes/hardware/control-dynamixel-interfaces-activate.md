---
id: control-dynamixel-interfaces-activate
type: reference
owner: equipo-ros2
updated: 2026-10-24
review_by: 2027-04-22
source: manual
confidentiality: internal
title: "Dynamixel export_state/command_interfaces, on_activate (dummy init, read/reset/write), on_deactivate"
domain: control
area: hardware
distro: jazzy
tested: false
audience: dev
summary: "Dynamixel exports position/velocity/effort states and position/velocity commands; on_activate zeroes dummy states, runs read, reset_command, write; on_deactivate only logs."
tags: [export_state_interfaces, export_command_interfaces, HW_IF_POSITION, HW_IF_VELOCITY, HW_IF_EFFORT, on_activate, on_deactivate, use_dummy, reset_command, rclcpp::Duration, rclcpp::Time, torque]
see: ["[[control-dynamixel-init]]", "[[control-dynamixel-read-write]]", "[[control-dynamixel-torque-mode]]", "[[control-hw-template-export]]", "[[control-dynamixel-plugin-urdf-launch]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: the explained snippet uses a member hw_joint_state_ that the class does not have (CONTROL-V47)"
  - "jazzy: the effort state holds a current in mA (CONTROL-V14)"
  - "jazzy: on_activate ignores the results of read()/write() and on_deactivate leaves the torque on (CONTROL-V48)"
  - "jazzy: export_* deprecated, removed in lyrical (CONTROL-V19)"
---
# Dynamixel export_state/command_interfaces, on_activate (dummy init, read/reset/write), on_deactivate

**TL;DR** The servos report position, velocity and current, and accept position and velocity goals, so three state and two command interfaces per joint point into `joints_`. `on_activate()` makes the command equal to the state and sends it once, so the servos hold where they are.

## Exports
```cpp
std::vector<hardware_interface::StateInterface> DynamixelHardware::export_state_interfaces()
{
  RCLCPP_DEBUG(rclcpp::get_logger(kDynamixelHardware), "export_state_interfaces");
  std::vector<hardware_interface::StateInterface> state_interfaces;
  for (uint i = 0; i < info_.joints.size(); i++) {
    state_interfaces.emplace_back(hardware_interface::StateInterface(
      info_.joints[i].name, hardware_interface::HW_IF_POSITION, &joints_[i].state.position));
    state_interfaces.emplace_back(hardware_interface::StateInterface(
      info_.joints[i].name, hardware_interface::HW_IF_VELOCITY, &joints_[i].state.velocity));
    state_interfaces.emplace_back(hardware_interface::StateInterface(
      info_.joints[i].name, hardware_interface::HW_IF_EFFORT, &joints_[i].state.effort));
  }

  return state_interfaces;
}

std::vector<hardware_interface::CommandInterface> DynamixelHardware::export_command_interfaces()
{
  RCLCPP_DEBUG(rclcpp::get_logger(kDynamixelHardware), "export_command_interfaces");
  std::vector<hardware_interface::CommandInterface> command_interfaces;
  for (uint i = 0; i < info_.joints.size(); i++) {
    command_interfaces.emplace_back(hardware_interface::CommandInterface(
      info_.joints[i].name, hardware_interface::HW_IF_POSITION, &joints_[i].command.position));
    command_interfaces.emplace_back(hardware_interface::CommandInterface(
      info_.joints[i].name, hardware_interface::HW_IF_VELOCITY, &joints_[i].command.velocity));
  }

  return command_interfaces;
}
```
The firmware has more operating modes (current and others); only position and velocity are registered. Export only the values the hardware really provides: here `effort` carries the current in mA that `read()` converts ([[control-dynamixel-read-write]]). The URDF must declare the same interfaces ([[control-dynamixel-plugin-urdf-launch]]).

## on_activate() and on_deactivate()
```cpp
CallbackReturn DynamixelHardware::on_activate(const rclcpp_lifecycle::State & /*previous_state*/)
{
  RCLCPP_DEBUG(rclcpp::get_logger(kDynamixelHardware), "start");
  for (uint i = 0; i < joints_.size(); i++) {
    if (use_dummy_ && std::isnan(joints_[i].state.position)) {
      joints_[i].state.position = 0.0;
      joints_[i].state.velocity = 0.0;
      joints_[i].state.effort = 0.0;
    }
  }

  // Create a zero duration explicitly
  rclcpp::Duration zero_duration(0, 0);
  // Or: auto zero_duration = rclcpp::Duration::from_seconds(0.0);

  // Time can be default-constructed or taken from a clock; you're ignoring it
  // anyway
  rclcpp::Time now;  // or rclcpp::Clock().now();

  read(now, zero_duration);
  reset_command();
  write(now, zero_duration);

  return CallbackReturn::SUCCESS;
}

CallbackReturn DynamixelHardware::on_deactivate(const rclcpp_lifecycle::State & /*previous_state*/)
{
  RCLCPP_DEBUG(rclcpp::get_logger(kDynamixelHardware), "stop");
  return CallbackReturn::SUCCESS;
}
```
- In dummy mode the states are still `NaN` from `on_init()`: they start at 0.
- `read()` gets the real positions, `reset_command()` copies them into the commands (velocity and effort commands 0), `write()` sends them: the servos hold their current position and the three methods are exercised once. `read()`/`write()` ignore `time` and `period`, so a default `rclcpp::Time` and a zero `Duration` are enough.
- `on_deactivate()` needs no bus action for these servos: only a debug log.

## Pitfalls
- `on_activate()` returns `SUCCESS` even if `read()` or `write()` failed (their results are not checked): check them if activation must fail without a bus.
- Torque stays on after deactivation, so the servos keep holding their last goal; call `enable_torque(false)` in `on_deactivate()` if the robot must go limp.
