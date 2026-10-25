---
id: cpp-logging
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "rclcpp logging: RCLCPP_DEBUG..FATAL, set the level in code or with --log-level, emulate_tty colors, format strings"
domain: cpp
area: basics
distro: humble
tested: false
audience: dev
summary: "RCLCPP_DEBUG/INFO/WARN/ERROR/FATAL, rcutils_logging_set_logger_level or get_logger().set_level, --ros-args --log-level, emulate_tty, printf formats and RCLCPP_INFO_STREAM."
tags: [logging, RCLCPP_DEBUG, RCLCPP_INFO, RCLCPP_WARN, RCLCPP_ERROR, RCLCPP_FATAL, RCLCPP_INFO_STREAM, rcutils_logging_set_logger_level, set_level, log-level, emulate_tty, logger_example.cpp, logs_test]
see: ["[[core-logging]]", "[[cpp-node-first-program]]", "[[cpp-launch-cpp-nodes]]", "[[cpp-learn-unit9-debugging]]"]
requires: [ros2-core]
version_notes:
  - "all: rcutils_logging_set_logger_level(name, RCUTILS_LOG_SEVERITY_DEBUG) and get_logger().set_level(rclcpp::Logger::Level::Debug) both exist in Humble; the --log-level value is case-insensitive (rcutils upper-cases it) — https://github.com/ros2/rclcpp/blob/humble/rclcpp/include/rclcpp/logger.hpp, https://github.com/ros2/rcutils/blob/humble/src/logging.c (CPP-V25)"
  - "all: RCLCPP_* pass the format string to rcutils_log, declared with a printf-format attribute: a non-literal format (ss.str().c_str()) warns with -Wformat-security [verify] — https://github.com/ros2/rcutils/blob/humble/include/rcutils/logging.h (CPP-V24)"
  - "course: the package.xml of logs_test has schematypepath=\"urn:oasis:names:tc:entity:xmlns:xml:catalog\" in its xml-model line; the attribute is schematypens=\"http://www.w3.org/2001/XMLSchema\" (harmless for the build) (CPP-V38)"
---
# rclcpp logging

**TL;DR** Five levels, `RCLCPP_DEBUG` < `RCLCPP_INFO` < `RCLCPP_WARN` < `RCLCPP_ERROR` < `RCLCPP_FATAL`, each `RCLCPP_X(logger, "printf format", args...)`. Messages below the logger level are dropped (default INFO). Set the level in code or at start with `--ros-args --log-level DEBUG`; in launch, `emulate_tty=True` keeps the colours. Python and general rules: [[core-logging]].

| Level | For |
|---|---|
| DEBUG | detailed information, during development |
| INFO | general information about what the node does |
| WARN | something unexpected happened or may happen soon |
| ERROR | an error that is not necessarily fatal for the node |
| FATAL | a severe error that will likely end the node |

## `src/logger_example.cpp` (package `logs_test`)
```cpp
#include <rclcpp/rclcpp.hpp>
#include <chrono>

using namespace std::chrono_literals;

class LogDemo : public rclcpp::Node
{
public:
    LogDemo() : Node("logger_example")
    {
        // Logger level configuration
        // Set logger level to DEBUG to see all messages
        auto ret = rcutils_logging_set_logger_level(
            this->get_logger().get_name(), RCUTILS_LOG_SEVERITY_DEBUG);
        if (ret != RCUTILS_RET_OK) {
            RCLCPP_ERROR(this->get_logger(), "Failed to set logger level");
        }

        // Create a timer with 200ms interval (0.2 seconds)
        timer_ = this->create_wall_timer(
            200ms, std::bind(&LogDemo::timer_callback, this));
    }

private:
    void timer_callback(){
        // prints a ROS2 log debugging
        RCLCPP_DEBUG(this->get_logger(), "Laser sensor detected, ready for distance measurements.");
        // prints a ROS2 log info
        RCLCPP_INFO(this->get_logger(), "All systems operational, robot ready to proceed.");
        // prints a ROS2 log warning
        RCLCPP_WARN(this->get_logger(), "Motor temperature approaching limit, monitoring closely.");
        // prints a ROS2 log error
        RCLCPP_ERROR(this->get_logger(), "Motor failure detected, unable to proceed with movement!");
        // prints a ROS2 log fatal
        RCLCPP_FATAL(this->get_logger(), "Critical error: Collision detected, emergency stop activated!");
    }

    rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char * argv[]){
    // initialize the ROS communication
    rclcpp::init(argc, argv);
    // declare the node constructor
    auto log_demo = std::make_shared<LogDemo>();
    // pause the program execution, waits for a request to kill the node (ctrl+c)
    rclcpp::spin(log_demo);
    // shutdown the ROS communication
    rclcpp::shutdown();
    return 0;
}
```
Every 0.2 s it prints the five lines: `[logger_example-1] [DEBUG] [1725464753.378706731] [logger_example]: Laser sensor detected, ready for distance measurements.` … `[FATAL] … Critical error: Collision detected, emergency stop activated!`.

CMake: `add_executable(logger_example src/logger_example.cpp)`, `ament_target_dependencies(logger_example rclcpp)`, `install(TARGETS logger_example DESTINATION lib/${PROJECT_NAME})` and `install(DIRECTORY launch DESTINATION share/${PROJECT_NAME}/)`; `package.xml` with `<depend>rclcpp</depend>` and description "ROS 2 debugging tools package with logging examples". Its xml-model line uses a wrong attribute name (`schematypepath`, CPP-V38).

## Setting the level
```cpp
// any level: RCUTILS_LOG_SEVERITY_DEBUG / _INFO / _WARN / _ERROR / _FATAL
rcutils_logging_set_logger_level("logger_name", RCUTILS_LOG_SEVERITY_WARN);
// the same through rclcpp (Humble ✓)
this->get_logger().set_level(rclcpp::Logger::Level::Warn);
```
```bash
ros2 run logs_test logger_example --ros-args --log-level DEBUG     # without changing the code; debug/DEBUG both work
```
With WARN only the WARN, ERROR and FATAL lines remain; a level set in code wins over the command line because it runs later. Rebuild after every code change.

## Colours in launch
`Node(package='logs_test', executable='logger_example', output='screen', emulate_tty=True)` (in `launch/logger_example.launch.py`) prints each level in its colour, as in a terminal ([[cpp-launch-cpp-nodes]]).

## Format strings
- `RCLCPP_INFO(logger, "%s", text.c_str())`, `%d`, `%.2f`, `%zu` (`size_t`) follow `printf`.
- Do not pass built text as the format: `RCLCPP_INFO(this->get_logger(), ss.str().c_str());` (official action tutorial, [[cpp-action-client]]) warns with `-Wformat-security` and breaks on a `%` in the text. Use `RCLCPP_INFO_STREAM(this->get_logger(), "Received feedback: " << value);` or `"%s"` (CPP-V24).

## Pitfalls
- Messages missing → the logger level is above them (DEBUG is hidden by default).
- No colours under `ros2 launch` → add `emulate_tty=True`.
