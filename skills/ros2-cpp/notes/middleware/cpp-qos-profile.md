---
id: cpp-qos-profile
type: reference
owner: equipo-ros2
updated: 2026-10-26
review_by: 2027-04-24
source: manual
confidentiality: internal
title: "rclcpp::QoS in code: depth, policy setters, PublisherOptions/SubscriptionOptions event callbacks, event info types"
domain: cpp
area: middleware
distro: humble
tested: false
audience: dev
summary: "rclcpp::QoS(depth) and its setters, Duration arguments, event_callbacks on PublisherOptions/SubscriptionOptions, QOS*Info fields, default warnings, policy kind numbers."
tags: [rclcpp::QoS, KeepLast, reliability, durability, deadline, lifespan, liveliness, liveliness_lease_duration, RMW_QOS_POLICY_RELIABILITY_RELIABLE, ReliabilityPolicy, PublisherOptions, SubscriptionOptions, event_callbacks, QOSOfferedIncompatibleQoSInfo, QOSRequestedIncompatibleQoSInfo, QOSLivelinessChangedInfo, last_policy_kind, use_default_callbacks]
see: ["[[core-qos-policies]]", "[[core-qos-events]]", "[[core-qos-usage]]", "[[cpp-qos-events-demo]]", "[[cpp-qos-liveliness-demo]]", "[[cpp-topic-subscriber]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: rclcpp/qos_event.hpp became rclcpp/event_handler.hpp; the QOS*Info and *EventCallbacks names stay; code that only includes rclcpp/rclcpp.hpp is unaffected — https://github.com/ros2/rclcpp/blob/jazzy/rclcpp/include/rclcpp/event_handler.hpp (CPP-V81)"
  - "all: the setters take the rmw enums (RMW_QOS_POLICY_…) or the rclcpp enum classes (rclcpp::ReliabilityPolicy…), Humble to Lyrical — https://github.com/ros2/rclcpp/blob/lyrical/rclcpp/include/rclcpp/qos.hpp (CPP-V82)"
  - "all: last_policy_kind is an rmw_qos_policy_kind_t bit: 2 DURABILITY, 4 DEADLINE, 8 LIVELINESS, 16 RELIABILITY, 32 HISTORY, 64 LIFESPAN, 128 DEPTH, 256 LIVELINESS_LEASE_DURATION — https://github.com/ros2/rmw/blob/humble/rmw/include/rmw/qos_policy_kind.h (CPP-V68)"
---
# rclcpp::QoS in code

**TL;DR** `rclcpp::QoS qos(10);` is KEEP_LAST with depth 10, RELIABLE, VOLATILE (the default profile). Change one policy at a time with its setter, then pass `qos` to `create_publisher` / `create_subscription`. To be told about QoS problems, fill `event_callbacks` of an `rclcpp::PublisherOptions` or `rclcpp::SubscriptionOptions` and pass the options as the last argument. What each policy means and which pairs are compatible: [[core-qos-policies]], [[core-qos-events]].

```cpp
rclcpp::QoS qos(10);                                        // KEEP_LAST, depth 10
qos.reliability(RMW_QOS_POLICY_RELIABILITY_BEST_EFFORT);    // or rclcpp::ReliabilityPolicy::BestEffort, or qos.best_effort()
qos.durability(RMW_QOS_POLICY_DURABILITY_TRANSIENT_LOCAL);  // or qos.transient_local() / qos.durability_volatile()
qos.history(RMW_QOS_POLICY_HISTORY_KEEP_LAST);              // or qos.keep_last(10) / qos.keep_all()
qos.deadline(std::chrono::milliseconds(1000));              // std::chrono durations convert to rclcpp::Duration
qos.lifespan(std::chrono::milliseconds(20000));
qos.liveliness(RMW_QOS_POLICY_LIVELINESS_MANUAL_BY_TOPIC);  // or AUTOMATIC
qos.liveliness_lease_duration(std::chrono::milliseconds(2000));

rclcpp::PublisherOptions pub_options;
pub_options.event_callbacks.incompatible_qos_callback =
    std::bind(&MyNode::on_incompatible, this, std::placeholders::_1);
pub_options.callback_group = events_group_;                 // optional: the group of the event callbacks
publisher_ = this->create_publisher<std_msgs::msg::String>("/qos_test", qos, pub_options);
```
The setters return the `QoS` object, so they chain: `rclcpp::QoS(rclcpp::KeepLast(1)).reliable().transient_local()` ([[core-qos-usage]]). Preset classes: `rclcpp::SensorDataQoS()`, `rclcpp::ServicesQoS()`, `rclcpp::SystemDefaultsQoS()`…

## Event callbacks
| Side | `event_callbacks.` member | Argument (`rclcpp::`) | Fields |
|---|---|---|---|
| publisher | `incompatible_qos_callback` | `QOSOfferedIncompatibleQoSInfo &` | `total_count`, `total_count_change`, `last_policy_kind` |
| publisher | `deadline_callback` | `QOSDeadlineOfferedInfo &` | `total_count`, `total_count_change` |
| publisher | `liveliness_callback` | `QOSLivelinessLostInfo &` | `total_count`, `total_count_change` |
| subscription | `incompatible_qos_callback` | `QOSRequestedIncompatibleQoSInfo &` | `total_count`, `total_count_change`, `last_policy_kind` |
| subscription | `deadline_callback` | `QOSDeadlineRequestedInfo &` | `total_count`, `total_count_change` |
| subscription | `liveliness_callback` | `QOSLivelinessChangedInfo &` | `alive_count`, `not_alive_count`, `alive_count_change`, `not_alive_count_change` |
| subscription | `message_lost_callback` | `QOSMessageLostInfo &` | — |

- A member function without parameters works too: `std::bind(&MyNode::on_deadline, this)` ignores the info argument (the course's deadline and publisher-liveliness callbacks do this).
- `last_policy_kind` is a bit of `rmw_qos_policy_kind_t`: 2 DURABILITY, 4 DEADLINE, 8 LIVELINESS, 16 RELIABILITY, 64 LIFESPAN, 256 LIVELINESS_LEASE_DURATION (CPP-V68).
- `use_default_callbacks` (true) installs rclcpp's own incompatible-QoS handlers where you set none: a subscription logs `New publisher discovered on topic '/qos_test', offering incompatible QoS. No messages will be sent to it. Last incompatible policy: RELIABILITY_QOS_POLICY`, a publisher `New subscription discovered on topic …, requesting incompatible QoS. …`.
- Event callbacks run through the executor like any callback; give them their own group (`pub_options.callback_group`, `SubscriptionOptions::callback_group`) when other callbacks block ([[cpp-qos-liveliness-demo]]).

## Pitfalls
- Passing `qos_profile` without the options → no custom event callbacks, only the default warnings.
- Comparing durations in the wrong unit: the course's demos take seconds (`deadline`, `lifespan`) or milliseconds (`liveliness_lease_duration`) as parameters and convert them with `std::chrono::milliseconds(…)`.
