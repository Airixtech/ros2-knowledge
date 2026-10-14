---
id: core-pkg-ament-cmake
type: reference
owner: equipo-ros2
updated: 2026-10-09
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "ament_cmake package: CMakeLists for C++ and Python scripts"
domain: core
area: build-run
distro: humble
tested: false
audience: dev
summary: "Canonical CMakeLists.txt for C++ executables, installing Python scripts and modules in ament_cmake; Lyrical-safe linking."
tags: [ament_cmake, CMakeLists, ament_target_dependencies, target_link_libraries, install, scripts]
see: ["[[core-pkg-workspace]]", "[[core-pkg-dependencies]]", "[[core-iface-package]]", "[[core-topic-cpp]]"]
requires: []
version_notes:
  - "lyrical: ament_target_dependencies deprecated in Kilted (CMake warning) and removed in Lyrical; use target_link_libraries with targets — https://docs.ros.org/en/rolling/Releases/Release-Kilted-Kaiju.html (V09)"
  - "lyrical: CMake 4.x on Ubuntu 26.04; old cmake_minimum_required values warn [verify] — https://docs.ros.org/en/rolling/Releases/lyrical/supported-platforms.html (V11)"
---
# ament_cmake package: CMakeLists for C++ and Python scripts

**TL;DR** Every dependency needs `find_package`. Executables go to `lib/${PROJECT_NAME}` and data dirs to `share/${PROJECT_NAME}`. `ament_package()` comes last. `ament_target_dependencies` is fine on Humble, but it is gone in Lyrical.

## C++ CMakeLists.txt
```cmake
cmake_minimum_required(VERSION 3.8)
project(my_cpp_pkg)
if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)

add_executable(talker src/talker.cpp)
target_include_directories(talker PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include> $<INSTALL_INTERFACE:include>)
target_compile_features(talker PUBLIC cxx_std_17)
ament_target_dependencies(talker rclcpp std_msgs)

install(TARGETS talker DESTINATION lib/${PROJECT_NAME})
install(DIRECTORY launch config DESTINATION share/${PROJECT_NAME})

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()
ament_package()
```

## Linking that also works in Lyrical
`ament_target_dependencies` [changed in Lyrical: deprecated in Kilted, removed in Lyrical]. The modern form uses imported targets:
```cmake
target_link_libraries(talker PUBLIC rclcpp::rclcpp ${std_msgs_TARGETS})   # [verify] on Humble (Phase 5)
```
Message packages export `<pkg>_TARGETS`, and libraries export `<pkg>::<pkg>`. Do not mix keyword (`PUBLIC`) and plain `target_link_libraries` calls on the same target. Some macros, like `ament_add_gtest`, use the plain form.

## Python scripts inside an ament_cmake package
Each script needs the shebang `#!/usr/bin/env python3` and exec permission (`chmod +x`). Run it with `ros2 run pkg script.py` (the name includes `.py`).
```cmake
find_package(ament_cmake REQUIRED)
find_package(rclpy REQUIRED)
install(DIRECTORY scripts launch DESTINATION share/${PROJECT_NAME})
install(PROGRAMS scripts/node_a.py scripts/node_b.py DESTINATION lib/${PROJECT_NAME})
ament_package()
```
For an importable Python module in ament_cmake: `find_package(ament_cmake_python REQUIRED)` + `ament_python_install_package(${PROJECT_NAME})`. Never mix this with `rosidl_generate_interfaces` in the same pkg. Keep interfaces in a dedicated pkg ([[core-iface-package]]). [≥Lyrical: `ament_python_install_package` may be called several times]

## Pitfalls
- A script without `chmod +x` or without a shebang is installed, but `ros2 run` cannot execute it.
- A new script that is not listed in `install(PROGRAMS ...)` is not found. Rebuild and re-source after editing CMakeLists.
- `find_package(X)` without a matching `package.xml` tag breaks rosdep and other machines ([[core-pkg-dependencies]]).
