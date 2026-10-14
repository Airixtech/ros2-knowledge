---
id: core-lifecycle-cpp-node
type: reference
owner: equipo-ros2
updated: 2026-10-14
review_by: 2027-04-12
source: manual
confidentiality: internal
title: "C++ managed node: LifecycleNode, LifecyclePublisher, CMake and launch"
domain: core
area: tools
distro: humble
tested: false
audience: dev
summary: "Complete rclcpp_lifecycle node with a LifecyclePublisher, its CMakeLists.txt, a LifecycleNode launch action and the transition_event topic."
tags: [rclcpp_lifecycle, LifecycleNode, LifecyclePublisher, managed node, on_configure, on_activate, transition_event, lifecycle_msgs, CMakeLists]
see: ["[[core-lifecycle-concepts]]", "[[core-lifecycle-node]]", "[[core-lifecycle-services-cli]]", "[[core-lifecycle-manager-client]]"]
requires: []
version_notes:
  - "humble: managed nodes also exist in Python (rclpy.lifecycle, new in Humble) — https://github.com/ros2/rclpy/tree/humble/rclpy/rclpy/lifecycle (V98)"
  - "humble: ament_package() must be the last call of CMakeLists.txt — https://docs.ros.org/en/humble/How-To-Guides/Ament-CMake-Documentation.html (V97)"
  - "lyrical: ament_target_dependencies deprecated in Kilted, removed in Lyrical; use target_link_libraries with exported targets — https://docs.ros.org/en/rolling/Releases/Release-Kilted-Kaiju.html (V09)"
---
# C++ managed node: LifecycleNode, LifecyclePublisher, CMake and launch

**TL;DR** A managed (lifecycle) node inherits from `rclcpp_lifecycle::LifecycleNode` and overrides `on_configure`, `on_activate`, `on_deactivate`, `on_cleanup`, `on_shutdown` and `on_error`, each returning `SUCCESS` or `FAILURE`. Its publishers are `LifecyclePublisher`s: they exist after configure and only publish while active. Python works too in Humble ([[core-lifecycle-node]]). States and transitions: [[core-lifecycle-concepts]].

This node simulates a laser driver that publishes on `/managed_scan` once its hardware is "connected". Every lifecycle program depends on `lifecycle_msgs`, `rclcpp_lifecycle` and `std_msgs`: add them to `package.xml` and `CMakeLists.txt`.
```bash
ros2 pkg create --build-type ament_cmake managed_scan --dependencies rclcpp
```

## src/managed_scan.cpp
```cpp
#include <chrono>
#include <iostream>
#include <memory>
#include <string>
#include <thread>
#include <utility>

#include "lifecycle_msgs/msg/transition.hpp"

#include "rclcpp/rclcpp.hpp"
#include "rclcpp/publisher.hpp"

#include "rclcpp_lifecycle/lifecycle_node.hpp"
#include "rclcpp_lifecycle/lifecycle_publisher.hpp"

#include "rcutils/logging_macros.h"

#include "std_msgs/msg/string.hpp"

using namespace std::chrono_literals;

class ManagedScan : public rclcpp_lifecycle::LifecycleNode
{
public:
  explicit ManagedScan(const std::string & node_name, bool intra_process_comms = false)
  : rclcpp_lifecycle::LifecycleNode(node_name,
      rclcpp::NodeOptions().use_intra_process_comms(intra_process_comms))
  {}

  void
  publish()
  {
    static size_t count = 0;
    auto msg = std::make_unique<std_msgs::msg::String>();
    msg->data = "Lifecycle HelloWorld #" + std::to_string(++count);

    if (!pub_->is_activated()) {
      RCLCPP_INFO(
        get_logger(), "Lifecycle publisher is currently inactive. Messages are not published.");
    } else {
      RCLCPP_INFO(
        get_logger(), "Lifecycle publisher is active. Publishing: [%s]", msg->data.c_str());
    }

    pub_->publish(std::move(msg));
  }

  rclcpp_lifecycle::node_interfaces::LifecycleNodeInterface::CallbackReturn
  on_configure(const rclcpp_lifecycle::State &)
  {
    pub_ = this->create_publisher<std_msgs::msg::String>("managed_scan", 10);
    timer_ = this->create_wall_timer(
      1s, std::bind(&ManagedScan::publish, this));

    RCLCPP_INFO(get_logger(), "on_configure() is called.");

    return rclcpp_lifecycle::node_interfaces::LifecycleNodeInterface::CallbackReturn::SUCCESS;
  }

  rclcpp_lifecycle::node_interfaces::LifecycleNodeInterface::CallbackReturn
  on_activate(const rclcpp_lifecycle::State &)
  {
    pub_->on_activate();

    RCUTILS_LOG_INFO_NAMED(get_name(), "on_activate() is called.");

    std::this_thread::sleep_for(2s);

    return rclcpp_lifecycle::node_interfaces::LifecycleNodeInterface::CallbackReturn::SUCCESS;
  }

  rclcpp_lifecycle::node_interfaces::LifecycleNodeInterface::CallbackReturn
  on_deactivate(const rclcpp_lifecycle::State &)
  {
    pub_->on_deactivate();

    RCUTILS_LOG_INFO_NAMED(get_name(), "on_deactivate() is called.");

    return rclcpp_lifecycle::node_interfaces::LifecycleNodeInterface::CallbackReturn::SUCCESS;
  }

  rclcpp_lifecycle::node_interfaces::LifecycleNodeInterface::CallbackReturn
  on_cleanup(const rclcpp_lifecycle::State &)
  {
    timer_.reset();
    pub_.reset();

    RCUTILS_LOG_INFO_NAMED(get_name(), "on cleanup is called.");

    return rclcpp_lifecycle::node_interfaces::LifecycleNodeInterface::CallbackReturn::SUCCESS;
  }

  rclcpp_lifecycle::node_interfaces::LifecycleNodeInterface::CallbackReturn
  on_shutdown(const rclcpp_lifecycle::State & state)
  {
    timer_.reset();
    pub_.reset();

    RCUTILS_LOG_INFO_NAMED(
      get_name(),
      "on shutdown is called from state %s.",
      state.label().c_str());

    return rclcpp_lifecycle::node_interfaces::LifecycleNodeInterface::CallbackReturn::SUCCESS;
  }

  rclcpp_lifecycle::node_interfaces::LifecycleNodeInterface::CallbackReturn
  on_error(const rclcpp_lifecycle::State &)
  {
    RCUTILS_LOG_INFO_NAMED(get_name(), "something went wrong!");

    return rclcpp_lifecycle::node_interfaces::LifecycleNodeInterface::CallbackReturn::FAILURE;
  }

private:
  std::shared_ptr<rclcpp_lifecycle::LifecyclePublisher<std_msgs::msg::String>> pub_;

  std::shared_ptr<rclcpp::TimerBase> timer_;
};

int main(int argc, char * argv[])
{
  // force flush of the stdout buffer.
  // this ensures a correct sync of all prints
  // even when executed simultaneously within the launch file.
  setvbuf(stdout, NULL, _IONBF, BUFSIZ);

  rclcpp::init(argc, argv);

  rclcpp::executors::SingleThreadedExecutor exe;

  std::shared_ptr<ManagedScan> lc_node =
    std::make_shared<ManagedScan>("managed_scan_node");

  exe.add_node(lc_node->get_node_base_interface());

  exe.spin();

  rclcpp::shutdown();

  return 0;
}
```
Adapted from the official `lifecycle_talker` demo ([ros2/demos lifecycle](https://github.com/ros2/demos/tree/humble/lifecycle/src)). `on_activate` is overridden, so it enables the publisher itself with `pub_->on_activate()` (the base class would do it otherwise).

## CMakeLists.txt
```cmake
cmake_minimum_required(VERSION 3.8)
project(managed_scan)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(lifecycle_msgs REQUIRED)
find_package(rclcpp_lifecycle REQUIRED)
find_package(std_msgs REQUIRED)

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

add_executable(scan_publisher src/managed_scan.cpp)
ament_target_dependencies(scan_publisher
  "lifecycle_msgs"
  "rclcpp_lifecycle"
  "std_msgs"
  rclcpp
)

install(TARGETS
  scan_publisher
  DESTINATION lib/${PROJECT_NAME})

install(DIRECTORY
  launch
  DESTINATION share/${PROJECT_NAME})

ament_package()
```

## launch/start_managed_scan.launch.py
A managed node is started with `LifecycleNode`, not `Node` (in Humble `namespace` is mandatory):
```python
from launch import LaunchDescription
from launch_ros.actions import LifecycleNode


def generate_launch_description():
    return LaunchDescription([
        LifecycleNode(package='managed_scan', executable='scan_publisher',
                      name='managed_scan_node', namespace='', output='screen')
    ])
```
```bash
ros2 launch managed_scan start_managed_scan.launch.py
ros2 topic list | grep /managed_scan_node/transition_event
ros2 topic echo /managed_scan_node/transition_event
```
Every managed node publishes `<node_name>/transition_event` (`lifecycle_msgs/msg/TransitionEvent`): echo it to see each state change. Nothing is printed until the first transition; `/managed_scan` does not exist yet either. Driving the transitions: [[core-lifecycle-services-cli]].

## Pitfalls
- If an earlier shell exported another `RMW_IMPLEMENTATION`, restart the ros2 daemon so the CLI sees the node ([[core-ros2-daemon]]).
- `pub_->publish()` while inactive does not send anything; rclcpp_lifecycle logs `Trying to publish message on the topic '…', but the publisher is not activated`.
