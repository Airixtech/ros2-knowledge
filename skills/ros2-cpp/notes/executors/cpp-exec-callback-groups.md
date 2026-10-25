---
id: cpp-exec-callback-groups
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "Callback groups in rclcpp: Reentrant vs MutuallyExclusive, SubscriptionOptions, service group argument, thread safety"
domain: cpp
area: executors
distro: humble
tested: false
audience: dev
summary: "create_callback_group(Reentrant|MutuallyExclusive), SubscriptionOptions::callback_group, create_service group argument; one Reentrant or separate exclusive groups; std::mutex for shared data."
tags: [callback group, create_callback_group, CallbackGroupType, Reentrant, MutuallyExclusive, SubscriptionOptions, rmw_qos_profile_services_default, race condition, std::mutex, lock_guard, std::atomic, thread safety]
see: ["[[cpp-exec-multithreaded]]", "[[cpp-exec-groups-demo]]", "[[core-exec-callback-groups]]", "[[core-exec-model]]", "[[cpp-exec-multi-node]]"]
requires: [ros2-core]
version_notes:
  - "course: the 6.6 snippet includes rclcpp/callback_groups.hpp, which does not exist; the header is rclcpp/callback_group.hpp (also included by rclcpp/rclcpp.hpp) — https://github.com/ros2/rclcpp/blob/humble/rclcpp/include/rclcpp/callback_group.hpp (CPP-V04)"
  - "course: with parallel groups, last_image_ is written by the image callback and read by the service callback at the same time without a lock (a data race); fixed with a std::mutex [verify] — https://en.cppreference.com/w/cpp/language/multithread, https://docs.ros.org/en/humble/How-To-Guides/Using-callback-groups.html (CPP-V05)"
  - "jazzy: create_service(name, cb, rclcpp::ServicesQoS(), group) added, the rmw_qos_profile_t form deprecated; kilted/lyrical: rmw_qos_profile_t form removed — https://github.com/ros2/rclcpp/blob/kilted/rclcpp/include/rclcpp/node.hpp (CPP-V23)"
---
# Callback groups in rclcpp

**TL;DR** Every entity without an explicit group joins the node's default group, a **MutuallyExclusive** one: its callbacks never overlap, even on a MultiThreadedExecutor. To let a long callback run while others keep working, either put them in **one Reentrant group** or in **separate MutuallyExclusive groups**, and use enough executor threads. Data shared between callbacks that can now overlap needs protection (`std::mutex`).

## The two types
| Type | Concurrency | Use when |
|---|---|---|
| `ReentrantCallbackGroup` | callbacks of the group (also several runs of the same callback) may run at the same time | callbacks are independent or protect their data (e.g. one callback per sensor) |
| `MutuallyExclusiveCallbackGroup` | only one callback of the group at a time; the others wait | callbacks touch the same hardware or non-thread-safe data |

Callbacks in **different** MutuallyExclusive groups may run in parallel; only those of the **same** group exclude each other. Official rules: [[core-exec-callback-groups]] and the callback-group guide in its `version_notes`.

## Creating groups and assigning entities
```cpp
// Create a reentrant callback group
auto reentrant_group = this->create_callback_group(
  rclcpp::CallbackGroupType::Reentrant);

// Create a mutually exclusive callback group
auto mutually_exclusive_group = this->create_callback_group(
  rclcpp::CallbackGroupType::MutuallyExclusive);
```
```cpp
rclcpp::SubscriptionOptions sub_options;
sub_options.callback_group = reentrant_group;

subscription_ = this->create_subscription<sensor_msgs::msg::Image>(
  "/camera/image",
  10,
  callback_function,
  sub_options);
```
Subscriptions take the group through `SubscriptionOptions`; timers, services and action servers take it as an argument. Keep the group in a member (`rclcpp::CallbackGroup::SharedPtr reentrant_group_1_;`).

## Solution 1: one Reentrant group
```cpp
#include "rclcpp/callback_group.hpp"
// ...
reentrant_group_1_ = this->create_callback_group(rclcpp::CallbackGroupType::Reentrant);
// ...
rclcpp::SubscriptionOptions sub_options;
sub_options.callback_group = reentrant_group_1_;

subscription_ = this->create_subscription<sensor_msgs::msg::Image>(
    image_topic_name_, 10,
    std::bind(&PlantDetectorNode::listener_callback, this, _1),
    sub_options);

// Create the service for plant detection
service_ = this->create_service<std_srvs::srv::Trigger>(
    "detect_plants",
    std::bind(&PlantDetectorNode::detect_plants_callback, this, _1, _2),
    rmw_qos_profile_services_default,
    reentrant_group_1_);
```

## Solution 2: two MutuallyExclusive groups
```cpp
mutuallyexclusive_group_1_ = this->create_callback_group(rclcpp::CallbackGroupType::MutuallyExclusive);
mutuallyexclusive_group_2_ = this->create_callback_group(rclcpp::CallbackGroupType::MutuallyExclusive);
// ...
rclcpp::SubscriptionOptions sub_options;
sub_options.callback_group = mutuallyexclusive_group_1_;
// subscription as above, then the service in the second group:
service_ = this->create_service<std_srvs::srv::Trigger>(
    "detect_plants",
    std::bind(&PlantDetectorNode::detect_plants_callback, this, _1, _2),
    rmw_qos_profile_services_default,
    mutuallyexclusive_group_2_);
```
The course's snippet includes `"rclcpp/callback_groups.hpp"`, a header that does not exist: it is `rclcpp/callback_group.hpp` (CPP-V04). The fragments use `_1`/`_2` without `using std::placeholders::_1;` (the full files write `std::placeholders::_1`). Both solutions work for the plant detector with a 2-thread MultiThreadedExecutor ([[cpp-exec-groups-demo]]); they are not interchangeable in general: separate exclusive groups give more control (each callback still never overlaps itself).

On Jazzy+ write the service QoS as `rclcpp::ServicesQoS()`; Kilted and Lyrical no longer accept `rmw_qos_profile_services_default` there (CPP-V23).

## Thread safety: protect the shared image (CPP-V05)
A race condition: two threads access the same data, at least one writes, and the result depends on their timing. Here `listener_callback()` assigns `last_image_` while `detect_plants_callback()` reads it. C++ offers mutexes and locks (`std::mutex`, `std::lock_guard`, `std::unique_lock`), `std::atomic` for simple values, thread-safe data structures, and designs that avoid shared state. The course's code has no lock; the fix:
```cpp
#include <mutex>

// members
mutable std::mutex image_mutex_;
cv::Mat last_image_;

void listener_callback(const sensor_msgs::msg::Image::SharedPtr msg) {
  RCLCPP_INFO(this->get_logger(), "Receiving video frame");
  try {
    cv::Mat image = cv_bridge::toCvCopy(msg, "bgr8")->image;
    std::lock_guard<std::mutex> lock(image_mutex_);
    last_image_ = image;
  } catch (cv_bridge::Exception &e) {
    RCLCPP_ERROR(this->get_logger(), "cv_bridge exception: %s", e.what());
  }
}

cv::Mat get_latest_image() const {
  std::lock_guard<std::mutex> lock(image_mutex_);
  return last_image_.clone();
}
// in detect_plants_callback(): cv::Mat image = get_latest_image(); if (!image.empty()) { ... detect_plant_in_image(image) ... }
```
The conversion runs outside the lock, so the lock is held only for the assignment; the detector works on its own copy. `[verify]` (build and run, Phase 5).

## Pitfalls
- More threads but no groups → no change (default MutuallyExclusive group, [[cpp-exec-multithreaded]]).
- Reentrant + a callback slower than its trigger rate → several runs of the same callback at once: protect its state too.
- A group created but not passed to the entity does nothing.
