---
id: cpp-learn-unit2-basics
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "C++ unit 2: teleop, mars_rover_systems, heartbeat programs, exercise 2.3 temperature monitor + launch"
domain: cpp
area: learn
distro: humble
tested: false
audience: students
summary: "Course unit 2 in C++: teleop_twist_keyboard, pkg mars_rover_systems, heartbeat executables, two_rover_heartbeat launch, temperature monitor exercise and solution."
tags: [course, unit 2, mars_rover_systems, teleop_twist_keyboard, heartbeat_executable, heartbeat_executable2, temperaturemonitor_executable, start_mars_rover_systems.launch.py, students]
see: ["[[cpp-learn-start-here]]", "[[cpp-node-first-program]]", "[[cpp-node-class]]", "[[cpp-launch-cpp-nodes]]", "[[core-learn-unit2-basics]]"]
requires: [ros2-core]
version_notes: []
---
# C++ unit 2: first programs and launch

**TL;DR** The Mars rover missions of unit 2 in C++ (the Python twin: [[core-learn-unit2-basics]]). Exercise specs are exact: graders check package, file, executable and node names. Code and explanations: [[cpp-node-first-program]], [[cpp-node-class]], [[cpp-launch-cpp-nodes]], [[cpp-pkg-cmake]].

## Move the rover
`ros2 run teleop_twist_keyboard teleop_twist_keyboard` publishes keyboard presses as Twist messages; keep the focus on that terminal, Ctrl+C to quit.
```
Moving around:
   u    i    o
   j    k    l
   m    ,    .
For Holonomic mode (strafing), hold down the shift key: U I O / J K L / M < >
t : up (+z)    b : down (-z)    anything else : stop
q/z : increase/decrease max speeds by 10%
w/x : increase/decrease only linear speed by 10%
e/c : increase/decrease only angular speed by 10%
```
Programs start with `ros2 run <package_name> <executable_file>` or, several at once, `ros2 launch <package_name> <launch_file>`.

## Exercises (pkg `mars_rover_systems`, `--dependencies rclcpp`)
- **Example 2.6** `src/heartbeat.cpp` → executable `heartbeat_executable`, prints `Mars rover 1 is alive...`; later the node `mars_rover_1` and then the `HeartbeatNode` class with a 1 s timer.
- **Exercise 2.1** `src/heartbeat_shutdown.cpp` → executable `heartbeat_executable_shutdown`, prints `Shutting down Mars rover 1...`.
- **Exercise 2.2** `src/heartbeat2.cpp` → executable `heartbeat_executable2`; same program, node `mars_rover_2`. Run both and check `ros2 node list` shows `/mars_rover_1` and `/mars_rover_2`.
- **Launch**: `launch/two_rover_heartbeat.launch.py` starts `heartbeat_executable` and `heartbeat_executable2` (`output='screen'`).
- **Exercise 2.3** `src/temperature_monitor.cpp` → executable `temperaturemonitor_executable`, a custom node class (node `temperature_monitor`); random temperature between `20.0` and `100.0` °C printed every second by a timer callback; above `70.0 °C` a warning with `RCLCPP_WARN(this->get_logger(), "warning message")` instead of `RCLCPP_INFO`. Launch file `start_mars_rover_systems.launch.py` starts `heartbeat_executable` and `temperaturemonitor_executable`, each with `emulate_tty=True` to see the warning colors. Expected: warnings such as `94.97°C` > 70 °C next to the `mars_rover_1` heartbeat; `ros2 node list` adds `/mars_rover_1` and `/temperature_monitor`.

## Solution of exercise 2.3
The course's hint for random numbers in C++:
```cpp
#include <random>
// In your class constructor or somewhere appropriate:
std::random_device rd;
std::mt19937 gen(rd());
std::uniform_real_distribution<double> temp_dist(20.0, 100.0);

// To generate a random temperature:
double temperature = temp_dist(gen);
```
The solution:
```cpp
#include "rclcpp/rclcpp.hpp"
#include <chrono>
#include <string>
#include <functional>
#include <random>

class TemperatureMonitorNode : public rclcpp::Node
{
public:
    TemperatureMonitorNode(double timer_period = 1.0)
    : Node("temperature_monitor"), temperature_threshold_(70.0), rd_(), gen_(rd_()), temp_dist_(20.0, 100.0)
    {
        RCLCPP_INFO(this->get_logger(), "Temperature Monitor Node has been started.");

        // Create a timer that triggers every second (1 Hz)
        timer_ = this->create_wall_timer(
            std::chrono::milliseconds(static_cast<int>(timer_period * 1000)),
            std::bind(&TemperatureMonitorNode::monitor_temperature_callback, this));
    }

private:
    void monitor_temperature_callback(){
        double current_temperature = get_temperature();
        RCLCPP_INFO(this->get_logger(), "Current temperature: %.2f°C", current_temperature);

        if (current_temperature > temperature_threshold_) {
            RCLCPP_WARN(this->get_logger(), "Warning: High temperature detected! %.2f°C", current_temperature);
        }
    }

    double get_temperature(){
        // Simulate getting a temperature reading (in reality, this would come from a sensor)
        return temp_dist_(gen_);
    }

    double temperature_threshold_;
    rclcpp::TimerBase::SharedPtr timer_;
    std::random_device rd_;
    std::mt19937 gen_;
    std::uniform_real_distribution<double> temp_dist_;
};

int main(int argc, char** argv){
    // initialize the ROS2 communication
    rclcpp::init(argc, argv);
    // declare the node constructor
    auto node = std::make_shared<TemperatureMonitorNode>(1.0);
    // keeps the node alive, waits for a request to kill the node (ctrl+c)
    rclcpp::spin(node);
    // shutdown the ROS2 communication
    rclcpp::shutdown();
    return 0;
}
```
The initializer list names the node (`Node("temperature_monitor")`), sets the threshold (`temperature_threshold_(70.0)`), creates the random source (`rd_()`), seeds the generator from it (`gen_(rd_())`) and sets the range (`temp_dist_(20.0, 100.0)`). Members are initialized in declaration order, so `rd_` must be declared before `gen_`.
```python
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='mars_rover_systems',
            executable='heartbeat_executable',
            output='screen',
            emulate_tty=True),
        Node(
            package='mars_rover_systems',
            executable='temperaturemonitor_executable',
            output='screen',
            emulate_tty=True)
    ])
```
CMakeLists with the three executables: [[cpp-pkg-cmake]].

## Checks
- TAB twice after `ros2 run mars_rover_systems` lists the executables; a missing one was not installed or not rebuilt.
- Key takeaways of the unit: a node does one task, a callback runs when an event occurs, the executor decides when callbacks run, and timers run callbacks periodically.
