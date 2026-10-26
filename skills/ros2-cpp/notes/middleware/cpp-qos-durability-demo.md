---
id: cpp-qos-durability-demo
type: reference
owner: equipo-ros2
updated: 2026-10-26
review_by: 2027-04-24
source: manual
confidentiality: internal
title: "C++ durability demo: one-shot TRANSIENT_LOCAL publisher and late subscriber, ros2 topic echo QoS flags"
domain: cpp
area: middleware
distro: humble
tested: false
audience: dev
summary: "publisher_durability.cpp sends one message (timer_->cancel()), subscriber_durability.cpp joins later; durability parameter, event callbacks, echo flags."
tags: [durability, TRANSIENT_LOCAL, VOLATILE, RMW_QOS_POLICY_DURABILITY_TRANSIENT_LOCAL, late-joining subscriber, timer cancel, SubscriptionOptions, QOSRequestedIncompatibleQoSInfo, publisher_durability.cpp, subscriber_durability.cpp]
see: ["[[core-qos-durability]]", "[[core-qos-durability-demo]]", "[[cpp-qos-profile]]", "[[cpp-qos-events-demo]]", "[[cpp-learn-inter-unit7-qos]]"]
requires: [ros2-core]
version_notes:
  - "humble: const MsgT::SharedPtr callbacks compile with a deprecation warning (also Lyrical); ConstSharedPtr is warning-free — https://github.com/ros2/rclcpp/blob/humble/rclcpp/include/rclcpp/any_subscription_callback.hpp (CPP-V46)"
---
# C++ durability demo

**TL;DR** The publisher sends a single message (its timer cancels itself on the first tick) and keeps spinning; a subscriber started later still gets that message only if **both** use TRANSIENT_LOCAL. Both take the parameter `durability` (`volatile` default, or `transient_local`). Concepts and results: [[core-qos-durability]]; Python twin: [[core-qos-durability-demo]].

## `src/subscriber_durability.cpp`
```cpp
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"

using std::placeholders::_1;

class SubscriberQos : public rclcpp::Node
{
public:
  SubscriberQos() : Node("subscriber_qos_obj")
  {
    this->declare_parameter<std::string>("durability", "volatile");
    this->get_parameter("durability", durability_);

    rclcpp::QoS qos_profile_subscriber(10);

    if (durability_ == "transient_local") {
      qos_profile_subscriber.durability(RMW_QOS_POLICY_DURABILITY_TRANSIENT_LOCAL);
    } else if (durability_ == "volatile") {
      qos_profile_subscriber.durability(RMW_QOS_POLICY_DURABILITY_VOLATILE);
    } else {
      RCLCPP_WARN(
        this->get_logger(),
        "Invalid value for parameter 'durability': '%s'. Using 'volatile' instead.",
        durability_.c_str());
      durability_ = "volatile";
      qos_profile_subscriber.durability(RMW_QOS_POLICY_DURABILITY_VOLATILE);
    }

    rclcpp::SubscriptionOptions subscription_options;
    subscription_options.event_callbacks.incompatible_qos_callback =
      std::bind(&SubscriberQos::incompatible_qos_info_callback, this, _1);

    subscription_ = this->create_subscription<std_msgs::msg::String>(
      "qos_test",
      qos_profile_subscriber,
      std::bind(&SubscriberQos::listener_callback, this, _1),
      subscription_options);
  }

private:
  void incompatible_qos_info_callback(rclcpp::QOSRequestedIncompatibleQoSInfo & event)
  {
    RCLCPP_ERROR(
      this->get_logger(),
      "SUBSCRIBER::: INCOMPATIBLE QoS Triggered!");
    RCLCPP_INFO(
      this->get_logger(),
      "Requested incompatible qos - total %d delta %d last_policy_kind: %d",
      event.total_count,
      event.total_count_change,
      event.last_policy_kind);
  }

  void listener_callback(const std_msgs::msg::String::SharedPtr msg)
  {
    RCLCPP_INFO(this->get_logger(), "Data Received = '%s'", msg->data.c_str());
  }

  rclcpp::Subscription<std_msgs::msg::String>::SharedPtr subscription_;
  std::string durability_;
};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<SubscriberQos>());
  rclcpp::shutdown();
  return 0;
}
```

## `src/publisher_durability.cpp`
```cpp
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"
#include <chrono>
#include <string>

using namespace std::chrono_literals;
using std::placeholders::_1;

class PublisherQoS : public rclcpp::Node
{
public:
  PublisherQoS() : Node("publisher_qos_obj"), msgs_id_(0)
  {
    // Declare and get parameter
    this->declare_parameter<std::string>("durability", "volatile");
    this->get_parameter("durability", durability_);

    rclcpp::QoS qos_profile_publisher(10);

    if (durability_ == "transient_local") {
      qos_profile_publisher.durability(RMW_QOS_POLICY_DURABILITY_TRANSIENT_LOCAL);
    } else if (durability_ == "volatile") {
      qos_profile_publisher.durability(RMW_QOS_POLICY_DURABILITY_VOLATILE);
    } else {
      RCLCPP_WARN(
        this->get_logger(),
        "Invalid value for parameter 'durability': '%s'. Using 'volatile' instead.",
        durability_.c_str());
      durability_ = "volatile";
      qos_profile_publisher.durability(RMW_QOS_POLICY_DURABILITY_VOLATILE);
    }

    rclcpp::PublisherOptions publisher_options;
    publisher_options.event_callbacks.incompatible_qos_callback =
      std::bind(&PublisherQoS::incompatible_qos_info_callback, this, _1);

    publisher_ = this->create_publisher<std_msgs::msg::String>(
      "/qos_test", qos_profile_publisher, publisher_options);

    timer_ = this->create_wall_timer(
      1000ms, std::bind(&PublisherQoS::publish_one_message, this));
  }

private:
  void incompatible_qos_info_callback(rclcpp::QOSOfferedIncompatibleQoSInfo & event)
  {
    RCLCPP_ERROR(
      this->get_logger(),
      "A subscriber is asking for an INCOMPATIBLE QoS Triggered!");
    RCLCPP_ERROR(
      this->get_logger(),
      "Offered incompatible qos - total %d delta %d last_policy_kind: %d",
      event.total_count,
      event.total_count_change,
      event.last_policy_kind);
  }

  void publish_one_message()
  {
    // Publish only once
    timer_->cancel();

    auto msg = std_msgs::msg::String();
    auto current_time = this->now();
    auto current_time_s = current_time.seconds();
    auto current_time_ns = current_time.nanoseconds();

    time_str_ =
      std::to_string(current_time_s) + "," + std::to_string(current_time_ns);
    dds_msg_str_ = std::to_string(msgs_id_) + ":" + time_str_;

    msg.data = dds_msg_str_;
    publisher_->publish(msg);
    RCLCPP_INFO(this->get_logger(), "Publishing: %s", msg.data.c_str());
  }

  std::string durability_;
  int msgs_id_;
  std::string time_str_;
  std::string dds_msg_str_;
  rclcpp::Publisher<std_msgs::msg::String>::SharedPtr publisher_;
  rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<PublisherQoS>());
  rclcpp::shutdown();
  return 0;
}
```
`timer_->cancel()` as the first line of the callback makes a one-shot timer: the callback runs once, the node keeps spinning (and keeps the stored message). CMake: `subscriber_durability_exe` and `publisher_durability_exe`, each with `ament_target_dependencies(<exe> rclcpp std_msgs)`.

## Runs
```bash
ros2 run qos_tests_pkg publisher_durability_exe --ros-args -p durability:=transient_local
#   [publisher_qos_obj]: Publishing: 0:1680120446.045713,1680120446045713462
ros2 run qos_tests_pkg subscriber_durability_exe --ros-args -p durability:=transient_local   # started later
#   [subscriber_qos_obj]: Data Received = '0:1680120446.045713,1680120446045713462'
ros2 topic echo --qos-durability transient_local --qos-reliability reliable /qos_test
```
`echo` with only `--qos-durability transient_local` got nothing in the course's run: once one QoS flag is given, the other policies come from the `sensor_data` preset (BEST_EFFORT), so add `--qos-reliability reliable`; without any flag, Humble's echo copies the publisher's QoS ([[core-qos-durability]]). A TRANSIENT_LOCAL subscriber with a VOLATILE publisher is incompatible (`last_policy_kind: 2`, DURABILITY).

## Pitfalls
- Publisher TRANSIENT_LOCAL, subscriber VOLATILE → compatible, but the late subscriber gets nothing old: it did not ask for history.
- Depth matters: TRANSIENT_LOCAL keeps only the last `depth` messages (10 here) for late joiners.
