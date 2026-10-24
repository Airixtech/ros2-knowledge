---
id: control-hw-interface-concept
type: reference
owner: equipo-ros2
updated: 2026-10-24
review_by: 2027-04-22
source: manual
confidentiality: internal
title: "Hardware interfaces: what they do, System/Actuator/Sensor, interface type values, the 5 steps"
domain: control
area: hardware
distro: jazzy
tested: false
audience: dev
order: 1
summary: "Hardware component = plugin between ros2_control and a device: System/Actuator/Sensor, method order, HW_IF_* interface types, vendor SDK, the five steps."
tags: [hardware interface, hardware component, SystemInterface, ActuatorInterface, SensorInterface, pluginlib, HW_IF_POSITION, HW_IF_VELOCITY, HW_IF_EFFORT, hardware_interface_type_values.hpp, on_init, read, write]
see: ["[[control-hw-template-header]]", "[[control-hw-template-init]]", "[[control-hw-template-export]]", "[[control-hw-template-activate-rw]]", "[[control-hw-plugin-export]]", "[[control-hw-package-build]]", "[[control-overview]]", "[[control-urdf-tag]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: component types as defined by the official docs (the course says a System makes the difference small) — https://github.com/ros-controls/control.ros.org/blob/jazzy/doc/getting_started/getting_started.rst (CONTROL-V21)"
  - "jazzy: since ros2_control 4.35.0 the framework creates a node for each component; humble: no node — https://github.com/ros-controls/ros2_control/blob/jazzy/hardware_interface/src/hardware_component_interface.cpp (CONTROL-V20)"
  - "jazzy: HW_IF_* are string constants in types/hardware_interface_type_values.hpp: 4 in Humble, 12 in Jazzy — https://github.com/ros-controls/ros2_control/blob/jazzy/hardware_interface/include/hardware_interface/types/hardware_interface_type_values.hpp (CONTROL-V16)"
---
# Hardware interfaces: what they do, System/Actuator/Sensor, interface type values, the 5 steps

**TL;DR** A hardware interface (hardware component) talks to ros2_control on one side and to one or more devices on the other: an intermediary and interpreter. A position sensor's raw reading goes in as a state value for the controllers; the controller's new target comes back as a command, converted to the format the device understands. ros2_control defines the abstract class, you write the derived class, so controllers never need to know the hardware.

## Plugin, not a node
The component is a pluginlib plugin loaded by the resource manager ([[control-hw-plugin-export]]), not a ROS node you start. [≥Jazzy 4.35: the framework also creates a node for it, named after the lower-case `<ros2_control name>`, reachable with `get_node()`; Humble creates none].

## Three types
| Type | For | Reads / writes |
|---|---|---|
| System | complex (multi-DOF) hardware on one logical communication channel, also complex transmissions (an industrial robot, a hand) | both |
| Actuator | simple 1-DOF hardware: one joint (a motor, a valve); also usable per motor on a modular bus | writes; reading optional |
| Sensor | sensing only, related to a joint (encoder) or a link (force-torque) | reads only |

Base classes: `hardware_interface::SystemInterface`, `hardware_interface::ActuatorInterface`, `hardware_interface::SensorInterface`. The course uses `SystemInterface` for everything; the types are not interchangeable in general (a Sensor cannot write).

## Method order (what the template implements)
| Method | Job |
|---|---|
| `on_init()` | first call: initialise data, validate the parameters from the URDF ([[control-hw-template-init]]) |
| `on_configure()` | open communication so that states can be read |
| `export_state_interfaces()` / `export_command_interfaces()` | which states the hardware offers, which commands it accepts ([[control-hw-template-export]]) |
| `on_activate()` / `on_deactivate()` | power up and enable movement / stop cleanly ([[control-hw-template-activate-rw]]) |
| `read()` / `write()` | in every loop: read states before the controllers run, write their commands after |

## Interface type values
String constants in `hardware_interface/types/hardware_interface_type_values.hpp`: `HW_IF_POSITION`, `HW_IF_VELOCITY`, `HW_IF_ACCELERATION`, `HW_IF_EFFORT` [≥Jazzy: also `HW_IF_CURRENT`, `HW_IF_TORQUE`, `HW_IF_FORCE`, `HW_IF_TEMPERATURE`, `HW_IF_PROPORTIONAL`, `HW_IF_INTEGRAL`, `HW_IF_DERIVATIVE`, `HW_IF_FEEDFORWARD`]. Interface names are strings: on Humble write `"current"` where Jazzy has a constant. Export only what your hardware really provides.

## The five steps
1. A package for the hardware interface ([[control-hw-template-header]]).
2. A header file declaring the class and its methods.
3. The `.cpp` source that talks to the hardware.
4. `CMakeLists.txt` and `package.xml` ([[control-hw-package-build]]).
5. Register the class as a plugin ([[control-hw-plugin-export]]).

## Pitfalls
- A hardware interface is always custom-made for one device: you include the driver or SDK of its manufacturer (usually on the seller's or manufacturer's website). The template of [[control-hw-template-header]] has none (it simulates a robot); the Dynamixel unit wraps one ([[control-dynamixel-sdk]]).
- Exporting an interface the hardware cannot supply gives controllers values that are never updated.
