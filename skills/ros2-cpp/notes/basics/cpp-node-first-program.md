---
id: cpp-node-first-program
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "First rclcpp program: rclcpp::init, a plain rclcpp::Node, RCLCPP_INFO vs std::cout, a counted loop, shutdown"
domain: cpp
area: basics
distro: humble
tested: false
audience: dev
summary: "rclcpp::init/shutdown, why init alone shows no node, std::make_shared<rclcpp::Node>, node->get_clock()->now(), RCLCPP_INFO, std::chrono and sleep_for."
tags: [rclcpp::init, rclcpp::shutdown, rclcpp::Node, make_shared, RCLCPP_INFO, std::cout, std::chrono, system_clock, sleep_for, heartbeat.cpp, ros2 node list]
see: ["[[cpp-node-class]]", "[[cpp-pkg-cmake]]", "[[core-node-skeleton]]", "[[core-time-timers]]", "[[cpp-logging]]"]
requires: [ros2-core]
version_notes:
  - "all: rclcpp, the C++ client library, and rclpy both build on the common C library rcl; other client libraries are community-maintained — https://docs.ros.org/en/humble/Concepts/Basic/About-Client-Libraries.html (CPP-V42)"
---
# First rclcpp program

**TL;DR** `rclcpp::init(argc, argv)` starts ROS 2 communication for the process but creates **no node**: nothing appears in `ros2 node list` until the program creates an `rclcpp::Node` and keeps running. Print with `RCLCPP_INFO` (log levels, node name) instead of `std::cout`.

`rclcpp` is the C++ client library: the API for nodes, publishers, subscribers, services and timers. It and `rclpy` sit on the common C library `rcl`; choosing between them: core-lang-choice in ros2-core ([[core-lang-choice]]).

## Step 1: init, print, shutdown (`src/heartbeat.cpp`)
```cpp
#include "rclcpp/rclcpp.hpp"
#include <iostream>

int main(int argc, char** argv){
    // initialize the ROS communication
    rclcpp::init(argc, argv);
    // print a message to the terminal
    std::cout << "Mars rover 1 is alive..." << std::endl;
    // shutdown the ROS communication
    rclcpp::shutdown();
    return 0;
}
```
`argc`/`argv` carry the command-line arguments (ROS arguments such as `--ros-args` included); `return 0` means success. Build it as `heartbeat_executable` ([[cpp-pkg-cmake]]) and run `ros2 run mars_rover_systems heartbeat_executable` → `Mars rover 1 is alive...`. Exercise 2.1 copies the file as `heartbeat_shutdown.cpp`, which prints `Shutting down Mars rover 1...` (executable `heartbeat_executable_shutdown`).

## Step 2: keep it running (C++ review: std::chrono, sleep_for)
The first program ends at once, so `ros2 node list` never shows it. A loop keeps it alive for 50 s:
```cpp
#include "rclcpp/rclcpp.hpp"
#include <chrono>
#include <thread>
#include <iostream>

int main(int argc, char** argv){
    // initialize the ROS communication
    rclcpp::init(argc, argv);

    int i = 0;
    int max_i = 50;
    while (i < max_i) {
        i++;
        auto time_stamp = std::chrono::system_clock::now();
        auto time_t = std::chrono::system_clock::to_time_t(time_stamp);
        // print a message to the terminal
        std::cout << i << ":Mars rover 1 is alive..." << time_t << std::endl;
        // Wait for 1 second
        std::this_thread::sleep_for(std::chrono::seconds(1));
    }

    // shutdown the ROS communication
    rclcpp::shutdown();
    return 0;
}
```
- `std::chrono::system_clock::now()` is the computer's wall-clock time (a `time_point`); `to_time_t()` turns it into a `std::time_t` calendar time (`1:Mars rover 1 is alive...1789654444`).
- `std::this_thread::sleep_for(std::chrono::seconds(1))` pauses the thread; `std::chrono` units are explicit (`std::chrono::seconds(1)`, `std::chrono::milliseconds(500)`).
- Still no node in `ros2 node list`: `init` only initializes communication.

## Step 3: a node, ROS time and logging
```cpp
#include "rclcpp/rclcpp.hpp"
#include <chrono>
#include <thread>
#include <memory>

int main(int argc, char** argv){
    // initialize the ROS communication
    rclcpp::init(argc, argv);

    // Create a node
    auto node = std::make_shared<rclcpp::Node>("mars_rover_1");

    int i = 0;
    int max_i = 50;
    while (i < max_i) {
        i++;
        auto ros_time_stamp = node->get_clock()->now();
        // print a message to the terminal using ROS2 logging
        RCLCPP_INFO(node->get_logger(), "%d:Mars rover 1 is alive...Time(nanoseconds=%ld, clock_type=ROS_TIME)",
                    i, ros_time_stamp.nanoseconds());
        // Wait for 1 second
        std::this_thread::sleep_for(std::chrono::seconds(1));
    }

    // shutdown the ROS communication
    rclcpp::shutdown();
    return 0;
}
```
- `std::make_shared<rclcpp::Node>("mars_rover_1")` creates the node and returns a shared pointer: ROS 2 manages nodes and entities with shared pointers. Now `/mars_rover_1` appears in `ros2 node list`.
- `node->get_clock()->now()` is the node's ROS clock: with simulation time (`use_sim_time`, `/clock`) it can run faster, slower, pause or reset independently of the computer clock ([[core-time-timers]]); `.nanoseconds()` gives the stamp. `std::chrono::system_clock::now()` never follows `/clock`.
- `RCLCPP_INFO(...)` logs through ROS 2: levels `RCLCPP_DEBUG`, `RCLCPP_INFO`, `RCLCPP_WARN`, `RCLCPP_ERROR`, `RCLCPP_FATAL` can be filtered and are tagged with the node name ([[cpp-logging]]).
- `ros2 node info /mars_rover_1` already lists `/parameter_events` (subscriber and publisher), `/rosout` and the six parameter services (`describe_parameters` … `set_parameters_atomically`) that every node creates ([[core-ros-args]]).

The loop still sleeps with `sleep_for`, which blocks the thread and ignores the ROS clock: the next step is a Node subclass with a timer callback ([[cpp-node-class]]).

## Pitfalls
- A program that only calls `init` → no node in the graph; one that ends immediately → it is gone before `ros2 node list` runs.
- `std::cout` output has no level, node name or timestamp and cannot be filtered: use `RCLCPP_*`.
- Two programs with the same node name → duplicate nodes in the graph; change the name (`mars_rover_2`) or remap it ([[core-ros-args]]).
