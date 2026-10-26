---
id: cpp-learn-inter-unit3-launch
type: reference
owner: equipo-ros2
updated: 2026-10-26
review_by: 2027-04-24
source: manual
confidentiality: internal
title: "Intermediate C++ Unit 3.2: launch_tests_pkg with move_robot.cpp and a main launch file that includes two others"
domain: cpp
area: learn
distro: humble
tested: false
audience: students
order: 12
summary: "launch_tests_pkg: move_robot.cpp turning node, move.launch.py, start_rviz.launch.py with LogInfo, main.launch.py including both, CMakeLists, run."
tags: [course, unit 3, launch_tests_pkg, move_robot.cpp, move_robot_exe, IncludeLaunchDescription, PythonLaunchDescriptionSource, LogInfo, rviz_config, launch_part.rviz, students]
see: ["[[core-launch-args-include]]", "[[core-launch-basics]]", "[[cpp-launch-cpp-nodes]]", "[[cpp-learn-inter-unit3-args]]", "[[core-learn-inter-unit3-launch]]"]
requires: [ros2-core]
version_notes:
  - "course: the notes point at 'this->timer_->cancel();' inside timer_callback(), but the listed move_robot.cpp has no such line; adding it as the first line makes the callback run once — course code (CPP-V51)"
---
# Intermediate C++ Unit 3.2: nested launch files

**TL;DR** Example 3.1 builds `launch_tests_pkg`: a C++ node that turns the rover, one launch file that starts it, one that starts RViz with a saved config and prints its path with `LogInfo`, and `main.launch.py`, which includes both with `IncludeLaunchDescription(PythonLaunchDescriptionSource(path))`. How includes and `LogInfo` work: [[core-launch-args-include]], [[core-launch-basics]].

## Create the package
```bash
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_cmake launch_tests_pkg --dependencies rclcpp geometry_msgs
cd ~/ros2_ws/src/launch_tests_pkg
mkdir launch
touch launch/main.launch.py
touch launch/move.launch.py
touch launch/start_rviz.launch.py
touch src/move_robot.cpp
mkdir rviz_config
```

## `src/move_robot.cpp`
```cpp
#include "geometry_msgs/msg/twist.hpp"
#include "rclcpp/rclcpp.hpp"
#include <chrono>
#include <thread>

using namespace std::chrono_literals;

class MoveRobot : public rclcpp::Node {
public:
  MoveRobot() : Node("move_robot_node") {
    publisher_ =
        this->create_publisher<geometry_msgs::msg::Twist>("/cmd_vel", 10);
    timer_ = this->create_wall_timer(
        1000ms, std::bind(&MoveRobot::timer_callback, this));
  }

  void timer_callback() { this->main_logic(); }

  void turn() {
    RCLCPP_INFO(this->get_logger(), "TURNING....");
    twist.linear.x = 0.5;
    twist.angular.z = 0.5;
    publisher_->publish(twist);
  }

  void main_logic() { turn(); }

private:
  geometry_msgs::msg::Twist twist;
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
`this->timer_->cancel();` as the first line of `timer_callback()` would make it run only once; the course mentions that line, but the file above does not have it (CPP-V51).

## `launch/move.launch.py`
```python
#!/usr/bin/env python3
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    move_robot_node = Node(
        package='launch_tests_pkg',
        executable='move_robot_exe',
        output='screen',
        name='move_robot_node',
        parameters=[{'use_sim_time': True}])

    # create and return launch description object
    return LaunchDescription([move_robot_node])
```

## `launch/start_rviz.launch.py`
```python
#!/usr/bin/env python3
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
import launch


def generate_launch_description():
    # RVIZ Configuration
    rviz_config_dir = os.path.join(get_package_share_directory('launch_tests_pkg'), 'rviz_config', 'launch_part.rviz')

    # This is to publish messages inside Launch files.
    message_info = launch.actions.LogInfo(msg=str(rviz_config_dir))

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        output='screen',
        name='rviz_node',
        parameters=[{'use_sim_time': True}],
        arguments=['-d', rviz_config_dir])

    # create and return launch description object
    return LaunchDescription([rviz_node, message_info])
```
`LogInfo(msg='…')` prints through the ROS logging system at launch time; it must be in the returned `LaunchDescription`. Here it prints the config path, a quick check that the right file is loaded.

## `launch/main.launch.py`
```python
#!/usr/bin/env python3
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    pkg_share = get_package_share_directory('launch_tests_pkg')
    launch_dir = os.path.join(pkg_share, 'launch')

    move_robot = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(launch_dir, 'move.launch.py')),
    )
    start_rviz = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(launch_dir, 'start_rviz.launch.py')),
    )

    return LaunchDescription([move_robot, start_rviz])
```
General form: `name = IncludeLaunchDescription(PythonLaunchDescriptionSource(FULL_PATH))` for each child, all of them in the returned list. `IncludeLaunchDescription` comes from `launch.actions`, `PythonLaunchDescriptionSource` from `launch.launch_description_sources`.

## `CMakeLists.txt`
```cmake
cmake_minimum_required(VERSION 3.8)
project(launch_tests_pkg)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(geometry_msgs REQUIRED)

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

add_executable(move_robot_exe src/move_robot.cpp)
ament_target_dependencies(move_robot_exe rclcpp geometry_msgs)

install(TARGETS
  move_robot_exe
  DESTINATION lib/${PROJECT_NAME})

# Install launch files.
install(DIRECTORY
  launch
  rviz_config
  DESTINATION share/${PROJECT_NAME}/)

ament_package()
```
`install(DIRECTORY launch rviz_config …)` puts both folders in the package's share directory, where `get_package_share_directory()` finds them.

## Run
```bash
cd ~/ros2_ws
colcon build --packages-select launch_tests_pkg
source install/setup.bash
ros2 launch launch_tests_pkg main.launch.py
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"   # stop the robot
```
The robot starts moving and RViz opens after some seconds, empty the first time (`launch_part.rviz` does not exist yet). Add the displays, save the config as `rviz_config/launch_part.rviz`, build again and relaunch: RViz opens with it. The Python version of the same unit: [[core-learn-inter-unit3-launch]].
