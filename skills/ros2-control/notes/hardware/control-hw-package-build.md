---
id: control-hw-package-build
type: reference
owner: equipo-ros2
updated: 2026-10-24
review_by: 2027-04-22
source: manual
confidentiality: internal
title: "CMakeLists.txt and package.xml of a hardware interface package (template and Dynamixel)"
domain: control
area: hardware
distro: jazzy
tested: false
audience: dev
summary: "Hardware interface CMakeLists: add_library SHARED, ament_target_dependencies, pluginlib_export_plugin_description_file, install lib/include/launch/config, exports; package.xml; Dynamixel differences."
tags: [CMakeLists.txt, package.xml, add_library, SHARED, ament_target_dependencies, target_link_libraries, pluginlib_export_plugin_description_file, install, ament_export_dependencies, CMAKE_CXX_STANDARD, dynamixel_workbench_toolbox]
see: ["[[control-hw-plugin-export]]", "[[control-hw-template-header]]", "[[control-dynamixel-sdk]]", "[[control-bringup-hardware-launch]]", "[[control-jazzy-to-lyrical]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: CMAKE_CXX_STANDARD 14 is raised to C++17 by the cxx_std_17 compile feature of the hardware_interface target [verify build] — https://github.com/ros-controls/ros2_control/blob/jazzy/hardware_interface/CMakeLists.txt (CONTROL-V29)"
  - "kilted: ament_target_dependencies deprecated; lyrical: removed, use target_link_libraries with namespaced targets (V09) — https://github.com/ros-controls/ros2_control_demos/blob/master/example_1/CMakeLists.txt (CONTROL-V29)"
---
# CMakeLists.txt and package.xml of a hardware interface package (template and Dynamixel)

**TL;DR** Build the hardware interface as a shared library, export its plugin description, install the library, headers and the `launch`/`config` folders, and export its dependencies. `package.xml` keeps the dependencies given to `ros2 pkg create` and adds the vendor library when there is one.

## CMakeLists.txt (template)
```cmake
cmake_minimum_required(VERSION 3.8)
project(my_robot_hardware_interface)

# Default to C++14
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 14)
endif()

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(hardware_interface REQUIRED)
find_package(pluginlib REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclcpp_lifecycle REQUIRED)

## COMPILE
add_library(
  ${PROJECT_NAME}
  SHARED
  src/my_robot_hardware_interface.cpp
)
target_include_directories(
  ${PROJECT_NAME}
  PRIVATE
  include
)
ament_target_dependencies(
  ${PROJECT_NAME}
  hardware_interface
  pluginlib
  rclcpp
  rclcpp_lifecycle
)

pluginlib_export_plugin_description_file(hardware_interface my_robot_hardware_interface.xml)

# INSTALL
install(
  TARGETS ${PROJECT_NAME}
  DESTINATION lib
)
install(
  DIRECTORY include/
  DESTINATION include
)
install(
  DIRECTORY
    launch
    config
  DESTINATION
    share/${PROJECT_NAME}/
)

if(BUILD_TESTING)
  find_package(ament_cmake_gtest REQUIRED)
endif()

## EXPORTS
ament_export_include_directories(
  include
)
ament_export_libraries(
  ${PROJECT_NAME}
)
ament_export_dependencies(
  hardware_interface
  pluginlib
  rclcpp
  rclcpp_lifecycle
)
ament_package()
```
- `add_library(… SHARED …)`: the plugin is a library loaded at run time; its target name is the `library path` of the plugin XML ([[control-hw-plugin-export]]).
- `pluginlib_export_plugin_description_file(...)` registers the plugin XML in the resource index.
- `install(TARGETS …)` and `install(DIRECTORY include/ …)` copy the binary to `lib` and the headers to `include`; the third `install` copies `launch` and `config` to the share folder ([[control-bringup-hardware-launch]]).
- The `EXPORTS` lines let other packages use this library.
- `C++14`: the `hardware_interface` target requires C++17 (`cxx_std_17`), which CMake applies when it links that target; drop the C++14 lines rather than rely on that [verify].
- [changed in Kilted: `ament_target_dependencies` deprecated] [changed in Lyrical: removed]. Lyrical form, as in the official demo:
```cmake
target_link_libraries(${PROJECT_NAME} PUBLIC
  hardware_interface::hardware_interface
  pluginlib::pluginlib
  rclcpp::rclcpp
  rclcpp_lifecycle::rclcpp_lifecycle
)
```

## package.xml (template, unchanged)
```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>my_robot_hardware_interface</name>
  <version>0.0.0</version>
  <description>TODO: Package description</description>
  <maintainer email="user@todo.todo">user</maintainer>
  <license>TODO: License declaration</license>

  <buildtool_depend>ament_cmake</buildtool_depend>

  <depend>hardware_interface</depend>
  <depend>pluginlib</depend>
  <depend>rclcpp</depend>
  <depend>rclcpp_lifecycle</depend>

  <test_depend>ament_lint_auto</test_depend>
  <test_depend>ament_lint_common</test_depend>

  <export>
    <build_type>ament_cmake</build_type>
  </export>
</package>
```
The template uses no external library, so nothing is added.

## Dynamixel package: what differs
```cmake
cmake_minimum_required(VERSION 3.5)
project(dynamixel_hardware_interface)

# Default to C99
if(NOT CMAKE_C_STANDARD)
  set(CMAKE_C_STANDARD 99)
endif()
# (same C++14 block)
if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(dynamixel_workbench_toolbox REQUIRED)   # no rclcpp_lifecycle in this package
add_library(${PROJECT_NAME} SHARED src/dynamixel_hardware_interface.cpp)
ament_target_dependencies(${PROJECT_NAME} rclcpp hardware_interface pluginlib dynamixel_workbench_toolbox)
pluginlib_export_plugin_description_file(hardware_interface dynamixel_hardware.xml)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # uncomment the line when a copyright and license is not present in all source files
  #set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # uncomment the line when this package is not in a git repo
  #set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_export_dependencies(rclcpp hardware_interface pluginlib dynamixel_workbench_toolbox)
```
The rest (`target_include_directories`, the three `install` calls, the include and library exports) is the template's. `find_package(dynamixel_workbench_toolbox)` finds the manufacturer's library and `ament_target_dependencies` links it. In `package.xml`:
```xml
<name>dynamixel_hardware_interface</name>
<maintainer email="to-do">user</maintainer>
<depend>rclcpp</depend>
<depend>hardware_interface</depend>
<depend>pluginlib</depend>
<depend>dynamixel_workbench_toolbox</depend>
```
Lyrical: link `dynamixel_workbench_toolbox::dynamixel_workbench_toolbox`, as the upstream `dynamixel_hardware` 0.6.1 does.

## Pitfalls
- `install(DIRECTORY launch config …)` fails at install time if either folder does not exist yet: create both before building.
- Vendor library missing from `package.xml` → `rosdep` does not install it and `find_package` fails on a new machine.
