---
id: core-jazzy-to-lyrical
title: "Jazzy → Lyrical changes (core, incl. Kilted)"
domain: core
area: migration
distro: lyrical
tested: false
audience: dev
summary: "What changes for user code from Jazzy to Lyrical (includes Kilted): platform, removed APIs (ament_target_dependencies, warn, ROS_LOCALHOST_ONLY), Nav2, rosbag2."
tags: [migration, lyrical, kilted, removals, breaking changes]
see: ["[[core-humble-to-jazzy]]", "[[core-migration-checklist]]"]
requires: []
version_notes:
  - "sources: https://docs.ros.org/en/rolling/Releases/Release-Kilted-Kaiju.html · https://docs.ros.org/en/rolling/Releases/Release-Lyrical-Luth.html · https://docs.ros.org/en/rolling/Releases/Lyrical-Luth-Complete-Changelog.html"
---
# Jazzy → Lyrical changes (core, incl. Kilted)

**TL;DR** Lyrical (LTS, May 2026 – May 2031) removes many APIs that were only deprecated in Humble and Jazzy: `ament_target_dependencies`, `logger.warn()`, `StaticSingleThreadedExecutor`, `ROS_LOCALHOST_ONLY`, `tf2/LinearMath/Quaternion.h` and positional static TF args. Kilted (May 2025 – Nov 2026) is the intermediate non-LTS release. `Vxx` = row in the repo's `reports/version_audit.md`.

| Area | Jazzy | Lyrical (Kilted changes marked K) | Ref |
|---|---|---|---|
| Platform | Ubuntu 24.04, Python 3.12, C++17 | Ubuntu 26.04 (Noble = Tier 3), Python 3.14 (min 3.12), **C++20**, CMake 4.x | V04, V11 |
| Gazebo | Harmonic | K: Ionic · Lyrical: **Jetty** | V64 |
| Middleware | Fast DDS 2.14, Cyclone 0.10 | Fast DDS 3.6, Cyclone 11; K: fastrtps→fastdds rename (`FASTDDS_DEFAULT_PROFILES_FILE`), Zenoh Tier 1 | V03, V58 |
| Discovery | `ROS_LOCALHOST_ONLY` deprecated | K: **removed** (no effect) | V01 |
| CMake | `ament_target_dependencies` | K: deprecated (warning) → Lyrical: **removed** → `target_link_libraries(t PUBLIC rclcpp::rclcpp ${msg_pkg_TARGETS})`; new `ament_cmake_ros_core::ament_ros_defaults` | V09 |
| rclpy | `warn()` deprecated | **removed** → `warning()`; K: EventsExecutor (exp.); `AsyncNode` (asyncio) | V22, V33 |
| rclcpp | `StaticSingleThreadedExecutor` | K: deprecated → **removed**; callback-group events executor; array range checks for params | V32, V33 |
| tf2 | `.h` and `.hpp` | K: `Quaternion.h` deprecated → **removed**; `tf2_ros/*.h` deprecated (`#warning`) | V44 |
| static TF CLI | positional args deprecated | **removed** (flags only) | V43 |
| Interfaces | `action_tutorials_interfaces` | K: **removed** → `example_interfaces/action/Fibonacci` (feedback `sequence`); `actionlib_msgs` removed; K: `nav_msgs/Goals` | V28, V29 |
| launch | — | K: `PathJoinSubstitution` concatenation; per-message log severity; new XML/YAML substitutions | V18 |
| rosbag2 | — | K: `play -i` multiple bags, progress bar, `info --sort`; circular recording; control via services and Python | V47, V49 |
| CLI | — | `ros2 param get` from all nodes, multi get/set; `doctor --report` adds actions/services/env; `service info --verbose`; `topic bw` multi-topic; fish shell | V39, V77 |
| RSP / URDF | parameter only | `robot_state_publisher` can read `robot_description` from a topic | V19 |
| Nav2 | Twist (stamped opt-in) | K: **TwistStamped default**, route server; Lyrical: Nav2 lifecycle-node refactor, following server | V54, V55 |
| Tracing | built in | snapshot mode, dual sessions, runtime opt-out | V40 |

Open `[verify]`: the Fast DDS 3 discovery CLI, Cyclone 11 XML compatibility and the CMake 4 minimum-version warnings. These are pending a Docker test in Phase 5.
Procedure: [[core-migration-checklist]].
