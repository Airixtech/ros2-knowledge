---
id: cpp-exec-multithreaded
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "MultiThreadedExecutor in rclcpp: ExecutorOptions and thread count, add_node, spin; why threads alone do not help"
domain: cpp
area: executors
distro: humble
tested: false
audience: dev
summary: "rclcpp::executors::MultiThreadedExecutor(ExecutorOptions(), 2), add_node, spin in try/catch; nproc; callbacks of the default group still never overlap."
tags: [MultiThreadedExecutor, SingleThreadedExecutor, ExecutorOptions, number_of_threads, add_node, executor.spin, hardware_concurrency, nproc, multi_threaded_executor.hpp]
see: ["[[cpp-exec-callback-groups]]", "[[cpp-exec-groups-demo]]", "[[cpp-exec-blocking]]", "[[core-exec-model]]", "[[cpp-exec-multi-node]]"]
requires: [ros2-core]
version_notes:
  - "all: MultiThreadedExecutor(options, number_of_threads = 0, yield_before_execute = false, timeout = -1); 0 threads = std::thread::hardware_concurrency(), at least 1 — https://github.com/ros2/rclcpp/blob/humble/rclcpp/src/rclcpp/executors/multi_threaded_executor.cpp (CPP-V26)"
---
# MultiThreadedExecutor in rclcpp

**TL;DR** Replace `rclcpp::spin(node)` by an explicit `rclcpp::executors::MultiThreadedExecutor executor(rclcpp::ExecutorOptions(), N);` + `executor.add_node(node);` + `executor.spin();`. Now N threads can run callbacks, **but only callbacks whose groups allow it**: with the default MutuallyExclusive group the plant detector still processes one callback at a time ([[cpp-exec-callback-groups]]).

Why: a robot does several things at once. Autonomous vehicles process several sensor streams while deciding where to drive, manipulators run perception and motion control together, industrial robots coordinate several operations and devices, drones run flight control next to their mission tasks. On one executor thread those callbacks queue behind each other ([[cpp-exec-blocking]]).

## Before and after
```cpp
// REST OF THE CODE
int main(int argc, char * argv[]){
  rclcpp::init(argc, argv);
  auto plant_detector_node = std::make_shared<PlantDetectorNode>();
  rclcpp::spin(plant_detector_node);
  rclcpp::shutdown();
  return 0;
}
```
```cpp
#include "rclcpp/executors/multi_threaded_executor.hpp"
// REST OF THE CODE IS IDENTICAL
int main(int argc, char * argv[]){
  rclcpp::init(argc, argv);
  auto plant_detector_node = std::make_shared<PlantDetectorNode>();

  // Use MultiThreadedExecutor
  rclcpp::executors::MultiThreadedExecutor executor(rclcpp::ExecutorOptions(), 2);
  executor.add_node(plant_detector_node);

  try {
    executor.spin();
  } catch (const std::exception & e) {
    RCLCPP_ERROR(plant_detector_node->get_logger(), "Exception: %s", e.what());
  }

  rclcpp::shutdown();
  return 0;
}
```
- The node is no longer passed to `rclcpp::spin()`: the executor owns the callback processing; `executor.spin()` runs until shutdown.
- The second argument is the number of threads; 2 is enough for two callbacks. With the default `0` the executor takes `std::thread::hardware_concurrency()` threads (CPP-V26). `nproc` prints the processing units of the machine (8 in the course environment).
- `rclcpp::executors::SingleThreadedExecutor` is the explicit form of what `rclcpp::spin()` uses.

## The surprise
Run with two threads, rover not facing the plant, call `/detect_plants`: still `success=False` after 10 s, and the timeline still shows `listener_callback` stopped during `detect_plants_callback`. Both callbacks are in the node's default **MutuallyExclusive** callback group, which never lets two of its callbacks run together, whatever the number of threads. Program and runs: [[cpp-exec-groups-demo]]; the fix: [[cpp-exec-callback-groups]].

## Pitfalls
- More threads than callbacks that may overlap gives nothing; fewer threads than overlapping callbacks makes the extra ones wait.
- `executor.spin()` can throw (for example a node added to two executors): the course wraps it in `try`/`catch`.
- Several nodes can share one executor and its threads ([[cpp-exec-multi-node]]).
