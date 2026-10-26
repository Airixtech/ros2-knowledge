---
id: cpp-lifecycle-manager-client
type: reference
owner: equipo-ros2
updated: 2026-10-26
review_by: 2027-04-24
source: manual
confidentiality: internal
title: "Own lifecycle manager in C++: ChangeState client"
domain: cpp
area: basics
distro: humble
tested: false
audience: dev
summary: "C++ node that configures then activates a managed node through its change_state service; CMake and launch for both nodes."
tags: [lifecycle manager, ChangeState, change_state client, TRANSITION_CONFIGURE, TRANSITION_ACTIVATE, wait_for_service, async_send_request, spin_until_future_complete, wait_for_result, WallRate, param_vel_lifecycle_node]
see: ["[[core-lifecycle-services-cli]]", "[[cpp-lifecycle-node]]", "[[cpp-lifecycle-param-node]]", "[[core-lifecycle-concepts]]", "[[core-srv-server]]", "[[cpp-learn-inter-unit9-lifecycle]]"]
requires: [ros2-core]
version_notes:
  - "lyrical: ament_target_dependencies deprecated in Kilted, removed in Lyrical — https://docs.ros.org/en/rolling/Releases/Release-Kilted-Kaiju.html (V09)"
  - "course (intermediate C++): ament_target_dependencies(lifecycle_manager \"lifecycle_msgs\" \"rclcpp_lifecycle\" \"std_msgs\") in a package that never calls find_package(std_msgs) and does not use it; list rclcpp lifecycle_msgs [verify] whether the original stops CMake — https://github.com/ament/ament_cmake/blob/humble/ament_cmake_target_dependencies/cmake/ament_target_dependencies.cmake (CPP-V67)"
---
# Own lifecycle manager in C++: ChangeState client

**TL;DR** A lifecycle manager is any node with a client to `<managed_node>/change_state` (`lifecycle_msgs/srv/ChangeState`): it sends `TRANSITION_CONFIGURE`, then `TRANSITION_ACTIVATE`, so nobody has to type the transitions. Nav2 ships a complete one, `nav2_lifecycle_manager` ([[core-lifecycle-concepts]]).

## src/lifecycle_manager.cpp
```cpp
#include <chrono>
#include <memory>
#include <string>
#include <thread>

//#include "lifecycle_msgs/msg/state.hpp"
#include "lifecycle_msgs/msg/transition.hpp"
#include "lifecycle_msgs/srv/change_state.hpp"

#include "rclcpp/rclcpp.hpp"

#include "rcutils/logging_macros.h"

using namespace std::chrono_literals;

static constexpr char const * change_state_topic = "/managed_scan_node/change_state";

template<typename FutureT, typename WaitTimeT>
std::future_status
wait_for_result(
  FutureT & future,
  WaitTimeT time_to_wait)
{
  auto end = std::chrono::steady_clock::now() + time_to_wait;
  std::chrono::milliseconds wait_period(100);
  std::future_status status = std::future_status::timeout;
  do {
    auto now = std::chrono::steady_clock::now();
    auto time_left = end - now;
    if (time_left <= std::chrono::seconds(0)) {break;}
    status = future.wait_for((time_left < wait_period) ? time_left : wait_period);
  } while (rclcpp::ok() && status != std::future_status::ready);
  return status;
}

class MyLifecycleServiceClient : public rclcpp::Node
{
private:
  std::shared_ptr<rclcpp::Client<lifecycle_msgs::srv::ChangeState>> client_change_state_;

public:
  explicit MyLifecycleServiceClient(const std::string & node_name)
  : Node(node_name)
  {}

  void
  init()
  {
    client_change_state_ = this->create_client<lifecycle_msgs::srv::ChangeState>(
      change_state_topic);
  }

  bool
  change_state(std::uint8_t transition, std::chrono::seconds time_out = 3s)
  {
    auto request = std::make_shared<lifecycle_msgs::srv::ChangeState::Request>();
    request->transition.id = transition;

    if (!client_change_state_->wait_for_service(time_out)) {
      RCLCPP_ERROR(
        get_logger(),
        "Service %s is not available.",
        client_change_state_->get_service_name());
      return false;
    }

    auto future_result = client_change_state_->async_send_request(request);

    auto future_status = wait_for_result(future_result, time_out);

    if (future_status != std::future_status::ready) {
      RCLCPP_ERROR(
        get_logger(), "Server time out while getting current state for node managed_scan_node");
      return false;
    }

    if (future_result.get()->success) {
      RCLCPP_INFO(
        get_logger(), "Transition %d successfully triggered.", static_cast<int>(transition));
      return true;
    } else {
      RCLCPP_WARN(
        get_logger(), "Failed to trigger transition %u", static_cast<unsigned int>(transition));
      return false;
    }
  }
};

void
sv_callback(std::shared_ptr<MyLifecycleServiceClient> lc_client)
{
  rclcpp::WallRate time_between_state_changes(0.1);  // 10s

  if (!lc_client->change_state(lifecycle_msgs::msg::Transition::TRANSITION_CONFIGURE))
    return;

  time_between_state_changes.sleep();
  if (!rclcpp::ok())
    return;

  if (!lc_client->change_state(lifecycle_msgs::msg::Transition::TRANSITION_ACTIVATE))
    return;
}

int main(int argc, char ** argv)
{
  setvbuf(stdout, NULL, _IONBF, BUFSIZ);

  rclcpp::init(argc, argv);

  auto manager_client_node = std::make_shared<MyLifecycleServiceClient>("manager_client");
  manager_client_node->init();

  rclcpp::executors::SingleThreadedExecutor exe;
  exe.add_node(manager_client_node);

  std::shared_future<void> script = std::async(
    std::launch::async,
    std::bind(sv_callback, manager_client_node));
  exe.spin_until_future_complete(script);

  rclcpp::shutdown();

  return 0;
}
```
Adapted from the official `lifecycle_service_client` demo ([ros2/demos lifecycle](https://github.com/ros2/demos/tree/humble/lifecycle/src)).
- **Create the client**: `create_client<lifecycle_msgs::srv::ChangeState>("/managed_scan_node/change_state")`.
- **Call it**: fill `request->transition.id` with `lifecycle_msgs::msg::Transition::TRANSITION_CONFIGURE` or `TRANSITION_ACTIVATE`, check `wait_for_service`, then `async_send_request` and wait with a timeout.
- The transitions run in a `std::async` thread while the executor spins until that future completes.

## CMakeLists.txt additions
```cmake
add_executable(lifecycle_manager
  src/lifecycle_manager.cpp)
ament_target_dependencies(lifecycle_manager
  "lifecycle_msgs"
  "rclcpp_lifecycle"
  "std_msgs"
)
```
```cmake
install(TARGETS
  scan_publisher
  lifecycle_manager  # <--- ADD THIS LINE!
  DESTINATION lib/${PROJECT_NAME})
```
Keep `ament_package()` as the last line ([[cpp-lifecycle-node]]).

## Launch both nodes
```python
from launch import LaunchDescription
from launch_ros.actions import LifecycleNode, Node


def generate_launch_description():
    return LaunchDescription([
        LifecycleNode(package='managed_scan', executable='scan_publisher',
                      name='managed_scan_node', namespace='', output='screen'),
        Node(package='managed_scan', name='manager_client_node',
             executable='lifecycle_manager', output='screen')
    ])
```
`managed_scan_node` starts unconfigured; `manager_client_node` configures it, waits 10 s and activates it, so `/managed_scan` starts publishing.

## Variant: the intermediate C++ course (`managed_node_tests`, unit 9.6)
The same program drives [[cpp-lifecycle-param-node]] instead of the laser node. Differences from the listing above:
- Includes: adds `<future>`; no commented `state.hpp` include and no `rcutils/logging_macros.h`.
- `static constexpr char const * change_state_topic = "/param_vel_lifecycle_node/change_state";` (a service name, despite the variable name).
- Class order: `public:` constructor, `init()` and `change_state()` first, then `private:` with `rclcpp::Client<lifecycle_msgs::srv::ChangeState>::SharedPtr client_change_state_;`.
- `change_state(std::uint8_t transition, std::chrono::seconds timeout = 3s)` (the explanation text still says `time_out`); logs through `this->get_logger()`; time-out message `"Timed out while requesting transition %d."` and failure message `"Failed to trigger transition %d."`, both with `static_cast<int>(transition)`.
- The thread function is `lifecycle_manager_callback(std::shared_ptr<MyLifecycleServiceClient> lc_client)` with braces around each `return`, and `rclcpp::WallRate time_between_state_changes(10.0);`: a 10 Hz rate, so only 0.1 s passes between configure and activate (the listing above waits 10 s with `0.1`).
- `main()` names the executor `executor` instead of `exe`.

CMake additions: `add_executable(lifecycle_manager src/lifecycle_manager.cpp)`, then `ament_target_dependencies(lifecycle_manager rclcpp lifecycle_msgs)` — the course lists `"lifecycle_msgs" "rclcpp_lifecycle" "std_msgs"`, but the package never finds `std_msgs` and the program uses neither it nor `rclcpp_lifecycle` (CPP-V67) — and `install(TARGETS managed_node_example lifecycle_manager DESTINATION lib/${PROJECT_NAME})`. The launch file adds `Node(package='managed_node_tests', name='manager_client_node', executable='lifecycle_manager', output='screen')` next to the `LifecycleNode` of `param_vel_lifecycle_node`. After `ros2 launch managed_node_tests start_managed_node.launch.py`, `ros2 lifecycle get /param_vel_lifecycle_node` prints `active [3]`.

## Pitfalls
- In Humble, `async_send_request` returns a `FutureAndRequestId`: `get()` may be called only once. Use `.future.share()` (as the official demo) if you read the result twice.
- `wait_for_service` with a short timeout fails when the managed node starts slower than the manager: retry or wait longer.
