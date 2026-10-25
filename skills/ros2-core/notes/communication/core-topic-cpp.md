---
id: core-topic-cpp
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "Publisher & subscriber (rclcpp)"
domain: core
area: communication
distro: humble
tested: false
audience: dev
summary: "rclcpp talker (wall timer + publisher) and listener (ConstSharedPtr callback) classes and their CMake lines."
tags: [rclcpp, publisher, subscription, create_wall_timer, ConstSharedPtr]
see: ["[[core-pkg-ament-cmake]]", "[[core-node-skeleton]]", "[[core-qos-usage]]"]
requires: []
version_notes:
  - "jazzy: the release notes say non-const shared_ptr<MessageT> subscription callbacks were removed (V27), but rclcpp 28.x still accepts them without a warning (only the deprecation wrapper was removed, #2431); Lyrical deprecates them again (#2975); ConstSharedPtr works everywhere — https://github.com/ros2/rclcpp/blob/jazzy/rclcpp/include/rclcpp/any_subscription_callback.hpp, https://github.com/ros2/rclcpp/blob/lyrical/rclcpp/CHANGELOG.rst (CPP-V46)"
  - "lyrical: ament_target_dependencies removed; use target_link_libraries — https://docs.ros.org/en/rolling/Releases/Release-Kilted-Kaiju.html (V09)"
---
# Publisher & subscriber (rclcpp)

**TL;DR** Keep publishers, subscriptions and timers as `SharedPtr` members. Subscription callbacks take `MessageT::ConstSharedPtr` (or `const MessageT &`), the shared-pointer form that is warning-free in every distro. C++ in depth (packages, services, actions, executors, components): the ros2-cpp skill.

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
- A callback written as `std::shared_ptr<MessageT>` (non-const, also `const MessageT::SharedPtr`) warns as deprecated on Humble and again on Lyrical; Jazzy and Kilted accept it silently although the Jazzy release notes call it removed (CPP-V46). Write `ConstSharedPtr`.
- A local `auto sub = create_subscription(...)` goes out of scope and silently stops receiving. Store it in a member.
- Sensor topics need `rclcpp::SensorDataQoS()` instead of the depth `10` ([[core-qos-usage]]).
