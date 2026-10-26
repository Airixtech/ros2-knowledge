---
id: cpp-qos-deadline-demo
type: reference
owner: equipo-ros2
updated: 2026-10-26
review_by: 2027-04-24
source: manual
confidentiality: internal
title: "C++ deadline demo: 1 s publisher with a 2 s pause, deadline parameter, deadline callbacks on both sides"
domain: cpp
area: middleware
distro: humble
tested: false
audience: dev
summary: "publisher_deadline.cpp pauses 2 s after six messages; both ends take deadline (s), register deadline_callback and incompatible_qos_callback."
tags: [deadline, deadline_callback, QOSDeadlineRequestedInfo, QOSDeadlineOfferedInfo, std::chrono::milliseconds, sleep_for, publisher_deadline.cpp, subscriber_deadline.cpp, swap_state_time_, time_pause_]
see: ["[[core-qos-deadline]]", "[[core-qos-deadline-demo]]", "[[cpp-qos-profile]]", "[[cpp-learn-inter-unit7-qos]]", "[[cpp-exec-blocking]]"]
requires: [ros2-core]
version_notes:
  - "course: the subscriber's deadline callback prints 'PUBLISHER::: Deadline Triggered!'; it reports the subscriber's requested-deadline-missed event — course code (CPP-V69)"
  - "humble: const MsgT::SharedPtr callbacks compile with a deprecation warning (also Lyrical); ConstSharedPtr is warning-free — https://github.com/ros2/rclcpp/blob/humble/rclcpp/include/rclcpp/any_subscription_callback.hpp (CPP-V46)"
---
# C++ deadline demo

**TL;DR** Both programs take the parameter `deadline` in seconds (default 1.0), set it with `qos.deadline(std::chrono::milliseconds(…))` and register a `deadline_callback` and an `incompatible_qos_callback`. The publisher sends one message per second and, after six, blocks its own timer callback for 2 s. A deadline shorter than a gap fires the deadline event on that side; a subscriber deadline shorter than the publisher's is incompatible. Scenarios and results: [[core-qos-deadline]], [[cpp-learn-inter-unit7-qos]]; Python twin: [[core-qos-deadline-demo]].

## `src/subscriber_deadline.cpp`
```cpp
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"
#include <chrono>
#include <string>

using std::placeholders::_1;

class SubscriberQos : public rclcpp::Node
{
public:
  SubscriberQos() : Node("subscriber_qos_obj")
  {
    this->declare_parameter<double>("deadline", 1.0);
    this->get_parameter("deadline", deadline_);

    deadline_ms_ = static_cast<int>(deadline_ * 1000.0);

    rclcpp::QoS qos_profile_subscriber(1);
    qos_profile_subscriber.deadline(std::chrono::milliseconds(deadline_ms_));

    rclcpp::SubscriptionOptions subscription_options;
    subscription_options.event_callbacks.incompatible_qos_callback =
      std::bind(&SubscriberQos::incompatible_qos_info_callback, this, _1);
    subscription_options.event_callbacks.deadline_callback =
      std::bind(&SubscriberQos::incompatible_deadline_callback, this);

    subscription_ = this->create_subscription<std_msgs::msg::String>(
      "qos_test",
      qos_profile_subscriber,
      std::bind(&SubscriberQos::listener_callback, this, _1),
      subscription_options);
  }

private:
  void incompatible_deadline_callback()
  {
    RCLCPP_ERROR(this->get_logger(), "PUBLISHER::: Deadline Triggered!");
  }

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
  double deadline_;
  int deadline_ms_;
};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<SubscriberQos>());
  rclcpp::shutdown();
  return 0;
}
```
`std::bind(&SubscriberQos::incompatible_deadline_callback, this)` binds a function without parameters: the bound object ignores the `QOSDeadlineRequestedInfo &` it is called with. The log label says `PUBLISHER` but this is the subscriber's event (CPP-V69).

## `src/publisher_deadline.cpp`
```cpp
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"
#include <chrono>
#include <thread>
#include <string>

using namespace std::chrono_literals;
using std::placeholders::_1;

class PublisherQoS : public rclcpp::Node
{
public:
  PublisherQoS() : Node("publisher_qos_obj"), msgs_id_(0), counter_(0)
  {
    this->declare_parameter<double>("deadline", 1.0);
    this->get_parameter("deadline", deadline_);

    deadline_ms_ = static_cast<int>(deadline_ * 1000.0);

    rclcpp::QoS qos_profile_publisher(1);
    qos_profile_publisher.deadline(std::chrono::milliseconds(deadline_ms_));

    rclcpp::PublisherOptions publisher_options;
    publisher_options.event_callbacks.incompatible_qos_callback =
      std::bind(&PublisherQoS::incompatible_qos_info_callback, this, _1);
    publisher_options.event_callbacks.deadline_callback =
      std::bind(&PublisherQoS::incompatible_deadline_callback, this);

    publisher_ = this->create_publisher<std_msgs::msg::String>(
      "/qos_test", qos_profile_publisher, publisher_options);

    timer_ = this->create_wall_timer(
      1000ms, std::bind(&PublisherQoS::timer_callback, this));

    timer_period_ = 1.0;
    swap_state_time_ = 5.0;
    time_pause_ = 2.0;
  }

private:
  void incompatible_deadline_callback()
  {
    RCLCPP_ERROR(this->get_logger(), "PUBLISHER::: Deadline Triggered!");
  }

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

    ++msgs_id_;
  }

  void timer_callback()
  {
    if (counter_ > static_cast<int>(swap_state_time_ / timer_period_)) {
      delta_ = 0.1;
      delta_ms_ = static_cast<int>(delta_ * 1000.0);
      range_steps_ = static_cast<int>(time_pause_ / delta_);

      for (int i = 0; i < range_steps_; i++) {
        std::this_thread::sleep_for(std::chrono::milliseconds(delta_ms_));
        RCLCPP_INFO(
          this->get_logger(),
          "Paused = %f / %f",
          (i * delta_),
          time_pause_);
      }
      counter_ = 0;
    } else {
      publish_one_message();
      ++counter_;
      RCLCPP_INFO(this->get_logger(), "Counter = %d", counter_);
    }
  }

  double deadline_;
  double timer_period_;
  double swap_state_time_;
  double time_pause_;
  double delta_;
  int counter_;
  int range_steps_;
  int delta_ms_;
  int deadline_ms_;
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
`counter_ > 5` (5.0 / 1.0) is reached after the sixth message (`Counter = 6`); the next tick sleeps 20 × 0.1 s inside the callback, logging `Paused = 0.000000 / 2.000000` … `Paused = 1.900000 / 2.000000`, so the gap between messages 5 and 6 is about 3 s. The single-threaded executor runs nothing else meanwhile ([[cpp-exec-blocking]]). CMake: `subscriber_deadline_exe`, `publisher_deadline_exe`.

## Working condition
```bash
ros2 run qos_tests_pkg publisher_deadline_exe --ros-args -p deadline:=10.0
ros2 run qos_tests_pkg subscriber_deadline_exe --ros-args -p deadline:=10.0
```
No event on either side: 10 s is longer than every gap, pause included, and subscriber 10.0 ≥ publisher 10.0 is compatible. The other scenarios (publisher 1.0 and 1.1, both 1.5, subscriber 1.0 against publisher 10.0 → incompatible with `last_policy_kind: 4`): [[cpp-learn-inter-unit7-qos]].

## Pitfalls
- A deadline equal to the nominal period (1.0 s for a 1 s timer) fires during normal publishing too: timer jitter makes some gaps slightly longer. Leave a margin (1.1–1.5 s).
- The deadline in seconds becomes whole milliseconds (`static_cast<int>(deadline_ * 1000.0)`): values under 1 ms truncate to 0, the "default" (unspecified) duration, which the middleware usually treats as infinite ([[core-qos-policies]]).
