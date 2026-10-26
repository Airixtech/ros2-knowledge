---
id: cpp-qos-liveliness-demo
type: reference
owner: equipo-ros2
updated: 2026-10-26
review_by: 2027-04-24
source: manual
confidentiality: internal
title: "C++ liveliness demo: AUTOMATIC vs MANUAL_BY_TOPIC, assert_liveliness timer, three callback groups, 3 threads"
domain: cpp
area: middleware
distro: humble
tested: false
audience: dev
summary: "publisher_liveliness.cpp with lease, publish and assert periods, assert_liveliness timer in its own group, 3-thread executor; subscriber prints liveliness changes."
tags: [liveliness, AUTOMATIC, MANUAL_BY_TOPIC, liveliness_lease_duration, assert_liveliness, QOSLivelinessChangedInfo, alive_count, not_alive_count, liveliness_callback, create_callback_group, MutuallyExclusive, MultiThreadedExecutor, publisher_liveliness.cpp, subscriber_liveliness.cpp]
see: ["[[core-qos-liveliness]]", "[[core-qos-liveliness-demo]]", "[[cpp-qos-profile]]", "[[cpp-exec-callback-groups]]", "[[cpp-exec-multithreaded]]", "[[cpp-learn-inter-unit7-qos]]"]
requires: [ros2-core]
version_notes:
  - "all: AUTOMATIC liveliness is asserted by the rmw layer, and under MANUAL_BY_TOPIC publishing a message also asserts it; the course says AUTOMATIC means 'alive while it publishes' and that publishing is not enough under MANUAL_BY_TOPIC — https://github.com/ros2/rmw/blob/humble/rmw/include/rmw/types.h (CPP-V72)"
  - "course: the publisher is titled publisher_liveliness.py and explained with Python (MutuallyExclusiveCallbackGroup(), PublisherEventCallbacks, MultiThreadedExecutor(num_threads=3)); the C++ forms are below — course code (CPP-V73)"
  - "humble: const MsgT::SharedPtr callbacks compile with a deprecation warning (also Lyrical); ConstSharedPtr is warning-free — https://github.com/ros2/rclcpp/blob/humble/rclcpp/include/rclcpp/any_subscription_callback.hpp (CPP-V46)"
---
# C++ liveliness demo

**TL;DR** The publisher takes `liveliness_lease_duration`, `publish_period` and `topic_assert_period` (milliseconds), `publish_assert` (bool) and `liveliness_policy` (`AUTOMATIC` or `MANUAL_BY_TOPIC`). It publishes from one timer, pauses 5 s inside that timer every few messages, and calls `assert_liveliness()` from a second timer. Each timer and the event callbacks have their own MutuallyExclusive group on a 3-thread executor, so the assert timer keeps running during the pause. The subscriber prints every liveliness change. Meaning of the policies and the scenario table: [[core-qos-liveliness]]; Python twin: [[core-qos-liveliness-demo]].

## `src/subscriber_liveliness.cpp`
```cpp
#include "rclcpp/rclcpp.hpp"
#include "rmw/types.h"
#include "std_msgs/msg/string.hpp"
#include <chrono>
#include <string>

using std::placeholders::_1;

class SubscriberQos : public rclcpp::Node
{
public:
  SubscriberQos() : Node("subscriber_qos_obj")
  {
    this->declare_parameter<int>("liveliness_lease_duration", 1000);
    this->declare_parameter<std::string>("liveliness_policy", "AUTOMATIC");

    this->get_parameter("liveliness_lease_duration", liveliness_lease_duration_);
    this->get_parameter("liveliness_policy", liveliness_policy_);

    rclcpp::QoS qos_profile_subscriber(1);
    qos_profile_subscriber.liveliness_lease_duration(
      std::chrono::milliseconds(liveliness_lease_duration_));

    if (liveliness_policy_ == "MANUAL_BY_TOPIC") {
      qos_profile_subscriber.liveliness(RMW_QOS_POLICY_LIVELINESS_MANUAL_BY_TOPIC);
    } else if (liveliness_policy_ == "AUTOMATIC") {
      qos_profile_subscriber.liveliness(RMW_QOS_POLICY_LIVELINESS_AUTOMATIC);
    } else {
      RCLCPP_WARN(
        this->get_logger(),
        "Invalid value for parameter 'liveliness_policy': '%s'. Using 'AUTOMATIC' instead.",
        liveliness_policy_.c_str());
      liveliness_policy_ = "AUTOMATIC";
      qos_profile_subscriber.liveliness(RMW_QOS_POLICY_LIVELINESS_AUTOMATIC);
    }

    rclcpp::SubscriptionOptions subscription_options;
    subscription_options.event_callbacks.incompatible_qos_callback =
      std::bind(&SubscriberQos::incompatible_qos_info_callback, this, _1);
    subscription_options.event_callbacks.liveliness_callback =
      std::bind(&SubscriberQos::incompatible_liveliness_callback, this, _1);

    subscription_ = this->create_subscription<std_msgs::msg::String>(
      "qos_test",
      qos_profile_subscriber,
      std::bind(&SubscriberQos::listener_callback, this, _1),
      subscription_options);
  }

private:
  void incompatible_liveliness_callback(rclcpp::QOSLivelinessChangedInfo & event)
  {
    RCLCPP_ERROR(this->get_logger(), "SUBSCRIBER::: Liveliness Triggered!");
    RCLCPP_ERROR(this->get_logger(), "alive_count = %d", event.alive_count);
    RCLCPP_ERROR(this->get_logger(), "not_alive_count = %d", event.not_alive_count);
    RCLCPP_ERROR(this->get_logger(), "alive_count_change = %d", event.alive_count_change);
    RCLCPP_ERROR(this->get_logger(), "not_alive_count_change = %d", event.not_alive_count_change);
    RCLCPP_ERROR(this->get_logger(), "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@");
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
  int liveliness_lease_duration_;
  std::string liveliness_policy_;
};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<SubscriberQos>());
  rclcpp::shutdown();
  return 0;
}
```

## `src/publisher_liveliness.cpp`
```cpp
#include "rclcpp/rclcpp.hpp"
#include "rmw/types.h"
#include "std_msgs/msg/string.hpp"
#include <chrono>
#include <string>
#include <thread>

using namespace std::chrono_literals;
using std::placeholders::_1;

class PublisherQoS : public rclcpp::Node {
public:
  PublisherQoS() : Node("publisher_qos_obj"), counter_(0) {
    group_timer_publisher_ = this->create_callback_group(
        rclcpp::CallbackGroupType::MutuallyExclusive);
    group_alive_timer_ = this->create_callback_group(
        rclcpp::CallbackGroupType::MutuallyExclusive);
    group_events_clb_ = this->create_callback_group(
        rclcpp::CallbackGroupType::MutuallyExclusive);

    this->declare_parameter<int>("liveliness_lease_duration", 1000);
    this->declare_parameter<int>("publish_period", 1000);
    this->declare_parameter<int>("topic_assert_period", 1000);
    this->declare_parameter<bool>("publish_assert", false);
    this->declare_parameter<std::string>("liveliness_policy", "AUTOMATIC");

    this->get_parameter("liveliness_lease_duration",
                        liveliness_lease_duration_);
    this->get_parameter("publish_period", publish_period_);
    this->get_parameter("topic_assert_period", topic_assert_period_);
    this->get_parameter("publish_assert", publish_assert_bool_);
    this->get_parameter("liveliness_policy", liveliness_policy_);

    rclcpp::QoS qos_profile_publisher(1);
    qos_profile_publisher.liveliness_lease_duration(
        std::chrono::milliseconds(liveliness_lease_duration_));

    if (liveliness_policy_ == "MANUAL_BY_TOPIC") {
      qos_profile_publisher.liveliness(
          RMW_QOS_POLICY_LIVELINESS_MANUAL_BY_TOPIC);
    } else if (liveliness_policy_ == "AUTOMATIC") {
      qos_profile_publisher.liveliness(RMW_QOS_POLICY_LIVELINESS_AUTOMATIC);
    } else {
      RCLCPP_WARN(this->get_logger(),
                  "Invalid value for parameter 'liveliness_policy': '%s'. "
                  "Using 'AUTOMATIC' instead.",
                  liveliness_policy_.c_str());
      liveliness_policy_ = "AUTOMATIC";
      qos_profile_publisher.liveliness(RMW_QOS_POLICY_LIVELINESS_AUTOMATIC);
    }

    rclcpp::PublisherOptions publisher_options;
    publisher_options.event_callbacks.incompatible_qos_callback =
        std::bind(&PublisherQoS::incompatible_qos_info_callback, this, _1);
    publisher_options.event_callbacks.liveliness_callback =
        std::bind(&PublisherQoS::incompatible_liveliness_callback, this);
    publisher_options.callback_group = group_events_clb_;

    publisher_ = this->create_publisher<std_msgs::msg::String>(
        "/qos_test", qos_profile_publisher, publisher_options);

    swap_state_time_ = 5.0;
    time_pause_ = 5.0;

    timer1_ = this->create_wall_timer(
        std::chrono::milliseconds(publish_period_),
        std::bind(&PublisherQoS::timer_callback, this), group_timer_publisher_);

    timer2_ = this->create_wall_timer(
        std::chrono::milliseconds(topic_assert_period_),
        std::bind(&PublisherQoS::alive_callback, this), group_alive_timer_);
  }

private:
  void incompatible_liveliness_callback() {
    RCLCPP_ERROR(this->get_logger(), "PUBLISHER::: Liveliness Triggered!");
  }

  void
  incompatible_qos_info_callback(rclcpp::QOSOfferedIncompatibleQoSInfo &event) {
    RCLCPP_ERROR(this->get_logger(),
                 "A subscriber is asking for an INCOMPATIBLE QoS Triggered!");
    RCLCPP_ERROR(
        this->get_logger(),
        "Offered incompatible qos - total %d delta %d last_policy_kind: %d",
        event.total_count, event.total_count_change, event.last_policy_kind);
  }

  void publish_one_message() {
    auto msg = std_msgs::msg::String();
    rclcpp::Time current_time = this->now();
    double seconds = current_time.seconds();
    double nanoseconds = current_time.nanoseconds();
    time_str_ = std::to_string(seconds) + "," + std::to_string(nanoseconds);
    msg.data = time_str_;
    publisher_->publish(msg);
    RCLCPP_INFO(this->get_logger(), "Publishing: %s", msg.data.c_str());
  }

  void timer_callback() {
    if (counter_ >
        static_cast<int>(swap_state_time_ / (publish_period_ / 1000.0))) {
      delta_ = 0.1;
      delta_ms_ = static_cast<int>(delta_ * 1000.0);
      range_steps_ = static_cast<int>(time_pause_ / delta_);
      for (int i = 0; i < range_steps_; i++) {
        std::this_thread::sleep_for(std::chrono::milliseconds(delta_ms_));
        RCLCPP_INFO(this->get_logger(), "Paused = %f / %f", (i * delta_),
                    time_pause_);
      }
      counter_ = 0;
    } else {
      publish_one_message();
      ++counter_;
      RCLCPP_INFO(this->get_logger(), "Counter = %d", counter_);
    }
  }

  void alive_callback() { i_am_alive(); }

  void i_am_alive() {
    if (publish_assert_bool_) {
      if (publisher_->assert_liveliness()) {
        RCLCPP_INFO(this->get_logger(), "Publisher Alive...");
      } else {
        RCLCPP_INFO(this->get_logger(), "Publisher Dead...");
      }
    }
  }

  int liveliness_lease_duration_;
  std::string liveliness_policy_;
  bool publish_assert_bool_;
  int publish_period_;
  int topic_assert_period_;
  double swap_state_time_;
  double time_pause_;
  double delta_;
  int counter_;
  int range_steps_;
  int delta_ms_;
  std::string time_str_;
  rclcpp::Publisher<std_msgs::msg::String>::SharedPtr publisher_;
  rclcpp::TimerBase::SharedPtr timer1_;
  rclcpp::TimerBase::SharedPtr timer2_;
  rclcpp::CallbackGroup::SharedPtr group_timer_publisher_;
  rclcpp::CallbackGroup::SharedPtr group_alive_timer_;
  rclcpp::CallbackGroup::SharedPtr group_events_clb_;
};

int main(int argc, char *argv[]) {
  rclcpp::init(argc, argv);
  std::shared_ptr<PublisherQoS> publisher_qos =
      std::make_shared<PublisherQoS>();
  rclcpp::executors::MultiThreadedExecutor executor(rclcpp::ExecutorOptions(),
                                                    3);
  executor.add_node(publisher_qos);
  executor.spin();
  rclcpp::shutdown();
  return 0;
}
```
CMake: `publisher_liveliness_exe`, `subscriber_liveliness_exe`; the complete `qos_tests_pkg` CMakeLists: [[cpp-learn-inter-unit7-qos]].

## Groups and threads (the course explains them in Python; C++ forms here, CPP-V73)
- **Three MutuallyExclusive groups** (`create_callback_group(rclcpp::CallbackGroupType::MutuallyExclusive)`): one for the publishing timer, one for the assert timer (the group is the third argument of `create_wall_timer`), one for the event callbacks (`publisher_options.callback_group`). Each callback never overlaps with itself, but the three kinds can run at the same time. A Reentrant group would let two runs of the same timer callback overlap ([[cpp-exec-callback-groups]]).
- **`MultiThreadedExecutor executor(rclcpp::ExecutorOptions(), 3)`**: three threads, one per kind of work. With a single thread, the 5 s sleep of `timer_callback()` would also stop the assert timer and the event callbacks ([[cpp-exec-multithreaded]]).
- **`assert_liveliness()`** returns `true` when the assertion was sent (`Publisher Alive...`).

## Runs (results in [[core-qos-liveliness]])
```bash
ros2 run qos_tests_pkg publisher_liveliness_exe --ros-args \
  -p liveliness_lease_duration:=2000 -p publish_period:=3000 -p topic_assert_period:=3000 \
  -p publish_assert:=false -p liveliness_policy:=AUTOMATIC
ros2 run qos_tests_pkg subscriber_liveliness_exe --ros-args \
  -p liveliness_lease_duration:=3000 -p liveliness_policy:=AUTOMATIC
```
- AUTOMATIC, lease 2000, publishing every 3000: no loss while the publisher runs, because the rmw layer asserts AUTOMATIC liveliness (CPP-V72). A subscriber lease of 1000 (< 2000) is incompatible: `last_policy_kind: 8` (LIVELINESS).
- The subscriber's callback fires when a publisher appears (`alive_count = 1`, `alive_count_change = 1`) and when it disappears (`alive_count = 0`, `alive_count_change = -1`).
The two MANUAL_BY_TOPIC publishers (same subscriber, lease 3000, AUTOMATIC):
```bash
ros2 run qos_tests_pkg publisher_liveliness_exe --ros-args \
  -p liveliness_lease_duration:=2000 -p publish_period:=1000 -p topic_assert_period:=3000 \
  -p publish_assert:=true -p liveliness_policy:=MANUAL_BY_TOPIC
ros2 run qos_tests_pkg publisher_liveliness_exe --ros-args \
  -p liveliness_lease_duration:=2000 -p publish_period:=4000 -p topic_assert_period:=1000 \
  -p publish_assert:=true -p liveliness_policy:=MANUAL_BY_TOPIC
```
- MANUAL_BY_TOPIC, lease 2000, publishing every 1000, asserting every 3000: alive during normal publishing (each message asserts liveliness, CPP-V72), lost in the 5 s pause (`not_alive_count = 1`), back at the next assert or message.
- MANUAL_BY_TOPIC, lease 2000, publishing every 4000, asserting every 1000: never lost; the assert timer runs in its own group and thread during the pause.

## Pitfalls
- Asserting faster than the lease only helps if the assert callback can run: on a single-threaded executor the blocking pause stops it too.
- The subscriber's policy is a requirement: AUTOMATIC accepts AUTOMATIC and MANUAL_BY_TOPIC publishers; MANUAL_BY_TOPIC accepts only MANUAL_BY_TOPIC ([[core-qos-policies]]).
