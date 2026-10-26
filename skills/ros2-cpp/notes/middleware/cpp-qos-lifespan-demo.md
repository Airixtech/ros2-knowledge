---
id: cpp-qos-lifespan-demo
type: reference
owner: equipo-ros2
updated: 2026-10-26
review_by: 2027-04-24
source: manual
confidentiality: internal
title: "C++ lifespan demo: one-shot RELIABLE + TRANSIENT_LOCAL publisher, message-age subscriber"
domain: cpp
area: middleware
distro: humble
tested: false
audience: dev
summary: "publisher_lifespan.cpp stores one stamped message; subscriber_lifespan.cpp joins later and prints its age; lifespan parameter in seconds."
tags: [lifespan, TRANSIENT_LOCAL, RELIABLE, message age, rclcpp::Time, nanoseconds, std::stod, publisher_lifespan.cpp, subscriber_lifespan.cpp, rmw/types.h]
see: ["[[core-qos-lifespan]]", "[[core-qos-lifespan-demo]]", "[[cpp-qos-durability-demo]]", "[[cpp-qos-profile]]", "[[cpp-learn-inter-unit7-qos]]"]
requires: [ros2-core]
version_notes:
  - "course: the age was computed with seconds_ + std::pow(nanoseconds_, -9) and now.seconds() + std::pow(now.nanoseconds(), -9); pow(x, -9) is x^-9, not x*1e-9, and the second field already holds the whole stamp in ns — https://en.cppreference.com/w/cpp/numeric/math/pow (CPP-V70)"
  - "all: lifespan is not a compatibility policy and the subscriber's value does not filter messages (the course calls it 'a requirement or filter'); expiry follows the publisher's lifespan — https://docs.ros.org/en/humble/Concepts/Intermediate/About-Quality-of-Service-Settings.html (CPP-V71)"
  - "course: 'start the subscriber first' contradicts the steps of the restrictive-lifespan test, which start the subscriber more than 5 s after the publisher — course text (CPP-V85)"
  - "humble: const MsgT::SharedPtr callbacks compile with a deprecation warning (also Lyrical); ConstSharedPtr is warning-free — https://github.com/ros2/rclcpp/blob/humble/rclcpp/include/rclcpp/any_subscription_callback.hpp (CPP-V46)"
---
# C++ lifespan demo

**TL;DR** The publisher stores one message stamped `"<seconds>,<nanoseconds>"` (RELIABLE + TRANSIENT_LOCAL, `lifespan` parameter in seconds) and keeps spinning. A subscriber that joins before the lifespan runs out gets it and prints its age; after that, it gets nothing. The publisher's lifespan decides; the subscriber's value changes nothing (CPP-V71). Concepts and the Python runs: [[core-qos-lifespan]]; Python twin: [[core-qos-lifespan-demo]].

## `src/subscriber_lifespan.cpp`
```cpp
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"
#include <chrono>
#include <cmath>
#include <string>

using std::placeholders::_1;

class SubscriberQos : public rclcpp::Node
{
public:
  SubscriberQos() : Node("subscriber_qos_obj")
  {
    // Declare and get parameter
    this->declare_parameter<double>("lifespan", 1.0);
    this->get_parameter("lifespan", lifespan_);

    lifespan_ms_ = static_cast<int>(lifespan_ * 1000.0);

    rclcpp::QoS qos_profile_subscriber(1);
    qos_profile_subscriber.lifespan(std::chrono::milliseconds(lifespan_ms_));
    qos_profile_subscriber.reliability(RMW_QOS_POLICY_RELIABILITY_RELIABLE);
    qos_profile_subscriber.durability(RMW_QOS_POLICY_DURABILITY_TRANSIENT_LOCAL);

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
    // The data has the format Seconds,NanoSeconds
    raw_data_ = msg->data;
    RCLCPP_INFO(this->get_logger(), "Data Received = %s seconds", raw_data_.c_str());

    delimiter_ = ",";
    last_ = 0;
    while ((next_ = raw_data_.find(delimiter_, last_)) != std::string::npos) {
      seconds_ = std::stod(raw_data_.substr(last_, next_ - last_));
      last_ = next_ + 1;
    }
    nanoseconds_ = std::stod(raw_data_.substr(last_));

    RCLCPP_INFO(this->get_logger(), "SPLIT = [%lf,%lf]", seconds_, nanoseconds_);
    RCLCPP_INFO(
      this->get_logger(), "seconds = %lf, nseconds = %lf",
      seconds_, nanoseconds_);

    // CPP-V70: the course wrote seconds_ + std::pow(nanoseconds_, -9) and
    // time_now_obj.seconds() + std::pow(time_now_obj.nanoseconds(), -9)
    total_seconds_ = nanoseconds_ * 1e-9;
    rclcpp::Time time_now_obj = this->now();
    total_current_time_ = time_now_obj.nanoseconds() * 1e-9;

    delta_ = total_current_time_ - total_seconds_;
    RCLCPP_INFO(this->get_logger(), "Message Age = %lf seconds", delta_);
  }

  rclcpp::Subscription<std_msgs::msg::String>::SharedPtr subscription_;
  double lifespan_;
  int lifespan_ms_;
  double total_seconds_;
  double total_current_time_;
  double seconds_;
  double nanoseconds_;
  double delta_;
  size_t last_;
  size_t next_;
  std::string raw_data_;
  std::string delimiter_;
};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<SubscriberQos>());
  rclcpp::shutdown();
  return 0;
}
```

## `src/publisher_lifespan.cpp`
```cpp
#include "rclcpp/rclcpp.hpp"
#include "rmw/types.h"
#include "std_msgs/msg/string.hpp"
#include <chrono>
#include <string>

using namespace std::chrono_literals;
using std::placeholders::_1;

class PublisherQoS : public rclcpp::Node
{
public:
  PublisherQoS() : Node("publisher_qos_obj")
  {
    this->declare_parameter<double>("lifespan", 1.0);
    this->get_parameter("lifespan", lifespan_);

    lifespan_ms_ = static_cast<int>(lifespan_ * 1000.0);

    rclcpp::QoS qos_profile_publisher(1);
    qos_profile_publisher.lifespan(std::chrono::milliseconds(lifespan_ms_));
    qos_profile_publisher.reliability(RMW_QOS_POLICY_RELIABILITY_RELIABLE);
    qos_profile_publisher.durability(RMW_QOS_POLICY_DURABILITY_TRANSIENT_LOCAL);

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
    timer_->cancel();

    auto msg = std_msgs::msg::String();
    rclcpp::Time current_time = this->now();
    double seconds = current_time.seconds();
    double nanoseconds = current_time.nanoseconds();

    time_str_ = std::to_string(seconds) + "," + std::to_string(nanoseconds);
    msg.data = time_str_;

    publisher_->publish(msg);
    RCLCPP_INFO(this->get_logger(), "Publishing: %s", msg.data.c_str());
  }

  double lifespan_;
  int lifespan_ms_;
  std::string time_str_;
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
Both fields come from the same stamp: `seconds()` (e.g. `1776968051.761862`) and `nanoseconds()` stored in a `double` (`1776968051761862144.000000`). The subscriber's `seconds_` is not needed for the age. CMake: `subscriber_lifespan_exe`, `publisher_lifespan_exe`.

## Runs
```bash
ros2 run qos_tests_pkg publisher_lifespan_exe --ros-args -p lifespan:=20.0
ros2 run qos_tests_pkg subscriber_lifespan_exe --ros-args -p lifespan:=20.0    # within 20 s
#   Data Received = 1776968051.761862,1776968051761862144.000000 seconds
#   Message Age = 4.321841 seconds
ros2 run qos_tests_pkg publisher_lifespan_exe --ros-args -p lifespan:=5.0
ros2 run qos_tests_pkg subscriber_lifespan_exe --ros-args -p lifespan:=5.0     # more than 5 s later: nothing
```
Start the publisher first, then the subscriber (CPP-V85). Even with TRANSIENT_LOCAL, a message older than the publisher's lifespan is no longer delivered. Lifespan only shows together with RELIABLE (no random losses) and TRANSIENT_LOCAL (a late subscriber can receive old data at all).

## Pitfalls
- Comparing stamps from different clocks: both nodes use `this->now()` (ROS time = system time without `use_sim_time`); with simulated time on one side the age is meaningless.
- `std::stod` of a 19-digit nanosecond stamp loses the last digits in a `double` (about 0.25 µs here): fine for ages in seconds, not for nanosecond comparisons.
