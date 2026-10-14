---
id: nav2-costmap-plugin-package
type: reference
owner: equipo-ros2
updated: 2026-10-10
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "Costmap layer plugin package: pkg create, CMakeLists.txt, package.xml export"
domain: nav2
area: plugins
distro: humble
tested: false
audience: dev
summary: "custom_nav2_costmap_plugin package: ros2 pkg create, CMakeLists.txt (library target, install, pluginlib_export_plugin_description_file), package.xml."
tags: [custom_nav2_costmap_plugin, ros2 pkg create, CMakeLists.txt, add_library, pluginlib_export_plugin_description_file, ament_target_dependencies, package.xml, costmap plugin]
see: ["[[nav2-plugin-description-xml]]", "[[nav2-costmap-plugin-gradient-layer]]", "[[nav2-costmap-plugin-config]]", "[[core-pkg-ament-cmake]]"]
requires: [ros2-core]
version_notes:
  - "humble: the <costmap_2d plugin=…/> export in package.xml is not read by pluginlib (the CMake macro registers the XML) — https://github.com/ros/pluginlib/blob/humble/pluginlib/include/pluginlib/class_loader_imp.hpp (NAV2-V56)"
  - "lyrical: ament_target_dependencies() is removed (deprecated in Kilted): use target_link_libraries(<lib> PUBLIC <pkg>::<pkg>) — https://docs.ros.org/en/rolling/Releases/Release-Kilted-Kaiju.html (NAV2-V68, V09)"
---
# Costmap layer plugin package: pkg create, CMakeLists.txt, package.xml

**TL;DR** Create a ROS 2 package for the costmap plugins, compile the plugin as a **library** and export it to the plugin system so that it can be found and used.

## Step 1: Create the package
```bash
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_cmake custom_nav2_costmap_plugin --dependencies rclcpp nav2_costmap_2d pluginlib
cd ~/ros2_ws
colcon build --packages-select custom_nav2_costmap_plugin
source install/setup.bash
```
Then add `src/gradient_layer.cpp` and `include/custom_nav2_costmap_plugin/gradient_layer.hpp` ([[nav2-costmap-plugin-gradient-layer]]) and the description file `gradient_layer.xml` ([[nav2-plugin-description-xml]]).

## CMakeLists.txt
```cmake
cmake_minimum_required(VERSION 3.8)
project(custom_nav2_costmap_plugin)

set(lib_name ${PROJECT_NAME}_core)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(nav2_costmap_2d REQUIRED)
find_package(pluginlib REQUIRED)

# You set a list of dependencies to make it more compact
set(dep_pkgs
  rclcpp
  nav2_costmap_2d
  pluginlib)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

# === Build ===
add_library(${lib_name} SHARED
  src/gradient_layer.cpp)
include_directories(include)

# === Installation ===
install(TARGETS ${lib_name}
  DESTINATION lib)

# === Ament work ===
# pluginlib_export_plugin_description_file() installs gradient_layer.xml
# file into "share" directory and sets ament indexes for it.
# This allows the plugin to be discovered as a plugin of required type.
pluginlib_export_plugin_description_file(nav2_costmap_2d gradient_layer.xml)
ament_target_dependencies(${lib_name} ${dep_pkgs})

ament_package()
```
- `set(lib_name ${PROJECT_NAME}_core)`: the library is `custom_nav2_costmap_plugin_core`, which is why `gradient_layer.xml` uses `<library path="custom_nav2_costmap_plugin_core">`.
- `dep_pkgs`: the list of dependencies of the library, used afterwards.
- `add_library(${lib_name} SHARED src/gradient_layer.cpp)`: compile `gradient_layer.cpp` into that library; `include_directories(include)` adds the header folder of the package.
- `install(TARGETS …)`: install the compiled library.
- `pluginlib_export_plugin_description_file(nav2_costmap_2d gradient_layer.xml)` and `ament_target_dependencies(…)`: make the library available to the plugin system (the first argument is the package of the base class).

## package.xml
```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>custom_nav2_costmap_plugin</name>
  <version>0.0.0</version>
  <description>TODO: Package description</description>
  <maintainer email="you@example.com">your_name</maintainer>
  <license>TODO: License declaration</license>

  <buildtool_depend>ament_cmake</buildtool_depend>

  <depend>rclcpp</depend>
  <depend>nav2_costmap_2d</depend>
  <depend>pluginlib</depend>

  <test_depend>ament_lint_auto</test_depend>
  <test_depend>ament_lint_common</test_depend>

  <export>
    <costmap_2d plugin="${prefix}/gradient_layer.xml" />
    <build_type>ament_cmake</build_type>
  </export>
</package>
```
The course changes only the `<costmap_2d plugin="${prefix}/gradient_layer.xml" />` line, to tell where the plugin info is. Nav2's own tutorial shows it too, but Humble's pluginlib finds the XML through the CMake macro above; the line is harmless (NAV2-V56).

## Pitfalls
- Forgetting `pluginlib_export_plugin_description_file()` → the costmap cannot find `custom_nav2_costmap_plugin/GradientLayer`.
- In Lyrical, replace `ament_target_dependencies()` with `target_link_libraries()` ([[core-pkg-ament-cmake]]).
