---
id: cpp-node-class
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "rclcpp Node subclass: constructor, create_wall_timer + std::bind callback, member state, spin and the executor"
domain: cpp
area: basics
distro: humble
tested: false
audience: dev
summary: "Node subclass with initializer list, create_wall_timer + std::bind, timer as member, rclcpp::spin; wall timer vs node-clock timer (rclcpp::create_timer)."
tags: [rclcpp::Node, class, inheritance, initializer list, create_wall_timer, create_timer, std::bind, TimerBase, rclcpp::spin, executor, callback, use_sim_time, HeartbeatNode]
see: ["[[cpp-node-first-program]]", "[[core-node-skeleton]]", "[[core-time-timers]]", "[[core-exec-model]]", "[[cpp-callbacks-functions]]", "[[cpp-humble-to-jazzy]]"]
requires: [ros2-core]
version_notes:
  - "humble: create_wall_timer builds a WallTimer on RCL_STEADY_TIME, so it ignores use_sim_time; a timer on the node clock is rclcpp::create_timer(node, clock, Duration, callback) — https://github.com/ros2/rclcpp/blob/humble/rclcpp/include/rclcpp/timer.hpp, https://github.com/ros2/rclcpp/blob/humble/rclcpp/include/rclcpp/create_timer.hpp (CPP-V01)"
  - "jazzy: Node::create_timer(period, callback, group) added (node clock) — https://github.com/ros2/rclcpp/blob/jazzy/rclcpp/include/rclcpp/node.hpp (CPP-V01)"
  - "course: the rover_name_ member is declared and never set or read (CPP-V40)"
---
# rclcpp Node subclass with a timer

**TL;DR** Inherit from `rclcpp::Node`, give the node its name in the constructor initializer list, create the timer in the constructor and store it in a member. `rclcpp::spin(node)` runs the executor that calls the callback. `create_wall_timer` uses the computer's steady clock, **not** the ROS clock: on simulation time use `rclcpp::create_timer(this, this->get_clock(), …)` (CPP-V01).

## `src/heartbeat.cpp`
```cpp
#include "rclcpp/rclcpp.hpp"
#include <chrono>
#include <string>
#include <functional>

class HeartbeatNode : public rclcpp::Node
{
public:
    HeartbeatNode(const std::string& rover_name, double timer_period = 0.2)
    : Node(rover_name)
    {
        // create a timer sending two parameters:
        // - the duration between two callbacks (timer_period seconds)
        // - the timer function (timer_callback)
        timer_ = this->create_wall_timer(
            std::chrono::milliseconds(static_cast<int>(timer_period * 1000)),
            std::bind(&HeartbeatNode::timer_callback, this));
    }

private:
    void timer_callback(){
        auto ros_time_stamp = this->get_clock()->now();
        RCLCPP_INFO(this->get_logger(), "%s is alive...Time(nanoseconds=%ld, clock_type=ROS_TIME)",
                    this->get_name(),
                    ros_time_stamp.nanoseconds());
    }

    rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char** argv){
    // initialize the ROS2 communication
    rclcpp::init(argc, argv);
    // declare the node constructor
    auto node = std::make_shared<HeartbeatNode>("mars_rover_1", 1.0);
    // keeps the node alive, waits for a request to kill the node (ctrl+c)
    rclcpp::spin(node);
    // shutdown the ROS2 communication
    rclcpp::shutdown();
    return 0;
}
```
Output (once per second): `[INFO] [1789656278.277600881] [mars_rover_1]: mars_rover_1 is alive...Time(nanoseconds=1789656278277597143, clock_type=ROS_TIME)`. The course's class also declares a `std::string rover_name_;` member that is never used (CPP-V40); the name lives in the node itself (`get_name()`).

## How it works
- **Inheritance**: `HeartbeatNode` *is* a node, so it has `this->get_logger()`, `this->get_clock()`, `this->create_wall_timer()`, and you add your own members.
- **Constructor**: `rover_name` becomes the node name; `timer_period` defaults to 0.2 s, and `main()` passes 1.0. `: Node(rover_name)` is the constructor initializer list: it builds the parent class (and members) before the constructor body runs.
- **Timer**: period in milliseconds (`timer_period * 1000`: 1.0 s → 1000 ms, 0.5 s → 500 ms, 0.2 s → 200 ms; `std::chrono::duration<double>(timer_period)` also works) and the callback `std::bind(&HeartbeatNode::timer_callback, this)` (member function + the object it runs on).
- **Callback**: code that ROS 2 runs when an event happens (timer expired, message received, service request). The executor watches the events and calls the ready callbacks: the event-driven model replaces the `while` + `sleep_for` loop, which blocks the thread ([[core-exec-model]]).
- **Spin**: `rclcpp::spin(node)` creates an executor, adds the node and processes its callbacks until shutdown (Ctrl+C or `rclcpp::shutdown()`). Without it `main()` reaches its end and the timer never fires.
- **Members**: timers, publishers, subscriptions, services and clients are stored as members (`rclcpp::TimerBase::SharedPtr timer_;`) so they live as long as the node; a local variable is destroyed at the end of the constructor and the callback stops.

Timers are the usual tool for periodic work: velocity commands, heartbeats, robot-state checks, controller updates, diagnostics.

## Wall timer vs node-clock timer (CPP-V01)
`create_wall_timer` builds a `WallTimer` on `RCL_STEADY_TIME`: it keeps firing in real time when the simulation is paused or runs faster, exactly like `sleep_for`. The callback's `get_clock()->now()` does follow sim time. For a timer driven by the node clock (`/clock` when `use_sim_time:=true`):
```cpp
// Humble (also valid later): free function on the node clock
timer_ = rclcpp::create_timer(this, this->get_clock(),
    rclcpp::Duration::from_seconds(timer_period),
    std::bind(&HeartbeatNode::timer_callback, this));
// [≥Jazzy] member function, same clock
timer_ = this->create_timer(std::chrono::duration<double>(timer_period),
    std::bind(&HeartbeatNode::timer_callback, this));
```
The Humble form is `[verify]` on a real run with sim time (Phase 5).

## Pitfalls
- Timer created into a local `auto timer = …` → destroyed when the constructor ends, the callback never runs.
- Forgetting `rclcpp::spin(node)` → the program exits right after creating the node.
- Expecting `create_wall_timer` to pause with the simulation → it does not (CPP-V01).
