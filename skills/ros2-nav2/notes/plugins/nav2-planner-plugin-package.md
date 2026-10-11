---
id: nav2-planner-plugin-package
type: reference
owner: equipo-ros2
updated: 2026-10-10
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "Planner plugin package: pkg create, CMakeLists.txt, package.xml export"
domain: nav2
area: plugins
distro: humble
tested: false
audience: dev
summary: "custom_nav2_planner_plugin package: ros2 pkg create with dependencies, CMakeLists.txt (straight_line_planner_core, pluginlib export for nav2_core), package.xml."
tags: [custom_nav2_planner_plugin, ros2 pkg create, CMakeLists.txt, straight_line_planner_core, pluginlib_export_plugin_description_file, nav2_core, PLUGINLIB__DISABLE_BOOST_FUNCTIONS, ament_export_libraries, package.xml]
see: ["[[nav2-planner-plugin-straight-line]]", "[[nav2-plugin-description-xml]]", "[[nav2-planner-plugin-config]]", "[[nav2-costmap-plugin-package]]"]
requires: [ros2-core]
version_notes:
  - "humble: PLUGINLIB__DISABLE_BOOST_FUNCTIONS is not read by pluginlib or class_loader (harmless); the <nav2_core plugin=…/> export in package.xml is not read either — https://github.com/ros/pluginlib/blob/humble/pluginlib/include/pluginlib/class_loader_imp.hpp (NAV2-V55, NAV2-V56)"
  - "lyrical: ament_target_dependencies() removed (deprecated in Kilted) — https://docs.ros.org/en/rolling/Releases/Release-Kilted-Kaiju.html (NAV2-V68, V09)"
---
# Planner plugin package: pkg create, CMakeLists.txt, package.xml

**TL;DR** Same procedure as the costmap plugin ([[nav2-costmap-plugin-package]]), with more dependencies and the base class package `nav2_core`.

## Step 1: Create the package
```bash
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_cmake custom_nav2_planner_plugin --dependencies rclcpp rclcpp_action rclcpp_lifecycle std_msgs visualization_msgs nav2_util nav2_msgs nav_msgs geometry_msgs builtin_interfaces tf2_ros nav2_costmap_2d nav2_core pluginlib
cd ~/ros2_ws
colcon build --packages-select custom_nav2_planner_plugin
source install/setup.bash
```

## CMakeLists.txt
```cmake
cmake_minimum_required(VERSION 3.8)
project(custom_nav2_planner_plugin)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclcpp_action REQUIRED)
find_package(rclcpp_lifecycle REQUIRED)
find_package(std_msgs REQUIRED)
find_package(visualization_msgs REQUIRED)
find_package(nav2_util REQUIRED)
find_package(nav2_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(builtin_interfaces REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(nav2_costmap_2d REQUIRED)
find_package(nav2_core REQUIRED)
find_package(pluginlib REQUIRED)

include_directories(include)

set(straight_plugin_name straight_line_planner_core)

set(dependencies
  rclcpp
  rclcpp_action
  rclcpp_lifecycle
  std_msgs
  visualization_msgs
  nav2_util
  nav2_msgs
  nav_msgs
  geometry_msgs
  builtin_interfaces
  tf2_ros
  nav2_costmap_2d
  nav2_core
  pluginlib
)

# StraightLine plugin related stuff
add_library(${straight_plugin_name} SHARED
  src/straight_line_planner.cpp)
ament_target_dependencies(${straight_plugin_name}
  ${dependencies})
target_compile_definitions(${straight_plugin_name} PUBLIC "PLUGINLIB__DISABLE_BOOST_FUNCTIONS")
pluginlib_export_plugin_description_file(nav2_core straight_line_plugin_info.xml)

install(TARGETS ${straight_plugin_name}
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY include/
  DESTINATION include/
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_export_include_directories(include)
ament_export_libraries(${straight_plugin_name})
ament_export_dependencies(${dependencies})
ament_package()
```
- Same structure as the costmap package; the description file is exported for the base package `nav2_core` ([[nav2-plugin-description-xml]]).
- `target_compile_definitions(… "PLUGINLIB__DISABLE_BOOST_FUNCTIONS")`: the course says it is needed to disable Boost functions. Humble's pluginlib never reads this define (a ROS 1 leftover, kept in Nav2's tutorial): harmless (NAV2-V55).

## package.xml
```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>custom_nav2_planner_plugin</name>
  <version>0.0.0</version>
  <description>TODO: Package description</description>
  <maintainer email="you@example.com">your_name</maintainer>
  <license>TODO: License declaration</license>

  <buildtool_depend>ament_cmake</buildtool_depend>

  <depend>rclcpp</depend>
  <depend>rclcpp_action</depend>
  <depend>rclcpp_lifecycle</depend>
  <depend>std_msgs</depend>
  <depend>visualization_msgs</depend>
  <depend>nav2_util</depend>
  <depend>nav2_msgs</depend>
  <depend>nav_msgs</depend>
  <depend>geometry_msgs</depend>
  <depend>builtin_interfaces</depend>
  <depend>tf2_ros</depend>
  <depend>nav2_costmap_2d</depend>
  <depend>nav2_core</depend>
  <depend>pluginlib</depend>

  <test_depend>ament_lint_auto</test_depend>
  <test_depend>ament_lint_common</test_depend>

  <export>
    <build_type>ament_cmake</build_type>
    <nav2_core plugin="${prefix}/straight_line_plugin_info.xml" />
  </export>
</package>
```

## Pitfalls
- A second plugin in the same package needs its own `add_library`, `install` and `pluginlib_export_plugin_description_file` ([[nav2-planner-plugin-wavy]]).
- `--dependencies` of `ros2 pkg create` only fills `package.xml` and `CMakeLists.txt` once; later dependencies must be added by hand in both.
