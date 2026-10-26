---
id: cpp-qos-events-demo
type: reference
owner: equipo-ros2
updated: 2026-10-26
review_by: 2027-04-24
source: manual
confidentiality: internal
title: "C++ incompatible-QoS demo: reliability-parameter publisher, RELIABLE subscriber, event callbacks, CMake"
domain: cpp
area: middleware
distro: humble
tested: false
audience: dev
summary: "publisher_custom_minimal_qos.cpp with a reliability parameter and incompatible_qos_callback, RELIABLE subscriber, CMake, compatible and incompatible runs."
tags: [qos_tests_pkg, publisher_custom_minimal_qos.cpp, subscriber_custom_minimal_qos.cpp, incompatible_qos_callback, QOSOfferedIncompatibleQoSInfo, RMW_QOS_POLICY_RELIABILITY_BEST_EFFORT, PublisherOptions, /qos_test, last_policy_kind]
see: ["[[core-qos-events]]", "[[core-qos-events-demo]]", "[[cpp-qos-profile]]", "[[cpp-learn-inter-unit7-qos]]", "[[cpp-topic-subscriber]]"]
requires: [ros2-core]
version_notes:
  - "course: the printed errors ('…INCOMPATIBLE QoS Triggered!', 'Offered incompatible qos…') come from the other demos' strings; this program prints the strings below — course code (CPP-V68)"
  - "humble: const MsgT::SharedPtr callbacks compile with a deprecation warning (also Lyrical); ConstSharedPtr is warning-free — https://github.com/ros2/rclcpp/blob/humble/rclcpp/include/rclcpp/any_subscription_callback.hpp (CPP-V46)"
---
# C++ incompatible-QoS demo

**TL;DR** The subscriber requires RELIABLE; the publisher's reliability comes from the parameter `reliability` (`reliable` or `best_effort`) and it registers an `incompatible_qos_callback`. With `best_effort` both ends are told and no message flows. C++ twin of [[core-qos-events-demo]]; concepts: [[core-qos-events]]; API: [[cpp-qos-profile]].

Package: `ros2 pkg create qos_tests_pkg --dependencies rclcpp std_msgs` (ament_cmake is the default build type), files in `src/`.

## `src/subscriber_custom_minimal_qos.cpp`
```cpp
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"

using std::placeholders::_1;

class SubscriberQos : public rclcpp::Node {
public:
  SubscriberQos() : Node("subscriber_qos_obj") {
    rclcpp::QoS qos_profile(10);
    qos_profile.reliability(RMW_QOS_POLICY_RELIABILITY_RELIABLE);

    subscription_ = this->create_subscription<std_msgs::msg::String>(
        "qos_test", qos_profile,
        std::bind(&SubscriberQos::listener_callback, this, _1));
  }

private:
  void listener_callback(const std_msgs::msg::String::SharedPtr msg) {
    RCLCPP_INFO(this->get_logger(), "Data Received = '%s'", msg->data.c_str());
  }

  rclcpp::Subscription<std_msgs::msg::String>::SharedPtr subscription_;
};

int main(int argc, char *argv[]) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<SubscriberQos>());
  rclcpp::shutdown();
  return 0;
}
```

## `src/publisher_custom_minimal_qos.cpp`
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
    // Declare the parameter with a default value
    this->declare_parameter<std::string>("reliability", "reliable");

    // Read the parameter value
    this->get_parameter("reliability", reliability_);

    rclcpp::QoS qos_profile_publisher(10);

    if (reliability_ == "reliable") {
      qos_profile_publisher.reliability(RMW_QOS_POLICY_RELIABILITY_RELIABLE);
    } else if (reliability_ == "best_effort") {
      qos_profile_publisher.reliability(RMW_QOS_POLICY_RELIABILITY_BEST_EFFORT);
    } else {
      RCLCPP_WARN(
        this->get_logger(),
        "Invalid value for parameter 'reliability': '%s'. Using 'reliable' instead.",
        reliability_.c_str());
      reliability_ = "reliable";
      qos_profile_publisher.reliability(RMW_QOS_POLICY_RELIABILITY_RELIABLE);
    }

    rclcpp::PublisherOptions publisher_options;
    publisher_options.event_callbacks.incompatible_qos_callback =
      std::bind(&PublisherQoS::incompatible_qos_info_callback, this, _1);

    publisher_ = this->create_publisher<std_msgs::msg::String>(
      "/qos_test", qos_profile_publisher, publisher_options);

    timer_ = this->create_wall_timer(
      1000ms, std::bind(&PublisherQoS::timer_callback, this));
  }

private:
  void incompatible_qos_info_callback(rclcpp::QOSOfferedIncompatibleQoSInfo & event)
  {
    RCLCPP_ERROR(
      this->get_logger(),
      "A subscriber is asking for an INCOMPATIBLE QoS!");
    RCLCPP_ERROR(
      this->get_logger(),
      "Offered incompatible QoS - total %d delta %d last_policy_kind: %d",
      event.total_count,
      event.total_count_change,
      event.last_policy_kind);
  }

  void timer_callback()
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

  std::string reliability_;
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
Each message is `"<id>:<seconds>,<nanoseconds>"`, e.g. `0:1680119145.802384,1680119145802384230`. The subscriber uses the relative name `qos_test` and the publisher `/qos_test`: the same topic for nodes in the root namespace. CMake: one `add_executable` + `ament_target_dependencies(<exe> rclcpp std_msgs)` per file (`publisher_custom_minimal_qos_exe`, `subscriber_custom_minimal_qos_exe`) and both in `install(TARGETS …)`; the complete file of the package: [[cpp-learn-inter-unit7-qos]].

## Runs
```bash
ros2 run qos_tests_pkg publisher_custom_minimal_qos_exe --ros-args -p reliability:=reliable
ros2 run qos_tests_pkg subscriber_custom_minimal_qos_exe          # Data Received = '0:1680119145.802384,…' once per second
ros2 run qos_tests_pkg publisher_custom_minimal_qos_exe --ros-args -p reliability:=best_effort
```
With `best_effort` the publisher logs, from its own callback:
```
[ERROR] [publisher_qos_obj]: A subscriber is asking for an INCOMPATIBLE QoS!
[ERROR] [publisher_qos_obj]: Offered incompatible QoS - total 1 delta 1 last_policy_kind: 16
```
and the subscriber, which set no callback, logs rclcpp's default warning: `[WARN] [subscriber_qos_obj]: New publisher discovered on topic '/qos_test', offering incompatible QoS. No messages will be sent to it. Last incompatible policy: RELIABILITY_QOS_POLICY`. `16` is RELIABILITY ([[cpp-qos-profile]]). Publisher BEST_EFFORT + subscriber RELIABLE is the incompatible pair; every other reliability pair connects ([[core-qos-policies]]).

## Pitfalls
- Only reliability differs here; when several policies are incompatible, the event names only the last one evaluated.
- A parameter value other than `reliable`/`best_effort` falls back to RELIABLE: a typo gives a compatible pair, and only the `Invalid value for parameter 'reliability'` warning tells you.
