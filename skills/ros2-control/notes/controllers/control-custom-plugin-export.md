---
id: control-custom-plugin-export
type: reference
owner: equipo-ros2
updated: 2026-10-24
review_by: 2027-04-22
source: manual
confidentiality: internal
title: "Register a controller plugin: PLUGINLIB_EXPORT_CLASS with ControllerInterface, rrbot_controller.xml, export to controller_interface"
domain: control
area: controllers
distro: jazzy
tested: false
audience: dev
summary: "Controller plugin: PLUGINLIB_EXPORT_CLASS(rrbot_controller::RRBotController, controller_interface::ControllerInterface), rrbot_controller.xml, pluginlib_export_plugin_description_file(controller_interface)."
tags: [custom controller, pluginlib, PLUGINLIB_EXPORT_CLASS, class_list_macros.hpp, controller_interface::ControllerInterface, rrbot_controller.xml, library path, class name, base_class_type, pluginlib_export_plugin_description_file, Loader for controller not found]
see: ["[[control-hw-plugin-export]]", "[[control-custom-package-build]]", "[[control-custom-header]]", "[[control-custom-config-launch]]", "[[control-controller-config]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: <library path> is the library name (CMake target), not a relative path — https://github.com/ros/pluginlib/blob/jazzy/pluginlib/include/pluginlib/class_loader_imp.hpp (CONTROL-V12)"
  - "jazzy: the controller manager loads controllers with a ClassLoader for package controller_interface — https://github.com/ros-controls/ros2_control/blob/jazzy/controller_manager/src/controller_manager.cpp (CONTROL-V77)"
---
# Register a controller plugin: PLUGINLIB_EXPORT_CLASS with ControllerInterface, rrbot_controller.xml, export to controller_interface

**TL;DR** A controller is loaded like a hardware interface ([[control-hw-plugin-export]]): a pluginlib macro after the namespace, a plugin description XML at the package root, and its export from `CMakeLists.txt`. The difference is the base class, `controller_interface::ControllerInterface`, and the package the XML is exported to, `controller_interface`.

## The macro (very end of rrbot_controller.cpp, after the namespace)
```cpp
#include "pluginlib/class_list_macros.hpp"

PLUGINLIB_EXPORT_CLASS(rrbot_controller::RRBotController, controller_interface::ControllerInterface)
```
It registers the class in the ROS 2 plugin system: first the class with its namespace, then the base class.

## rrbot_controller.xml (next to CMakeLists.txt)
```bash
touch ~/ros2_ws/src/rrbot_controller/rrbot_controller.xml
```
```xml
<library path="rrbot_controller">
  <class name="rrbot_controller/RRBotController"
         type="rrbot_controller::RRBotController"
         base_class_type="controller_interface::ControllerInterface">
    <description>RRBotController ros2_control controller.</description>
  </class>
</library>
```
- `library path`: the **library name**, the CMake target `rrbot_controller` (file `librrbot_controller.so`); the course calls it a relative path.
- `name`: the plugin name, written as the controller's `type` in the YAML ([[control-custom-config-launch]]); `type`: namespace and class; `base_class_type`: the base class. The nested `description` says what the plugin does.
- One XML lists every plugin of the package.

## Export the XML (CMakeLists.txt)
```cmake
pluginlib_export_plugin_description_file(controller_interface rrbot_controller.xml)
```
First the package of the base class, then the XML path relative to the package. The controller manager looks for controllers only among the XML files exported to `controller_interface`. The rest of the build file: [[control-custom-package-build]].

## Pitfalls
- `pluginlib_export_plugin_description_file(hardware_interface …)` copied from a hardware package → the controller manager never finds the controller: "Loader for controller '…' (type '…') not found."
- YAML `type` not equal to the XML `name` → the same message ([[control-controller-config]]).
- Macro inside the namespace braces → the class is not registered.
