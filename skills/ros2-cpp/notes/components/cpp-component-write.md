---
id: cpp-component-write
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "Write rclcpp components: NodeOptions constructor, RCLCPP_COMPONENTS_REGISTER_NODE, visibility_control.h, SHARED library"
domain: cpp
area: components
distro: humble
tested: false
audience: dev
summary: "Component = Node class with an explicit NodeOptions constructor, no main(), registered with RCLCPP_COMPONENTS_REGISTER_NODE, built as SHARED library with rclcpp_components_register_nodes."
tags: [component, rclcpp_components, RCLCPP_COMPONENTS_REGISTER_NODE, register_node_macro.hpp, rclcpp_components_register_nodes, NodeOptions, add_library SHARED, visibility_control.h, COMPOSITION_BUILDING_DLL, RobotStatusService]
see: ["[[cpp-component-run]]", "[[cpp-component-demo]]", "[[core-composition]]", "[[cpp-cmake-library]]"]
requires: [ros2-core]
version_notes:
  - "all: visibility_control.h, the COMPOSITION_BUILDING_DLL define and the COMPOSITION__ header guards are copied from the composition demo of ros2/demos (Apache-2.0, Open Source Robotics Foundation); rename them after your package; the composition dependency is not needed — https://github.com/ros2/demos/tree/humble/composition (CPP-V34)"
  - "course: robot_status_component.cpp uses std::setprecision without #include <iomanip>; no rclcpp header includes it [verify] (CPP-V39)"
---
# Write rclcpp components

**TL;DR** A component is an `rclcpp::Node` subclass with an `explicit Class(const rclcpp::NodeOptions & options)` constructor and **no `main()`**, registered at the end of the `.cpp` with `RCLCPP_COMPONENTS_REGISTER_NODE(ns::Class)`, compiled into a SHARED library and registered in CMake with `rclcpp_components_register_nodes(<lib> "ns::Class")`. A container process loads it at run time, or an own executable links it at compile time ([[cpp-component-run]]). Composition is an rclcpp feature: there is no Python component container ([[core-composition]]).

## Package
```bash
source /opt/ros/humble/setup.bash
cd ~/ros2_ws/src
ros2 pkg create rover_components --build-type ament_cmake --dependencies rclcpp rclcpp_components composition std_srvs
```
`rclcpp_components` and `std_srvs` are needed; `composition` is the demo package the course copies from, not needed by your package (CPP-V34).

## `include/rover_components/robot_status_component.hpp`
```cpp
#ifndef COMPOSITION__ROBOT_STATUS_COMPONENT_HPP_
#define COMPOSITION__ROBOT_STATUS_COMPONENT_HPP_

#include "rover_components/visibility_control.h"
#include "rclcpp/rclcpp.hpp"
#include "std_srvs/srv/trigger.hpp"

namespace rover_components
{

class RobotStatusService : public rclcpp::Node
{
public:
  COMPOSITION_PUBLIC
  explicit RobotStatusService(const rclcpp::NodeOptions & options);

private:
  void get_status_callback(
    const std::shared_ptr<std_srvs::srv::Trigger::Request> request,
    std::shared_ptr<std_srvs::srv::Trigger::Response> response);

  rclcpp::Service<std_srvs::srv::Trigger>::SharedPtr srv_;
};

}  // namespace rover_components

#endif  // COMPOSITION__ROBOT_STATUS_COMPONENT_HPP_
```

## `src/robot_status_component.cpp`
```cpp
#include "rover_components/robot_status_component.hpp"

#include <chrono>
#include <iomanip>   // std::setprecision; missing in the course's file (CPP-V39)
#include <iostream>
#include <memory>
#include <utility>
#include <random>
#include <sstream>

#include "rclcpp/rclcpp.hpp"
#include "std_srvs/srv/trigger.hpp"

namespace rover_components
{
RobotStatusService::RobotStatusService(const rclcpp::NodeOptions & options)
: Node("robot_status_service", options)
{
  // Create a service that will handle status queries from mission control
  srv_ = create_service<std_srvs::srv::Trigger>(
    "get_robot_status",
    std::bind(&RobotStatusService::get_status_callback, this,
              std::placeholders::_1, std::placeholders::_2));

  RCLCPP_INFO(this->get_logger(), "Robot Status Service Component Ready...");
}

void RobotStatusService::get_status_callback(
  const std::shared_ptr<std_srvs::srv::Trigger::Request> request,
  std::shared_ptr<std_srvs::srv::Trigger::Response> response){
  (void)request; // Suppress unused parameter warning
  // Generate simulated rover status data for Mars mission
  std::random_device rd;
  std::mt19937 gen(rd());
  std::uniform_real_distribution<> battery_dist(20.0, 100.0);
  std::uniform_real_distribution<> temp_dist(25.0, 80.0);
  std::uniform_int_distribution<> bool_dist(0, 1);

  double battery_level = battery_dist(gen);
  double temperature = temp_dist(gen);
  bool camera_status = bool_dist(gen);
  bool motor_statuses[4] = {
    static_cast<bool>(bool_dist(gen)),
    static_cast<bool>(bool_dist(gen)),
    static_cast<bool>(bool_dist(gen)),
    static_cast<bool>(bool_dist(gen))
  };

  // Construct response message for mission control
  response->success = true;

  std::ostringstream status_report;
  status_report << "Battery Level: " << std::fixed << std::setprecision(2) << battery_level << "%, "
                << "Temperature: " << std::fixed << std::setprecision(2) << temperature << "°C, "
                << "Camera: " << (camera_status ? "Operational" : "Faulty") << ", "
                << "Motor 1: " << (motor_statuses[0] ? "Operational" : "Faulty") << ", "
                << "Motor 2: " << (motor_statuses[1] ? "Operational" : "Faulty") << ", "
                << "Motor 3: " << (motor_statuses[2] ? "Operational" : "Faulty") << ", "
                << "Motor 4: " << (motor_statuses[3] ? "Operational" : "Faulty") << ", ";

  response->message = status_report.str();

  RCLCPP_INFO(this->get_logger(), "Status report requested by mission control");
}

}

#include "rclcpp_components/register_node_macro.hpp"
RCLCPP_COMPONENTS_REGISTER_NODE(rover_components::RobotStatusService)
```
The class lives in the namespace `rover_components`; the registration macro at the end makes the class loadable by name. Being only a shared library, the component has no `main()`.

## `include/rover_components/visibility_control.h`
Copied from the composition demo (Apache-2.0; rename the `COMPOSITION_` prefix after your package, CPP-V34). It marks which symbols the shared library exports (on Windows `dllexport`/`dllimport`, with GCC `visibility("default")`); background: <https://gcc.gnu.org/wiki/Visibility>.
```cpp
// Copyright 2016 Open Source Robotics Foundation, Inc.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#ifndef COMPOSITION__VISIBILITY_CONTROL_H_
#define COMPOSITION__VISIBILITY_CONTROL_H_

#ifdef __cplusplus
extern "C"
{
#endif

// This logic was borrowed (then namespaced) from the examples on the gcc wiki:
//     https://gcc.gnu.org/wiki/Visibility

#if defined _WIN32 || defined __CYGWIN__
  #ifdef __GNUC__
    #define COMPOSITION_EXPORT __attribute__ ((dllexport))
    #define COMPOSITION_IMPORT __attribute__ ((dllimport))
  #else
    #define COMPOSITION_EXPORT __declspec(dllexport)
    #define COMPOSITION_IMPORT __declspec(dllimport)
  #endif
  #ifdef COMPOSITION_BUILDING_DLL
    #define COMPOSITION_PUBLIC COMPOSITION_EXPORT
  #else
    #define COMPOSITION_PUBLIC COMPOSITION_IMPORT
  #endif
  #define COMPOSITION_PUBLIC_TYPE COMPOSITION_PUBLIC
  #define COMPOSITION_LOCAL
#else
  #define COMPOSITION_EXPORT __attribute__ ((visibility("default")))
  #define COMPOSITION_IMPORT
  #if __GNUC__ >= 4
    #define COMPOSITION_PUBLIC __attribute__ ((visibility("default")))
    #define COMPOSITION_LOCAL  __attribute__ ((visibility("hidden")))
  #else
    #define COMPOSITION_PUBLIC
    #define COMPOSITION_LOCAL
  #endif
  #define COMPOSITION_PUBLIC_TYPE
#endif

#ifdef __cplusplus
}
#endif

#endif  // COMPOSITION__VISIBILITY_CONTROL_H_
```

## CMakeLists.txt
```cmake
cmake_minimum_required(VERSION 3.8)
project(rover_components)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclcpp_components REQUIRED)
find_package(std_srvs REQUIRED)

include_directories(include)

add_library(robot_status_component SHARED src/robot_status_component.cpp)
target_compile_definitions(robot_status_component PRIVATE "COMPOSITION_BUILDING_DLL")
ament_target_dependencies(robot_status_component
  "rclcpp"
  "rclcpp_components"
  "std_srvs")

rclcpp_components_register_nodes(robot_status_component "rover_components::RobotStatusService")

install(TARGETS
  robot_status_component
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin)

# Install headers if you have any
install(DIRECTORY include/
  DESTINATION include/)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
```
- `add_library(… SHARED …)`: a shared library instead of an executable.
- `target_compile_definitions(… PRIVATE "COMPOSITION_BUILDING_DLL")`: inside the library the macros export.
- `rclcpp_components_register_nodes(…)`: adds the class to the ament index so `ros2 component types` and the containers find it.
- `install(TARGETS … LIBRARY DESTINATION lib …)`: the library goes to `lib/`, not `lib/${PROJECT_NAME}`.

## Pitfalls
- A constructor without `NodeOptions` (or not `explicit … (const rclcpp::NodeOptions &)`) cannot be loaded by a container.
- The class name in `RCLCPP_COMPONENTS_REGISTER_NODE` and in `rclcpp_components_register_nodes` must be the same fully qualified name.
- Two packages that both copy the demo's `COMPOSITION__VISIBILITY_CONTROL_H_` guard skip each other's header when included together: rename (CPP-V34).
