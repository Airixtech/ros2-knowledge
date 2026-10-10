---
id: nav2-plugin-description-xml
title: "Plugin description XML: library path, class name, type, base_class_type"
domain: nav2
area: plugins
distro: humble
tested: false
audience: dev
summary: "pluginlib description XML: library path = CMake target, class type, base_class_type, optional name used in the YAML."
tags: [pluginlib, plugin description XML, library path, class name, class type, base_class_type, class_libraries, gradient_layer.xml, straight_line_plugin_info.xml, regulated_pure_pursuit_controller_info.xml]
see: ["[[nav2-costmap-plugin-package]]", "[[nav2-planner-plugin-package]]", "[[nav2-controller-plugin-package]]", "[[nav2-plugins-overview]]"]
requires: [ros2-core]
version_notes:
  - "humble: pluginlib finds this XML through the ament index entry created by pluginlib_export_plugin_description_file() in CMake; the package.xml export line is not read — https://github.com/ros/pluginlib/blob/humble/pluginlib/include/pluginlib/class_loader_imp.hpp (NAV2-V56)"
---
# Plugin description XML: library path, class name, type, base_class_type

**TL;DR** For the system to load your plugin, create an information file in XML format, with any name, in the package root. It holds what pluginlib needs to find the compiled library of the plugin, the name you give it, and the namespace and class it uses.

## Costmap layer (gradient_layer.xml)
```bash
cd ~/ros2_ws/src/custom_nav2_costmap_plugin
touch gradient_layer.xml
```
```xml
<library path="custom_nav2_costmap_plugin_core">
  <class name="custom_nav2_costmap_plugin/GradientLayer" type="custom_nav2_costmap_plugin::GradientLayer" base_class_type="nav2_costmap_2d::Layer">
    <description>This is an example plugin which puts repeating costs gradients to costmap</description>
  </class>
</library>
```
- `library path`: the name of the library when you compile it, defined in `CMakeLists.txt` ([[nav2-costmap-plugin-package]]).
- `class type`: the **CUSTOM_PLUGIN_NAMESPACE**::**CUSTOM_CLASS** of your `.cpp` and `.hpp` files: here `custom_nav2_costmap_plugin` and `GradientLayer`.
- `class base_class_type`: the **base class with its namespace** your class derives from.
- `class name`: optional; if not placed, the name is the same as the `class type`. Using it makes your code more readable. Here the name is `custom_nav2_costmap_plugin/GradientLayer`, and it is what the YAML `plugin:` uses.

## Planner (straight_line_plugin_info.xml)
```bash
cd ~/ros2_ws/src/custom_nav2_planner_plugin
touch straight_line_plugin_info.xml
```
```xml
<library path="straight_line_planner_core">
  <class name="StraightLineCustomPlugin" type="nav2_straightline_planner_namespace_name::StraightLine" base_class_type="nav2_core::GlobalPlanner">
    <description>This is an example plugin which produces straight line path.</description>
  </class>
</library>
```
Same structure as the costmap one, with different names: the YAML loads `plugin: StraightLineCustomPlugin` ([[nav2-planner-plugin-config]]).

## Controller (regulated_pure_pursuit_controller_info.xml)
```bash
cd ~/ros2_ws/src/custom_nav2_controller_plugin
touch regulated_pure_pursuit_controller_info.xml
```
```xml
<library path="custom_pursuit_controller_plugin_core">
  <class type="custom_nav2_controller_plugin::RegulatedPurePursuitController" base_class_type="nav2_core::Controller">
    <description>Pure Pursuit Controller</description>
  </class>
</library>
```
There is no `<class name>`: when adding this plugin to the `.yaml` file, the name is the one in the `class type`, `custom_nav2_controller_plugin::RegulatedPurePursuitController` ([[nav2-controller-plugin-config]]). Several libraries can share one file inside `<class_libraries> … </class_libraries>`; the course's first version of this file did so, with the namespace `custom_nav2_controller_plugin_namespace_name`.

## Pitfalls
- `library path` ≠ the CMake library target → "Failed to load library" when the server configures.
- The YAML `plugin:` must equal `name` (or `type` when there is no `name`).
- The XML is found through `pluginlib_export_plugin_description_file(<base package> <file>.xml)` in CMake; the `<costmap_2d plugin=…/>` or `<nav2_core plugin=…/>` line in `package.xml` is a ROS 1 leftover that Humble's pluginlib ignores (harmless).
