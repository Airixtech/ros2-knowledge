---
id: control-dynamixel-read-write
type: reference
owner: equipo-ros2
updated: 2026-10-24
review_by: 2027-04-22
source: manual
confidentiality: internal
title: "Dynamixel read (syncRead, getSyncReadData, unit conversion) and write (velocity, effort, position branches)"
domain: control
area: hardware
distro: jazzy
tested: false
audience: dev
summary: "Dynamixel read: syncRead, getSyncReadData, rad/rad/s/mA conversion; write: velocity if any velocity command, effort error, else position; dummy mirror."
tags: [read, write, syncRead, getSyncReadData, syncWrite, convertValue2Radian, convertValue2Velocity, convertValue2Current, convertVelocity2Value, convertRadian2Value, use_dummy, velocity control, position control, effort control]
see: ["[[control-dynamixel-init]]", "[[control-dynamixel-torque-mode]]", "[[control-dynamixel-interfaces-activate]]", "[[control-hw-template-activate-rw]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: conversions are rad, rad/s and mA (the course says m/s and m/A) — https://github.com/ROBOTIS-GIT/dynamixel-workbench/blob/ros2/dynamixel_workbench_toolbox/src/dynamixel_workbench_toolbox/dynamixel_workbench.cpp (CONTROL-V14)"
  - "jazzy: a Present_Load fallback is converted with the current unit, so effort is not a current on those servos (CONTROL-V37)"
  - "jazzy: read() returns OK after a failed Sync Read and converts the zero-initialised raw values (CONTROL-V48)"
---
# Dynamixel read (syncRead, getSyncReadData, unit conversion) and write (velocity, effort, position branches)

**TL;DR** `read()` gets position, velocity and current of all servos in one Sync Read and converts them to joint units; `write()` sends velocity goals if any joint has a non-zero velocity command, refuses effort, and otherwise sends position goals, each in one Sync Write. In dummy mode no bus is used: the position command becomes the state.

## read()
```cpp
return_type DynamixelHardware::read(
  const rclcpp::Time & /*time*/, const rclcpp::Duration & /*period*/)
{
  if (use_dummy_) {
    return return_type::OK;
  }

  std::vector<uint8_t> ids(info_.joints.size(), 0);
  std::vector<int32_t> positions(info_.joints.size(), 0);
  std::vector<int32_t> velocities(info_.joints.size(), 0);
  std::vector<int32_t> currents(info_.joints.size(), 0);

  std::copy(joint_ids_.begin(), joint_ids_.end(), ids.begin());
  const char * log = nullptr;

  if (!dynamixel_workbench_.syncRead(kPresentPositionVelocityCurrentIndex,
      ids.data(), ids.size(), &log))
  {
    RCLCPP_ERROR(rclcpp::get_logger(kDynamixelHardware), "%s", log);
  }

  if (!dynamixel_workbench_.getSyncReadData(
      kPresentPositionVelocityCurrentIndex, ids.data(), ids.size(),
      control_items_[kPresentCurrentItem]->address,
      control_items_[kPresentCurrentItem]->data_length, currents.data(), &log))
  {
    RCLCPP_ERROR(rclcpp::get_logger(kDynamixelHardware), "%s", log);
  }

  if (!dynamixel_workbench_.getSyncReadData(
      kPresentPositionVelocityCurrentIndex, ids.data(), ids.size(),
      control_items_[kPresentVelocityItem]->address,
      control_items_[kPresentVelocityItem]->data_length, velocities.data(), &log))
  {
    RCLCPP_ERROR(rclcpp::get_logger(kDynamixelHardware), "%s", log);
  }

  if (!dynamixel_workbench_.getSyncReadData(
      kPresentPositionVelocityCurrentIndex, ids.data(), ids.size(),
      control_items_[kPresentPositionItem]->address,
      control_items_[kPresentPositionItem]->data_length, positions.data(), &log))
  {
    RCLCPP_ERROR(rclcpp::get_logger(kDynamixelHardware), "%s", log);
  }

  for (uint i = 0; i < ids.size(); i++) {
    joints_[i].state.position = dynamixel_workbench_.convertValue2Radian(ids[i], positions[i]);
    joints_[i].state.velocity = dynamixel_workbench_.convertValue2Velocity(ids[i], velocities[i]);
    joints_[i].state.effort = dynamixel_workbench_.convertValue2Current(currents[i]);
  }

  return return_type::OK;
}
```
- Dummy mode: nothing to read.
- Local vectors (one entry per joint, 0), a copy of the ids, a `log` pointer for the Workbench's messages.
- `syncRead()` reads the block of all pinged servos; `getSyncReadData()` extracts current, velocity and position from it.
- Conversions from the raw 32-bit values: `convertValue2Radian` → rad, `convertValue2Velocity` → **rad/s**, `convertValue2Current` → **mA** (the course says m/s and m/A). The `effort` state therefore holds a current, not a torque.

## write()
```cpp
return_type DynamixelHardware::write(
  const rclcpp::Time & /*time*/, const rclcpp::Duration & /*period*/)
{
  if (use_dummy_) {
    for (auto & joint : joints_) {
      joint.state.position = joint.command.position;
    }

    return return_type::OK;
  }

  std::vector<uint8_t> ids(info_.joints.size(), 0);
  std::vector<int32_t> commands(info_.joints.size(), 0);

  std::copy(joint_ids_.begin(), joint_ids_.end(), ids.begin());
  const char * log = nullptr;

  if (std::any_of(
      joints_.cbegin(), joints_.cend(), [](auto j) {return j.command.velocity != 0.0;}))
  {
    // Velocity control
    set_control_mode(ControlMode::Velocity);
    for (uint i = 0; i < ids.size(); i++) {
      commands[i] = dynamixel_workbench_.convertVelocity2Value(
        ids[i], static_cast<float>(joints_[i].command.velocity));
    }

    if (!dynamixel_workbench_.syncWrite(kGoalVelocityIndex, ids.data(),
        ids.size(), commands.data(), 1, &log))
    {
      RCLCPP_ERROR(rclcpp::get_logger(kDynamixelHardware), "%s", log);
    }
    return return_type::OK;
  } else if (std::any_of(
      joints_.cbegin(), joints_.cend(), [](auto j) {return j.command.effort != 0.0;}))
  {
    // Effort control
    RCLCPP_ERROR(rclcpp::get_logger(kDynamixelHardware), "Effort control is not implemented");
    return return_type::ERROR;
  }

  // Position control
  set_control_mode(ControlMode::Position);
  for (uint i = 0; i < ids.size(); i++) {
    commands[i] = dynamixel_workbench_.convertRadian2Value(
      ids[i], static_cast<float>(joints_[i].command.position));
  }

  if (!dynamixel_workbench_.syncWrite(kGoalPositionIndex, ids.data(),
      ids.size(), commands.data(), 1, &log))
  {
    RCLCPP_ERROR(rclcpp::get_logger(kDynamixelHardware), "%s", log);
  }

  return return_type::OK;
}
```
- Dummy mode mirrors each position command into the state: a perfect execution, to test the control pipeline without hardware.
- Any non-zero velocity command → velocity mode for all servos, the commands converted from **rad/s** (`convertVelocity2Value`) and sent with one `syncWrite()`.
- Otherwise a non-zero effort command → `ERROR` (not implemented).
- Otherwise position mode: the position commands converted from rad (`convertRadian2Value`) and sent with one `syncWrite()`.

## Pitfalls
- A failed Sync Read is only logged: `read()` still returns `OK` and converts the zero-initialised raw values, so the states jump instead of keeping their last value.
- The mode is chosen for all servos at once: one joint with a velocity command turns every servo to velocity mode.
- Returning `ERROR` from `write()` triggers the component's error handling ([[control-hw-template-activate-rw]]); effort commands are never exported here, so they stay 0.
