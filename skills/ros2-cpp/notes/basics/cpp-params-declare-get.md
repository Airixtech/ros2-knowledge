---
id: cpp-params-declare-get
type: reference
owner: equipo-ros2
updated: 2026-10-26
review_by: 2027-04-24
source: manual
confidentiality: internal
title: "rclcpp parameters: declare_parameter<T> with default and ParameterDescriptor, get_parameter, read once vs on every tick"
domain: cpp
area: basics
distro: humble
tested: false
audience: dev
summary: "declare_parameter<T>(name, default, descriptor), get_parameter().as_double() or get_parameter(name, var), startup snapshot vs reading on every timer tick."
tags: [declare_parameter, get_parameter, as_double, ParameterDescriptor, rcl_interfaces, parameter override, ros2 param set, create_wall_timer, publish_rate, MoveRobot, parameter_tests_node.cpp]
see: ["[[core-param-api]]", "[[core-param-yaml-cli]]", "[[cpp-params-callback]]", "[[cpp-node-class]]", "[[cpp-learn-inter-unit5-params]]", "[[core-launch-args-include]]"]
requires: [ros2-core]
version_notes:
  - "all: ROS 2 has no parameter server; each node stores its own parameters and get_parameter() reads that copy (the course says 'from the ROS 2 parameter server') — https://docs.ros.org/en/humble/Concepts/Basic/About-Parameters.html (CPP-V57)"
  - "all: create_wall_timer is a template on std::chrono::duration<Rep, Period>; the duration_cast to nanoseconds is optional (the course calls it 'the format required by the timer') — https://github.com/ros2/rclcpp/blob/humble/rclcpp/include/rclcpp/create_timer.hpp (CPP-V58)"
---
# rclcpp parameters: declare, get, read again

**TL;DR** Declare each parameter in the constructor with its type and default: `this->declare_parameter<double>("linear_speed", 0.0, descriptor)`. Overrides from a launch file, `--ros-args -p` or a YAML file are applied at that moment. Read the value with `this->get_parameter("linear_speed").as_double()`, or `this->get_parameter("linear_speed", member_)`. A value read only in the constructor is a startup snapshot: to follow `ros2 param set`, read it again where it is used. ROS 2 keeps parameters inside each node; there is no parameter server (CPP-V57). Concepts and the Python API: [[core-param-api]].

## `src/parameter_tests_node.cpp` (final version, unit 5.4)
```cpp
#include "geometry_msgs/msg/twist.hpp"
#include "rclcpp/rclcpp.hpp"
#include <algorithm>
#include <chrono>

class MoveRobot : public rclcpp::Node {
public:
  MoveRobot() : Node("move_robot_node") {
    // Parameter descriptors
    rcl_interfaces::msg::ParameterDescriptor linear_desc;
    linear_desc.description = "Linear speed of the robot in m/s.";
    rcl_interfaces::msg::ParameterDescriptor angular_desc;
    angular_desc.description = "Angular speed of the robot in rad/s.";
    rcl_interfaces::msg::ParameterDescriptor rate_desc;
    rate_desc.description =
        "Rate in Hz at which velocity commands are published.";

    // Declare parameters (typed, with defaults)
    this->declare_parameter<double>("linear_speed", 0.0, linear_desc);
    this->declare_parameter<double>("angular_speed", 0.0, angular_desc);
    this->declare_parameter<double>("publish_rate", 1.0, rate_desc);

    // Read parameters once at startup
    linear_speed_ = this->get_parameter("linear_speed").as_double();
    angular_speed_ = this->get_parameter("angular_speed").as_double();
    publish_rate_ = this->get_parameter("publish_rate").as_double();

    publisher_ =
        this->create_publisher<geometry_msgs::msg::Twist>("/cmd_vel", 10);

    // Create timer based on publish_rate
    double safe_rate = std::max(0.1, publish_rate_);
    auto period = std::chrono::duration<double>(1.0 / safe_rate);
    timer_ = this->create_wall_timer(
        std::chrono::duration_cast<std::chrono::nanoseconds>(period),
        std::bind(&MoveRobot::timer_callback, this));
  }

private:
  void timer_callback() {
    // Read parameters again every time the timer runs
    linear_speed_ = this->get_parameter("linear_speed").as_double();
    angular_speed_ = this->get_parameter("angular_speed").as_double();
    publish_rate_ = this->get_parameter("publish_rate").as_double();

    RCLCPP_INFO(this->get_logger(),
                "MoveRobot started | linear=%.2f angular=%.2f rate=%.2f Hz",
                linear_speed_, angular_speed_, publish_rate_);

    twist_.linear.x = linear_speed_;
    twist_.angular.z = angular_speed_;
    publisher_->publish(twist_);
  }

  double linear_speed_;
  double angular_speed_;
  double publish_rate_;
  rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr publisher_;
  rclcpp::TimerBase::SharedPtr timer_;
  geometry_msgs::msg::Twist twist_;
};

int main(int argc, char *argv[]) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<MoveRobot>());
  rclcpp::shutdown();
  return 0;
}
```
The first version (unit 5.3) is the same file without the three `get_parameter` lines in `timer_callback()`: `ros2 param set /move_robot_node angular_speed 0.5` then answers `Set parameter successful`, but the log keeps `angular=0.00` and the robot does not move. Package, CMake and runs: [[cpp-learn-inter-unit5-params]].

## How it works
- **Descriptor** (optional): `rcl_interfaces::msg::ParameterDescriptor` with a `description`, shown by `ros2 param describe /move_robot_node angular_speed` (`Type: double`, `Description: Angular speed of the robot in rad/s.`). It can also hold ranges and `read_only` ([[core-param-api]]).
- **Declare**: `declare_parameter<double>(name, default, descriptor)` registers the typed parameter; the default is used only when nothing overrides it. Undeclared parameters are rejected unless the node is built with `rclcpp::NodeOptions().allow_undeclared_parameters(true)`.
- **Overrides first**: `parameters=[{'linear_speed': …}]` in a launch file ([[core-launch-args-include]]), `--ros-args -p linear_speed:=0.3` or `--params-file` are applied when the parameter is declared, so the first `get_parameter` already returns them.
- **Read**: `get_parameter(name)` returns an `rclcpp::Parameter`; `.as_double()` (also `as_int()`, `as_bool()`, `as_string()`) converts it to the declared type. The two-argument form `this->get_parameter("reliability", reliability_)` writes into a member (the QoS demos of [[cpp-qos-events-demo]] use it).
- **Read again**: reading in `timer_callback()` makes `linear_speed` and `angular_speed` follow `ros2 param set`. `publish_rate` is read too, but the timer period was fixed when the timer was created: a new rate needs a new timer, or the validation callback of [[cpp-params-callback]].
- **Timer**: `std::max(0.1, publish_rate_)` avoids a division by zero, `duration<double>(1.0 / safe_rate)` turns Hz into seconds. `create_wall_timer` accepts any `std::chrono` duration; the `duration_cast` to nanoseconds is optional (CPP-V58).

## Pitfalls
- Reading parameters only in the constructor → `ros2 param set` succeeds and the node ignores it.
- `ros2 param set /move_robot_node angular_speed 0` (integer) on a double parameter → `Setting parameter failed: Wrong parameter type, parameter {angular_speed} is of type {double}, setting it to {integer} is not allowed.` Write `0.0` ([[core-param-yaml-cli]]).
- `get_parameter` on a name that was never declared throws `rclcpp::exceptions::ParameterNotDeclaredException`.
