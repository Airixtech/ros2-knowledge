---
id: control-hw-template-export
type: reference
owner: equipo-ros2
updated: 2026-10-24
review_by: 2027-04-22
source: manual
confidentiality: internal
title: "Template export_state_interfaces and export_command_interfaces (HW_IF_POSITION)"
domain: control
area: hardware
distro: jazzy
tested: false
audience: dev
summary: "export_state_interfaces/export_command_interfaces: one StateInterface/CommandInterface per joint pointing into member vectors; deprecated in Jazzy, removed in Lyrical."
tags: [export_state_interfaces, export_command_interfaces, StateInterface, CommandInterface, HW_IF_POSITION, info_, joints, on_export_state_interfaces, set_state, get_command, operation modes]
see: ["[[control-hw-template-init]]", "[[control-hw-template-activate-rw]]", "[[control-hw-interface-concept]]", "[[control-dynamixel-interfaces-activate]]", "[[control-jazzy-to-lyrical]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: these vector-returning methods are deprecated ('Exporting is handled by the Framework'); lyrical: removed in ros2_control 6.12.0; humble: the only way — https://github.com/ros-controls/ros2_control/blob/jazzy/hardware_interface/include/hardware_interface/hardware_component_interface.hpp (CONTROL-V19)"
  - "jazzy: interface type constants per distro (CONTROL-V16)"
---
# Template export_state_interfaces and export_command_interfaces (HW_IF_POSITION)

**TL;DR** These two methods tell ros2_control which states your hardware offers and which commands it accepts, by handing out one interface object per joint that points into your own storage. ros2_control does not know your firmware's operation modes: you register them here.

## export_state_interfaces()
```cpp
std::vector<hardware_interface::StateInterface>
RRBotSystemPositionOnlyHardware::export_state_interfaces()
{
  std::vector<hardware_interface::StateInterface> state_interfaces;
  for (uint i = 0; i < info_.joints.size(); i++)
  {
    state_interfaces.emplace_back(hardware_interface::StateInterface(
      info_.joints[i].name, hardware_interface::HW_IF_POSITION, &hw_states_[i]));
  }

  return state_interfaces;
}
```
It loops over the joints of the configuration (`info_`) and exports `position` as the only state of each. Other values exist (`HW_IF_VELOCITY`, `HW_IF_ACCELERATION`, `HW_IF_EFFORT`…, [[control-hw-interface-concept]]): export the ones your hardware provides.

## export_command_interfaces()
```cpp
std::vector<hardware_interface::CommandInterface>
RRBotSystemPositionOnlyHardware::export_command_interfaces()
{
  std::vector<hardware_interface::CommandInterface> command_interfaces;
  for (uint i = 0; i < info_.joints.size(); i++)
  {
    command_interfaces.emplace_back(hardware_interface::CommandInterface(
      info_.joints[i].name, hardware_interface::HW_IF_POSITION, &hw_commands_[i]));
  }

  return command_interfaces;
}
```
Firmware often has several operation modes (position, velocity, current…); which ones your actuator supports is in its documentation. The template accepts only position commands.

## Versions
- [Humble: this is the only way to export].
- [≥Jazzy: deprecated. If these methods return interfaces, the framework uses them and the helpers `set_state()`, `get_command()`… cannot be used. The official Jazzy demo does not override them: the framework creates the interfaces declared in `<ros2_control>` and the code reads and writes them by name, e.g. `set_state("joint1/position", value)` ([[control-hw-template-activate-rw]])].
- [changed in Lyrical: removed in ros2_control 6.12.0; `override` on them is a compile error ([[control-jazzy-to-lyrical]])].

## Pitfalls
- The interfaces hold raw pointers into `hw_states_`/`hw_commands_`: size the vectors in `on_init()` and never resize them afterwards.
- Export the same names the URDF declares (`<command_interface name="position"/>`), or controllers cannot claim them.
