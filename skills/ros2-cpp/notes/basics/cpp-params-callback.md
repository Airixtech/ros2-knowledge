---
id: cpp-params-callback
type: reference
owner: equipo-ros2
updated: 2026-10-26
review_by: 2027-04-24
source: manual
confidentiality: internal
title: "Validating parameter changes in rclcpp: add_on_set_parameters_callback, SetParametersResult, the callback handle"
domain: cpp
area: basics
distro: humble
tested: false
audience: dev
summary: "add_on_set_parameters_callback with SetParametersResult (successful, reason), keep the handle, limits per parameter, startup values; Jazzy pre/post callbacks."
tags: [add_on_set_parameters_callback, SetParametersResult, OnSetParametersCallbackHandle, rclcpp::Parameter, get_name, as_double, parameter validation, InvalidParameterValueException, add_pre_set_parameters_callback, add_post_set_parameters_callback, param_vel_node, parameter_tests_callback.cpp]
see: ["[[cpp-params-declare-get]]", "[[core-param-api]]", "[[core-param-yaml-cli]]", "[[cpp-lifecycle-param-node]]", "[[cpp-learn-inter-unit5-params]]"]
requires: [ros2-core]
version_notes:
  - "course: the 5.10 listing rejects angular_speed > 2.0 with the reason '…cannot be higher than 1.0'; 5.11 and the CLI output say 2.0, used here (CPP-V59)"
  - "all: the handle keeps the callback registered ('The callback is valid as long as the smart pointer is alive'); the course says it stores the callback's response — https://github.com/ros2/rclcpp/blob/humble/rclcpp/include/rclcpp/node.hpp (CPP-V60)"
  - "all: declare_parameter passes the initial value to the callbacks already registered and throws InvalidParameterValueException on rejection; the course's checks skip startup values only because the callback is added after declaring — https://github.com/ros2/rclcpp/blob/humble/rclcpp/src/rclcpp/node_interfaces/node_parameters.cpp (CPP-V61)"
  - "jazzy: add_pre_set_parameters_callback (modify the list before validation) and add_post_set_parameters_callback (act after a successful set) exist next to add_on_set_parameters_callback; Humble has only the latter — https://github.com/ros2/rclcpp/blob/jazzy/rclcpp/include/rclcpp/node.hpp (CPP-V80)"
---
# Validating parameter changes in rclcpp

**TL;DR** `callback_handle_ = this->add_on_set_parameters_callback(std::bind(&Node::cb, this, std::placeholders::_1));` registers a function that receives the `std::vector<rclcpp::Parameter>` about to be set and returns an `rcl_interfaces::msg::SetParametersResult`. `successful = false` rejects the whole set, and `reason` is the text the caller sees. Keep the returned handle in a member: the callback stays registered only while the handle is alive (CPP-V60). Python version and descriptor ranges: [[core-param-api]].

## `src/parameter_tests_callback.cpp` (unit 5.10)
```cpp
#include "geometry_msgs/msg/twist.hpp"
#include "rcl_interfaces/msg/parameter_descriptor.hpp"
#include "rcl_interfaces/msg/set_parameters_result.hpp"
#include "rclcpp/rclcpp.hpp"
#include <algorithm>
#include <chrono>
#include <functional>
#include <string>
#include <vector>

using namespace std::chrono_literals;

class MoveRobot : public rclcpp::Node {
public:
  MoveRobot() : Node("param_vel_node") {
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

    // Read initial values
    linear_speed_ = this->get_parameter("linear_speed").as_double();
    angular_speed_ = this->get_parameter("angular_speed").as_double();
    publish_rate_ = this->get_parameter("publish_rate").as_double();

    publisher_ =
        this->create_publisher<geometry_msgs::msg::Twist>("/cmd_vel", 10);

    timer_ = this->create_wall_timer(
        1000ms, std::bind(&MoveRobot::timer_callback, this));

    callback_handle_ = this->add_on_set_parameters_callback(
        std::bind(&MoveRobot::parameters_callback, this, std::placeholders::_1));
  }

private:
  rcl_interfaces::msg::SetParametersResult
  parameters_callback(const std::vector<rclcpp::Parameter> &parameters) {
    rcl_interfaces::msg::SetParametersResult result;
    result.successful = true;
    result.reason = "Parameters accepted.";

    for (const auto &parameter : parameters) {
      if (parameter.get_name() == "linear_speed") {
        if (parameter.as_double() > 1.0) {
          result.successful = false;
          result.reason = "Parameter 'linear_speed' cannot be higher than 1.0";
          RCLCPP_WARN(this->get_logger(),
                      "Parameter 'linear_speed' not changed: value too high.");
          return result;
        }
      }
      if (parameter.get_name() == "angular_speed") {
        if (parameter.as_double() > 2.0) {
          result.successful = false;
          result.reason = "Parameter 'angular_speed' cannot be higher than 2.0";  // CPP-V59
          RCLCPP_WARN(this->get_logger(),
                      "Parameter 'angular_speed' not changed: value too high.");
          return result;
        }
      }
    }
    RCLCPP_INFO(this->get_logger(), "Parameters changed successfully.");
    return result;
  }

  void timer_callback() {
    // Read parameters at runtime
    linear_speed_ = this->get_parameter("linear_speed").as_double();
    angular_speed_ = this->get_parameter("angular_speed").as_double();
    publish_rate_ = this->get_parameter("publish_rate").as_double();

    RCLCPP_INFO(this->get_logger(),
                "linear_speed=%.2f | angular_speed=%.2f | publish_rate=%.2f",
                linear_speed_, angular_speed_, publish_rate_);

    twist_.linear.x = linear_speed_;
    twist_.angular.z = angular_speed_;
    publisher_->publish(twist_);
  }

  double linear_speed_;
  double angular_speed_;
  double publish_rate_;
  geometry_msgs::msg::Twist twist_;
  rclcpp::TimerBase::SharedPtr timer_;
  rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr publisher_;
  OnSetParametersCallbackHandle::SharedPtr callback_handle_;
};

int main(int argc, char **argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<MoveRobot>());
  rclcpp::shutdown();
  return 0;
}
```
CMake: `add_executable(param_tests_callback_node src/parameter_tests_callback.cpp)`, `ament_target_dependencies(param_tests_callback_node rclcpp geometry_msgs rcl_interfaces)` (`find_package(rclcpp)` already finds `rcl_interfaces`, which rcl exports) and the new target in `install(TARGETS …)`.

## Runs
```bash
ros2 run parameter_tests param_tests_callback_node
ros2 param set /param_vel_node angular_speed 0.1   # Set parameter successful: Parameters accepted.
ros2 param set /param_vel_node angular_speed 2.1   # Setting parameter failed: Parameter 'angular_speed' cannot be higher than 2.0
```
The node logs `Parameters changed successfully.` and then `linear_speed=0.00 | angular_speed=0.10 | publish_rate=1.00` on every tick; after the rejected set it logs `[WARN] … Parameter 'angular_speed' not changed: value too high.` and keeps `angular_speed=0.10`.

## How it works
- **The callback** gets the parameters of one atomic set: `set_parameters` (what `ros2 param set` and `ros2 param load` call) applies them one by one, so the vector holds a single parameter; only `set_parameters_atomically` passes several at once. Check each by `get_name()`; `as_double()` is safe here because a value of the wrong type was already rejected by the declared type before the callback runs.
- **The result**: `successful` (accept or reject all of them) and `reason` (returned to the caller; `ros2 param set` prints it after `Set parameter successful:` or `Setting parameter failed:`).
- **The handle**: `OnSetParametersCallbackHandle::SharedPtr`. Keeping it is what keeps the callback on; resetting it (or `remove_on_set_parameters_callback`) removes the callback (CPP-V60).
- **Startup values**: `declare_parameter` also passes the default or override through the callbacks registered before it, and throws `rclcpp::exceptions::InvalidParameterValueException` if one rejects it. Here the callback is added after the declarations, so a launch override such as `linear_speed: 5.0` is accepted unchecked (CPP-V61). Register the callback first to validate startup values too.
- **Do not change the node from the callback**: it only decides. Apply the new values where they are read (here in the timer); in Jazzy, `add_post_set_parameters_callback` runs after a successful set (CPP-V80).

## Pitfalls
- A local `auto handle = add_on_set_parameters_callback(…)` → the callback disappears at the end of the constructor and every value is accepted.
- Returning `successful = false` without a `reason` → the caller sees an empty failure message.
