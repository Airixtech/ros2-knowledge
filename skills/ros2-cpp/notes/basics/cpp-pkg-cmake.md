---
id: cpp-pkg-cmake
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "ament_cmake package for C++ nodes: ros2 pkg create, layout, CMakeLists (add_executable, ament_target_dependencies, install), package.xml"
domain: cpp
area: basics
distro: humble
tested: false
audience: dev
summary: "Create an ament_cmake C++ package, its src/include layout, CMakeLists with add_executable, ament_target_dependencies, install; colcon build."
tags: [ament_cmake, ros2 pkg create, CMakeLists.txt, add_executable, ament_target_dependencies, install, colcon build, packages-select, mars_rover_systems]
see: ["[[core-pkg-ament-cmake]]", "[[core-pkg-workspace]]", "[[core-colcon-build]]", "[[cpp-cmake-library]]", "[[cpp-node-first-program]]", "[[cpp-humble-to-jazzy]]"]
requires: [ros2-core]
version_notes:
  - "all: colcon build --packages-select builds only the listed packages, not their dependencies (the course says 'and their dependencies'); --packages-up-to adds them — https://github.com/colcon/colcon-package-selection/blob/master/colcon_package_selection/package_selection/select_skip.py (CPP-V47)"
  - "lyrical: ament_target_dependencies deprecated in Kilted (CMake warning) and removed in Lyrical; target_link_libraries(tgt PUBLIC rclcpp::rclcpp) works since Humble — https://github.com/ament/ament_cmake/blob/lyrical/ament_cmake_target_dependencies/CHANGELOG.rst (CPP-V19, V09)"
---
# ament_cmake package for C++ nodes

**TL;DR** A C++ package is an `ament_cmake` package: `package.xml`, `CMakeLists.txt`, `src/` (`.cpp`) and `include/<package_name>/` (`.hpp`). Each executable needs three CMake lines: `add_executable`, `ament_target_dependencies` and `install(TARGETS … DESTINATION lib/${PROJECT_NAME})`. Build from the workspace root, then source `install/setup.bash`.

## Create and build
Packages always go in the workspace's `src` folder ([[core-pkg-workspace]]).
```bash
source /opt/ros/humble/setup.bash
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_cmake mars_rover_systems --dependencies rclcpp
# general form: ros2 pkg create --build-type ament_cmake <package_name> --dependencies <dep_1> <dep_2>
cd ~/ros2_ws
colcon build                                           # whole workspace, from ~/ros2_ws
colcon build --packages-select mars_rover_systems     # only this package
source ~/ros2_ws/install/setup.bash
ros2 pkg list | grep mars_rover_systems
```
`ros2 pkg create` prints the package data (`package format: 3`, `version: 0.0.0`, `build type: ament_cmake`, `dependencies: ['rclcpp']`) and creates `package.xml`, `CMakeLists.txt`, `src/` and `include/mars_rover_systems/`. It also warns `Unknown license 'TODO: License declaration'` and lists the ament license identifiers: Apache-2.0, BSL-1.0, BSD-2.0, BSD-2-Clause, BSD-3-Clause, GPL-3.0-only, LGPL-3.0-only, MIT, MIT-0. Build right after creating a package: it checks that the listed dependencies resolve (`Starting >>> mars_rover_systems` … `Summary: 1 package finished`).

```
ros2_ws/
    src/
        mars_rover_systems/
            package.xml
            CMakeLists.txt
            src/
            include/
        mars_rover_anotherpackage/
            ...
```

## One executable = three entries
```cmake
# Create executable
add_executable(executable_name src/source_file.cpp)
# Add dependencies
ament_target_dependencies(executable_name rclcpp)
# Install executables
install(TARGETS executable_name
  DESTINATION lib/${PROJECT_NAME})
```
- `add_executable(heartbeat_executable src/heartbeat.cpp)`: the executable name is what `ros2 run` uses; the source path is relative to the package root.
- `ament_target_dependencies(heartbeat_executable rclcpp)`: the ROS 2 packages the executable uses (each one needs a `find_package`).
- `install(TARGETS …)`: puts the binary where `ros2 run <name_of_the_package> <executable_name>` finds it.

## Complete CMakeLists.txt (end of unit 2: three executables and a launch folder)
```cmake
cmake_minimum_required(VERSION 3.8)
project(mars_rover_systems)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)

# Create executables
add_executable(heartbeat_executable src/heartbeat.cpp)
add_executable(heartbeat_executable2 src/heartbeat2.cpp)
add_executable(temperaturemonitor_executable src/temperature_monitor.cpp)

# Add dependencies
ament_target_dependencies(heartbeat_executable rclcpp)
ament_target_dependencies(heartbeat_executable2 rclcpp)
ament_target_dependencies(temperaturemonitor_executable rclcpp)

# Install executables
install(TARGETS
  heartbeat_executable
  heartbeat_executable2
  temperaturemonitor_executable
  DESTINATION lib/${PROJECT_NAME})

# Install launch files
install(DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}/)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
```
The course grows this file step by step: first only `heartbeat_executable`, then `heartbeat_executable_shutdown` (exercise 2.1), then `heartbeat_executable2`, the launch folder and `temperaturemonitor_executable` ([[cpp-learn-unit2-basics]]). `install(DIRECTORY …)` works for any folder the package ships (launch, config…). A header and a library of your own: [[cpp-cmake-library]].

Typing `ros2 run mars_rover_systems` and TAB twice lists the installed executables (`--prefix  heartbeat_executable  heartbeat_executable_shutdown`): an executable missing there was not added to `install(TARGETS …)` or the package was not rebuilt.

## Linking that also works in Lyrical
[changed in Lyrical: `ament_target_dependencies` removed (deprecated in Kilted)] — the target form is valid since Humble ([[core-pkg-ament-cmake]]):
```cmake
target_link_libraries(heartbeat_executable PUBLIC rclcpp::rclcpp)
```

## Pitfalls
- `colcon build --packages-select <pkg>` builds only that package, **not** its dependencies: build them first or use `--packages-up-to` (CPP-V47).
- Running `colcon build` outside `~/ros2_ws`, or a package outside `src/` → nothing (or the wrong folder) is built.
- After editing CMakeLists or adding an executable: rebuild and `source ~/ros2_ws/install/setup.bash` in every terminal.
