---
id: cpp-exec-spin-some
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "spin vs spin_some in rclcpp: an own loop that processes ready callbacks and exits cleanly"
domain: cpp
area: executors
distro: humble
tested: false
audience: dev
summary: "rclcpp::spin keeps processing callbacks; rclcpp::spin_some runs the ready ones and returns, so an own loop can exit from a flag."
tags: [rclcpp::spin, rclcpp::spin_some, rclcpp::ok, rclcpp::shutdown, own loop, shutdown flag, busy wait, sleep_for, callback_spinonce_function.cpp]
see: ["[[core-exec-spin]]", "[[cpp-callbacks-timing-demo]]", "[[cpp-srv-sync-async]]", "[[cpp-node-class]]"]
requires: [ros2-core]
version_notes:
  - "all: Executor::spin_some(max_duration = 0) collects the work that is ready once and executes it, then returns — https://github.com/ros2/rclcpp/blob/humble/rclcpp/include/rclcpp/executor.hpp (CPP-V29)"
  - "course: the output shown for ros2 run contains launch lines ([INFO] [launch]: …) and process prefixes, which only ros2 launch prints (CPP-V18)"
---
# spin vs spin_some in rclcpp

**TL;DR** `rclcpp::spin(node)` keeps the executor processing callbacks until ROS 2 shuts down (Ctrl+C or `rclcpp::shutdown()`). `rclcpp::spin_some(node)` processes the callbacks that are ready now and returns control: inside `while (rclcpp::ok())` your own loop decides when to stop, here from a flag a callback sets. Add a short sleep to the loop, or it busy-waits.

## `src/callback_spinonce_function.cpp`
```cpp
#include <rclcpp/rclcpp.hpp>
#include <chrono>
#include <thread>
#include <vector>
#include <string>
#include <functional>

class RobotStatus : public rclcpp::Node {
public:
    RobotStatus() : Node("robot_status"),
                    time_robot_on_(0.0),
                    timer_period_(0.1),
                    main_task_period_(1.0),
                    shutdown_flag_(false),
                    robot_status_({"Robot Booting Up...", "Robot Ready...", "Robot ShuttingDown..."}) {

        timer_counter_timer_ = this->create_wall_timer(
            std::chrono::duration<double>(timer_period_),
            std::bind(&RobotStatus::timer_counter, this));

        main_task_timer_ = this->create_wall_timer(
            std::chrono::duration<double>(main_task_period_),
            std::bind(&RobotStatus::main_task, this));
    }

    void robot_message(const std::string& text, const std::string& robot_name = "Robot-1") {
        RCLCPP_INFO(this->get_logger(), "%s: %s", robot_name.c_str(), text.c_str());
    }

    void timer_counter() {
        time_robot_on_ += timer_period_;
        RCLCPP_INFO(this->get_logger(), "Updated Time Robot On=%.1f", time_robot_on_);
    }

    void main_task() {
        if (shutdown_flag_) {
            return;  // Skip the main task if shutting down
        }

        std::this_thread::sleep_for(std::chrono::seconds(10));

        if (!robot_status_.empty()) {
            std::string status = robot_status_.front();
            robot_status_.erase(robot_status_.begin());
            robot_message(status);

            if (status.find("ShuttingDown") != std::string::npos) {
                RCLCPP_INFO(this->get_logger(), "Shutting down node...");
                shutdown_flag_ = true;  // Set the shutdown flag
            } else {
                RCLCPP_INFO(this->get_logger(), "Continue....");
            }
        }
    }

    bool is_shutdown_requested() const {
        return shutdown_flag_;
    }

private:
    double time_robot_on_;
    double timer_period_;
    double main_task_period_;
    bool shutdown_flag_;
    std::vector<std::string> robot_status_;
    rclcpp::TimerBase::SharedPtr timer_counter_timer_;
    rclcpp::TimerBase::SharedPtr main_task_timer_;
};

int main(int argc, char** argv) {
    rclcpp::init(argc, argv);
    auto robot_status_node = std::make_shared<RobotStatus>();

    // Use spin_some inside a loop instead of spin
    while (rclcpp::ok()) {
        rclcpp::spin_some(robot_status_node);  // Handle callbacks
        if (robot_status_node->is_shutdown_requested()) {
            RCLCPP_INFO(robot_status_node->get_logger(), "Node has been shut down.");
            rclcpp::shutdown();  // Shutdown ROS2 client library
            break;  // Break out of the loop to end the script
        }

        // Small sleep to prevent busy waiting
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }

    return 0;
}
```
The change compared with the usual `main()` is only the loop that replaces `rclcpp::spin(robot_status_node); rclcpp::shutdown();`. Uncomment `callback_spinonce_function` in the package's CMakeLists ([[cpp-learn-unit5-callbacks]]), build and `ros2 run basics_ros2_multithreading callback_spinonce_function`:
```
[INFO] [1699961681.594387750] [robot_status]: Updated Time Robot On=0.1
...
[INFO] [1699961682.478321812] [robot_status]: Updated Time Robot On=1.0
[INFO] [1699961692.492271459] [robot_status]: Robot-1: Robot Booting Up...
[INFO] [1699961692.493165003] [robot_status]: Continue....
[INFO] [1699961692.494654214] [robot_status]: Updated Time Robot On=1.1
...
[INFO] [1699961712.521814133] [robot_status]: Robot-1: Robot ShuttingDown...
[INFO] [1699961712.522782044] [robot_status]: Shutting down node...
[INFO] [1699961712.534885406] [robot_status]: Node has been shut down.
```
The program ends by itself (no Ctrl+C). Note the 10 s gaps: `main_task()` sleeps 10 s inside its callback and `timer_counter()` waits, as in [[cpp-callbacks-functions]]. (The course's printed output is from `ros2 launch`: it shows launch lines and `[callback_spinonce_function-1]` prefixes, CPP-V18.)

## When to use which
- `spin()`: the node lives until shutdown; the normal case.
- `spin_some()` in a loop: you need control between processing rounds (check a flag, a future, do other work). Python version: [[core-exec-spin]].
- `spin_until_future_complete(node, future)`: wait for one result from `main()` ([[cpp-srv-client]]).

## Pitfalls
- Without the `sleep_for(10ms)`, `spin_some()` returns at once when nothing is ready and the loop uses a whole CPU core (CPP-V29).
- One `spin_some()` right after creating a node usually finds no message yet: the first messages need discovery time ([[cpp-learn-unit3-quiz]]).
