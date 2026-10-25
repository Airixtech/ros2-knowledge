---
id: cpp-topic-subscriber
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "rclcpp subscriber: create_subscription with rclcpp::QoS, callback signature, storing the last message"
domain: cpp
area: communication
distro: humble
tested: false
audience: dev
summary: "create_subscription<LaserScan>(topic, rclcpp::QoS(10).reliability(Reliable), std::bind(..., _1)), callback signature, QoS compatibility, spin, std::min_element."
tags: [create_subscription, rclcpp::Subscription, rclcpp::QoS, ReliabilityPolicy, std::bind, std::placeholders::_1, SharedPtr, ConstSharedPtr, LaserScan, min_element, subscriber_obstacle_detector.cpp]
see: ["[[core-topic-cpp]]", "[[cpp-recipe-laserscan]]", "[[core-qos-usage]]", "[[core-qos-policies]]", "[[cpp-topic-publisher]]"]
requires: [ros2-core]
version_notes:
  - "humble: callbacks taking std::shared_ptr<MsgT> (MsgT::SharedPtr, also when declared const) compile with a deprecation warning; jazzy/kilted: no warning (rclcpp #2431); lyrical: deprecated again (#2975); MsgT::ConstSharedPtr or const MsgT & is warning-free everywhere — https://github.com/ros2/rclcpp/blob/humble/rclcpp/include/rclcpp/any_subscription_callback.hpp, https://github.com/ros2/rclcpp/blob/lyrical/rclcpp/CHANGELOG.rst (CPP-V46)"
---
# rclcpp subscriber

**TL;DR** `create_subscription<MsgT>(topic, qos, callback)` in the constructor, stored in a `rclcpp::Subscription<MsgT>::SharedPtr` member; the callback runs only while the node spins. The subscriber's QoS must be compatible with the publisher's (check with `ros2 topic info <topic> -v`). Prefer `MsgT::ConstSharedPtr msg` in the callback: the course's `const MsgT::SharedPtr msg` warns on Humble and Lyrical (CPP-V46).

## `src/subscriber_obstacle_detector.cpp` (minimum distance)
```cpp
#include "rclcpp/rclcpp.hpp"
// import the LaserScan module from sensor_msgs interface
#include "sensor_msgs/msg/laser_scan.hpp"
// import Quality of Service library, to set the correct profile and reliability to read sensor data.
#include "rclcpp/qos.hpp"
#include <algorithm>

class ObstacleDetectorNode : public rclcpp::Node
{
public:
    ObstacleDetectorNode(const std::string& node_name = "obstacle_detector_node")
        : Node(node_name)
    {
        // create the subscriber object
        // in this case, the subscriptor will be subscribed on /laser_scan topic with a queue size of 10 messages.
        // use the LaserScan module for /laser_scan topic
        // send the received info to the laserscan_callback method.
        auto qos = rclcpp::QoS(10).reliability(rclcpp::ReliabilityPolicy::Reliable);  // is the most used to read LaserScan data

        subscriber_ = this->create_subscription<sensor_msgs::msg::LaserScan>(
            "/laser_scan",
            qos,
            std::bind(&ObstacleDetectorNode::laserscan_callback, this, std::placeholders::_1)
        );

        RCLCPP_INFO(this->get_logger(), "%s Ready...", this->get_name());
    }

private:
    rclcpp::Subscription<sensor_msgs::msg::LaserScan>::SharedPtr subscriber_;

    void laserscan_callback(const sensor_msgs::msg::LaserScan::SharedPtr msg){
        // Find the minimum distance in the ranges array
        float min_distance = *std::min_element(msg->ranges.begin(), msg->ranges.end());

        // Log the minimum distance value
        RCLCPP_INFO(this->get_logger(), "Minimum distance: %.2f meters", min_distance);
    }
};

int main(int argc, char** argv){
    rclcpp::init(argc, argv);
    auto node = std::make_shared<ObstacleDetectorNode>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}
```
Output: `[INFO] [1724778650.814256725] [obstacle_detector_node]: Minimum distance: 1.94 meters`, changing as you drive with teleop. Build: executable `subscriber_obstacle_detector_executable`, `ament_target_dependencies(… rclcpp std_msgs sensor_msgs geometry_msgs)` ([[cpp-pkg-cmake]]).

## The four parts of `create_subscription`
- **Message type** (template argument): `sensor_msgs::msg::LaserScan`, so the subscription is strongly typed.
- **Topic**: `/laser_scan`.
- **QoS**: depth 10 and RELIABLE here. The publisher of `/laser_scan` is RELIABLE (`ros2 topic info /laser_scan -v` → `Reliability: RELIABLE`, `Durability: VOLATILE`), so a RELIABLE request is compatible; a RELIABLE subscriber never receives from a BEST_EFFORT publisher ([[core-qos-policies]]). `ros2 topic echo` takes the same choices as flags: `--qos-profile` (`sensor_data`, `services_default`, `parameters`…), `--qos-depth`, `--qos-history`, `--qos-reliability`, `--qos-durability`.
- **Callback**: `std::bind(&ObstacleDetectorNode::laserscan_callback, this, std::placeholders::_1)`: member function + object + `_1`, the message the executor passes later.

## C++ review
- `class ObstacleDetectorNode : public rclcpp::Node` and `: Node(node_name)`: public inheritance and base-class initialization; the default argument lets you write `std::make_shared<ObstacleDetectorNode>()`. The name is passed by `const` reference (no copy).
- `public:` constructor, `private:` subscription and callback (internal details).
- `msg->ranges` (access through the smart pointer), `msg->ranges.begin()`/`end()` (iterators), `std::min_element(...)` from `<algorithm>` returns an iterator, `*` dereferences it.
- `auto` deduces long types (`auto qos`, `auto node`); `this->get_logger()`, `this->get_name()` come from `rclcpp::Node`.

## Pitfalls
- No `rclcpp::spin(node)` → messages arrive but the callback never runs.
- `std::min_element` on an empty `ranges` dereferences `end()` (undefined); NaN values break the comparison. Check the size and filter invalid readings (NaN, inf, outside `range_min`/`range_max`) in robust code ([[cpp-recipe-laserscan]]).
- Incompatible QoS (e.g. RELIABLE subscriber, BEST_EFFORT publisher) → silence, no error ([[core-qos-usage]]).
- Warning-free callback in every distro: `void laserscan_callback(const sensor_msgs::msg::LaserScan::ConstSharedPtr msg)` (CPP-V46).
