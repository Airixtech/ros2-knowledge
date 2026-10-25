---
id: cpp-action-client
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "rclcpp_action client: create_client, wait_for_action_server, SendGoalOptions callbacks, WrappedResult codes"
domain: cpp
area: communication
distro: humble
tested: false
audience: dev
summary: "rclcpp_action::create_client<Rotate>(this, \"rotate\"), wait_for_action_server, SendGoalOptions goal/feedback/result callbacks, async_send_goal, ResultCode switch."
tags: [rclcpp_action, create_client, ClientGoalHandle, SendGoalOptions, goal_response_callback, feedback_callback, result_callback, WrappedResult, ResultCode, async_send_goal, Rotate, action_client.cpp]
see: ["[[cpp-action-server]]", "[[cpp-action-custom-timeout]]", "[[core-action-cli-status]]", "[[core-action-client]]", "[[cpp-logging]]"]
requires: [ros2-core]
version_notes:
  - "course: the explained goal_response_callback(std::shared_future<GoalHandleRotate::SharedPtr>) is the pre-Humble form; since rclcpp_action 5.0.0 (#1311) the callback receives the goal handle, and Humble has no compatibility shim — https://github.com/ros2/rclcpp/blob/humble/rclcpp_action/include/rclcpp_action/client.hpp (CPP-V08)"
  - "course: the launch output is labelled [example62-1]; the process started by example72_launch_file.launch.py is action_client_node, labelled [action_client_node-1] (CPP-V09)"
  - "all: RCLCPP_INFO(logger, ss.str().c_str()) passes a non-literal format string (as the official tutorial does); GCC -Wformat-security warns and a % in the text would be read as a conversion [verify] — https://github.com/ros2/rcutils/blob/humble/include/rcutils/logging.h (CPP-V24)"
---
# rclcpp_action client

**TL;DR** `rclcpp_action::create_client<ActionT>(this, "name")`, `wait_for_action_server()`, build `ActionT::Goal`, fill `SendGoalOptions` with three callbacks (goal accepted or rejected, feedback, result) and call `async_send_goal()`; then spin. The goal-response callback takes `GoalHandle::SharedPtr` (`nullptr` = rejected) on Humble and later (CPP-V08).

## Package
```bash
cd ~/ros2_ws/src
ros2 pkg create my_action_client --build-type ament_cmake --dependencies rclcpp rclcpp_action leo_description
```
`leo_description` holds the action interface `leo_description/action/Rotate` (goal `float64 rotation_time`, result `bool success`, feedback `float64 elapsed_time`).

## `src/action_client.cpp`
```cpp
#include "leo_description/action/rotate.hpp"
#include "rclcpp/rclcpp.hpp"
#include "rclcpp_action/rclcpp_action.hpp"
#include <functional>
#include <future>
#include <memory>
#include <sstream>
#include <string>

class MyActionClient : public rclcpp::Node {
public:
  using Rotate = leo_description::action::Rotate;
  using GoalHandleRotate = rclcpp_action::ClientGoalHandle<Rotate>;

  MyActionClient() : Node("my_action_client") {
    this->client_ptr_ = rclcpp_action::create_client<Rotate>(this, "rotate");
  }

  void send_goal(double seconds) {
    using namespace std::placeholders;

    if (!this->client_ptr_->wait_for_action_server()) {
      RCLCPP_ERROR(this->get_logger(),
                   "Action server not available after waiting");
      rclcpp::shutdown();
      return;
    }

    auto goal_msg = Rotate::Goal();
    goal_msg.rotation_time = seconds;

    RCLCPP_INFO(this->get_logger(), "Sending goal");

    auto send_goal_options = rclcpp_action::Client<Rotate>::SendGoalOptions();
    send_goal_options.goal_response_callback =
        std::bind(&MyActionClient::goal_response_callback, this, _1);
    send_goal_options.feedback_callback =
        std::bind(&MyActionClient::feedback_callback, this, _1, _2);
    send_goal_options.result_callback =
        std::bind(&MyActionClient::result_callback, this, _1);

    this->client_ptr_->async_send_goal(goal_msg, send_goal_options);
  }

private:
  rclcpp_action::Client<Rotate>::SharedPtr client_ptr_;

  void goal_response_callback(const GoalHandleRotate::SharedPtr &goal_handle) {
    if (!goal_handle) {
      RCLCPP_ERROR(this->get_logger(), "Goal rejected :(");
    } else {
      RCLCPP_INFO(this->get_logger(), "Goal accepted :)");
    }
  }

  void feedback_callback(GoalHandleRotate::SharedPtr,
                         const std::shared_ptr<const Rotate::Feedback> feedback) {
    std::stringstream ss;
    ss << "Received feedback: " << feedback->elapsed_time;
    RCLCPP_INFO(this->get_logger(), ss.str().c_str());
  }

  void result_callback(const GoalHandleRotate::WrappedResult &result) {
    switch (result.code) {
    case rclcpp_action::ResultCode::SUCCEEDED:
      break;
    case rclcpp_action::ResultCode::ABORTED:
      RCLCPP_ERROR(this->get_logger(), "Goal was aborted");
      return;
    case rclcpp_action::ResultCode::CANCELED:
      RCLCPP_ERROR(this->get_logger(), "Goal was canceled");
      return;
    default:
      RCLCPP_ERROR(this->get_logger(), "Unknown result code");
      return;
    }
    std::stringstream ss;
    ss << "Result: " << (result.result->success ? "true" : "false");
    RCLCPP_INFO(this->get_logger(), ss.str().c_str());
    rclcpp::shutdown();
  }
};

int main(int argc, char **argv) {
  rclcpp::init(argc, argv);
  auto action_client = std::make_shared<MyActionClient>();
  action_client->send_goal(5.0);
  rclcpp::spin(action_client);
  return 0;
}
```
- `create_client<Rotate>(this, "rotate")`: the node that holds the client and the action name; the action type is the template argument.
- `wait_for_action_server()` without a timeout waits until the server appears.
- `SendGoalOptions`: `goal_response_callback` (accepted → valid handle, rejected → `nullptr`), `feedback_callback` (every feedback message: `feedback->elapsed_time`), `result_callback` (`result.code` is `SUCCEEDED`, `ABORTED`, `CANCELED` or unknown; `result.result->success`).
- `async_send_goal()` returns at once; `rclcpp::spin()` runs the three callbacks. `rclcpp::shutdown()` in the result callback ends `spin()` and the program.
- The explanation of the course shows `goal_response_callback(std::shared_future<GoalHandleRotate::SharedPtr> future)` with `future.get()`: that is the form of distros before Humble and does not compile on Humble (CPP-V08). The file above is right.
- Logging a `std::stringstream` with `RCLCPP_INFO(logger, ss.str().c_str())` passes it as a format string; prefer `RCLCPP_INFO_STREAM(this->get_logger(), "Received feedback: " << feedback->elapsed_time);` (CPP-V24, [[cpp-logging]]).

## CMakeLists.txt and launch
```cmake
cmake_minimum_required(VERSION 3.8)
project(my_action_client)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclcpp_action REQUIRED)
find_package(leo_description REQUIRED)

add_executable(action_client_node src/action_client.cpp)
ament_target_dependencies(action_client_node
  "rclcpp"
  "rclcpp_action"
  "leo_description")

install(TARGETS action_client_node
  DESTINATION lib/${PROJECT_NAME})

install(DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}/)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
```
```python
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='my_action_client',
            executable='action_client_node',
            output='screen'),
    ])
```
`launch/example72_launch_file.launch.py`; with the server `ros2 run leo_description rotate_action_server.py` running, `ros2 launch my_action_client example72_launch_file.launch.py` turns the rover left for 5 s and prints `Goal accepted :)`, `Received feedback: 8.344650268554688e-05` … `Received feedback: 5.027088165283203`, `Result: true`, then the process finishes cleanly. The course's output labels the process `[example62-1]`; this launch prints `[action_client_node-1]` (CPP-V09).

## Pitfalls
- A goal-response callback written with `std::shared_future` → compile error on Humble+ (CPP-V08).
- Forgetting `rclcpp::spin()` after `async_send_goal()` → no callback runs.
- Same action name and **same interface package** on both sides, or the client never matches the server ([[cpp-action-custom-timeout]]).
