---
id: core-learn-inter-unit3-launch
type: reference
owner: equipo-ros2
updated: 2026-10-14
review_by: 2027-04-12
source: manual
confidentiality: internal
title: "Intermediate Unit 3: launch_tests_pkg (move, RViz, main launch)"
domain: core
area: learn-intermediate
distro: humble
tested: false
audience: students
summary: "Unit 3 package launch_tests_pkg: move_robot node, move and RViz launch files, a main launch that includes both, setup.py."
tags: [course, unit 3, launch_tests_pkg, IncludeLaunchDescription, PythonLaunchDescriptionSource, rviz2, LogInfo, move_robot, students]
see: ["[[core-launch-args-include]]", "[[core-launch-substitutions]]", "[[core-learn-inter-unit4-launch-formats]]", "[[core-learn-inter-start-here]]"]
requires: []
version_notes:
  - "all: IncludeLaunchDescription also accepts a plain path (type picked by extension) — https://github.com/ros2/launch/blob/humble/launch/launch/actions/include_launch_description.py (V104)"
---
# Intermediate Unit 3: launch_tests_pkg (move, RViz, main launch)

**TL;DR** A main launch file starts two other launch files with `IncludeLaunchDescription(PythonLaunchDescriptionSource(<full path>))`: one moves the robot, one opens RViz with a saved config and logs its path with `LogInfo`. Technical background: [[core-launch-args-include]], [[core-launch-substitutions]].

## Create the package
```bash
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_python launch_tests_pkg --dependencies rclpy launch_ros
cd ~/ros2_ws/src/launch_tests_pkg
mkdir launch
touch launch/main.launch.py launch/move.launch.py launch/start_rviz.launch.py
touch launch_tests_pkg/move_robot.py
mkdir rviz_config
```

## launch_tests_pkg/move_robot.py
Publishes one `/cmd_vel` command that makes the robot turn.
```python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class MoveRobot(Node):

    def __init__(self):
        super().__init__('test')
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        self.cmd = Twist()
        self.turn()

    def turn(self):
        self.get_logger().info("TURNING....")
        self.cmd.linear.x = 0.5
        self.cmd.angular.z = 0.5
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
    try:
        move_robot_node = MoveRobot()
        rclpy.spin(move_robot_node)
        move_robot_node.destroy_node()
        rclpy.shutdown()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
```
`try/except KeyboardInterrupt`: Ctrl+C raises `KeyboardInterrupt`; catching it and doing nothing (`pass`) avoids a page of error messages when you stop the program.

## launch/move.launch.py
```python
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    move_robot_node = Node(
        package='launch_tests_pkg',
        executable='move_robot_exe',
        output='screen',
        name='move_robot_node',
        parameters=[{'use_sim_time': True}]
    )

    # create and return launch description object
    return LaunchDescription(
        [
            move_robot_node
        ]
    )
```

## launch/start_rviz.launch.py
```python
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
import launch


def generate_launch_description():

    # RVIZ Configuration
    rviz_config_dir = os.path.join(get_package_share_directory('launch_tests_pkg'), 'rviz_config', 'launch_part.rviz')

    # This is to publish messages inside Launch files.
    message_info = launch.actions.LogInfo(
        msg=str(rviz_config_dir))

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        output='screen',
        name='rviz_node',
        parameters=[{'use_sim_time': True}],
        arguments=['-d', rviz_config_dir])

    # create and return launch description object
    return LaunchDescription(
        [
            rviz_node,
            message_info
        ]
    )
```
`LogInfo(msg=…)` posts a message to the ROS logging system at launch time: create the action, then add it to the `LaunchDescription`.

## launch/main.launch.py
```python
#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():

    pkg_box_bot_gazebo = get_package_share_directory('launch_tests_pkg')

    move_robot = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_box_bot_gazebo, 'launch', 'move.launch.py'),
        )
    )

    start_rviz = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_box_bot_gazebo, 'launch', 'start_rviz.launch.py'),
        )
    )

    return LaunchDescription([
        move_robot,
        start_rviz,
    ])
```
`PythonLaunchDescriptionSource` (from `launch.launch_description_sources`) needs the **full path** of the file; `IncludeLaunchDescription` (from `launch.actions`) wraps it.

## setup.py
```python
from setuptools import setup
import os
from glob import glob

package_name = 'launch_tests_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'rviz_config'), glob('rviz_config/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='user',
    maintainer_email='user@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'move_robot_exe = launch_tests_pkg.move_robot:main',
        ],
    },
)
```

## Run
```bash
cd ~/ros2_ws/
colcon build --symlink-install --packages-select launch_tests_pkg
source install/setup.bash
source /home/simulations/ros2_sims_ws/install/setup.bash   # robot model for RViz
ros2 launch launch_tests_pkg main.launch.py
```
The robot starts turning and RViz opens after 15–30 s, empty the first time (`launch_part.rviz` does not exist yet). Add the displays, save the config as `rviz_config/launch_part.rviz`, rebuild and relaunch: RViz opens with it.

## Pitfalls
- `__del__` publishes the stop command when Python destroys the object, which can be after `rclpy.shutdown()`: the stop may never reach the robot. Stop the robot explicitly before shutting down.
- The node publishes a single command in `__init__`; if nothing else publishes, the robot keeps the last command.
