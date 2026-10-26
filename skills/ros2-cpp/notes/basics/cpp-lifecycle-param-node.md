---
id: cpp-lifecycle-param-node
type: reference
owner: equipo-ros2
updated: 2026-10-26
review_by: 2027-04-24
source: manual
confidentiality: internal
title: "rclcpp_lifecycle node with parameters: read in on_configure, rejected while ACTIVE, LifecyclePublisher checks"
domain: cpp
area: basics
distro: humble
tested: false
audience: dev
summary: "Managed node that declares parameters, reads them in on_configure, rejects changes while ACTIVE and publishes /cmd_vel only when activated."
tags: [rclcpp_lifecycle, LifecycleNode, LifecyclePublisher, CallbackReturn, on_configure, on_activate, on_cleanup, on_error, get_current_state, PRIMARY_STATE_ACTIVE, is_activated, get_node_base_interface, add_on_set_parameters_callback, param_vel_lifecycle_node, managed_node_example.cpp]
see: ["[[cpp-lifecycle-node]]", "[[core-lifecycle-concepts]]", "[[core-lifecycle-services-cli]]", "[[cpp-params-callback]]", "[[cpp-lifecycle-manager-client]]", "[[cpp-learn-inter-unit9-lifecycle]]"]
requires: [ros2-core]
version_notes:
  - "all: on_error returning SUCCESS leads to unconfigured, FAILURE (or an error) to finalized; the course says on_error always ends in finalized while its program returns SUCCESS — https://github.com/ros2/rcl/blob/humble/rcl_lifecycle/src/default_state_machine.c (CPP-V65)"
  - "all: rclcpp_lifecycle has a managed publisher (LifecyclePublisher) but no managed subscription class, from Humble to Lyrical — https://github.com/ros2/rclcpp/tree/lyrical/rclcpp_lifecycle/include/rclcpp_lifecycle (CPP-V66)"
  - "all: the base LifecycleNode::on_activate()/on_deactivate() activate or deactivate every managed entity (each LifecyclePublisher); an override calls publisher_->on_activate() itself or the parent's on_activate(state) — https://github.com/ros2/rclcpp/blob/humble/rclcpp_lifecycle/src/lifecycle_node.cpp (CPP-V83)"
  - "all: publish() on an inactive LifecyclePublisher sends nothing and logs a warning, which the is_activated() check avoids — https://github.com/ros2/rclcpp/blob/humble/rclcpp_lifecycle/include/rclcpp_lifecycle/lifecycle_publisher.hpp (CPP-V84)"
---
# Managed node with parameters

**TL;DR** The node declares its parameters in the constructor but reads them in `on_configure()`, where it also validates them and creates the `LifecyclePublisher` and the timer. It publishes only after `activate`, and its parameter callback rejects every change while the node is `ACTIVE`: to change a value, deactivate, set it, and run `cleanup` → `configure` → `activate` so the new values are read. The base of every managed node (laser example, launch action, `transition_event`): [[cpp-lifecycle-node]]; states: [[core-lifecycle-concepts]].

## `src/managed_node_example.cpp` (package `managed_node_tests`, unit 9.4)
```cpp
#include "geometry_msgs/msg/twist.hpp"
#include "lifecycle_msgs/msg/state.hpp"
#include "rcl_interfaces/msg/parameter_descriptor.hpp"
#include "rcl_interfaces/msg/set_parameters_result.hpp"
#include "rclcpp/rclcpp.hpp"
#include "rclcpp_lifecycle/lifecycle_node.hpp"
#include "rclcpp_lifecycle/lifecycle_publisher.hpp"
#include <chrono>
#include <functional>
#include <memory>
#include <string>
#include <vector>

using CallbackReturn =
    rclcpp_lifecycle::node_interfaces::LifecycleNodeInterface::CallbackReturn;
using namespace std::chrono_literals;

class MoveRobotLifecycle : public rclcpp_lifecycle::LifecycleNode {
public:
  MoveRobotLifecycle()
      : rclcpp_lifecycle::LifecycleNode("param_vel_lifecycle_node") {
    // Parameter descriptors
    rcl_interfaces::msg::ParameterDescriptor linear_desc;
    linear_desc.description = "Linear speed of the robot in m/s.";
    rcl_interfaces::msg::ParameterDescriptor angular_desc;
    angular_desc.description = "Angular speed of the robot in rad/s.";
    rcl_interfaces::msg::ParameterDescriptor rate_desc;
    rate_desc.description =
        "Rate in Hz at which velocity commands are published.";

    // Declare parameters
    this->declare_parameter<double>("linear_speed", 0.0, linear_desc);
    this->declare_parameter<double>("angular_speed", 0.0, angular_desc);
    this->declare_parameter<double>("publish_rate", 1.0, rate_desc);

    // Register parameter callback
    callback_handle_ = this->add_on_set_parameters_callback(std::bind(
        &MoveRobotLifecycle::parameters_callback, this, std::placeholders::_1));

    RCLCPP_INFO(this->get_logger(),
                "Lifecycle node created. Currently unconfigured.");
  }

protected:
  CallbackReturn on_configure(const rclcpp_lifecycle::State &) {
    RCLCPP_INFO(this->get_logger(), "Configuring node...");

    // Read parameters
    linear_speed_ = this->get_parameter("linear_speed").as_double();
    angular_speed_ = this->get_parameter("angular_speed").as_double();
    publish_rate_ = this->get_parameter("publish_rate").as_double();

    if (publish_rate_ <= 0.0) {
      RCLCPP_ERROR(this->get_logger(), "publish_rate must be greater than 0.0");
      return CallbackReturn::FAILURE;
    }

    // Create lifecycle publisher
    publisher_ =
        this->create_publisher<geometry_msgs::msg::Twist>("/cmd_vel", 10);

    // Create timer
    auto period = std::chrono::duration<double>(1.0 / publish_rate_);
    timer_ = this->create_wall_timer(
        std::chrono::duration_cast<std::chrono::nanoseconds>(period),
        std::bind(&MoveRobotLifecycle::timer_callback, this));

    RCLCPP_INFO(this->get_logger(),
                "Node configured successfully. linear_speed=%.2f "
                "angular_speed=%.2f publish_rate=%.2f",
                linear_speed_, angular_speed_, publish_rate_);

    return CallbackReturn::SUCCESS;
  }

  CallbackReturn on_activate(const rclcpp_lifecycle::State &) {
    RCLCPP_INFO(this->get_logger(), "Activating node...");
    publisher_->on_activate();
    return CallbackReturn::SUCCESS;
  }

  CallbackReturn on_deactivate(const rclcpp_lifecycle::State &) {
    RCLCPP_INFO(this->get_logger(), "Deactivating node...");
    publisher_->on_deactivate();
    return CallbackReturn::SUCCESS;
  }

  CallbackReturn on_cleanup(const rclcpp_lifecycle::State &) {
    RCLCPP_INFO(this->get_logger(), "Cleaning up node...");
    timer_.reset();
    publisher_.reset();
    return CallbackReturn::SUCCESS;
  }

  CallbackReturn on_shutdown(const rclcpp_lifecycle::State &) {
    RCLCPP_INFO(this->get_logger(), "Shutting down node...");
    timer_.reset();
    publisher_.reset();
    return CallbackReturn::SUCCESS;
  }

  CallbackReturn on_error(const rclcpp_lifecycle::State &) {
    RCLCPP_ERROR(this->get_logger(),
                 "An error occurred. Cleaning up resources...");
    timer_.reset();
    publisher_.reset();
    return CallbackReturn::SUCCESS;
  }

private:
  rcl_interfaces::msg::SetParametersResult
  parameters_callback(const std::vector<rclcpp::Parameter> &parameters) {
    rcl_interfaces::msg::SetParametersResult result;

    // Reject parameter changes while ACTIVE
    if (this->get_current_state().id() ==
        lifecycle_msgs::msg::State::PRIMARY_STATE_ACTIVE) {
      result.successful = false;
      result.reason = "Parameters cannot be changed while the node is ACTIVE.";
      RCLCPP_WARN(this->get_logger(),
                  "Rejected parameter change: node is ACTIVE.");
      return result;
    }

    // Basic validation
    for (const auto &parameter : parameters) {
      if (parameter.get_name() == "publish_rate" &&
          parameter.as_double() <= 0.0) {
        result.successful = false;
        result.reason = "Parameter 'publish_rate' must be greater than 0.0.";
        return result;
      }
    }

    result.successful = true;
    result.reason = "Parameters accepted.";
    RCLCPP_INFO(this->get_logger(), "Parameter change accepted.");
    return result;
  }

  void timer_callback() {
    if (!publisher_ || !publisher_->is_activated()) {
      return;
    }

    // Read parameters at runtime
    linear_speed_ = this->get_parameter("linear_speed").as_double();
    angular_speed_ = this->get_parameter("angular_speed").as_double();

    geometry_msgs::msg::Twist twist;
    twist.linear.x = linear_speed_;
    twist.angular.z = angular_speed_;

    RCLCPP_INFO(this->get_logger(),
                "Publishing command | linear=%.2f angular=%.2f", linear_speed_,
                angular_speed_);

    publisher_->publish(twist);
  }

  double linear_speed_;
  double angular_speed_;
  double publish_rate_;
  rclcpp_lifecycle::LifecyclePublisher<geometry_msgs::msg::Twist>::SharedPtr
      publisher_;
  rclcpp::TimerBase::SharedPtr timer_;
  OnSetParametersCallbackHandle::SharedPtr callback_handle_;
};

int main(int argc, char **argv) {
  rclcpp::init(argc, argv);
  auto node = std::make_shared<MoveRobotLifecycle>();
  rclcpp::spin(node->get_node_base_interface());
  rclcpp::shutdown();
  return 0;
}
```
Launch file `launch/start_managed_node.launch.py`: `LifecycleNode(package='managed_node_tests', executable='managed_node_example', name='param_vel_lifecycle_node', namespace='', output='screen')`. Package, CMake and the exercises: [[cpp-learn-inter-unit9-lifecycle]].

## How it works
- **Constructor = creation only**: parameters and the validation callback exist, but nothing reads them; the node starts `unconfigured`, with no publisher on `/cmd_vel` (`ros2 topic info /cmd_vel -v` → `Publisher count: 0`).
- **`on_configure()` = setup**: read the parameters, validate them (`publish_rate <= 0.0` → `FAILURE`, the node stays `unconfigured`), create the publisher and the timer. (The course's explanation quotes this function with one more comment, `// Avoid invalid publish rate`, before the check.) Reading here, not in the constructor, lets you change parameters before `ros2 lifecycle set … configure` and keeps creation and configuration apart, which is what the lifecycle tools expect.

| State | What happens there |
|---|---|
| unconfigured | the node exists; nothing is initialized |
| configure → inactive | parameters read, everything set up |
| active | the node works (publishes) |

- **`on_activate()` / `on_deactivate()`**: switch the `LifecyclePublisher` on and off. The timer keeps running while inactive; `timer_callback()` returns early unless `publisher_->is_activated()`. Publishing on an inactive publisher would only log a warning (CPP-V84). Calling the parent's `LifecycleNode::on_activate(state)` would activate every managed publisher at once (CPP-V83).
- **`on_cleanup()`** releases what `on_configure()` created, back to `unconfigured`; **`on_shutdown()`** does the same on the way to `finalized`. **`on_error()`** runs after an uncaught exception in a transition: it returns `SUCCESS` here, so the node goes back to `unconfigured`; returning `FAILURE` would take it to `finalized` (CPP-V65).
- **Parameters while ACTIVE are rejected**: `ros2 param set /param_vel_lifecycle_node angular_speed 0.5` → `Setting parameter failed: Parameters cannot be changed while the node is ACTIVE.` Deactivate first; the speeds are re-read by the timer after `activate`, but a new `publish_rate` needs `cleanup` + `configure` because the timer period is set in `on_configure()`.
- **Spinning**: a `LifecycleNode` is not an `rclcpp::Node`; `rclcpp::spin(node->get_node_base_interface())` spins it.
- Publishers have a managed type (`LifecyclePublisher`); subscriptions do not, up to Lyrical (CPP-V66): a subscription callback keeps running in every state, so check `get_current_state()` in it if needed.

## Pitfalls
- Overriding `on_activate()` without `publisher_->on_activate()` (or the parent's `on_activate`) → the node reports `active` but publishes nothing, and each `publish()` logs the warning (CPP-V83, V84).
- Changing `publish_rate` and only deactivating/activating again → the old period stays: the timer is created in `on_configure()`, so run `cleanup` and `configure`.
