---
id: cpp-learn-inter-unit7-qos
type: reference
owner: equipo-ros2
updated: 2026-10-26
review_by: 2027-04-24
source: manual
confidentiality: internal
title: "Intermediate C++ Unit 7: qos_tests_pkg, /laser_scan QoS exercise, deadline exercises, liveliness runs, QoS in bags"
domain: cpp
area: learn
distro: humble
tested: false
audience: students
order: 16
summary: "qos_tests_pkg CMakeLists, exercise 7.1 (/laser_scan subscriber) with solution, exercise 7.2 deadline scenarios and results, liveliness and bag pointers."
tags: [course, unit 7, qos_tests_pkg, subscriber_scan_qos.cpp, /laser_scan, ros2 topic info --verbose, deadline scenarios, last_policy_kind, qos_override.yaml, students]
see: ["[[cpp-qos-profile]]", "[[cpp-qos-events-demo]]", "[[cpp-qos-deadline-demo]]", "[[cpp-qos-liveliness-demo]]", "[[core-qos-policies]]", "[[core-bag-play]]", "[[core-learn-inter-unit7-8-qos-dds]]"]
requires: [ros2-core]
version_notes:
  - "course: 'the subscriber must also use … RELIABLE to establish communication' with the RELIABLE /laser_scan publisher; a BEST_EFFORT subscriber is compatible with a RELIABLE publisher too — https://docs.ros.org/en/humble/Concepts/Intermediate/About-Quality-of-Service-Settings.html (CPP-V87)"
  - "humble: const MsgT::SharedPtr callbacks compile with a deprecation warning (also Lyrical); ConstSharedPtr is warning-free — https://github.com/ros2/rclcpp/blob/humble/rclcpp/include/rclcpp/any_subscription_callback.hpp (CPP-V46)"
---
# Intermediate C++ Unit 7: QoS

**TL;DR** All QoS programs live in `qos_tests_pkg` (C++ demos: [[cpp-qos-events-demo]], [[cpp-qos-durability-demo]], [[cpp-qos-deadline-demo]], [[cpp-qos-lifespan-demo]], [[cpp-qos-liveliness-demo]]). Exercise 7.1 writes a subscriber for the simulator's `/laser_scan`; exercise 7.2 runs the deadline demo with values that break it in three ways. Policies and the compatibility table: [[core-qos-policies]]; Python twin: [[core-learn-inter-unit7-8-qos-dds]].

## `CMakeLists.txt` of `qos_tests_pkg` (complete, end of the unit)
```cmake
cmake_minimum_required(VERSION 3.8)
project(qos_tests_pkg)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # uncomment the line when a copyright and license is not present in all source files
  #set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # uncomment the line when this package is not in a git repo
  #set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

add_executable(publisher_custom_minimal_qos_exe src/publisher_custom_minimal_qos.cpp)
ament_target_dependencies(publisher_custom_minimal_qos_exe rclcpp std_msgs)

add_executable(subscriber_custom_minimal_qos_exe src/subscriber_custom_minimal_qos.cpp)
ament_target_dependencies(subscriber_custom_minimal_qos_exe rclcpp std_msgs)

add_executable(subscriber_scan_qos_exe src/subscriber_scan_qos.cpp)
ament_target_dependencies(subscriber_scan_qos_exe rclcpp std_msgs sensor_msgs)

add_executable(subscriber_durability_exe src/subscriber_durability.cpp)
ament_target_dependencies(subscriber_durability_exe rclcpp std_msgs)

add_executable(publisher_durability_exe src/publisher_durability.cpp)
ament_target_dependencies(publisher_durability_exe rclcpp std_msgs)

add_executable(subscriber_deadline_exe src/subscriber_deadline.cpp)
ament_target_dependencies(subscriber_deadline_exe rclcpp std_msgs)

add_executable(publisher_deadline_exe src/publisher_deadline.cpp)
ament_target_dependencies(publisher_deadline_exe rclcpp std_msgs)

add_executable(subscriber_lifespan_exe src/subscriber_lifespan.cpp)
ament_target_dependencies(subscriber_lifespan_exe rclcpp std_msgs)

add_executable(publisher_lifespan_exe src/publisher_lifespan.cpp)
ament_target_dependencies(publisher_lifespan_exe rclcpp std_msgs)

add_executable(publisher_liveliness_exe src/publisher_liveliness.cpp)
ament_target_dependencies(publisher_liveliness_exe rclcpp std_msgs)

add_executable(subscriber_liveliness_exe src/subscriber_liveliness.cpp)
ament_target_dependencies(subscriber_liveliness_exe rclcpp std_msgs)

install(TARGETS
  publisher_custom_minimal_qos_exe
  subscriber_custom_minimal_qos_exe
  subscriber_scan_qos_exe
  subscriber_durability_exe
  publisher_durability_exe
  subscriber_deadline_exe
  publisher_deadline_exe
  subscriber_lifespan_exe
  publisher_lifespan_exe
  publisher_liveliness_exe
  subscriber_liveliness_exe
  DESTINATION lib/${PROJECT_NAME})

ament_package()
```
The course grows this file page by page (first two executables, then `find_package(sensor_msgs)` and the scan subscriber, then each policy's pair). Package: `ros2 pkg create qos_tests_pkg --dependencies rclcpp std_msgs`; build with `colcon build --packages-select qos_tests_pkg`.

## Exercise 7.1: a QoS-compatible subscriber for `/laser_scan`
Write `subscriber_scan_qos.cpp` and set `history`, `depth`, `reliability` and `liveliness` so it receives the simulator's scans. Inspect the publisher with `ros2 topic info /laser_scan --verbose` (`-v`): `Node name: laser_bridge`, `Reliability: RELIABLE`, `History (Depth): UNKNOWN`, `Durability: VOLATILE`, `Lifespan: Infinite`, `Deadline: Infinite`, `Liveliness: AUTOMATIC`, `Liveliness lease duration: Infinite`. VOLATILE is typical for sensors; infinite deadline and lifespan are simulation defaults (a real sensor has a fixed rate, and stale scans are useless).

Solution, `src/subscriber_scan_qos.cpp`:
```cpp
#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/laser_scan.hpp"
#include <memory>

using std::placeholders::_1;

class SubscriberScanQoS : public rclcpp::Node {
public:
  SubscriberScanQoS() : Node("subscriber_scan_qos") {
    rclcpp::QoS qos_profile(10);
    qos_profile.history(RMW_QOS_POLICY_HISTORY_KEEP_LAST);
    qos_profile.reliability(RMW_QOS_POLICY_RELIABILITY_RELIABLE);
    qos_profile.liveliness(RMW_QOS_POLICY_LIVELINESS_AUTOMATIC);

    subscription_ = this->create_subscription<sensor_msgs::msg::LaserScan>(
        "/laser_scan", qos_profile,
        std::bind(&SubscriberScanQoS::laser_callback, this, _1));
  }

private:
  void laser_callback(const sensor_msgs::msg::LaserScan::SharedPtr msg) {
    RCLCPP_INFO(this->get_logger(),
                "Laser scan received. Number of ranges: %zu",
                msg->ranges.size());
  }

  rclcpp::Subscription<sensor_msgs::msg::LaserScan>::SharedPtr subscription_;
};

int main(int argc, char *argv[]) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<SubscriberScanQoS>());
  rclcpp::shutdown();
  return 0;
}
```
`rclcpp::QoS qos_profile(10)` already means KEEP_LAST with depth 10 (the queue keeps the last 10 scans); the `history` line only makes it explicit. RELIABLE and AUTOMATIC match the publisher. A BEST_EFFORT subscriber would connect too: a RELIABLE publisher serves both kinds (CPP-V87).

## Exercise 7.2: deadline scenarios (demo: [[cpp-qos-deadline-demo]])
| Publisher `deadline` | Subscriber `deadline` | Result |
|---|---|---|
| 10.0 | 10.0 | working condition: no event on either side |
| 1.0 | 10.0 | publisher `PUBLISHER::: Deadline Triggered!` about once per second (jitter pushes some 1 s gaps over 1.0) and during the pause; the subscriber reports nothing |
| 1.1 | 10.0 | publisher event only after the pause |
| 1.5 | 1.5 | the subscriber reports twice during the ~3 s gap (1.5 s apart); the publisher reports once, when the pause ends: its event callback waits for the blocked timer callback on the single-threaded executor |
| 10.0 | 1.0 | incompatible (a subscriber may not request a shorter deadline than offered): both report `… incompatible qos - total 1 delta 1 last_policy_kind: 4` (DEADLINE) |

A deadline equal to the nominal period is too strict in practice; leave a margin (1.5 s for a 1 s publisher).

## Liveliness and bags
- Liveliness runs (AUTOMATIC with a slow publisher, MANUAL_BY_TOPIC with slow or fast asserts): [[cpp-qos-liveliness-demo]], results in [[core-qos-liveliness]].
- QoS in bags (Example 7.3): `ros2 bag record /laser_scan -o rover_scan_bag`, replay with `ros2 bag play --remap /laser_scan:=/laser_scan2 -l rover_scan_bag` and check `ros2 topic info /laser_scan2 --verbose` (publisher `rosbag2_player`, the recorded QoS); override on replay with `--qos-profile-overrides-path qos_override.yaml` ([[core-bag-play]]).
