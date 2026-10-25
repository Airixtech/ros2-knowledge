---
id: cpp-action-custom-timeout
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "Custom GoToPose action in C++: one interface package for both sides, client timeout with async_cancel_goal"
domain: cpp
area: communication
distro: humble
tested: false
audience: dev
summary: "custom_interfaces/action/GoToPose client: 100 ms timer cancels the goal after 30 s (async_cancel_goal); same interface on both sides."
tags: [rclcpp_action, custom action, GoToPose.action, custom_interfaces, async_cancel_goal, timeout, create_wall_timer, goal handle, NodeOptions, custom_action_client.cpp]
see: ["[[cpp-action-client]]", "[[cpp-action-nested-client]]", "[[core-iface-package]]", "[[core-action-client]]", "[[cpp-learn-unit7-actions]]"]
requires: [ros2-core]
version_notes:
  - "course: the unit says the rover then continues to (-13, -3), but the client never sends that goal and the server ignores the cancel; the logs end with SUCCEEDED at the first goal — https://github.com/ros2/rcl/blob/humble/rcl_action/src/rcl_action/goal_state_machine.c (CPP-V11)"
---
# Custom GoToPose action with a client timeout

**TL;DR** Put `GoToPose.action` in your interface package (`custom_interfaces`, [[core-iface-package]]) and use **that** type on both sides: an interface with the same fields in another package (`leo_description/action/GoToPose`) is a different type, and client and server would not talk. The client starts a 30 s timeout when the goal is accepted and, from a 100 ms timer, requests the cancellation with `async_cancel_goal()`. A cancel is only a request: the server has to honour it ([[cpp-action-server]]).

## The action (unit 7.7)
```
# Goal definition
float64 x
float64 y
float64 yaw
---
# Result definition
bool success
---
# Feedback definition
string feedback
```
Three sections separated by `---` (goal, result, feedback); keep all separators even if a section is empty. The file name sets the generated class names (CamelCase: `GoToPose`). `ros2 interface show custom_interfaces/action/GoToPose` after build and source.

## `src/custom_action_client.cpp` (in `my_action_client`)
```cpp
#include <chrono>
#include <functional>
#include <memory>
#include <string>
#include "custom_interfaces/action/go_to_pose.hpp"
#include "rclcpp/rclcpp.hpp"
#include "rclcpp_action/rclcpp_action.hpp"

class CustomActionClient : public rclcpp::Node {
public:
  using GoToPose = custom_interfaces::action::GoToPose;
  using GoalHandleGoToPose = rclcpp_action::ClientGoalHandle<GoToPose>;

  explicit CustomActionClient(const rclcpp::NodeOptions &options)
      : Node("custom_action_client", options) {
    action_client_ = rclcpp_action::create_client<GoToPose>(this, action_name_);

    timeout_timer_ = create_wall_timer(
        std::chrono::milliseconds(100),
        std::bind(&CustomActionClient::check_goal_timeout, this));

    RCLCPP_INFO(get_logger(), "Custom action client started.");

    RCLCPP_INFO(get_logger(), "Goal timeout: %.1f seconds",
                goal_timeout_seconds_);
  }

  bool send_goal(double x, double y, double yaw) {
    using namespace std::placeholders;

    if (!rclcpp::ok()) {
      return false;
    }

    RCLCPP_INFO(get_logger(), "Waiting for action server '%s'...",
                action_name_.c_str());

    if (!action_client_->wait_for_action_server(std::chrono::seconds(10))) {
      if (rclcpp::ok()) {
        RCLCPP_ERROR(get_logger(),
                     "Action server '%s' was not available "
                     "after 10 seconds.",
                     action_name_.c_str());
      }

      return false;
    }

    GoToPose::Goal goal_msg;
    goal_msg.x = x;
    goal_msg.y = y;
    goal_msg.yaw = yaw;

    RCLCPP_INFO(get_logger(), "Sending goal: x=%.2f, y=%.2f, yaw=%.2f", x, y,
                yaw);

    auto send_goal_options = rclcpp_action::Client<GoToPose>::SendGoalOptions();

    send_goal_options.goal_response_callback =
        std::bind(&CustomActionClient::goal_response_callback, this, _1);

    send_goal_options.feedback_callback =
        std::bind(&CustomActionClient::feedback_callback, this, _1, _2);

    send_goal_options.result_callback =
        std::bind(&CustomActionClient::result_callback, this, _1);

    current_goal_handle_.reset();
    goal_active_ = false;
    timeout_triggered_ = false;

    action_client_->async_send_goal(goal_msg, send_goal_options);

    return true;
  }

private:
  const std::string action_name_ = "/go_to_pose";

  // Maximum amount of time allowed for the goal.
  const double goal_timeout_seconds_ = 30.0;

  rclcpp_action::Client<GoToPose>::SharedPtr action_client_;

  rclcpp::TimerBase::SharedPtr timeout_timer_;

  GoalHandleGoToPose::SharedPtr current_goal_handle_;

  rclcpp::Time goal_start_time_;

  bool goal_active_ = false;
  bool timeout_triggered_ = false;

  void goal_response_callback(const GoalHandleGoToPose::SharedPtr &goal_handle) {
    if (!goal_handle) {
      RCLCPP_ERROR(get_logger(), "Goal was rejected by the action server.");

      goal_active_ = false;
      return;
    }

    current_goal_handle_ = goal_handle;
    goal_start_time_ = now();
    goal_active_ = true;
    timeout_triggered_ = false;

    RCLCPP_INFO(get_logger(), "Goal accepted. Timeout starts now.");
  }

  void feedback_callback(GoalHandleGoToPose::SharedPtr,
                         const std::shared_ptr<const GoToPose::Feedback> feedback) {
    (void)feedback;
  }

  void result_callback(const GoalHandleGoToPose::WrappedResult &result) {
    goal_active_ = false;
    current_goal_handle_.reset();

    switch (result.code) {
    case rclcpp_action::ResultCode::SUCCEEDED:
      RCLCPP_INFO(get_logger(), "The robot reached the goal.");
      break;

    case rclcpp_action::ResultCode::ABORTED:
      RCLCPP_WARN(get_logger(), "The action server aborted the goal.");
      break;

    case rclcpp_action::ResultCode::CANCELED:
      if (timeout_triggered_) {
        RCLCPP_WARN(get_logger(),
                    "The goal was canceled because the timeout expired.");
      } else {
        RCLCPP_WARN(get_logger(), "The goal was canceled.");
      }
      break;

    default:
      RCLCPP_ERROR(get_logger(), "Unknown action result.");
      break;
    }
  }

  void check_goal_timeout() {
    if (!goal_active_ || timeout_triggered_ || !current_goal_handle_) {
      return;
    }

    const double elapsed_seconds = (now() - goal_start_time_).seconds();

    if (elapsed_seconds < goal_timeout_seconds_) {
      return;
    }

    timeout_triggered_ = true;
    goal_active_ = false;

    RCLCPP_WARN(get_logger(),
                "The robot did not reach the goal within %.1f seconds.",
                goal_timeout_seconds_);

    RCLCPP_WARN(get_logger(), "Requesting cancellation of the current goal.");

    action_client_->async_cancel_goal(current_goal_handle_);
  }
};

int main(int argc, char **argv) {
  rclcpp::init(argc, argv);

  auto action_client =
      std::make_shared<CustomActionClient>(rclcpp::NodeOptions());

  if (!action_client->send_goal(-8.0, 6.0, 1.57)) {
    RCLCPP_ERROR(action_client->get_logger(), "Could not send the goal.");

    rclcpp::shutdown();
    return 1;
  }

  rclcpp::spin(action_client);

  rclcpp::shutdown();
  return 0;
}
```
Flow: start node → create the client → wait for `/go_to_pose` (up to 10 s) → send x, y, yaw → server accepts → store the goal handle (needed to cancel) and start the 30 s timeout **at acceptance** → feedback (ignored here) → either the goal succeeds, the server aborts it, or the timeout expires and the client requests cancellation → final result (`timeout_triggered_` tells a timeout cancel from another one). `async_send_goal()` returns at once; `rclcpp::spin()` runs the timer and the callbacks. The course writes `voidgoal_response_callback` and `voidfeedback_callback` (spaces lost in the export).

## What the course claims vs what runs (CPP-V11)
The text says that after the timeout the rover avoids the meteor and continues to (−13, −3). Nothing sends that goal, and the server does not stop Nav2 on cancel: the logs show `Requesting cancellation of the current goal.`, `Received request to cancel goal.`, then `Navigation succeeded.` and `The robot reached the goal.` 48 s later. To get the intended behaviour: make the server honour the cancel ([[cpp-action-nested-client]]) and send the second goal when the cancel completes `[verify]`:
```cpp
case rclcpp_action::ResultCode::CANCELED:
  if (timeout_triggered_) {
    send_goal(-13.0, -3.0, 0.0);   // the astronaut's real location; the course gives no yaw
  }
  break;
```

## CMakeLists.txt and package.xml (additions to `my_action_client`)
```cmake
# New GoToPose interface
find_package(custom_interfaces REQUIRED)

# Timeout-based action client using custom_interfaces
add_executable(custom_action_client_node src/custom_action_client.cpp)
ament_target_dependencies(custom_action_client_node
  rclcpp
  rclcpp_action
  custom_interfaces
)

install(TARGETS
	action_client_node
	custom_action_client_node
  DESTINATION lib/${PROJECT_NAME})
```
Plus `<depend>custom_interfaces</depend>` in `package.xml`. Run: `ros2 launch leo_description loc_nav.launch.py`, `ros2 run my_action_server custom_action_server_node`, `ros2 run my_action_client custom_action_client_node`.

## Pitfalls
- Client on `custom_interfaces/action/GoToPose`, server on `leo_description/action/GoToPose` → they never match.
- `async_cancel_goal()` needs the handle stored in the goal-response callback; before acceptance there is nothing to cancel.
- The timeout here is wall time (`create_wall_timer`, `now()` on the node clock): with sim time the two clocks differ ([[cpp-node-class]]).
