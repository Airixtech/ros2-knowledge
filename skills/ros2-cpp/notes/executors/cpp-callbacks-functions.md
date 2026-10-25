---
id: cpp-callbacks-functions
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "Functions vs callbacks in rclcpp: who calls them, a timer callback, one callback at a time on one thread"
domain: cpp
area: executors
distro: humble
tested: false
audience: dev
summary: "Functions called in sequence vs callbacks run by the executor on events; callback period vs processing time; single-threaded spin."
tags: [callback, function, event, timer, executor, rclcpp::spin, single-threaded, callback period, processing time, function.cpp, RobotStatus]
see: ["[[cpp-callbacks-timing-demo]]", "[[cpp-exec-blocking]]", "[[core-learn-concepts-callbacks]]", "[[core-exec-model]]", "[[cpp-node-class]]"]
requires: [ros2-core]
version_notes: []
---
# Functions vs callbacks in rclcpp

**TL;DR** A function runs when your code calls it; a callback runs when an **event** makes it ready (a timer expires, a message or a service request arrives, an action event happens) and the executor picks it. `rclcpp::spin(node)` uses a single-threaded executor: one callback at a time, so a callback that takes longer than a timer period delays everything else. Concepts in plain words: [[core-learn-concepts-callbacks]].

## A program that calls its functions (`src/function.cpp`, package `basics_ros2_multithreading`)
```cpp
#include <rclcpp/rclcpp.hpp>
#include <chrono>
#include <thread>

void robot_message(const std::string& text, const std::string& robot_name = "Robot-1") {
    std::cout << robot_name << ": " << text << std::endl;
}

int main(int argc, char** argv) {
    rclcpp::init(argc, argv);

    double period = 1.0;
    robot_message("Robot Booting Up...");
    std::this_thread::sleep_for(std::chrono::duration<double>(period));

    robot_message("Robot Ready...");
    std::this_thread::sleep_for(std::chrono::duration<double>(period));

    robot_message("Robot ShuttingDown...");

    rclcpp::shutdown();
    return 0;
}
```
Output: `Robot-1: Robot Booting Up...`, `Robot-1: Robot Ready...`, `Robot-1: Robot ShuttingDown...`. A function is a reusable block of code for one task; `main()` decides when each one runs.

## Two tasks, still called by hand
A class keeps the elapsed time and offers one method per task; `main_task()` coordinates them:
```cpp
#include <rclcpp/rclcpp.hpp>
#include <chrono>
#include <thread>
#include <string>

class RobotStatus : public rclcpp::Node {
public:
    RobotStatus() : Node("robot_status"), time_robot_on_(0.0) {}

    void robot_message(const std::string& text, const std::string& robot_name = "Robot-1") {
        RCLCPP_INFO(this->get_logger(), "%s: %s", robot_name.c_str(), text.c_str());
    }

    void timer_counter(double time_passed) {
        time_robot_on_ += time_passed;
        RCLCPP_INFO(this->get_logger(), "Updated Time Robot On=%f", time_robot_on_);
    }

    void main_task() {
        double period = 1.0;

        robot_message("Robot Booting Up...");
        std::this_thread::sleep_for(std::chrono::duration<double>(period));
        timer_counter(period);

        robot_message("Robot Ready...");
        std::this_thread::sleep_for(std::chrono::duration<double>(period));
        timer_counter(period);

        robot_message("Robot ShuttingDown...");
    }

private:
    double time_robot_on_;
};

int main(int argc, char** argv) {
    rclcpp::init(argc, argv);

    auto robot_status_node = std::make_shared<RobotStatus>();
    robot_status_node->main_task();

    rclcpp::shutdown();
    return 0;
}
```
Output: `Robot-1: Robot Booting Up...`, `Updated Time Robot On=1.000000`, `Robot-1: Robot Ready...`, `Updated Time Robot On=2.000000`, `Robot-1: Robot ShuttingDown...`. It works, but the program must decide when each function runs, which gets hard as tasks grow.

## From functions to callbacks
Make `main_task()` and `timer_counter()` timer callbacks (every 1.0 s and every 0.1 s) and let `rclcpp::spin()` run them: [[cpp-callbacks-timing-demo]]. Two numbers matter for every callback:
- **callback period**: how often it becomes ready (the timer period);
- **callback processing time**: how long it runs once started.

With near-zero processing time each callback runs on schedule (30 `timer_counter` calls and 3 `main_task` calls in 3 s). With 1.0 s and 1.5 s of simulated processing (perception work such as image processing, object detection or face recognition takes long) only 4 `timer_counter` calls happen: on the single-threaded executor a ready callback waits until the running one ends. This holds for **every** kind of callback: timers, subscriptions, services and actions.

## Pitfalls
- A `sleep_for` or a long computation inside a callback delays all other callbacks of that executor ([[cpp-exec-blocking]]).
- A callback period shorter than the time the thread is busy cannot be kept: the late timer runs once when the thread is free, and the missed periods are not made up (4 calls instead of 30 in the course's run).
- More threads alone do not fix it: [[cpp-exec-multithreaded]], [[cpp-exec-callback-groups]].
