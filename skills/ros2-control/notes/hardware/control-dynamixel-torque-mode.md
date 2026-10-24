---
id: control-dynamixel-torque-mode
type: reference
owner: equipo-ros2
updated: 2026-10-24
review_by: 2027-04-22
source: manual
confidentiality: internal
title: "Dynamixel enable_torque, set_control_mode (position/velocity), reset_command"
domain: control
area: hardware
distro: jazzy
tested: false
audience: dev
summary: "DynamixelHardware helpers: enable_torque (torqueOn/torqueOff, torque_enabled_ flag), set_control_mode (torque off, setVelocity/PositionControlMode, torque on), reset_command."
tags: [enable_torque, torqueOn, torqueOff, torque_enabled_, set_control_mode, setVelocityControlMode, setPositionControlMode, force_set, ControlMode, reset_command, operating mode]
see: ["[[control-dynamixel-init]]", "[[control-dynamixel-read-write]]", "[[control-dynamixel-interfaces-activate]]", "[[control-dynamixel-header]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: logic: the first enable_torque(false) does nothing (the flag starts false), and a mode switch zeroes the commands of that cycle through reset_command() (CONTROL-V49)"
---
# Dynamixel enable_torque, set_control_mode (position/velocity), reset_command

**TL;DR** Three private helpers. `enable_torque()` switches the motors' torque on or off for all joints; `set_control_mode()` changes every servo to velocity or position mode, with the torque off while it does; `reset_command()` makes the command equal to the current state, a fresh start for the control algorithm.

## enable_torque()
```cpp
return_type DynamixelHardware::enable_torque(const bool enabled)
{
  const char * log = nullptr;

  if (enabled && !torque_enabled_) {
    for (uint i = 0; i < info_.joints.size(); ++i) {
      if (!dynamixel_workbench_.torqueOn(joint_ids_[i], &log)) {
        RCLCPP_FATAL(rclcpp::get_logger(kDynamixelHardware), "%s", log);
        return return_type::ERROR;
      }
    }
    reset_command();
    RCLCPP_INFO(rclcpp::get_logger(kDynamixelHardware), "Torque enabled");
  } else if (!enabled && torque_enabled_) {
    for (uint i = 0; i < info_.joints.size(); ++i) {
      if (!dynamixel_workbench_.torqueOff(joint_ids_[i], &log)) {
        RCLCPP_FATAL(rclcpp::get_logger(kDynamixelHardware), "%s", log);
        return return_type::ERROR;
      }
    }
    RCLCPP_INFO(rclcpp::get_logger(kDynamixelHardware), "Torque disabled");
  }

  torque_enabled_ = enabled;
  return return_type::OK;
}
```
A wrapper around the Workbench's `torqueOn()`/`torqueOff()`: it acts only when the requested state differs from the flag `torque_enabled_`, and resets the commands when torque comes on.

## set_control_mode()
```cpp
return_type DynamixelHardware::set_control_mode(const ControlMode & mode, const bool force_set)
{
  const char * log = nullptr;

  if (mode == ControlMode::Velocity && (force_set || control_mode_ != ControlMode::Velocity)) {
    bool torque_enabled = torque_enabled_;
    if (torque_enabled) {
      enable_torque(false);
    }

    for (uint i = 0; i < joint_ids_.size(); ++i) {
      if (!dynamixel_workbench_.setVelocityControlMode(joint_ids_[i], &log)) {
        RCLCPP_FATAL(rclcpp::get_logger(kDynamixelHardware), "%s", log);
        return return_type::ERROR;
      }
    }
    RCLCPP_INFO(rclcpp::get_logger(kDynamixelHardware), "Velocity control");
    control_mode_ = ControlMode::Velocity;

    if (torque_enabled) {
      enable_torque(true);
    }
  } else if (mode == ControlMode::Position && (force_set || control_mode_ != ControlMode::Position)) {
    bool torque_enabled = torque_enabled_;
    if (torque_enabled) {
      enable_torque(false);
    }

    for (uint i = 0; i < joint_ids_.size(); ++i) {
      if (!dynamixel_workbench_.setPositionControlMode(joint_ids_[i], &log)) {
        RCLCPP_FATAL(rclcpp::get_logger(kDynamixelHardware), "%s", log);
        return return_type::ERROR;
      }
    }
    RCLCPP_INFO(rclcpp::get_logger(kDynamixelHardware), "Position control");
    control_mode_ = ControlMode::Position;

    if (torque_enabled) {
      enable_torque(true);
    }
  } else if (control_mode_ != ControlMode::Velocity && control_mode_ != ControlMode::Position) {
    RCLCPP_FATAL(
      rclcpp::get_logger(kDynamixelHardware), "Only position/velocity control are implemented");
    return return_type::ERROR;
  }

  return return_type::OK;
}
```
The Workbench's `setVelocityControlMode()` and `setPositionControlMode()` change all controlled servos at once; other operating modes are not implemented. `force_set` (used by `on_init()`) writes the mode even if the flag says it is already set.

## reset_command()
```cpp
return_type DynamixelHardware::reset_command()
{
  for (uint i = 0; i < joints_.size(); i++) {
    joints_[i].command.position = joints_[i].state.position;
    joints_[i].command.velocity = 0.0;
    joints_[i].command.effort = 0.0;
  }

  return return_type::OK;
}
```
Command = state removes the control error, so the joint holds where it is: useful at start-up and after a mode change.

## Pitfalls
- `torque_enabled_` starts `false`, so the first `enable_torque(false)` of `on_init()` sends nothing: servos that still have torque on from a previous run keep it while the mode is written (whether the servo then refuses the mode change depends on its control table [verify]).
- Every mode switch passes through `enable_torque(true)`, which calls `reset_command()`: in the `write()` cycle that switches to velocity mode the velocity commands are zeroed before they are sent, so the servos get 0 for one cycle.
- The return values of `enable_torque()` and `set_control_mode()` are not checked by `on_init()` and `write()`.
