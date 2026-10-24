---
id: control-hw-template-header
type: reference
owner: equipo-ros2
updated: 2026-10-24
review_by: 2027-04-22
source: manual
confidentiality: internal
title: "Hardware interface template (RRBot): package, header with the SystemInterface methods, .cpp skeleton"
domain: control
area: hardware
distro: jazzy
tested: false
audience: dev
summary: "my_robot_hardware_interface package, header RRBotSystemPositionOnlyHardware : SystemInterface with on_init(params), export_*, read/write; .cpp includes and namespace."
tags: [my_robot_hardware_interface, RRBotSystemPositionOnlyHardware, SystemInterface, header, RCLCPP_SHARED_PTR_DEFINITIONS, CallbackReturn, HardwareComponentInterfaceParams, hardware_component_interface_params.hpp, ros2 pkg create, ros2_control_demos]
see: ["[[control-hw-interface-concept]]", "[[control-hw-template-init]]", "[[control-hw-template-export]]", "[[control-hw-template-activate-rw]]", "[[control-hw-package-build]]", "[[control-humble-to-jazzy]]", "[[control-jazzy-to-lyrical]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: on_init(const HardwareComponentInterfaceParams &) since ros2_control 4.34.0; humble: on_init(const HardwareInfo &), no hardware_component_interface_params.hpp — https://github.com/ros-controls/ros2_control/blob/jazzy/hardware_interface/include/hardware_interface/hardware_component_interface.hpp (CONTROL-V18)"
  - "jazzy: export_state_interfaces/export_command_interfaces are deprecated; lyrical (ros2_control 6.12.0): removed, so this header does not compile there — https://github.com/ros-controls/ros2_control/blob/master/hardware_interface/CHANGELOG.rst (CONTROL-V19)"
  - "jazzy: the template is ros2_control_demos example_1 (Apache-2.0) in its Humble shape with the Jazzy on_init — https://github.com/ros-controls/ros2_control_demos/blob/humble/example_1/hardware/rrbot.cpp (CONTROL-V18)"
  - "jazzy: the course text says my_robot_hardware.cpp in 4.7–4.10; the file is my_robot_hardware_interface.cpp (CONTROL-V45)"
---
# Hardware interface template (RRBot): package, header with the SystemInterface methods, .cpp skeleton

**TL;DR** Put the hardware interface in its own package (simpler dependencies, modular code), name it `…_hardware_interface`, and write a class derived from `hardware_interface::SystemInterface` that overrides the lifecycle and I/O methods. The template simulates a 2-joint robot; replace its bodies with calls to your driver.

## Package
```bash
cd ~/ros2_ws/src
ros2 pkg create --build-type=ament_cmake my_robot_hardware_interface --dependencies hardware_interface pluginlib rclcpp rclcpp_lifecycle
```
It creates `CMakeLists.txt`, `package.xml`, `src/` and `include/my_robot_hardware_interface/`.

## include/my_robot_hardware_interface/my_robot_hardware_interface.hpp
```cpp
#ifndef ROS2_CONTROL_DEMO_HARDWARE__RRBOT_SYSTEM_HPP_
#define ROS2_CONTROL_DEMO_HARDWARE__RRBOT_SYSTEM_HPP_

#include <memory>
#include <string>
#include <vector>

#include "hardware_interface/handle.hpp"
#include "hardware_interface/hardware_info.hpp"
#include "hardware_interface/system_interface.hpp"
#include "hardware_interface/types/hardware_component_interface_params.hpp"
#include "hardware_interface/types/hardware_interface_return_values.hpp"
#include "rclcpp/macros.hpp"
#include "rclcpp_lifecycle/node_interfaces/lifecycle_node_interface.hpp"
#include "rclcpp_lifecycle/state.hpp"

using CallbackReturn =
  rclcpp_lifecycle::node_interfaces::LifecycleNodeInterface::CallbackReturn;

namespace my_robot_hardware_interface
{
class RRBotSystemPositionOnlyHardware : public hardware_interface::SystemInterface
{
public:
  RCLCPP_SHARED_PTR_DEFINITIONS(RRBotSystemPositionOnlyHardware);

  CallbackReturn
  on_init(const hardware_interface::HardwareComponentInterfaceParams & params) override;

  CallbackReturn
  on_configure(const rclcpp_lifecycle::State & previous_state) override;

  std::vector<hardware_interface::StateInterface>
  export_state_interfaces() override;

  std::vector<hardware_interface::CommandInterface>
  export_command_interfaces() override;

  CallbackReturn
  on_activate(const rclcpp_lifecycle::State & previous_state) override;

  CallbackReturn
  on_deactivate(const rclcpp_lifecycle::State & previous_state) override;

  hardware_interface::return_type read(
    const rclcpp::Time & time, const rclcpp::Duration & period) override;

  hardware_interface::return_type
  write(const rclcpp::Time & time, const rclcpp::Duration & period) override;

private:
  // Parameters for the RRBot simulation
  double hw_start_sec_;
  double hw_stop_sec_;
  double hw_slowdown_;

  // Store the command for the simulated robot
  std::vector<double> hw_commands_;
  std::vector<double> hw_states_;
};
}  // namespace my_robot_hardware_interface

#endif
```
- Header guard: any unique name (the course keeps the one of the official demo). `using CallbackReturn` lets you write `CallbackReturn::SUCCESS`/`ERROR` (`hardware_interface::CallbackReturn` is the same type).
- Namespace = package name. `SystemInterface` tells ros2_control this is a System ([[control-hw-interface-concept]]). `RCLCPP_SHARED_PTR_DEFINITIONS` adds the shared-pointer aliases.
- Private members hold what the driver needs (here the three URDF parameters) and the state/command storage the export methods point to.

## src/my_robot_hardware_interface.cpp (skeleton)
```cpp
#include "my_robot_hardware_interface/my_robot_hardware_interface.hpp"

#include <chrono>
#include <cmath>
#include <limits>
#include <memory>
#include <vector>

#include "hardware_interface/types/hardware_interface_type_values.hpp"
#include "rclcpp/rclcpp.hpp"

namespace my_robot_hardware_interface
{
// the methods of the next notes go here
}  // namespace my_robot_hardware_interface
```
Then `PLUGINLIB_EXPORT_CLASS` after the closing brace ([[control-hw-plugin-export]]).

## Versions
- [Humble: `on_init(const hardware_interface::HardwareInfo & info)` and no `types/hardware_component_interface_params.hpp`: [[control-humble-to-jazzy]]].
- [≥Jazzy: the two `export_…()` methods are deprecated: the official Jazzy demo declares only `on_init`, `on_configure`, `on_activate`, `on_deactivate`, `read`, `write` and no storage vectors] [changed in Lyrical: they are removed, so `override` on them fails to compile: [[control-jazzy-to-lyrical]]].

## Pitfalls
- File names: the course's text says `my_robot_hardware.cpp` in some steps; the file and the CMake source list use `my_robot_hardware_interface.cpp`.
- Methods are defined inside the namespace braces; the export macro outside.
