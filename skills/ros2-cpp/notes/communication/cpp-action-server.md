---
id: cpp-action-server
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "rclcpp_action server: handle_goal, handle_cancel, handle_accepted, execute in a thread, feedback, succeed/abort"
domain: cpp
area: communication
distro: humble
tested: false
audience: dev
summary: "rclcpp_action::create_server<GoToPose>(this, name, handle_goal, handle_cancel, handle_accepted); execute in a detached std::thread; publish_feedback, succeed, abort, canceled."
tags: [rclcpp_action, create_server, ServerGoalHandle, GoalResponse, ACCEPT_AND_EXECUTE, CancelResponse, handle_accepted, std::thread, publish_feedback, succeed, abort, is_canceling, GoToPose]
see: ["[[cpp-action-nested-client]]", "[[cpp-action-client]]", "[[core-action-server]]", "[[core-action-cli-status]]", "[[cpp-action-custom-timeout]]"]
requires: [ros2-core]
version_notes:
  - "all: a goal whose cancel request was accepted is CANCELING and may still end as SUCCEEDED, ABORTED or CANCELED; the server must check is_canceling() and call canceled() itself — https://github.com/ros2/rcl/blob/humble/rcl_action/src/rcl_action/goal_state_machine.c, https://docs.ros.org/en/humble/Tutorials/Intermediate/Writing-an-Action-Server-Client/Cpp.html (CPP-V11)"
---
# rclcpp_action server

**TL;DR** `rclcpp_action::create_server<ActionT>(this, "name", handle_goal, handle_cancel, handle_accepted)`. `handle_goal` accepts or rejects, `handle_cancel` accepts or rejects a cancel request, `handle_accepted` must return quickly, so it starts `execute()` in a new thread. `execute()` publishes feedback and ends the goal with `succeed()`, `abort()` or, after checking `is_canceling()`, `canceled()`.

## Creating the server
```cpp
class MyActionServer : public rclcpp::Node
{
public:
  using GoToPose = leo_description::action::GoToPose;
  using GoalHandleGoToPose = rclcpp_action::ServerGoalHandle<GoToPose>;
  using NavigateToPose = nav2_msgs::action::NavigateToPose;
  using GoalHandleNavigateToPose = rclcpp_action::ClientGoalHandle<NavigateToPose>;

  MyActionServer() : Node("my_action_server")
  {
    using namespace std::placeholders;

    // Action server to accept goals
    this->action_server_ = rclcpp_action::create_server<GoToPose>(
      this,
      "go_to_pose",
      std::bind(&MyActionServer::handle_goal, this, _1, _2),
      std::bind(&MyActionServer::handle_cancel, this, _1),
      std::bind(&MyActionServer::handle_accepted, this, _1));
    // ... publisher and Nav2 client: cpp-action-nested-client
  }
```
The five arguments: the node, the action name `go_to_pose`, and the three callbacks; `_1`, `_2` are the arguments rclcpp passes later. `#include "rclcpp_action/rclcpp_action.hpp"` brings the C++ action API. The `using` aliases keep the long types readable. The goal type `leo_description/action/GoToPose`: goal `float64 x`, `float64 y`, `float64 yaw`; result `bool success`; feedback `string feedback`.

## The three callbacks
```cpp
rclcpp_action::GoalResponse handle_goal(
  const rclcpp_action::GoalUUID & uuid,
  std::shared_ptr<const GoToPose::Goal> goal){
  RCLCPP_INFO(
    this->get_logger(),
    "Received goal request: x=%.2f, y=%.2f, yaw=%.2f",
    goal->x, goal->y, goal->yaw);

  return rclcpp_action::GoalResponse::ACCEPT_AND_EXECUTE;
}

rclcpp_action::CancelResponse handle_cancel(
  const std::shared_ptr<GoalHandleGoToPose> goal_handle){
  RCLCPP_INFO(this->get_logger(), "Received request to cancel goal");

  return rclcpp_action::CancelResponse::ACCEPT;
}

void handle_accepted(
  const std::shared_ptr<GoalHandleGoToPose> goal_handle){
  std::thread{
    std::bind(&MyActionServer::execute, this, goal_handle)
  }.detach();
}
```
- `handle_goal` receives the unique goal id and the goal; `ACCEPT_AND_EXECUTE` accepts it (the file adds `(void)uuid;` to silence the warning).
- `handle_cancel` only decides whether a cancel request is accepted: **accepting does not stop anything** in your code. The execute logic must check it.
- `handle_accepted` runs right after acceptance; `execute()` may take long (the robot navigates), so it runs in another thread and the executor stays free. The file writes `std::thread{std::bind(&MyActionServer::execute, this, _1), goal_handle}.detach();`, the same thing.

## `execute()`
```cpp
RCLCPP_INFO(this->get_logger(), "Executing goal");
const auto goal = goal_handle->get_goal();
auto feedback = std::make_shared<GoToPose::Feedback>();
auto result = std::make_shared<GoToPose::Result>();

feedback->feedback = "Navigating to goal...";
goal_handle->publish_feedback(feedback);

bool navigation_result =
  send_navigation_goal(goal->x, goal->y, goal->yaw);

if (navigation_result) {
  RCLCPP_INFO(this->get_logger(), "Goal reached successfully!");
  result->success = true;
  goal_handle->succeed(result);
} else {
  RCLCPP_INFO(this->get_logger(), "Failed to reach goal :(");
  result->success = false;
  goal_handle->abort(result);
}
```
`goal->x`, `goal->y`, `goal->yaw` are the requested pose; `succeed(result)` marks the goal done, `abort(result)` failed. `send_navigation_goal()` is the Nav2 client of [[cpp-action-nested-client]].

## Honour the cancel (CPP-V11)
The course's `execute()` never looks at cancel requests, so an accepted cancel changes nothing and the goal can still end `SUCCEEDED` (CANCELING → SUCCEEDED is a legal transition). The official C++ server checks it in its loop:
```cpp
if (goal_handle->is_canceling()) {
  result->success = false;
  goal_handle->canceled(result);
  return;
}
```
A server that waits on another action must also cancel that inner goal ([[cpp-action-nested-client]]).

## Pitfalls
- Long work inside `handle_accepted` (no thread) blocks the executor: no feedback, no cancel handling ([[cpp-exec-blocking]]).
- Every accepted goal must end in `succeed()`, `abort()` or `canceled()` ([[core-action-server]]).
- `ros2 action list` / `ros2 action info /go_to_pose -t` / `ros2 action send_goal /go_to_pose leo_description/action/GoToPose "{x: -8.0, y: 6.0, yaw: 1.57}"` test the server from the CLI ([[core-action-cli-status]]).
