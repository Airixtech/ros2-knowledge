---
id: cpp-exec-groups-demo
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "Plant detector with a MultiThreadedExecutor and callback groups: three variants as diffs, launch, results"
domain: cpp
area: executors
distro: humble
tested: false
audience: dev
summary: "plant_detector_multithreading(_callbackgroups).cpp as diffs of the single-threaded demo: 2-thread executor, Reentrant group, two exclusive groups; CMake, launch, runs."
tags: [plant_detector_multithreading.cpp, plant_detector_multithreading_callbackgroups.cpp, MultiThreadedExecutor, Reentrant, MutuallyExclusive, callback groups, detect_plants, launch, CMake, timing CSV]
see: ["[[cpp-exec-plant-detector-demo]]", "[[cpp-exec-multithreaded]]", "[[cpp-exec-callback-groups]]", "[[cpp-learn-unit6-multithreading]]"]
requires: [ros2-core]
version_notes:
  - "course: the CMake additions list std_msgs in ament_target_dependencies without find_package(std_msgs); it is found only because sensor_msgs exports it — https://github.com/ament/ament_cmake/blob/humble/ament_cmake_export_dependencies/cmake/ament_cmake_export_dependencies-extras.cmake.in (CPP-V20)"
  - "course: plant_detector_multithreading.launch.py imports Trace from tracetools_launch and never uses it (CPP-V40); the 6.5 output prints 'Plant Detecte!' (CPP-V18)"
---
# Plant detector: executor and group variants

**TL;DR** Three programs, each the single-threaded demo ([[cpp-exec-plant-detector-demo]]) with a few lines changed. Results with the rover not facing the plant: **2 threads only → still fails**; **2 threads + one Reentrant group → finds the plant**; **2 threads + two MutuallyExclusive groups → finds the plant**. Why: [[cpp-exec-multithreaded]], [[cpp-exec-callback-groups]].

## Variant 1: `src/plant_detector_multithreading.cpp` (unit 6.3)
Same class as the demo, with these differences:
- includes add `<rclcpp/callback_group.hpp>` and `<rclcpp/executors/multi_threaded_executor.hpp>`;
- CSV files `multithreaded_listener_callback_timings.csv` and `multithreaded_detect_plants_callback_timings.csv`, CSV labels `multithreaded_listener_callback` / `multithreaded_detect_plants_callback`, summary title `=== MULTITHREADED CALLBACK TIMING SUMMARY ===` and lines `multithreaded_listener_callback: …` / `multithreaded_detect_plants_callback: …`;
- `(void)request; // Unused parameter` in both service functions;
- `main()`:
```cpp
int main(int argc, char *argv[]) {
  rclcpp::init(argc, argv);
  auto plant_detector_node = std::make_shared<PlantDetectorNode>();

  // Use MultiThreadedExecutor with 2 threads
  rclcpp::executors::MultiThreadedExecutor executor(rclcpp::ExecutorOptions(),
                                                    2);
  executor.add_node(plant_detector_node);

  try {
    executor.spin();
  } catch (const std::exception &e) {
    RCLCPP_ERROR(plant_detector_node->get_logger(), "Exception: %s", e.what());
  }

  rclcpp::shutdown();
  return 0;
}
```
Launch file `plant_detector_multithreading.launch.py` = the demo's launch with `executable='plant_detector_multithreading'` (the course's copy also has `from tracetools_launch.action import Trace`, unused: drop it, CPP-V40). CMake additions:
```cmake
add_executable(plant_detector_multithreading src/plant_detector_multithreading.cpp)

ament_target_dependencies(plant_detector_multithreading
  rclcpp
  std_msgs
  sensor_msgs
  std_srvs
  geometry_msgs
  cv_bridge
  OpenCV
)

# Install executables
install(TARGETS
  plant_detector_multithreading
  DESTINATION lib/${PROJECT_NAME}
)
```
`std_msgs` has no `find_package` here: it builds only because `sensor_msgs` exports it; add `find_package(std_msgs REQUIRED)` (CPP-V20). Result: `success=False`, the image callback still pauses during the search.

## Variant 2: one Reentrant group (`src/plant_detector_multithreading_callbackgroups.cpp`, unit 6.5)
Variant 1 plus, in the constructor (the course's 6.5 and 6.6 files drop the two extra includes: `<rclcpp/rclcpp.hpp>` already brings `callback_group.hpp` and `multi_threaded_executor.hpp`):
```cpp
    // Create a reentrant callback group
    reentrant_group_1_ =
        this->create_callback_group(rclcpp::CallbackGroupType::Reentrant);

    // Set up subscription options to use the reentrant callback group
    rclcpp::SubscriptionOptions sub_options;
    sub_options.callback_group = reentrant_group_1_;

    subscription_ = this->create_subscription<sensor_msgs::msg::Image>(
        image_topic_name_, 10,
        std::bind(&PlantDetectorNode::listener_callback_wrapper, this,
                  std::placeholders::_1),
        sub_options);
    // ...
    srv_ = this->create_service<std_srvs::srv::Trigger>(
        "detect_plants",
        std::bind(&PlantDetectorNode::detect_plants_callback_wrapper, this,
                  std::placeholders::_1, std::placeholders::_2),
        rmw_qos_profile_services_default, reentrant_group_1_);
```
member `rclcpp::CallbackGroup::SharedPtr reentrant_group_1_;`, CSV prefix `reentrant_` (`reentrant_listener_callback_timings.csv`, `reentrant_detect_plants_callback_timings.csv`, labels `reentrant_listener_callback` / `reentrant_detect_plants_callback`, title `=== REENTRANT CALLBACK TIMING SUMMARY ===`). Launch `plant_detector_multithreading_callbackgroups.launch.py` (executable `plant_detector_multithreading_callbackgroups`) and CMake as in variant 1 with that name. Result: `success=True`; `Receiving video frame` keeps appearing between `Processing Image for Plants...` lines and the rover stops at the first glimpse of the plant (the course's log even prints `Plant Detecte!`, CPP-V18). Add the lock of [[cpp-exec-callback-groups]] (CPP-V05).

## Variant 3: two MutuallyExclusive groups (same file, unit 6.6)
Replace the group lines:
```cpp
    // Create two mutually exclusive callback groups
    mutuallyexclusive_group_1_ = this->create_callback_group(
        rclcpp::CallbackGroupType::MutuallyExclusive);
    mutuallyexclusive_group_2_ = this->create_callback_group(
        rclcpp::CallbackGroupType::MutuallyExclusive);

    // Set up subscription options to use the mutually exclusive callback group
    rclcpp::SubscriptionOptions sub_options;
    sub_options.callback_group = mutuallyexclusive_group_1_;
    // ... subscription as in variant 2 ...
    srv_ = this->create_service<std_srvs::srv::Trigger>(
        "detect_plants",
        std::bind(&PlantDetectorNode::detect_plants_callback_wrapper, this,
                  std::placeholders::_1, std::placeholders::_2),
        rmw_qos_profile_services_default, mutuallyexclusive_group_2_);
```
members `mutuallyexclusive_group_1_`, `mutuallyexclusive_group_2_`; CSV prefix `mutuallyexclusive_`, title `=== MUTUALLY EXCLUSIVE CALLBACK TIMING SUMMARY ===`. Same launch file and executable. Result: `success=True`, the same timeline as variant 2.

## Run (each variant)
```bash
cd ~/ros2_ws && colcon build --packages-select basics_ros2_multithreading && source install/setup.bash
ros2 launch basics_ros2_multithreading plant_detector_multithreading_callbackgroups.launch.py
ros2 run teleop_twist_keyboard teleop_twist_keyboard     # face away from the plant first
source ~/ros2_ws/install/setup.bash && ros2 service call /detect_plants std_srvs/srv/Trigger "{}"
```
Stop the launch with Ctrl+C to write the CSV summary. The course plots the files with its own timeline viewer (one per variant).

| Variant | Executor | Groups | `/detect_plants` from a blind start |
|---|---|---|---|
| demo (5.5) | `rclcpp::spin` (1 thread) | default | `success=False` (stale image) |
| 1 (6.3) | MultiThreaded, 2 threads | default | `success=False` |
| 2 (6.5) | MultiThreaded, 2 threads | 1 Reentrant | `success=True` |
| 3 (6.6) | MultiThreaded, 2 threads | 2 MutuallyExclusive | `success=True` |
