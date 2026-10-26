---
id: cpp-learn-inter-unit4-launch
type: reference
owner: equipo-ros2
updated: 2026-10-26
review_by: 2027-04-24
source: manual
confidentiality: internal
title: "Intermediate C++ Unit 4: python/xml/yaml main launch files, move_robot_with_arguments.cpp, namespace pitfall"
domain: cpp
area: learn
distro: humble
tested: false
audience: students
order: 14
summary: "One launch system in Python, XML and YAML: arguments, includes, namespaced group; C++ node alternating forward and turning; absolute cmd_vel."
tags: [course, unit 4, launch_tests_pkg, python_main.launch.py, xml_main.launch.xml, yaml_main.launch.yaml, PushRosNamespace, GroupAction, FindPackageShare, PathJoinSubstitution, move_robot_with_arguments.cpp, mazinger, students]
see: ["[[core-launch-xml-yaml]]", "[[core-launch-args-include]]", "[[core-launch-substitutions]]", "[[cpp-learn-inter-unit3-launch]]", "[[core-learn-inter-unit4-launch-formats]]"]
requires: [ros2-core]
version_notes:
  - "course: 'there is no equivalent tag for logging' in XML; LogInfo is exposed as <log message=…/> (YAML: - log: {message: …}) — https://github.com/ros2/launch/blob/humble/launch/launch/actions/log_info.py (CPP-V53)"
  - "course: move_with_arguments.launch.yaml starts exec 'move_robot_with_params_exe', which the package does not build; the C++ node is move_robot_with_arguments.cpp (move_robot_with_arguments_exe) — course CMakeLists (CPP-V54)"
---
# Intermediate C++ Unit 4: one launch system in three formats

**TL;DR** The same parent launch file is written in Python, XML and YAML: four arguments, an included RViz launch file, and the robot's launch file included inside a group that pushes a namespace. The C++ node alternates every second between going forward and turning, with both speeds as parameters. All formats run with `ros2 launch <package> <file> name:=value`, and can include each other. Syntax side by side: [[core-launch-xml-yaml]]; Python twin: [[core-learn-inter-unit4-launch-formats]].

## `launch/python_main.launch.py`
```python
import launch
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction, IncludeLaunchDescription, LogInfo
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import PushRosNamespace
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    package_name = 'launch_tests_pkg'

    # Declare launch arguments (can be overridden from the command line)
    turning_speed_arg = DeclareLaunchArgument('turning_speed', default_value='0.2')
    forward_speed_arg = DeclareLaunchArgument('forward_speed', default_value='0.1')
    rviz_config_file_name_arg = DeclareLaunchArgument('rviz_config_file_name', default_value='launch_part.rviz')
    custom_namespace_arg = DeclareLaunchArgument('custom_namespace', default_value='mazinger')

    turning_speed = LaunchConfiguration('turning_speed')
    forward_speed = LaunchConfiguration('forward_speed')
    rviz_config_file_name = LaunchConfiguration('rviz_config_file_name')
    custom_namespace = LaunchConfiguration('custom_namespace')

    # Print launch arguments (for debugging / teaching)
    log_args = [
        LogInfo(msg=['turning_speed: ', turning_speed]),
        LogInfo(msg=['forward_speed: ', forward_speed]),
        LogInfo(msg=['rviz_config_file_name: ', rviz_config_file_name]),
        LogInfo(msg=['custom_namespace: ', custom_namespace]),
    ]

    # Include another launch file: RViz
    start_rviz_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare(package_name),
                'launch',
                'start_rviz_with_arguments.launch.py',
            ])
        ),
        launch_arguments={
            'rviz_config_file_name': rviz_config_file_name,
        }.items(),
    )

    # Include another launch file: move robot (pushed into a namespace)
    move_robot_with_namespace_launch = GroupAction(
        actions=[
            PushRosNamespace(custom_namespace),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    PathJoinSubstitution([
                        FindPackageShare(package_name),
                        'launch',
                        'move_with_arguments.launch.py',
                    ])
                ),
                launch_arguments={
                    'turning_speed': turning_speed,
                    'forward_speed': forward_speed,
                }.items(),
            ),
        ],
    )

    return LaunchDescription([
        turning_speed_arg,
        forward_speed_arg,
        rviz_config_file_name_arg,
        custom_namespace_arg,
        *log_args,
        start_rviz_launch,
        move_robot_with_namespace_launch,
    ])
```
- `PathJoinSubstitution([FindPackageShare(package_name), 'launch', '<file>'])` builds `<package_share>/launch/<file>` at run time (e.g. `~/ros2_ws/install/launch_tests_pkg/share/launch_tests_pkg/launch/start_rviz_with_arguments.launch.py`).
- `launch_arguments={…}.items()` passes values to the child's own `DeclareLaunchArgument`s.
- `GroupAction` + `PushRosNamespace(custom_namespace)`: nodes started inside the group get the namespace, so relative topics become `/mazinger/cmd_vel`, `/mazinger/odom`.
- `*log_args` unpacks the list: `LaunchDescription` expects actions, not a list inside the list.

## `launch/start_rviz_with_arguments.launch.py` (child, used by all three formats)
```python
import launch
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

# Usage examples:
# ros2 launch launch_tests_pkg start_rviz_with_arguments.launch.py
# ros2 launch launch_tests_pkg start_rviz_with_arguments.launch.py rviz_config_file_name:=launch_part.rviz


def generate_launch_description():
    package_name = 'launch_tests_pkg'

    rviz_config_file_name = LaunchConfiguration('rviz_config_file_name')

    rviz_config_file_name_arg = DeclareLaunchArgument(
        'rviz_config_file_name',
        default_value='launch_part.rviz',
    )

    rviz_config_path = PathJoinSubstitution([
        FindPackageShare(package_name),
        'rviz_config',
        rviz_config_file_name,
    ])

    log_rviz_path = LogInfo(msg=['RViz config: ', rviz_config_path])

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz_node',
        output='screen',
        emulate_tty=True,
        parameters=[{'use_sim_time': True}],
        arguments=['-d', rviz_config_path],
    )

    return LaunchDescription([
        rviz_config_file_name_arg,
        log_rviz_path,
        rviz_node,
    ])
```

## `launch/move_with_arguments.launch.py` (child)
```python
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    turning_speed_arg = DeclareLaunchArgument("turning_speed", default_value="1.0")
    forward_speed_arg = DeclareLaunchArgument("forward_speed", default_value="1.0")

    turning_speed_f = LaunchConfiguration('turning_speed')
    forward_speed_f = LaunchConfiguration('forward_speed')

    move_robot_node = Node(
        package='launch_tests_pkg',
        executable='move_robot_with_arguments_exe',
        output='screen',
        name='move_robot_node',
        emulate_tty=True,
        parameters=[{
            'turning_speed': turning_speed_f,
            'forward_speed': forward_speed_f,
        }])

    # create and return launch description object
    return LaunchDescription([
        turning_speed_arg,
        forward_speed_arg,
        move_robot_node
    ])
```
Flow: parent passes `turning_speed`, `forward_speed` → child receives them as its own arguments → the node gets them as parameters.

## `src/move_robot_with_arguments.cpp`
```cpp
#include "geometry_msgs/msg/twist.hpp"
#include "rclcpp/rclcpp.hpp"
#include <chrono>
#include <string>

using namespace std::chrono_literals;

class MoveRobot : public rclcpp::Node {
public:
  MoveRobot() : Node("move_robot_node"), mode_("turning") {
    // Declare parameters with default values
    this->declare_parameter<double>("turning_speed", 1.0);
    this->declare_parameter<double>("forward_speed", 1.0);

    // Read parameter values
    turning_speed_ = this->get_parameter("turning_speed").as_double();
    forward_speed_ = this->get_parameter("forward_speed").as_double();

    RCLCPP_INFO(this->get_logger(), "turning_speed: %.2f", turning_speed_);
    RCLCPP_INFO(this->get_logger(), "forward_speed: %.2f", forward_speed_);

    // Use relative topic name so namespaces from launch files are respected
    publisher_ =
        this->create_publisher<geometry_msgs::msg::Twist>("cmd_vel", 10);

    timer_ = this->create_wall_timer(
        1000ms, std::bind(&MoveRobot::timer_callback, this));
  }

private:
  void timer_callback() {
    if (mode_ == "turning") {
      go_forward();
      mode_ = "go_forward";
    } else {
      turn();
      mode_ = "turning";
    }
  }

  void turn() {
    twist_.linear.x = 0.0;
    twist_.angular.z = turning_speed_;
    RCLCPP_INFO(this->get_logger(), "TURNING AT SPEED ==> %.2f", turning_speed_);
    publisher_->publish(twist_);
  }

  void go_forward() {
    twist_.linear.x = forward_speed_;
    twist_.angular.z = 0.0;
    RCLCPP_INFO(this->get_logger(), "GOING FORWARD AT SPEED ==> %.2f",
                forward_speed_);
    publisher_->publish(twist_);
  }

  std::string mode_;
  double turning_speed_;
  double forward_speed_;
  geometry_msgs::msg::Twist twist_;
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
CMakeLists.txt: the unit 3.2 file ([[cpp-learn-inter-unit3-launch]]) plus `add_executable(move_robot_with_arguments_exe src/move_robot_with_arguments.cpp)`, `ament_target_dependencies(move_robot_with_arguments_exe rclcpp geometry_msgs)` and the new target in `install(TARGETS move_robot_exe move_robot_with_arguments_exe DESTINATION lib/${PROJECT_NAME})`. Build with `colcon build --symlink-install --packages-select launch_tests_pkg`.

## Run and the namespace pitfall
```bash
ros2 launch launch_tests_pkg python_main.launch.py turning_speed:=1.0 forward_speed:=0.3
```
The robot does not move: the relative `cmd_vel` became `/mazinger/cmd_vel` inside the namespaced group, and the robot listens on `/cmd_vel`. Fix: publish on the absolute name `"/cmd_vel"` (a leading `/` ignores the namespace), rebuild, relaunch; the rover now goes forward and turns in short intervals. Keeping the relative name and remapping in the launch file is the other way ([[core-launch-args-include]]).

## `launch/xml_main.launch.xml` and `launch/move_with_arguments.launch.xml`
```xml
<launch>
  <!-- Declare launch arguments -->
  <arg name="turning_speed" default="0.2"/>
  <arg name="forward_speed" default="0.1"/>
  <arg name="rviz_config_file_name" default="launch_part.rviz"/>
  <arg name="custom_namespace" default="mazinger"/>

  <!-- Include RViz launch file -->
  <include file="$(find-pkg-share launch_tests_pkg)/launch/start_rviz_with_arguments.launch.py">
    <arg name="rviz_config_file_name" value="$(var rviz_config_file_name)"/>
  </include>

  <!-- Group with explicit namespace push -->
  <group>
    <push-ros-namespace namespace="$(var custom_namespace)"/>
    <!-- Include move robot launch file -->
    <include file="$(find-pkg-share launch_tests_pkg)/launch/move_with_arguments.launch.xml">
      <arg name="turning_speed" value="$(var turning_speed)"/>
      <arg name="forward_speed" value="$(var forward_speed)"/>
    </include>
  </group>
</launch>
```
```xml
<launch>
  <!-- Declare launch arguments -->
  <arg name="turning_speed" default="0.0"/>
  <arg name="forward_speed" default="0.0"/>

  <!-- Node definition -->
  <node pkg="launch_tests_pkg" exec="move_robot_with_arguments_exe" name="move_robot_node" output="screen" emulate_tty="true">
    <!-- Parameters -->
    <param name="turning_speed" value="$(var turning_speed)"/>
    <param name="forward_speed" value="$(var forward_speed)"/>
  </node>
</launch>
```
`$(var name)` = `LaunchConfiguration('name')`, `$(find-pkg-share pkg)` = `FindPackageShare`, `<group>` + `<push-ros-namespace>` = `GroupAction` + `PushRosNamespace`. XML can log too: `<log message="turning_speed: $(var turning_speed)"/>` (the course says it cannot, CPP-V53). The XML parent includes the Python RViz file: formats mix freely. Run: `ros2 launch launch_tests_pkg xml_main.launch.xml turning_speed:=1.1 forward_speed:=0.5`.

## `launch/yaml_main.launch.yaml` and `launch/move_with_arguments.launch.yaml`
```yaml
launch:
# args that can be set from the command line or a default will be used
- arg:
    name: "turning_speed"
    default: "0.0"
- arg:
    name: "forward_speed"
    default: "0.0"
- arg:
    name: "rviz_config_file_name"
    default: "launch_part.rviz"
- arg:
    name: "custom_namespace"
    default: "crimson_typhoon"

- include:
    file: "$(find-pkg-share launch_tests_pkg)/launch/start_rviz_with_arguments.launch.py"
    arg:
      - name: "rviz_config_file_name"
        value: "$(var rviz_config_file_name)"

- group:
    - push-ros-namespace:
        namespace: "$(var custom_namespace)"
    - include:
        file: "$(find-pkg-share launch_tests_pkg)/launch/move_with_arguments.launch.yaml"
        arg:
          - name: "turning_speed"
            value: "$(var turning_speed)"
          - name: "forward_speed"
            value: "$(var forward_speed)"
```
```yaml
launch:
# args that can be set from the command line or a default will be used
- arg:
    name: "turning_speed"
    default: "0.0"
- arg:
    name: "forward_speed"
    default: "0.0"

- node:
    pkg: "launch_tests_pkg"
    exec: "move_robot_with_arguments_exe"   # CPP-V54: the course writes move_robot_with_params_exe
    name: "move_robot_node"
    param:
      - name: "turning_speed"
        value: "$(var turning_speed)"
      - name: "forward_speed"
        value: "$(var forward_speed)"
```
The export collapsed both YAML files into single lines; the nesting above follows the official YAML launch examples. Run: `ros2 launch launch_tests_pkg yaml_main.launch.yaml turning_speed:=1.0 forward_speed:=1.0 rviz_config_file_name:=launch_part_2.rviz`. `launch_part_2.rviz` does not exist yet, so RViz opens unconfigured: set it up (the course changes the fixed frame and the laser points' colour and size) and save it under that name.
