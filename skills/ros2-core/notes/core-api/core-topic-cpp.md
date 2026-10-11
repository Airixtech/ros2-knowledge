---
id: core-topic-cpp
type: reference
owner: equipo-ros2
updated: 2026-10-09
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "Publisher & subscriber (rclcpp)"
domain: core
area: core-api
distro: humble
tested: false
audience: dev
summary: "rclcpp talker (wall timer + publisher) and listener (ConstSharedPtr callback) classes and their CMake lines."
tags: [rclcpp, publisher, subscription, create_wall_timer, ConstSharedPtr]
see: ["[[core-pkg-ament-cmake]]", "[[core-node-skeleton]]", "[[core-qos-usage]]"]
requires: []
version_notes:
  - "jazzy: non-const shared_ptr<MessageT> subscription callbacks removed — https://docs.ros.org/en/rolling/Releases/Release-Jazzy-Jalisco.html (V27)"
  - "lyrical: ament_target_dependencies removed; use target_link_libraries — https://docs.ros.org/en/rolling/Releases/Release-Kilted-Kaiju.html (V09)"
---
# Publisher & subscriber (rclcpp)

**TL;DR** Keep publishers, subscriptions and timers as `SharedPtr` members. Subscription callbacks take `MessageT::ConstSharedPtr`, which is the only shared-pointer form left in Jazzy+.

## Talker / listener
```cpp
#include <chrono>
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"
using namespace std::chrono_literals;

class Talker : public rclcpp::Node {
public:
  Talker() : Node("talker") {
    pub_ = create_publisher<std_msgs::msg::String>("chatter", 10);
    timer_ = create_wall_timer(500ms, [this]() {
      std_msgs::msg::String msg; msg.data = "hello " + std::to_string(count_++);
      pub_->publish(msg);
    });
  }
private:
  rclcpp::Publisher<std_msgs::msg::String>::SharedPtr pub_;
  rclcpp::TimerBase::SharedPtr timer_;
  size_t count_{0};
};

class Listener : public rclcpp::Node {
public:
  Listener() : Node("listener") {
    sub_ = create_subscription<std_msgs::msg::String>("chatter", 10,
      [this](std_msgs::msg::String::ConstSharedPtr msg) {
        RCLCPP_INFO(get_logger(), "heard: %s", msg->data.c_str()); });
  }
private:
  rclcpp::Subscription<std_msgs::msg::String>::SharedPtr sub_;
};
```

## CMake
`add_executable(talker src/talker.cpp)` + `ament_target_dependencies(talker rclcpp std_msgs)` + `install(TARGETS talker DESTINATION lib/${PROJECT_NAME})` ([[core-pkg-ament-cmake]]).
[changed in Lyrical: `ament_target_dependencies` removed → `target_link_libraries(talker PUBLIC rclcpp::rclcpp ${std_msgs_TARGETS})`]

## Pitfalls
- A callback written as `std::shared_ptr<MessageT>` (non-const) is deprecated in Humble and fails to compile on Jazzy+.
- A local `auto sub = create_subscription(...)` goes out of scope and silently stops receiving. Store it in a member.
- Sensor topics need `rclcpp::SensorDataQoS()` instead of the depth `10` ([[core-qos-usage]]).
