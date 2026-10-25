---
id: control-custom-interfaces
type: reference
owner: equipo-ros2
updated: 2026-10-24
review_by: 2027-04-22
source: manual
confidentiality: internal
title: "command_interface_configuration and state_interface_configuration (INDIVIDUAL, ALL, NONE; <joint>/<interface>), get_ordered_interfaces"
domain: control
area: controllers
distro: jazzy
tested: false
audience: dev
summary: "Controller interface claims: InterfaceConfiguration INDIVIDUAL/ALL/NONE (+BEST_EFFORT, REGEX), names joint/interface, order of command_interfaces_, helpers get_ordered_interfaces."
tags: [custom controller, command_interface_configuration, state_interface_configuration, InterfaceConfiguration, interface_configuration_type, INDIVIDUAL, ALL, NONE, INDIVIDUAL_BEST_EFFORT, REGEX, get_ordered_interfaces, helpers.hpp, get_prefix_name, command_interfaces_]
see: ["[[control-custom-header]]", "[[control-custom-configure]]", "[[control-custom-activate-update]]", "[[control-hw-interface-concept]]", "[[control-cli-list]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: also INDIVIDUAL_BEST_EFFORT and REGEX; humble: ALL, INDIVIDUAL, NONE only — https://github.com/ros-controls/ros2_control/blob/jazzy/controller_interface/include/controller_interface/controller_interface_base.hpp (CONTROL-V76)"
  - "jazzy: the course's get_ordered_interfaces compares get_name() (<joint>/<interface>) with a joint name and never matches; with INDIVIDUAL the loans follow the requested order; use controller_interface::get_ordered_interfaces — https://github.com/ros-controls/ros2_control/blob/jazzy/controller_interface/include/controller_interface/helpers.hpp (CONTROL-V55)"
---
# command_interface_configuration and state_interface_configuration (INDIVIDUAL, ALL, NONE; <joint>/<interface>), get_ordered_interfaces

**TL;DR** These two methods tell the controller manager which command interfaces the controller needs to write and which state interfaces it needs to read. It claims them when the controller is activated and hands them over in `command_interfaces_` and `state_interfaces_`.

## The two methods
```cpp
controller_interface::InterfaceConfiguration
RRBotController::command_interface_configuration() const {
  controller_interface::InterfaceConfiguration command_interfaces_config;
  command_interfaces_config.type =
      controller_interface::interface_configuration_type::INDIVIDUAL;

  command_interfaces_config.names.reserve(joint_names_.size());
  for (const auto &joint : joint_names_) {
    command_interfaces_config.names.push_back(joint + "/" + interface_name_);
  }

  return command_interfaces_config;
}

controller_interface::InterfaceConfiguration
RRBotController::state_interface_configuration() const {
  controller_interface::InterfaceConfiguration state_interfaces_config;
  state_interfaces_config.type =
      controller_interface::interface_configuration_type::INDIVIDUAL;

  state_interfaces_config.names.reserve(joint_names_.size());
  for (const auto &joint : joint_names_) {
    state_interfaces_config.names.push_back(joint + "/" + interface_name_);
  }

  return state_interfaces_config;
}
```
- A full interface name is `<joint_name>/<interface_type>`, for example `joint1/position` (`ros2 control list_hardware_interfaces` shows them, [[control-cli-list]]). `reserve()` only allocates the vector once.
- The names come from the parameters, so this pattern barely changes between controllers. Here the state interface uses the same `interface_name_`: the joints must export a state interface of that name too.

| Type | Claims |
|---|---|
| `INDIVIDUAL` | exactly the listed names; activation fails if one is missing |
| `ALL` | every available interface |
| `NONE` | nothing |
| `INDIVIDUAL_BEST_EFFORT` [≥Jazzy] | the listed names that exist |
| `REGEX` [≥Jazzy] | names matching regular expressions |

## Order of the loaned interfaces
With `INDIVIDUAL`, `command_interfaces_[i]` and `state_interfaces_[i]` come in the order of the returned names, so index `i` is joint `joint_names_[i]` ([[control-custom-activate-update]] relies on it). With `ALL`, `INDIVIDUAL_BEST_EFFORT` or `REGEX` the order is not guaranteed: sort them with the helper of `controller_interface/helpers.hpp` [verify build]:
```cpp
#include "controller_interface/helpers.hpp"

std::vector<std::reference_wrapper<hardware_interface::LoanedCommandInterface>> ordered;
if (!controller_interface::get_ordered_interfaces(
      command_interfaces_, joint_names_, interface_name_, ordered)) {
  return CallbackReturn::ERROR;  // e.g. in on_activate: an interface is missing
}
```

## The course's get_ordered_interfaces()
The course adds its own template, placed after `state_interface_configuration()`, to fill `ordered_interfaces` in the order of `joint_names`:
```cpp
template <typename T>
bool get_ordered_interfaces(
    std::vector<T> &unordered_interfaces,
    const std::vector<std::string> &joint_names,
    const std::string &interface_type,
    std::vector<std::reference_wrapper<T>> &ordered_interfaces) {
  for (const auto &joint_name : joint_names) {
    for (auto &command_interface : unordered_interfaces) {
      if ((command_interface.get_name() == joint_name) &&
          (command_interface.get_interface_name() == interface_type)) {
        ordered_interfaces.push_back(std::ref(command_interface));
      }
    }
  }

  return joint_names.size() == ordered_interfaces.size();
}
```
It is never called, and it would not work: `get_name()` returns the full name `joint1/position`, never equal to `joint1`, so it always returns `false`. The official helper compares `get_prefix_name()` (the joint). Leave this template out.

## Pitfalls
- A name the hardware does not export → the controller does not activate (the controller manager logs which interface is missing).
- Two active controllers cannot claim the same command interface; any number can read a state interface.
