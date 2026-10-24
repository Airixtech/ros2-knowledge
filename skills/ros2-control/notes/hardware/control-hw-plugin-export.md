---
id: control-hw-plugin-export
type: reference
owner: equipo-ros2
updated: 2026-10-24
review_by: 2027-04-22
source: manual
confidentiality: internal
title: "PLUGINLIB_EXPORT_CLASS and the plugin description XML (library path, name, type, base_class_type)"
domain: control
area: hardware
distro: jazzy
tested: false
audience: dev
summary: "Register a hardware interface: PLUGINLIB_EXPORT_CLASS(ns::Class, hardware_interface::SystemInterface), plugin XML library path/name/type/base_class_type, pluginlib_export_plugin_description_file."
tags: [pluginlib, PLUGINLIB_EXPORT_CLASS, class_list_macros.hpp, plugin description, library path, class name, type, base_class_type, pluginlib_export_plugin_description_file, my_robot_hardware_interface.xml, dynamixel_hardware.xml]
see: ["[[control-hw-package-build]]", "[[control-urdf-tag]]", "[[control-hw-template-header]]", "[[control-dynamixel-plugin-urdf-launch]]", "[[control-hw-interface-concept]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: <library path> is the library name (CMake target ${PROJECT_NAME}), not a namespace; name is optional and defaults to type; base_class_type is required — https://github.com/ros/pluginlib/blob/jazzy/pluginlib/include/pluginlib/class_loader_imp.hpp (CONTROL-V12)"
---
# PLUGINLIB_EXPORT_CLASS and the plugin description XML (library path, name, type, base_class_type)

**TL;DR** The package compiles without these, but ros2_control could not load the plugin: register the class with a macro in the `.cpp`, describe it in an XML file at the package root, and export that file from `CMakeLists.txt`. The `name` in the XML is what the URDF `<plugin>` uses.

## The macro (end of the .cpp, after the namespace)
```cpp
#include "pluginlib/class_list_macros.hpp"

PLUGINLIB_EXPORT_CLASS(my_robot_hardware_interface::RRBotSystemPositionOnlyHardware, hardware_interface::SystemInterface)
```
First argument: the fully qualified class (`namespace::Class`); second: the base class.

## my_robot_hardware_interface.xml (next to CMakeLists.txt)
```xml
<library path="my_robot_hardware_interface">
  <class name="my_robot_hardware_interface/RRBotSystemPositionOnlyHardware"
         type="my_robot_hardware_interface::RRBotSystemPositionOnlyHardware"
         base_class_type="hardware_interface::SystemInterface">
    <description>ros2_control minimal hardware interface template</description>
  </class>
</library>
```
| Element / attribute | Meaning |
|---|---|
| `library path` | the **library name**, i.e. the CMake target `${PROJECT_NAME}` (file `libmy_robot_hardware_interface.so`). The course calls it "the namespace": it matches the namespace only because both are named after the package. |
| `class name` | the plugin name written in the URDF `<plugin>` ([[control-urdf-tag]]); by convention `namespace/Class`. Optional: without it the name is the `type`; set it to avoid confusion. |
| `type` | namespace and class that implement the plugin |
| `base_class_type` | the base class (`hardware_interface::SystemInterface`); required, and it must match the base class the loader asks for, or the class is not registered |
| `description` | free text |

## Export the file (CMakeLists.txt)
```cmake
pluginlib_export_plugin_description_file(hardware_interface my_robot_hardware_interface.xml)
```
At build time this installs a pointer to the XML into the resource index under `hardware_interface` (the package of the base class), so pluginlib can find and load the library ([[control-hw-package-build]]).

## The Dynamixel plugin
```cpp
#include "pluginlib/class_list_macros.hpp"

PLUGINLIB_EXPORT_CLASS(dynamixel_hardware::DynamixelHardware, hardware_interface::SystemInterface)
```
```xml
<library path="dynamixel_hardware_interface">
  <class name="dynamixel_hardware/DynamixelHardware"
         type="dynamixel_hardware::DynamixelHardware"
         base_class_type="hardware_interface::SystemInterface">
    <description>Dynamixel hardware interface plugin for ros2_control</description>
  </class>
</library>
```
Saved as `dynamixel_hardware.xml` and exported with `pluginlib_export_plugin_description_file(hardware_interface dynamixel_hardware.xml)`. Here the library (`dynamixel_hardware_interface`, the package) and the namespace (`dynamixel_hardware`) differ: the path follows the library, the name and type follow the code.

## Pitfalls
- URDF `<plugin>` not equal to the XML `name` → the resource manager cannot find the plugin.
- Macro inside the namespace braces, or a `type` with another namespace than the code → the class is not found at load time.
- XML not exported from CMake → ros2_control does not know the plugin exists, although the library builds.
