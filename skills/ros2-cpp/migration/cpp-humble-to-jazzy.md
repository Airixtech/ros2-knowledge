---
id: cpp-humble-to-jazzy
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "The course's rclcpp code on Jazzy, Kilted and Lyrical: what changes"
domain: cpp
area: migration
distro: humble
tested: false
audience: dev
summary: "Porting the Humble C++ code: ament_target_dependencies removed, cv_bridge.hpp, tf2 .hpp headers, create_service QoS, Node::create_timer, ConstSharedPtr callbacks."
tags: [migration, jazzy, kilted, lyrical, ament_target_dependencies, target_link_libraries, cv_bridge.hpp, Quaternion.hpp, create_service, ServicesQoS, create_timer, ConstSharedPtr, RCLCPP_VERSION_GTE, __has_include]
see: ["[[core-humble-to-jazzy]]", "[[core-jazzy-to-lyrical]]", "[[cpp-pkg-cmake]]", "[[cpp-cmake-library]]", "[[cpp-node-class]]"]
requires: [ros2-core]
version_notes:
  - "lyrical: ament_target_dependencies deprecated in Kilted, removed in Lyrical — https://github.com/ament/ament_cmake/blob/lyrical/ament_cmake_target_dependencies/CHANGELOG.rst (CPP-V19)"
  - "jazzy: cv_bridge 4.0.0 removed cv_bridge/cv_bridge.h — https://github.com/ros-perception/vision_opencv/blob/rolling/cv_bridge/CHANGELOG.rst (CPP-V21)"
  - "lyrical: tf2/LinearMath/Quaternion.h and Matrix3x3.h removed — https://github.com/ros2/geometry2/tree/lyrical/tf2/include/tf2/LinearMath (CPP-V22)"
  - "jazzy/kilted: create_service with rmw_qos_profile_t deprecated (Jazzy) then removed (Kilted) — https://github.com/ros2/rclcpp/blob/kilted/rclcpp/include/rclcpp/node.hpp (CPP-V23)"
  - "jazzy: Node::create_timer(period, callback, group) added — https://github.com/ros2/rclcpp/blob/jazzy/rclcpp/include/rclcpp/node.hpp (CPP-V01)"
  - "humble/lyrical: shared_ptr<MsgT> subscription callbacks deprecated (Humble #1713, again in Lyrical #2975), accepted without warning on Jazzy/Kilted (#2431) — https://github.com/ros2/rclcpp/blob/lyrical/rclcpp/CHANGELOG.rst (CPP-V46)"
---
# The course's rclcpp code on Jazzy, Kilted and Lyrical

**TL;DR** Most of the course's C++ builds unchanged on Jazzy. What breaks, in order: `cv_bridge/cv_bridge.h` (Jazzy), `create_service(…, rmw_qos_profile_services_default, group)` (Kilted), `ament_target_dependencies` and the tf2 `.h` headers (Lyrical). Forms valid from Humble to Lyrical are listed first; general ROS 2 changes: [[core-humble-to-jazzy]], [[core-jazzy-to-lyrical]].

| Course code (Humble) | Jazzy | Kilted | Lyrical | Write instead |
|---|---|---|---|---|
| `ament_target_dependencies(tgt rclcpp …)` | ✓ | deprecated (warning) | **removed** | `target_link_libraries(tgt PUBLIC rclcpp::rclcpp ${std_msgs_TARGETS} cv_bridge::cv_bridge ${OpenCV_LIBS})` — valid since Humble ([[cpp-cmake-library]]) |
| `#include <cv_bridge/cv_bridge.h>` | **removed** (cv_bridge 4.0.0) | removed | removed | `cv_bridge/cv_bridge.hpp`; Humble's cv_bridge 3.2.1 has only `.h` (portable: `__has_include`) |
| `tf2/LinearMath/Quaternion.h`, `Matrix3x3.h` | ✓ | ✓ | **removed** | `Quaternion.hpp`, `Matrix3x3.hpp` — exist since Humble |
| `create_service<T>(name, cb, rmw_qos_profile_services_default, group)` | deprecated | **removed** | removed | `create_service<T>(name, cb, rclcpp::ServicesQoS(), group)` (Jazzy+) |
| `create_wall_timer(...)` when sim time matters | ✓ | ✓ | ✓ | Humble `rclcpp::create_timer(this, this->get_clock(), Duration, cb)`; Jazzy+ also `this->create_timer(period, cb)` ([[cpp-node-class]]) |
| callbacks `const MsgT::SharedPtr msg` | ✓ no warning | ✓ no warning | deprecated (warning) | `MsgT::ConstSharedPtr msg` — warning-free everywhere |

## One source for several distros
```cpp
#if __has_include(<cv_bridge/cv_bridge.hpp>)
#include <cv_bridge/cv_bridge.hpp>
#else
#include <cv_bridge/cv_bridge.h>
#endif

#include "rclcpp/version.h"
#if RCLCPP_VERSION_GTE(28, 0, 0)   // Jazzy's rclcpp is 28.x
srv_ = create_service<std_srvs::srv::Trigger>("detect_plants", cb, rclcpp::ServicesQoS(), group_);
#else
srv_ = create_service<std_srvs::srv::Trigger>("detect_plants", cb, rmw_qos_profile_services_default, group_);
#endif
```
`rclcpp/version.h` is generated in every rclcpp since Humble (Humble 16.x, Jazzy 28.x, Kilted 29.x, Lyrical 32.x at the time of the audit) `[verify]` build.

## Unchanged
`rclcpp::init/spin/shutdown`, `create_publisher`, `create_subscription` with `rclcpp::QoS`, `MultiThreadedExecutor(ExecutorOptions(), n)`, `create_callback_group`, `SubscriptionOptions`, `add_pre_shutdown_callback`, `rclcpp_action` client and server (goal-response callback with `GoalHandle::SharedPtr` since before Humble), `RCLCPP_COMPONENTS_REGISTER_NODE`, `rclcpp_components_register_nodes`, the `ros2 component` CLI.

## Checklist
1. Replace `ament_target_dependencies` by target linking (needed for Lyrical, quiet on Kilted).
2. Switch to `.hpp` headers that exist since Humble (tf2) and add the cv_bridge include guard.
3. Pass `rclcpp::QoS` to `create_service` on Jazzy+.
4. Use `ConstSharedPtr` callbacks.
5. Rebuild with `-Wall -Wextra` and read the deprecation warnings.
