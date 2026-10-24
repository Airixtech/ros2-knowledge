---
id: control-dynamixel-init
type: reference
owner: equipo-ros2
updated: 2026-10-24
review_by: 2027-04-22
source: manual
confidentiality: internal
title: "Dynamixel on_init: joint ids, dummy mode, usb_port and baud_rate, ping, control items, Sync Write/Read handlers"
domain: control
area: hardware
distro: jazzy
tested: false
audience: dev
summary: "DynamixelHardware::on_init: joint id params, NaN init, use_dummy early return, DynamixelWorkbench init/ping, torque and position mode, getItemInfo fallbacks, addSyncWriteHandler/addSyncReadHandler."
tags: [on_init, DynamixelWorkbench, init, ping, getItemInfo, ControlItem, addSyncWriteHandler, addSyncReadHandler, Sync Write, Sync Read, use_dummy, usb_port, baud_rate, id, Goal_Velocity, Moving_Speed, Present_Load]
see: ["[[control-dynamixel-header]]", "[[control-dynamixel-interfaces-activate]]", "[[control-dynamixel-read-write]]", "[[control-dynamixel-torque-mode]]", "[[control-dynamixel-plugin-urdf-launch]]", "[[control-hw-template-init]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: control-table items are looked up on the first servo only: all servos must share the control table (CONTROL-V36)"
  - "jazzy: const auto & info_ shadows the member info_, which holds the same data (CONTROL-V38)"
  - "jazzy: on_init(HardwareComponentInterfaceParams) since 4.34.0; humble: on_init(const HardwareInfo &) (CONTROL-V18)"
---
# Dynamixel on_init: joint ids, dummy mode, usb_port and baud_rate, ping, control items, Sync Write/Read handlers

**TL;DR** About 120 lines, but a plain sequence: read the URDF parameters, stop early in dummy mode, otherwise open the bus, ping every servo, put them in position mode with torque on, look up the control-table registers and prepare one Sync Write per command type and one Sync Read for all states.

```cpp
CallbackReturn DynamixelHardware::on_init(
  const hardware_interface::HardwareComponentInterfaceParams & params)
{
  RCLCPP_DEBUG(rclcpp::get_logger(kDynamixelHardware), "configure");
  if (hardware_interface::HardwareComponentInterface::on_init(params) !=
    CallbackReturn::SUCCESS)
  {
    return CallbackReturn::ERROR;
  }

  const auto & info_ = params.hardware_info;

  joints_.resize(info_.joints.size(), Joint());
  joint_ids_.resize(info_.joints.size(), 0);

  for (uint i = 0; i < info_.joints.size(); i++) {
    joint_ids_[i] = std::stoi(info_.joints[i].parameters.at("id"));
    joints_[i].state.position = std::numeric_limits<double>::quiet_NaN();
    joints_[i].state.velocity = std::numeric_limits<double>::quiet_NaN();
    joints_[i].state.effort = std::numeric_limits<double>::quiet_NaN();
    joints_[i].command.position = std::numeric_limits<double>::quiet_NaN();
    joints_[i].command.velocity = std::numeric_limits<double>::quiet_NaN();
    joints_[i].command.effort = std::numeric_limits<double>::quiet_NaN();
    RCLCPP_INFO(rclcpp::get_logger(kDynamixelHardware), "joint_id %d: %d", i, joint_ids_[i]);
  }

  if (info_.hardware_parameters.find("use_dummy") != info_.hardware_parameters.end() &&
    info_.hardware_parameters.at("use_dummy") == "true")
  {
    use_dummy_ = true;
    RCLCPP_INFO(rclcpp::get_logger(kDynamixelHardware), "dummy mode");
    return CallbackReturn::SUCCESS;
  }

  auto usb_port = info_.hardware_parameters.at("usb_port");
  auto baud_rate = std::stoi(info_.hardware_parameters.at("baud_rate"));
  const char * log = nullptr;

  RCLCPP_INFO(rclcpp::get_logger(kDynamixelHardware), "usb_port: %s", usb_port.c_str());
  RCLCPP_INFO(rclcpp::get_logger(kDynamixelHardware), "baud_rate: %d", baud_rate);

  if (!dynamixel_workbench_.init(usb_port.c_str(), baud_rate, &log)) {
    RCLCPP_FATAL(rclcpp::get_logger(kDynamixelHardware), "%s", log);
    return CallbackReturn::ERROR;
  }

  for (uint i = 0; i < info_.joints.size(); ++i) {
    uint16_t model_number = 0;
    if (!dynamixel_workbench_.ping(joint_ids_[i], &model_number, &log)) {
      RCLCPP_FATAL(rclcpp::get_logger(kDynamixelHardware), "%s", log);
      return CallbackReturn::ERROR;
    }
  }

  enable_torque(false);
  set_control_mode(ControlMode::Position, true);
  enable_torque(true);

  const ControlItem * goal_position =
    dynamixel_workbench_.getItemInfo(joint_ids_[0], kGoalPositionItem);
  if (goal_position == nullptr) {
    return CallbackReturn::ERROR;
  }

  const ControlItem * goal_velocity =
    dynamixel_workbench_.getItemInfo(joint_ids_[0], kGoalVelocityItem);
  if (goal_velocity == nullptr) {
    goal_velocity = dynamixel_workbench_.getItemInfo(joint_ids_[0], kMovingSpeedItem);
  }
  if (goal_velocity == nullptr) {
    return CallbackReturn::ERROR;
  }

  const ControlItem * present_position =
    dynamixel_workbench_.getItemInfo(joint_ids_[0], kPresentPositionItem);
  if (present_position == nullptr) {
    return CallbackReturn::ERROR;
  }

  const ControlItem * present_velocity =
    dynamixel_workbench_.getItemInfo(joint_ids_[0], kPresentVelocityItem);
  if (present_velocity == nullptr) {
    present_velocity = dynamixel_workbench_.getItemInfo(joint_ids_[0], kPresentSpeedItem);
  }
  if (present_velocity == nullptr) {
    return CallbackReturn::ERROR;
  }

  const ControlItem * present_current =
    dynamixel_workbench_.getItemInfo(joint_ids_[0], kPresentCurrentItem);
  if (present_current == nullptr) {
    present_current = dynamixel_workbench_.getItemInfo(joint_ids_[0], kPresentLoadItem);
  }
  if (present_current == nullptr) {
    return CallbackReturn::ERROR;
  }

  control_items_[kGoalPositionItem] = goal_position;
  control_items_[kGoalVelocityItem] = goal_velocity;
  control_items_[kPresentPositionItem] = present_position;
  control_items_[kPresentVelocityItem] = present_velocity;
  control_items_[kPresentCurrentItem] = present_current;

  if (!dynamixel_workbench_.addSyncWriteHandler(
      control_items_[kGoalPositionItem]->address,
      control_items_[kGoalPositionItem]->data_length, &log))
  {
    RCLCPP_FATAL(rclcpp::get_logger(kDynamixelHardware), "%s", log);
    return CallbackReturn::ERROR;
  }

  if (!dynamixel_workbench_.addSyncWriteHandler(
      control_items_[kGoalVelocityItem]->address,
      control_items_[kGoalVelocityItem]->data_length, &log))
  {
    RCLCPP_FATAL(rclcpp::get_logger(kDynamixelHardware), "%s", log);
    return CallbackReturn::ERROR;
  }

  uint16_t start_address = std::min(
    control_items_[kPresentPositionItem]->address,
    control_items_[kPresentCurrentItem]->address);
  uint16_t read_length = control_items_[kPresentPositionItem]->data_length +
    control_items_[kPresentVelocityItem]->data_length +
    control_items_[kPresentCurrentItem]->data_length + 2;
  if (!dynamixel_workbench_.addSyncReadHandler(start_address, read_length, &log)) {
    RCLCPP_FATAL(rclcpp::get_logger(kDynamixelHardware), "%s", log);
    return CallbackReturn::ERROR;
  }

  return CallbackReturn::SUCCESS;
}
```

## Step by step
1. The base `on_init(params)` parses `<ros2_control>`; `params.hardware_info` (a `HardwareInfo`: hardware, joints, interfaces, parameters) is used through a local `info_`, which shadows the member of the same name that holds the same data.
2. Per joint: the servo id from the joint's `<param name="id">`, and `NaN` for every state and command (nothing read or sent yet); the ids are logged.
3. `use_dummy` = `true` → dummy mode: return `SUCCESS` before anything touches the bus.
4. `usb_port` and `baud_rate` from the `<hardware>` params; `log` receives the Workbench's messages.
5. `init()` opens the bus; `ping()` checks that every configured servo answers. Any failure logs the Workbench message and returns `ERROR`.
6. Torque off before the operating mode changes, position mode, torque on so the motors can move ([[control-dynamixel-torque-mode]]).
7. `getItemInfo()` returns a `ControlItem` (address and data length of a control-table register): `Goal_Position`, `Goal_Velocity` (older models: `Moving_Speed`), `Present_Position`, `Present_Velocity` (`Present_Speed`), `Present_Current` (`Present_Load`). A missing register → `ERROR`. They are stored in `control_items_`.
8. Sync Write sends one type of command to many servos in one packet: one handler for goal position (index 0), one for goal velocity (index 1).
9. Sync Read gets the states of many servos in one exchange: one block from the lower of the two addresses, long enough for position, velocity and current (`+ 2` as in the upstream code).

## Pitfalls
- The registers are looked up on `joint_ids_[0]` only: every servo on the bus must have the same control table (same series).
- The bus is opened in `on_init()` (as in the upstream package), not in `on_configure()` as the ros2_control guide suggests ([[control-hw-template-init]]): a missing USB adapter makes the plugin fail to load.
- `use_dummy` is compared with the string `"true"`: `True` or `1` do not enable dummy mode.
