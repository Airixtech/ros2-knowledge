---
id: core-learn-inter-unit4-launch-formats
type: reference
owner: equipo-ros2
updated: 2026-10-14
review_by: 2027-04-12
source: manual
confidentiality: internal
title: "Intermediate Unit 4: move_robot nodes with arguments and with parameters"
domain: core
area: learn-intermediate
distro: humble
tested: false
audience: students
summary: "Unit 4 files: RViz and move launches with arguments, move_robot node reading argv vs parameters, setup.py for every launch format."
tags: [course, unit 4, launch_tests_pkg, move_robot_with_arguments, move_robot_with_params, get_parameter_value, double_value, launch arguments, students]
see: ["[[core-launch-substitutions]]", "[[core-launch-xml-yaml]]", "[[core-launch-node-arguments]]", "[[core-param-api]]"]
requires: []
version_notes:
  - "all: the course's move_robot_with_arguments.py used 'if … if …' (both branches every tick); fixed to elif — (V102)"
---
# Intermediate Unit 4: move_robot nodes with arguments and with parameters

**TL;DR** The same launch exists in Python ([[core-launch-substitutions]]: `python_main.launch.py`), XML and YAML ([[core-launch-xml-yaml]]). The Python version passes the speeds to the node as command-line **arguments**; XML and YAML pass them as **parameters**, so there are two versions of the node. Files go in `launch_tests_pkg` from [[core-learn-inter-unit3-launch]].

## Python version: included launch files
```bash
cd ~/ros2_ws/src/launch_tests_pkg
touch launch/python_main.launch.py launch/start_rviz_with_arguments.launch.py launch/move_with_arguments.launch.py
touch launch_tests_pkg/move_robot_with_arguments.py
```
`start_rviz_with_arguments.launch.py`:
```python
import os
from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.actions import LogInfo


def generate_launch_description():

    package_description = "launch_tests_pkg"

    rviz_config_file_name = LaunchConfiguration('rviz_config_file_name')

    rviz_config_file_name_arg = DeclareLaunchArgument('rviz_config_file_name', default_value='launch_part.rviz')

    global_path_to_rviz_file = PathJoinSubstitution([
        FindPackageShare(package_description),
        'rviz_config',
        rviz_config_file_name
    ])

    message_path = LogInfo(msg=global_path_to_rviz_file)

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        output='screen',
        name='rviz_node',
        parameters=[{'use_sim_time': True}],
        arguments=['-d', global_path_to_rviz_file])

    # create and return the launch description object
    return LaunchDescription(
        [
            rviz_config_file_name_arg,
            rviz_node,
            message_path
        ]
    )
```
`move_with_arguments.launch.py`:
```python
import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    turning_speed_arg = DeclareLaunchArgument(
        "turning_speed", default_value="1.0"
    )
    forward_speed_arg = DeclareLaunchArgument(
        "forward_speed", default_value="1.0"
    )

    turning_speed_f = LaunchConfiguration('turning_speed')
    forward_speed_f = LaunchConfiguration('forward_speed')

    move_robot_node = Node(
        package='launch_tests_pkg',
        executable='move_robot_with_arguments_exe',
        output='screen',
        name='move_robot_node',
        emulate_tty=True,
        arguments=["-turning_speed", turning_speed_f,
                   "-forward_speed", forward_speed_f,
                   ]
    )

    # create and return launch description object
    return LaunchDescription(
        [
            turning_speed_arg,
            forward_speed_arg,
            move_robot_node
        ]
    )
```

## Node with arguments (`move_robot_with_arguments.py`)
```python
import rclpy
# import the ROS2 python libraries
from rclpy.node import Node
# import the Twist module from geometry_msgs interface
from geometry_msgs.msg import Twist
import argparse


class MoveRobot(Node):

    def __init__(self, args):
        super().__init__('test')
        self.argument_parsing(args)
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        self.cmd = Twist()
        self.timer_period = 1.0
        self.mode = "turning"
        self.create_timer(self.timer_period, self.timer_callback)

    def argument_parsing(self, args):
        parser = argparse.ArgumentParser(description='Dummy Example for Arguments use')
        parser.add_argument('-turning_speed',
                            type=float,
                            metavar='1.0',
                            default=1.0,
                            help="The Turning speed in radians per second")
        parser.add_argument('-forward_speed',
                            type=float,
                            metavar='1.0',
                            default=1.0,
                            help="The Move Forward speed in meters per second")
        self.args = parser.parse_args(args[1:])

    def timer_callback(self):
        """
        Change the mode each time this callback is triggered.
        """
        if self.mode == "turning":
            self.go_forwards()
            self.mode = "go_forward"
        elif self.mode == "go_forward":
            self.turn()
            self.mode = "turning"
        else:
            pass

    def turn(self):
        self.cmd.linear.x = 0.0
        self.cmd.angular.z = self.args.turning_speed
        self.get_logger().info("TURNING...."+str(self.cmd.angular.z))
        self.publisher_.publish(self.cmd)

    def go_forwards(self):
        self.cmd.linear.x = self.args.forward_speed
        self.cmd.angular.z = 0.0
        self.get_logger().info("GOING FORWARD...."+str(self.cmd.linear.x))
        self.publisher_.publish(self.cmd)

    def stop(self):
        self.get_logger().info("STOPPING....")
        self.cmd.linear.x = 0.0
        self.cmd.angular.z = 0.0
        self.publisher_.publish(self.cmd)
        self.get_logger().info("STOPPED")

    def __del__(self):
        self.stop()


def main(args=None):
    rclpy.init(args=args)
    print("args==="+str(args))
    args_without_ros = rclpy.utilities.remove_ros_args(args)
    print("clean ROS args==="+str(args_without_ros))
    try:
        move_robot_node = MoveRobot(args_without_ros)
        rclpy.spin(move_robot_node)
        move_robot_node.destroy_node()
        rclpy.shutdown()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
```
The course version used two `if` in `timer_callback`: both ran on every tick and the robot only turned. With `elif` it alternates.

## Node with parameters (`move_robot_with_params.py`, for XML and YAML)
Same class without argparse; `__init__` and the getters change:
```python
    def __init__(self):
        super().__init__('test')
        self.declare_parameter('turning_speed', 0.1)
        self.declare_parameter('forward_speed', 0.1)
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        self.cmd = Twist()
        self.getting_params()
        self.timer_period = 1.0
        self.mode = "turning"
        self.create_timer(self.timer_period, self.timer_callback)

    def getting_params(self):
        self.turning_speed = self.get_parameter('turning_speed').get_parameter_value().double_value
        self.forward_speed = self.get_parameter('forward_speed').get_parameter_value().double_value
        self.get_logger().info("############### turning_speed...."+str(self.turning_speed))
        self.get_logger().info("############### forward_speed...."+str(self.forward_speed))
```
`turn()` and `go_forwards()` use `self.turning_speed` / `self.forward_speed` (log `"GOING FORWARDS...."`), and `main()` builds `MoveRobot()` without arguments. Declare each parameter with a default value: without it Humble warns, and Lyrical refuses it ([[core-param-api]]). Typed read: `get_parameter('NAME').get_parameter_value().double_value` (also `bool_value`, `string_value`, `integer_value`), or simply `.value`.

## setup.py changes
Install every file of `launch/` (Python, XML, YAML) and add the entry points:
```python
        (os.path.join('share', package_name, 'launch'), glob('launch/*')),
```
```python
            'move_robot_exe = launch_tests_pkg.move_robot:main',
            'move_robot_with_arguments_exe = launch_tests_pkg.move_robot_with_arguments:main',
            'move_robot_with_params_exe = launch_tests_pkg.move_robot_with_params:main',
```

## Run
```bash
cd ~/ros2_ws/
colcon build --symlink-install --packages-select launch_tests_pkg
source install/setup.bash
# Remember to source to be able to see the 3D model
source /home/simulations/ros2_sims_ws/install/setup.bash
ros2 launch launch_tests_pkg python_main.launch.py turning_speed:=6.0 forward_speed:=0.2
```
The XML and YAML runs are in [[core-launch-xml-yaml]]. With `turning_speed:=5.0` the robot can exceed its limits: restart the simulation. For the YAML run, launch once with `rviz_config_file_name:=launch_part_2.rviz`, change the fixed frame and the laser color/size, and save the new config under that name.

## Pitfalls
- XML/YAML values like `turning_speed:=1` arrive as integers and the node fails: the parameter was declared as a double. Write `1.0`.
- The course's `__del__` stop has the same problem as in Unit 3 ([[core-learn-inter-unit3-launch]]).
