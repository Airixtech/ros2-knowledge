---
id: control-dynamixel-header
type: reference
owner: equipo-ros2
updated: 2026-10-24
review_by: 2027-04-22
source: manual
confidentiality: internal
title: "Dynamixel hardware interface header (JointValue, Joint, ControlMode, members) and .cpp constants"
domain: control
area: hardware
distro: jazzy
tested: false
audience: dev
summary: "DynamixelHardware : SystemInterface header: JointValue/Joint structs, ControlMode enum, DynamixelWorkbench member, control_items_, joint_ids_; .cpp control-table item constants."
tags: [DynamixelHardware, dynamixel_hardware, DynamixelWorkbench, dynamixel_workbench.h, JointValue, Joint, ControlMode, control_items_, ControlItem, joint_ids_, use_dummy_, Goal_Position, Present_Position, Moving_Speed, Present_Load]
see: ["[[control-dynamixel-sdk]]", "[[control-dynamixel-init]]", "[[control-hw-template-header]]", "[[control-dynamixel-torque-mode]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: the explanation names the namespace my_robot_hardware_interface and 'protected variables'; the header uses dynamixel_hardware and private members (CONTROL-V46)"
  - "jazzy: export_state/command_interfaces deprecated, removed in lyrical: the header does not compile there (CONTROL-V19)"
  - "jazzy: on_init(HardwareComponentInterfaceParams) since ros2_control 4.34.0; humble: HardwareInfo (CONTROL-V18)"
---
# Dynamixel hardware interface header (JointValue, Joint, ControlMode, members) and .cpp constants

**TL;DR** Same methods as the template ([[control-hw-template-header]]) plus three helpers, and the manufacturer's `DynamixelWorkbench` object that talks to the servos. State and command are kept per joint in small structs.

## include/dynamixel_hardware_interface/dynamixel_hardware_interface.hpp
```cpp
#ifndef DYNAMIXEL_HARDWARE__DYNAMIXEL_HARDWARE_HPP_
#define DYNAMIXEL_HARDWARE__DYNAMIXEL_HARDWARE_HPP_

#include <map>
#include <vector>

#include "hardware_interface/types/hardware_component_interface_params.hpp"
#include "rclcpp/macros.hpp"
#include <hardware_interface/handle.hpp>
#include <hardware_interface/hardware_info.hpp>
#include <hardware_interface/system_interface.hpp>
#include <rclcpp_lifecycle/state.hpp>

#include <dynamixel_workbench_toolbox/dynamixel_workbench.h>

using hardware_interface::return_type;
using CallbackReturn =
  rclcpp_lifecycle::node_interfaces::LifecycleNodeInterface::CallbackReturn;

namespace dynamixel_hardware
{
struct JointValue
{
  double position{0.0};
  double velocity{0.0};
  double effort{0.0};
};

struct Joint
{
  JointValue state{};
  JointValue command{};
};

enum class ControlMode
{
  Position,
  Velocity,
  Torque,
  Currrent,
  ExtendedPosition,
  MultiTurn,
  CurrentBasedPosition,
  PWM,
};

class DynamixelHardware : public hardware_interface::SystemInterface
{
public:
  RCLCPP_SHARED_PTR_DEFINITIONS(DynamixelHardware)

  CallbackReturn
  on_init(const hardware_interface::HardwareComponentInterfaceParams & params) override;

  std::vector<hardware_interface::StateInterface>
  export_state_interfaces() override;

  std::vector<hardware_interface::CommandInterface>
  export_command_interfaces() override;

  CallbackReturn
  on_activate(const rclcpp_lifecycle::State & previous_state) override;

  CallbackReturn
  on_deactivate(const rclcpp_lifecycle::State & previous_state) override;

  return_type read(const rclcpp::Time & time, const rclcpp::Duration & period) override;

  return_type write(const rclcpp::Time & time, const rclcpp::Duration & period) override;

private:
  return_type enable_torque(const bool enabled);

  return_type set_control_mode(const ControlMode & mode, const bool force_set = false);

  return_type reset_command();

  DynamixelWorkbench dynamixel_workbench_;
  std::map<const char * const, const ControlItem *> control_items_;
  std::vector<Joint> joints_;
  std::vector<uint8_t> joint_ids_;
  bool torque_enabled_{false};
  ControlMode control_mode_{ControlMode::Position};
  bool use_dummy_{false};
};
}  // namespace dynamixel_hardware

#endif  // DYNAMIXEL_HARDWARE__DYNAMIXEL_HARDWARE_HPP_
```
- `#include <dynamixel_workbench_toolbox/dynamixel_workbench.h>` brings the manufacturer's `DynamixelWorkbench` class; the member `dynamixel_workbench_` is the object that talks to the servos.
- `using hardware_interface::return_type` allows `return_type::OK`; the `CallbackReturn` alias is for convenience too.
- `JointValue` (position, velocity, effort) is used twice in `Joint`: the state and the command of each joint.
- `ControlMode` lists the Dynamixel operating modes; only position and velocity are implemented ([[control-dynamixel-torque-mode]]). `Currrent` (three r) is spelled so in the upstream code too.
- Private helpers: `enable_torque()` switches torque on/off, `set_control_mode()` changes the operating mode, `reset_command()` makes the command equal to the state. The other private members store parameters from the URDF `<param>` tags and data (servo ids, control-table items, flags).

## src/dynamixel_hardware_interface.cpp (start)
```cpp
#include <algorithm>
#include <array>
#include <string>
#include <limits>
#include <vector>

#include "dynamixel_hardware_interface/dynamixel_hardware_interface.hpp"
#include "hardware_interface/types/hardware_interface_return_values.hpp"
#include "hardware_interface/types/hardware_interface_type_values.hpp"
#include "rclcpp/rclcpp.hpp"

namespace dynamixel_hardware
{
constexpr const char * kDynamixelHardware = "DynamixelHardware";
constexpr uint8_t kGoalPositionIndex = 0;
constexpr uint8_t kGoalVelocityIndex = 1;
constexpr uint8_t kPresentPositionVelocityCurrentIndex = 0;
constexpr const char * kGoalPositionItem = "Goal_Position";
constexpr const char * kGoalVelocityItem = "Goal_Velocity";
constexpr const char * kMovingSpeedItem = "Moving_Speed";
constexpr const char * kPresentPositionItem = "Present_Position";
constexpr const char * kPresentVelocityItem = "Present_Velocity";
constexpr const char * kPresentSpeedItem = "Present_Speed";
constexpr const char * kPresentCurrentItem = "Present_Current";
constexpr const char * kPresentLoadItem = "Present_Load";
}  // namespace dynamixel_hardware
```
`kDynamixelHardware` is the logger name. The indexes number the sync handlers in the order `on_init()` adds them (write 0 = goal position, write 1 = goal velocity, read 0 = position + velocity + current). The item names are control-table registers; `Moving_Speed`, `Present_Speed` and `Present_Load` are the names of older servos, used as fallbacks ([[control-dynamixel-init]]).

## Pitfalls
- The course text explains this header with the namespace `my_robot_hardware_interface` and "protected variables": the code uses `dynamixel_hardware` and private members.
- `on_activate()` uses `std::isnan`: add `#include <cmath>` (the list above does not have it).
