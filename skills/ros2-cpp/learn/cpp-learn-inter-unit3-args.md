---
id: cpp-learn-inter-unit3-args
type: reference
owner: equipo-ros2
updated: 2026-10-26
review_by: 2027-04-24
source: manual
confidentiality: internal
title: "Intermediate C++ Unit 3.3: launch_args_example_pkg, launch arguments passed to a C++ node as parameters"
domain: cpp
area: learn
distro: humble
tested: false
audience: students
order: 13
summary: "Dummy launch printing two arguments, start_with_arguments.launch.py passing three arguments as parameters to move_robot_with_args.cpp; CMake, runs."
tags: [course, unit 3, launch_args_example_pkg, DeclareLaunchArgument, LaunchConfiguration, LogInfo, parameters, arguments_examples_demo, move_robot_with_args.cpp, students]
see: ["[[core-launch-substitutions]]", "[[core-launch-args-include]]", "[[cpp-params-declare-get]]", "[[cpp-learn-inter-unit3-launch]]", "[[cpp-learn-inter-unit4-launch]]"]
requires: [ros2-core]
version_notes:
  - "course: the override example runs 'move_robot.launch.py', which this package does not have; its launch file is start_with_arguments.launch.py — course commands (CPP-V52)"
  - "course: 'One of them (msg) has a default value' means extra_msg — course text (CPP-V79)"
---
# Intermediate C++ Unit 3.3: launch arguments as node parameters

**TL;DR** Example 3.2 first prints two launch arguments (`extra_msg` with a default, `important_msg` required), then passes three arguments to a C++ node as ROS parameters. Three layers: `DeclareLaunchArgument` (what the user can override with `name:=value`), `LaunchConfiguration` (a placeholder resolved at run time, not the value), and `parameters=[{…}]` (initial parameter overrides of the node, not `argv`). Launch side: [[core-launch-substitutions]]; node side: [[cpp-params-declare-get]].

## Create the files
```bash
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_cmake launch_args_example_pkg --dependencies rclcpp geometry_msgs
cd ~/ros2_ws/src/launch_args_example_pkg
mkdir launch
touch launch/start_with_arguments.launch.py
touch launch/start_with_arguments_dummy.launch.py
chmod +x launch/start_with_arguments.launch.py
chmod +x launch/start_with_arguments_dummy.launch.py
touch src/move_robot_with_args.cpp
```

## `launch/start_with_arguments_dummy.launch.py`
```python
import launch

# These log actions are: https://github.com/ros2/launch/blob/master/launch/launch/actions
# Logging, for example: https://github.com/ros2/launch/blob/master/launch/launch/actions/log_info.py


def generate_launch_description():
    return launch.LaunchDescription([
        launch.actions.DeclareLaunchArgument('extra_msg', default_value='hello world'),
        launch.actions.DeclareLaunchArgument('important_msg'),
        launch.actions.LogInfo(msg=launch.substitutions.LaunchConfiguration('extra_msg')),
        launch.actions.LogInfo(msg=launch.substitutions.LaunchConfiguration('important_msg')),
    ])
```
```bash
cd ~/ros2_ws
colcon build --packages-select launch_args_example_pkg
source install/setup.bash
ros2 launch launch_args_example_pkg start_with_arguments_dummy.launch.py extra_msg:="ROS2 is Great!" important_msg:="Execute Order 66"
#   [INFO] [launch.user]: ROS2 is Great!
#   [INFO] [launch.user]: Execute Order 66
```
`extra_msg` has a default and is optional; `important_msg` has none, so launch refuses to start without it.

## `launch/start_with_arguments.launch.py`
```python
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    linear_speed_arg = DeclareLaunchArgument(
        'linear_speed',
        default_value='0.2',
        description='Linear speed of the robot'
    )
    angular_speed_arg = DeclareLaunchArgument(
        'angular_speed',
        default_value='0.8',
        description='Angular speed of the robot'
    )
    publish_rate_arg = DeclareLaunchArgument(
        'publish_rate',
        default_value='10.0',
        description='Rate at which commands are published'
    )

    linear_speed = LaunchConfiguration('linear_speed')
    angular_speed = LaunchConfiguration('angular_speed')
    publish_rate = LaunchConfiguration('publish_rate')

    log_linear = LogInfo(msg=['linear_speed: ', linear_speed])
    log_angular = LogInfo(msg=['angular_speed: ', angular_speed])
    log_rate = LogInfo(msg=['publish_rate: ', publish_rate])

    move_robot_node = Node(
        package='launch_args_example_pkg',
        executable='arguments_examples_demo',
        output='screen',
        emulate_tty=True,
        parameters=[{
            'linear_speed': linear_speed,
            'angular_speed': angular_speed,
            'publish_rate': publish_rate,
        }],
    )

    return LaunchDescription([
        linear_speed_arg,
        angular_speed_arg,
        publish_rate_arg,
        log_linear,
        log_angular,
        log_rate,
        move_robot_node,
    ])
```

## `src/move_robot_with_args.cpp`
```cpp
#include "geometry_msgs/msg/twist.hpp"
#include "rclcpp/rclcpp.hpp"
#include <algorithm>
#include <chrono>

class MoveRobot : public rclcpp::Node {
public:
  MoveRobot() : Node("move_robot_node") {
    // Declare parameters (typed, with defaults)
    this->declare_parameter<double>("linear_speed", 0.2);
    this->declare_parameter<double>("angular_speed", 0.8);
    this->declare_parameter<double>("publish_rate", 10.0);

    // Read parameters once at startup
    linear_speed_ = this->get_parameter("linear_speed").as_double();
    angular_speed_ = this->get_parameter("angular_speed").as_double();
    publish_rate_ = this->get_parameter("publish_rate").as_double();

    publisher_ =
        this->create_publisher<geometry_msgs::msg::Twist>("/cmd_vel", 10);

    // Create timer based on publish_rate
    double safe_rate = std::max(0.1, publish_rate_);
    auto period = std::chrono::duration<double>(1.0 / safe_rate);
    timer_ = this->create_wall_timer(
        std::chrono::duration_cast<std::chrono::nanoseconds>(period),
        std::bind(&MoveRobot::timer_callback, this));

    RCLCPP_INFO(this->get_logger(),
                "MoveRobot started | linear=%.2f angular=%.2f rate=%.2f Hz",
                linear_speed_, angular_speed_, publish_rate_);
  }

private:
  void timer_callback() {
    geometry_msgs::msg::Twist twist;
    twist.linear.x = linear_speed_;
    twist.angular.z = angular_speed_;
    publisher_->publish(twist);
  }

  double linear_speed_;
  double angular_speed_;
  double publish_rate_;
  rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr publisher_;
  rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char *argv[]) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<MoveRobot>());
  rclcpp::shutdown();
  return 0;
}
```
The flow on the node side: declare typed parameters with fallback defaults (0.2, 0.8, 10.0) → launch overrides are already applied when the constructor reads them → one startup snapshot in the members. A later `ros2 param set` changes nothing here; [[cpp-params-declare-get]] reads them again on every tick.

## `CMakeLists.txt`
The `ros2 pkg create` template with `install(DIRECTORY launch DESTINATION share/${PROJECT_NAME}/)` before `ament_package()`. For the dummy launch file only `find_package(rclcpp REQUIRED)` was needed; the node adds:
```cmake
find_package(geometry_msgs REQUIRED)

add_executable(arguments_examples_demo src/move_robot_with_args.cpp)
ament_target_dependencies(arguments_examples_demo rclcpp geometry_msgs)

install(TARGETS
  arguments_examples_demo
  DESTINATION lib/${PROJECT_NAME})
```
The lint block of the template is the one in [[cpp-learn-inter-unit3-launch]].

## Run
```bash
cd ~/ros2_ws
colcon build --packages-select launch_args_example_pkg
source install/setup.bash
ros2 launch launch_args_example_pkg start_with_arguments.launch.py
# Another example
ros2 launch launch_args_example_pkg start_with_arguments.launch.py linear_speed:=0.0 angular_speed:=0.0
# Another example
ros2 launch launch_args_example_pkg start_with_arguments.launch.py linear_speed:=0.3 angular_speed:=1.0 publish_rate:=5.0
```
Default run:
```
[INFO] [launch.user]: linear_speed: 0.2
[INFO] [launch.user]: angular_speed: 0.8
[INFO] [launch.user]: publish_rate: 10.0
[INFO] [arguments_examples_demo-1]: process started with pid [7493]
[arguments_examples_demo-1] [INFO] [1773932941.576426571] [move_robot_node]: MoveRobot started | linear=0.20 angular=0.80 rate=10.00 Hz
```
Overrides go on the same command (`ros2 launch launch_args_example_pkg start_with_arguments.launch.py linear_speed:=0.1 angular_speed:=1.2`, CPP-V52). `ros2 launch … --show-args` lists the three arguments with their descriptions and defaults.
