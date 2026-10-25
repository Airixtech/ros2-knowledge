---
id: control-custom-package-build
type: reference
owner: equipo-ros2
updated: 2026-10-24
review_by: 2027-04-22
source: manual
confidentiality: internal
title: "CMakeLists.txt and package.xml of a controller package (rrbot_controller), Lyrical target_link_libraries"
domain: control
area: controllers
distro: jazzy
tested: false
audience: dev
summary: "rrbot_controller CMakeLists: add_library SHARED, generator expressions, ament_target_dependencies, install, exports; Lyrical target_link_libraries; package.xml; colcon build."
tags: [custom controller, CMakeLists.txt, add_library, SHARED, target_include_directories, BUILD_INTERFACE, INSTALL_INTERFACE, ament_target_dependencies, target_link_libraries, control_msgs_TARGETS, install, ament_export_dependencies, CMAKE_CXX_STANDARD, package.xml, colcon build]
see: ["[[control-custom-plugin-export]]", "[[control-hw-package-build]]", "[[control-custom-header]]", "[[control-custom-config-launch]]", "[[control-jazzy-to-lyrical]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: PLUGINLIB__DISABLE_BOOST_FUNCTIONS is read by no pluginlib version (humble, jazzy): left out — https://github.com/ros-controls/ros2_controllers/blob/jazzy/forward_command_controller/CMakeLists.txt (CONTROL-V58)"
  - "jazzy: the course's explanation says launch files are installed; the CMakeLists.txt installs only the library and include/ (CONTROL-V59)"
  - "jazzy: CMAKE_CXX_STANDARD 14 is raised to C++17 by controller_interface's cxx_std_17 [verify build] — https://github.com/ros-controls/ros2_control/blob/jazzy/controller_interface/CMakeLists.txt (CONTROL-V29)"
  - "lyrical: ament_target_dependencies removed (V09); target_link_libraries with namespaced targets — https://github.com/ros-controls/ros2_controllers/blob/master/forward_command_controller/CMakeLists.txt (CONTROL-V29)"
  - "jazzy: example_interfaces and the test_depend entries are not used by the code (CONTROL-V81)"
---
# CMakeLists.txt and package.xml of a controller package (rrbot_controller), Lyrical target_link_libraries

**TL;DR** Build the controller as a shared library, export its plugin XML ([[control-custom-plugin-export]]), install library and headers, and export the dependencies. `package.xml` keeps the dependencies given to `ros2 pkg create`.

## CMakeLists.txt
```cmake
cmake_minimum_required(VERSION 3.5)
project(rrbot_controller)

# Default to C++14
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 14)
endif()

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(control_msgs REQUIRED)
find_package(controller_interface REQUIRED)
find_package(hardware_interface REQUIRED)
find_package(pluginlib REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclcpp_lifecycle REQUIRED)
find_package(realtime_tools REQUIRED)
find_package(example_interfaces REQUIRED)

add_library(
  rrbot_controller
  SHARED
  src/rrbot_controller.cpp
)
target_include_directories(
  rrbot_controller
  PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)
ament_target_dependencies(
  rrbot_controller
  control_msgs
  controller_interface
  hardware_interface
  pluginlib
  rclcpp
  rclcpp_lifecycle
  realtime_tools
)

pluginlib_export_plugin_description_file(controller_interface rrbot_controller.xml)

install(
  TARGETS
  rrbot_controller
  RUNTIME DESTINATION bin
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
)

install(
  DIRECTORY include/
  DESTINATION include
)

ament_export_include_directories(
  include
)
ament_export_libraries(
  rrbot_controller
)
ament_export_dependencies(
  control_msgs
  controller_interface
  hardware_interface
  pluginlib
  rclcpp
  rclcpp_lifecycle
  realtime_tools
)

ament_package()
```
- `add_library(... SHARED ...)`: a plugin is a shared library. `target_include_directories` uses generator expressions (`$<BUILD_INTERFACE:…>`, `$<INSTALL_INTERFACE:…>`) for the include path at build and after install.
- `install(...)` copies the library to `lib` and the headers to `include`; the course's explanation also mentions launch files, but this file installs none. Unit 7.17 adds the `config` folder ([[control-custom-config-launch]]). The `ament_export_*` lines make headers, library and dependencies usable by other packages.
- The course has one more line, `target_compile_definitions(rrbot_controller PUBLIC "PLUGINLIB__DISABLE_BOOST_FUNCTIONS")` "to prevent pluginlib from using boost": no pluginlib version reads that definition, so it is left out.
- C++14: `controller_interface` requires C++17 on its target, which raises the standard when linking [verify build].

[changed in Lyrical: `ament_target_dependencies` is removed; link the targets instead, as the official controllers do]:
```cmake
target_link_libraries(rrbot_controller PUBLIC
  controller_interface::controller_interface
  hardware_interface::hardware_interface
  pluginlib::pluginlib
  rclcpp::rclcpp
  rclcpp_lifecycle::rclcpp_lifecycle
  realtime_tools::realtime_tools
  ${control_msgs_TARGETS})
```

## package.xml
```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>rrbot_controller</name>
  <version>0.0.0</version>
  <description>Controller for exemplary RRBot robot.</description>
  <maintainer email="you@example.com">Your Name</maintainer>
  <license>Apache License 2.0</license>

  <buildtool_depend>ament_cmake</buildtool_depend>

  <depend>control_msgs</depend>
  <depend>controller_interface</depend>
  <depend>hardware_interface</depend>
  <depend>pluginlib</depend>
  <depend>rclcpp</depend>
  <depend>rclcpp_lifecycle</depend>
  <depend>realtime_tools</depend>
  <depend>example_interfaces</depend>

  <test_depend>ament_cmake_gmock</test_depend>
  <test_depend>controller_manager</test_depend>
  <test_depend>hardware_interface</test_depend>
  <test_depend>ros2_control_test_assets</test_depend>

  <export>
    <build_type>ament_cmake</build_type>
  </export>
</package>
```
The `<depend>` lines are those of `ros2 pkg create`; nothing else is needed while the controller uses no external library. The course's file names the two upstream authors as maintainers: put your own. `example_interfaces` and the test dependencies are not used by the code.

## Build
```bash
cd ~/ros2_ws && colcon build --packages-select rrbot_controller
```
If it fails, read the compiler messages one by one; for example, a method signature that does not match the base class makes its `override` fail ([[control-custom-header]]).
