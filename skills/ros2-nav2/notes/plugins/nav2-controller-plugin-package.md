---
id: nav2-controller-plugin-package
type: reference
owner: equipo-ros2
updated: 2026-10-10
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "Controller plugin package: pkg create, CMakeLists.txt, package.xml export"
domain: nav2
area: plugins
distro: humble
tested: false
audience: dev
summary: "custom_nav2_controller_plugin package: ros2 pkg create, CMakeLists.txt (C++17, custom_pursuit_controller_plugin_core, pluginlib export for nav2_core), package.xml."
tags: [custom_nav2_controller_plugin, ros2 pkg create, CMakeLists.txt, custom_pursuit_controller_plugin_core, CMAKE_CXX_STANDARD, pluginlib_export_plugin_description_file, nav2_core, package.xml]
see: ["[[nav2-controller-plugin-rpp]]", "[[nav2-plugin-description-xml]]", "[[nav2-controller-plugin-config]]", "[[nav2-planner-plugin-package]]"]
requires: [ros2-core]
version_notes:
  - "humble: PLUGINLIB__DISABLE_BOOST_FUNCTIONS has no effect and the <nav2_core plugin=…/> line of package.xml is not read by pluginlib (both harmless) — https://github.com/ros/pluginlib/blob/humble/pluginlib/include/pluginlib/class_loader_imp.hpp (NAV2-V55, NAV2-V56)"
  - "lyrical: ament_target_dependencies() removed (deprecated in Kilted) — https://docs.ros.org/en/rolling/Releases/Release-Kilted-Kaiju.html (NAV2-V68, V09)"
---
# Controller plugin package: pkg create, CMakeLists.txt, package.xml

**TL;DR** Same steps as the costmap and planner plugins ([[nav2-planner-plugin-package]]), for a plugin of base class `nav2_core::Controller`.

## Step 1: Create the package
```bash
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_cmake custom_nav2_controller_plugin --dependencies rclcpp geometry_msgs nav2_costmap_2d pluginlib nav_msgs nav2_util nav2_core tf2
cd ~/ros2_ws
colcon build --packages-select custom_nav2_controller_plugin
source install/setup.bash
```

## CMakeLists.txt
```cmake
cmake_minimum_required(VERSION 3.8)
project(custom_nav2_controller_plugin)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

set(CMAKE_CXX_STANDARD 17)

set(custom_nav2_controller_plugin_name custom_pursuit_controller_plugin_core)

include_directories(include)

set(dependencies
  rclcpp
  geometry_msgs
  nav2_costmap_2d
  pluginlib
  nav_msgs
  nav2_util
  nav2_core
  tf2
)

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(nav2_costmap_2d REQUIRED)
find_package(pluginlib REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(nav2_util REQUIRED)
find_package(nav2_core REQUIRED)
find_package(tf2 REQUIRED)

add_library(${custom_nav2_controller_plugin_name} SHARED
  src/regulated_pure_pursuit_controller.cpp)

# prevent pluginlib from using boost
target_compile_definitions(${custom_nav2_controller_plugin_name} PUBLIC "PLUGINLIB__DISABLE_BOOST_FUNCTIONS")

ament_target_dependencies(${custom_nav2_controller_plugin_name}
  ${dependencies}
)

install(TARGETS ${custom_nav2_controller_plugin_name}
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin
)

install(DIRECTORY include/
  DESTINATION include/
)

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

ament_export_include_directories(include)
ament_export_libraries(${custom_nav2_controller_plugin_name})
ament_export_dependencies(${dependencies})

pluginlib_export_plugin_description_file(nav2_core regulated_pure_pursuit_controller_info.xml)

ament_package()
```
The library name `custom_pursuit_controller_plugin_core` is the `library path` of `regulated_pure_pursuit_controller_info.xml` ([[nav2-plugin-description-xml]]); C++17 is needed by the RPP code (`std::clamp`).

## package.xml
```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>custom_nav2_controller_plugin</name>
  <version>0.0.0</version>
  <description>TODO: Package description</description>
  <maintainer email="you@example.com">your_name</maintainer>
  <license>TODO: License declaration</license>

  <buildtool_depend>ament_cmake</buildtool_depend>

  <depend>rclcpp</depend>
  <depend>geometry_msgs</depend>
  <depend>nav2_costmap_2d</depend>
  <depend>pluginlib</depend>
  <depend>nav_msgs</depend>
  <depend>nav2_util</depend>
  <depend>nav2_core</depend>
  <depend>tf2</depend>

  <test_depend>ament_lint_auto</test_depend>
  <test_depend>ament_lint_common</test_depend>

  <export>
    <build_type>ament_cmake</build_type>
    <nav2_core plugin="${prefix}/regulated_pure_pursuit_controller_info.xml" />
  </export>
</package>
```

## Pitfalls
- The comment "prevent pluginlib from using boost" is outdated: Humble's pluginlib does not use Boost (NAV2-V55).
- `RUNTIME DESTINATION bin` (here) vs `lib/${PROJECT_NAME}` (planner package): irrelevant for a shared library on Linux, which installs to `lib`.
