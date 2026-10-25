---
id: cpp-cmake-library
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "Own header and library in an ament_cmake package: include/<pkg>, add_library, target_link_libraries, OpenCV, package.xml"
domain: cpp
area: basics
distro: humble
tested: false
audience: dev
summary: "mars_rover_tasks CMakeLists: include_directories, add_library + target_link_libraries, cv_bridge/OpenCV, tf2, custom_interfaces; package.xml with libopencv-dev."
tags: [add_library, target_link_libraries, include_directories, target_include_directories, OpenCV, OpenCV_LIBRARIES, cv_bridge, tf2, package.xml, libopencv-dev, rosdep, mars_rover_tasks]
see: ["[[cpp-pkg-cmake]]", "[[core-pkg-ament-cmake]]", "[[core-pkg-dependencies]]", "[[cpp-recipe-cv-bridge]]", "[[cpp-iface-use]]"]
requires: [ros2-core]
version_notes:
  - "course: <depend>OpenCV</depend> (and <depend>opencv2</depend> in unit 5.5) are not rosdep keys, so rosdep install fails; the key is libopencv-dev, as in cv_bridge's own package.xml — https://github.com/ros/rosdistro/blob/master/rosdep/base.yaml, https://github.com/ros-perception/vision_opencv/blob/humble/cv_bridge/package.xml (CPP-V03)"
  - "lyrical: ament_target_dependencies removed (deprecated in Kilted) — https://github.com/ament/ament_cmake/blob/lyrical/ament_cmake_target_dependencies/CHANGELOG.rst (CPP-V19, V09)"
---
# Own header and library in an ament_cmake package

**TL;DR** Headers go in `include/<package_name>/` and are included as `"<package_name>/file.hpp"`; the compiler finds them through `include_directories(include)` (or per target, `target_include_directories`). Code shared by several executables becomes a library (`add_library`) that the executables link with `target_link_libraries`. Every package you use needs `find_package` in CMake **and** a `<depend>` in package.xml with a valid rosdep key.

## The plant detector library (unit 3.7)
The course provides `plant_detector.hpp` (class `PlantDetector`, method `predict()`), `plant_detector.cpp` and the model file `best_plant_detector_model.pth` in its extra-files repository (link given in the course). The header goes to `include/mars_rover_tasks/`, the source to `src/`, and the node includes `"mars_rover_tasks/plant_detector.hpp"` ([[cpp-recipe-cv-bridge]]).

## Complete CMakeLists.txt of `mars_rover_tasks` (end of unit 3)
```cmake
cmake_minimum_required(VERSION 3.8)
project(mars_rover_tasks)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(cv_bridge REQUIRED)
find_package(OpenCV REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_geometry_msgs REQUIRED)
find_package(custom_interfaces REQUIRED)  # Add this line

# Include directories
include_directories(include)

add_executable(subscriber_obstacle_detector_executable src/subscriber_obstacle_detector.cpp)
ament_target_dependencies(subscriber_obstacle_detector_executable
  rclcpp
  std_msgs
  sensor_msgs
  geometry_msgs
)

add_executable(publish_mars_rover_move_executable src/publish_mars_rover_move.cpp)
ament_target_dependencies(publish_mars_rover_move_executable rclcpp geometry_msgs)

# Build plant detector library
add_library(plant_detector_lib src/plant_detector.cpp)
target_link_libraries(plant_detector_lib ${OpenCV_LIBRARIES})

add_executable(image_plant_detector_executable src/plant_detector_node.cpp)
ament_target_dependencies(image_plant_detector_executable
  rclcpp
  sensor_msgs
  std_msgs
  nav_msgs
  cv_bridge
  OpenCV
  custom_interfaces  # Add this line
)
target_link_libraries(image_plant_detector_executable plant_detector_lib)

add_executable(autonomous_exploration_executable src/autonomous_exploration.cpp)
ament_target_dependencies(autonomous_exploration_executable
  rclcpp
  sensor_msgs
  geometry_msgs
  nav_msgs
  tf2
  tf2_geometry_msgs
)

install(TARGETS
  subscriber_obstacle_detector_executable
  publish_mars_rover_move_executable
  image_plant_detector_executable
  autonomous_exploration_executable
  DESTINATION lib/${PROJECT_NAME})

install(DIRECTORY launch DESTINATION share/${PROJECT_NAME}/)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
```
What each addition does:
- `find_package(cv_bridge REQUIRED)` and `find_package(OpenCV REQUIRED)`: convert ROS images to OpenCV and process them.
- `include_directories(include)`: the compiler finds `mars_rover_tasks/plant_detector.hpp`. Per-target form: `target_include_directories(<tgt> PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include> $<INSTALL_INTERFACE:include>)` ([[core-pkg-ament-cmake]]).
- `add_library(plant_detector_lib src/plant_detector.cpp)` + `target_link_libraries(plant_detector_lib ${OpenCV_LIBRARIES})`: the detector is built once as a library linked against OpenCV.
- `target_link_libraries(image_plant_detector_executable plant_detector_lib)`: the node links the library; `ament_target_dependencies` adds its ROS packages.
- `nav_msgs`, `tf2`, `tf2_geometry_msgs` arrive with the odometry and yaw code of 3.7 ([[cpp-pub-sub-node]]); `custom_interfaces` with `RoverEvents` in 3.9 ([[cpp-iface-use]]).

## package.xml
The dependency list of the course, with the OpenCV key corrected (CPP-V03):
```xml
<buildtool_depend>ament_cmake</buildtool_depend>
<depend>rclcpp</depend>
<depend>geometry_msgs</depend>
<depend>sensor_msgs</depend>
<depend>std_msgs</depend>
<depend>nav_msgs</depend>
<depend>cv_bridge</depend>
<depend>libopencv-dev</depend>   <!-- the course writes <depend>OpenCV</depend>: not a rosdep key -->
<depend>tf2</depend>
<depend>tf2_geometry_msgs</depend>
<depend>custom_interfaces</depend>
<test_depend>ament_lint_auto</test_depend>
<test_depend>ament_lint_common</test_depend>
```
Use your name and e-mail in `<maintainer>` (the generated `user@todo.todo` is a placeholder) and a real license id.

## Linking that also works in Lyrical
[changed in Lyrical: `ament_target_dependencies` removed] — targets exported since Humble:
```cmake
target_link_libraries(image_plant_detector_executable PUBLIC
  rclcpp::rclcpp cv_bridge::cv_bridge ${sensor_msgs_TARGETS} ${std_msgs_TARGETS} ${nav_msgs_TARGETS}
  ${custom_interfaces_TARGETS} ${OpenCV_LIBS} plant_detector_lib)
```
`${OpenCV_LIBS}` is OpenCV's documented variable. Mixing this keyword form with the plain `target_link_libraries(tgt lib)` call on the same target is an error: use one style per target ([[core-pkg-ament-cmake]]).

## Pitfalls
- `rosdep install` stops at `<depend>OpenCV</depend>` / `<depend>opencv2</depend>` ("Cannot locate rosdep definition"); colcon does not read the tag, so the build hides the error (CPP-V03).
- A package used in `ament_target_dependencies` without its own `find_package` may still build because another package exports it (`sensor_msgs` brings `std_msgs`, `geometry_msgs`): declare it anyway (CPP-V20).
- Header in `include/` but no include path → `fatal error: mars_rover_tasks/plant_detector.hpp: No such file or directory`.
