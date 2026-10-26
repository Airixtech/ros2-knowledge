---
id: cpp-learn-inter-unit9-lifecycle
type: reference
owner: equipo-ros2
updated: 2026-10-26
review_by: 2027-04-24
source: manual
confidentiality: internal
title: "Intermediate C++ Unit 9: managed_node_tests, parameters on a managed node, own lifecycle manager, exercises"
domain: cpp
area: learn
distro: humble
tested: false
audience: students
order: 18
summary: "managed_node_tests package, CMakeLists, launch files, the CLI walk-through, exercise 9.1 (parameters while active), exercise 9.2 (shutdown service), Nav2."
tags: [course, unit 9, managed_node_tests, managed_node_example, param_vel_lifecycle_node, lifecycle_manager, ros2 lifecycle, LifecycleNode launch, std_srvs Empty, shutdown_managed_node, students]
see: ["[[cpp-lifecycle-param-node]]", "[[cpp-lifecycle-manager-client]]", "[[cpp-lifecycle-node]]", "[[core-lifecycle-services-cli]]", "[[core-lifecycle-concepts]]", "[[core-learn-inter-unit9-lifecycle]]"]
requires: [ros2-core]
version_notes:
  - "course: the unit opens with a scan_publisher / managed_scan package and file, but builds managed_node_tests with managed_node_example.cpp (node param_vel_lifecycle_node, /cmd_vel) — course code (CPP-V63)"
  - "course: 'on_configuring' and 'after having done the activation, the node is in an inactive state' mean on_configure and 'after the configuration' — course text (CPP-V64)"
  - "all: managed nodes exist in Python too since Humble (rclpy.lifecycle); the course says C++ only — https://github.com/ros2/rclpy/tree/humble/rclpy/rclpy/lifecycle (CPP-V62)"
---
# Intermediate C++ Unit 9: managed nodes

**TL;DR** Package `managed_node_tests` holds the managed node of [[cpp-lifecycle-param-node]] (`managed_node_example`, node `param_vel_lifecycle_node`) and the manager of [[cpp-lifecycle-manager-client]] (`lifecycle_manager`). The unit drives the node through its states by hand, then with the manager, and shows why its parameters can change only when it is not active. States and transitions: [[core-lifecycle-concepts]]; services and CLI: [[core-lifecycle-services-cli]]. Python works too (`rclpy.lifecycle`, CPP-V62).

## Package, CMake, launch
```bash
cd ~/ros2_ws/src
ros2 pkg create managed_node_tests --dependencies rclcpp geometry_msgs lifecycle_msgs rclcpp_lifecycle
```
Every lifecycle application depends on `lifecycle_msgs` and `rclcpp_lifecycle`. The unit's first sentences name a `scan_publisher` in a `managed_scan` package; that is the Python course's example ([[cpp-lifecycle-node]]), not this package (CPP-V63).
```cmake
cmake_minimum_required(VERSION 3.8)
project(managed_node_tests)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(lifecycle_msgs REQUIRED)
find_package(rclcpp_lifecycle REQUIRED)

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

add_executable(managed_node_example src/managed_node_example.cpp)
ament_target_dependencies(managed_node_example rclcpp geometry_msgs lifecycle_msgs rclcpp_lifecycle)

install(TARGETS
  managed_node_example
  DESTINATION lib/${PROJECT_NAME})

install(DIRECTORY
  launch
  DESTINATION share/${PROJECT_NAME})

ament_package()
```
`launch/start_managed_node.launch.py`, first version, then with the manager (9.6):
```python
from launch import LaunchDescription
from launch_ros.actions import LifecycleNode, Node


def generate_launch_description():
    return LaunchDescription([
        LifecycleNode(package='managed_node_tests', executable='managed_node_example',
                      name='param_vel_lifecycle_node', namespace='', output='screen'),
        Node(package='managed_node_tests', name='manager_client_node',
             executable='lifecycle_manager', output='screen')
    ])
```
The first version has only the `LifecycleNode` (and imports only `LifecycleNode`). Build: `cd ~/ros2_ws && colcon build --packages-select managed_node_tests && source install/setup.bash`; run: `ros2 launch managed_node_tests start_managed_node.launch.py`.

## Walk-through (9.4–9.5)
```bash
ros2 topic list | grep /param_vel_lifecycle_node/transition_event
ros2 topic echo /param_vel_lifecycle_node/transition_event      # keep it open
ros2 topic info /cmd_vel -v                                     # Publisher count: 0 (still unconfigured)
ros2 service call /param_vel_lifecycle_node/get_state lifecycle_msgs/srv/GetState {}   # label='unconfigured'
ros2 lifecycle get /param_vel_lifecycle_node                    # unconfigured [1]
ros2 lifecycle set /param_vel_lifecycle_node configure          # Transitioning successful
ros2 topic info /cmd_vel -v                                     # Publisher count: 1, Node name: param_vel_lifecycle_node
ros2 lifecycle list param_vel_lifecycle_node -a                 # the full state machine
ros2 topic echo /cmd_vel                                        # nothing yet: inactive
ros2 lifecycle set /param_vel_lifecycle_node activate           # now it publishes
ros2 lifecycle set /param_vel_lifecycle_node deactivate         # pause
ros2 lifecycle set /param_vel_lifecycle_node shutdown           # finalized: still in ros2 node list, cannot come back
```
The echo shows `unconfigured → configuring` and `configuring → inactive` (ids 1 → 10 → 2). After the configuration (CPP-V64) the node is `inactive`. To restart from scratch: `deactivate` → `cleanup` → `configure` → `activate`. With the manager of 9.6 in the launch file, `ros2 lifecycle get /param_vel_lifecycle_node` prints `active [3]` right after launch.

## Exercise 9.1: parameters on a managed node
Launch, `configure` and `activate`, then `ros2 param set /param_vel_lifecycle_node angular_speed 0.5` → `Setting parameter failed: Parameters cannot be changed while the node is ACTIVE.` The procedure: `deactivate`, set `angular_speed 0.5`, `cleanup`, `configure`, `activate`; the robot moves. The same way you can change `publish_rate`, which without the lifecycle would need a restart of the node.

## Exercise 9.2: a shutdown service
Add to the program a service server `shutdown_managed_node` of type `std_srvs/srv/Empty` whose callback triggers the shutdown transition of the managed node. Relaunch: the manager brings the node to `active` and it publishes on `/cmd_vel`. Call the service from a terminal: the node must go to `finalized`, publishing stops, and `ros2 lifecycle get /param_vel_lifecycle_node` confirms the state.

## Nav2 (9.8)
Nav2 wraps its servers in `nav2_util::LifecycleNode` (with a bond to the lifecycle manager) and drives them with `nav2_lifecycle_manager` and its `manage_nodes` service: this is in the ros2-nav2 skill (notes `nav2-lifecycle-manager`, `nav2-lifecycle-manage-nodes`).
