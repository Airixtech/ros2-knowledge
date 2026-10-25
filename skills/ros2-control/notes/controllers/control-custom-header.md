---
id: control-custom-header
type: reference
owner: equipo-ros2
updated: 2026-10-24
review_by: 2027-04-22
source: manual
confidentiality: internal
title: "Custom controller: the five steps, package and dependencies, header (ControllerInterface methods, JointJog subscriber, realtime tools)"
domain: control
area: controllers
distro: jazzy
tested: false
audience: dev
summary: "Custom controller steps, ros2 pkg create dependencies, RRBotController : ControllerInterface header: on_init, interface configurations, lifecycle callbacks, update, RealtimeBuffer, RealtimePublisher."
tags: [custom controller, controller_interface, ControllerInterface, rrbot_controller, RRBotController, ros2 pkg create, header, CallbackReturn, on_init, update, JointJog, JointControllerState, RealtimeBuffer, RealtimePublisher, realtime_buffer.hpp, realtime_publisher.hpp]
see: ["[[control-custom-init]]", "[[control-custom-configure]]", "[[control-custom-interfaces]]", "[[control-custom-activate-update]]", "[[control-custom-plugin-export]]", "[[control-custom-package-build]]", "[[control-custom-config-launch]]", "[[control-controller-lifecycle]]", "[[control-hw-template-header]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: the course says the unit is for Galactic, but its code needs the Jazzy API (bool set_value, get_optional) — https://github.com/ros-controls/ros2_control/blob/jazzy/hardware_interface/include/hardware_interface/handle.hpp (CONTROL-V50)"
  - "jazzy: realtime_buffer.h and realtime_publisher.h are deprecated (#warning), the .hpp headers exist since Humble; kilted: the .h headers are removed — https://github.com/ros-controls/realtime_tools/blob/kilted/realtime_tools/include/realtime_tools/realtime_publisher.hpp (CONTROL-V73)"
  - "jazzy: ControllerInterface API (on_init, *_interface_configuration, update, CallbackReturn) unchanged from Humble to Lyrical — https://github.com/ros-controls/ros2_control/blob/jazzy/controller_interface/include/controller_interface/controller_interface_base.hpp (CONTROL-V77)"
  - "jazzy: code origin is the RRBotController of the 2021 ros2_control workshop — https://control.ros.org/jazzy/_downloads/9889caef43ffab44b1fb8d6d1e5f0372/2021-06_RosConFR_Getting_started_with_ros2_control.pdf (CONTROL-V50)"
---
# Custom controller: the five steps, package and dependencies, header (ControllerInterface methods, JointJog subscriber, realtime tools)

**TL;DR** When no controller of ros2_controllers fits ([[control-builtin-forward]]), write one: a class derived from `controller_interface::ControllerInterface`, built as a pluginlib plugin. The course's example, `RRBotController`, forwards the positions of a `control_msgs/msg/JointJog` message to the joints. It comes from the ros2_control maintainers' 2021 workshop.

## Five steps
1. Create a package for the controller.
2. Write a header with the controller's interface.
3. Implement the logic in a `.cpp` ([[control-custom-init]], [[control-custom-configure]], [[control-custom-interfaces]], [[control-custom-activate-update]]).
4. Configure `CMakeLists.txt` and `package.xml` ([[control-custom-package-build]]), and
5. register the controller as a plugin ([[control-custom-plugin-export]]).

## Package
A separate package keeps the controller modular; ending its name with `_controller` is a good convention.
```bash
cd ~/ros2_ws/src
ros2 pkg create --build-type=ament_cmake rrbot_controller --dependencies control_msgs controller_interface hardware_interface pluginlib rclcpp rclcpp_lifecycle realtime_tools example_interfaces
```
It creates `CMakeLists.txt`, `package.xml`, `src/` and `include/rrbot_controller/`. The code never uses `example_interfaces` (harmless).

## include/rrbot_controller/rrbot_controller.hpp
```cpp
// Copyright (c) 2021, Bence Magyar and Denis Stogl. Licensed under the Apache License, Version 2.0.
#ifndef RRBOT_CONTROLLER__RRBOT_CONTROLLER_HPP_
#define RRBOT_CONTROLLER__RRBOT_CONTROLLER_HPP_

#include <memory>
#include <string>
#include <vector>

#include "controller_interface/controller_interface.hpp"
#include "rclcpp_lifecycle/node_interfaces/lifecycle_node_interface.hpp"
#include "rclcpp_lifecycle/state.hpp"
#include "realtime_tools/realtime_buffer.hpp"     // the course includes realtime_buffer.h
#include "realtime_tools/realtime_publisher.hpp"  // the course includes realtime_publisher.h

#include "control_msgs/msg/joint_controller_state.hpp"
#include "control_msgs/msg/joint_jog.hpp"

namespace rrbot_controller {
using CallbackReturn =
    rclcpp_lifecycle::node_interfaces::LifecycleNodeInterface::CallbackReturn;

class RRBotController : public controller_interface::ControllerInterface {
public:
  RRBotController();

  CallbackReturn on_init() override;

  controller_interface::InterfaceConfiguration
  command_interface_configuration() const override;

  controller_interface::InterfaceConfiguration
  state_interface_configuration() const override;

  CallbackReturn
  on_configure(const rclcpp_lifecycle::State &previous_state) override;

  CallbackReturn
  on_activate(const rclcpp_lifecycle::State &previous_state) override;

  CallbackReturn
  on_deactivate(const rclcpp_lifecycle::State &previous_state) override;

  controller_interface::return_type
  update(const rclcpp::Time &time, const rclcpp::Duration &period) override;

protected:
  std::vector<std::string> joint_names_;
  std::string interface_name_;

  // Command subscribers and Controller State publisher
  using ControllerCommandMsg = control_msgs::msg::JointJog;

  rclcpp::Subscription<ControllerCommandMsg>::SharedPtr command_subscriber_ =
      nullptr;
  realtime_tools::RealtimeBuffer<std::shared_ptr<ControllerCommandMsg>>
      input_command_;

  using ControllerStateMsg = control_msgs::msg::JointControllerState;
  using ControllerStatePublisher =
      realtime_tools::RealtimePublisher<ControllerStateMsg>;

  rclcpp::Publisher<ControllerStateMsg>::SharedPtr s_publisher_;
  std::unique_ptr<ControllerStatePublisher> state_publisher_;
};

} // namespace rrbot_controller

#endif // RRBOT_CONTROLLER__RRBOT_CONTROLLER_HPP_
```
The `.hpp` headers of realtime_tools exist from Humble on; the course's `.h` names are deprecated in Jazzy (a compiler warning) [changed in Kilted: removed, the course header does not compile]. The course's explanation also shows a commented-out `#include "rrbot_controller/visibility_control.h"`: the package has no such file.

## What the parts are
- Header guards, so the file is included once.
- `CallbackReturn` alias: lets the code write `CallbackReturn::SUCCESS` and `CallbackReturn::ERROR` instead of the full `rclcpp_lifecycle::node_interfaces::LifecycleNodeInterface::CallbackReturn` (`controller_interface` declares the same alias).
- The namespace matches the package name.
- Every controller derives from `controller_interface::ControllerInterface`. It must implement `on_init()`, `command_interface_configuration()`, `state_interface_configuration()` and `update()`; the lifecycle callbacks (`on_configure`, `on_activate`, `on_deactivate`…) are optional and succeed by default ([[control-controller-lifecycle]]).
- Members: the `joints` and `interface_name` parameters; a subscriber for `JointJog` commands, whose callback hands the latest message to `update()` through a `RealtimeBuffer`; a `JointControllerState` publisher wrapped in a `RealtimePublisher`, so `update()` never waits for the middleware.

The course notes that these method names changed over ros2_control releases and says the unit is for Galactic: the code is Jazzy's API ([[control-custom-activate-update]]). Check your ros2_control version; per distro: [[control-humble-to-jazzy]], [[control-jazzy-to-lyrical]].

## Pitfalls
- A method signature that does not match the base class (missing `const` on the interface configurations) → the `override` fails to compile.
- Kilted/Lyrical: `.h` includes of realtime_tools no longer exist; Lyrical also removes the `RealtimePublisher` members used in [[control-custom-configure]].
