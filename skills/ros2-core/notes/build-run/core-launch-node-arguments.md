---
id: core-launch-node-arguments
type: reference
owner: equipo-ros2
updated: 2026-10-14
review_by: 2027-04-12
source: manual
confidentiality: internal
title: "Node command-line arguments from launch: argparse and remove_ros_args"
domain: core
area: build-run
distro: humble
tested: false
audience: dev
summary: "Pass non-ROS arguments to an rclpy node with Node(arguments=[...]), strip ROS args with remove_ros_args, parse with argparse."
tags: [arguments, argparse, remove_ros_args, rclpy.utilities, Node arguments, sys.argv, mutually exclusive group, nargs, metavar]
see: ["[[core-launch-substitutions]]", "[[core-param-api]]", "[[core-ros-args]]", "[[core-learn-inter-unit6-groups-demo]]"]
requires: []
version_notes:
  - "humble: name-only declare_parameter warns (Humble-Kilted); Lyrical raises TypeError — https://github.com/ros2/rclpy/blob/lyrical/rclpy/rclpy/node.py (V84)"
---
# Node command-line arguments from launch: argparse and remove_ros_args

**TL;DR** `Node(arguments=[...])` appends plain command-line arguments to the process, before `--ros-args`. In the node, `rclpy.utilities.remove_ros_args(args)` returns `sys.argv` without the ROS part, and `argparse` parses the rest (skip element 0, the executable path). For values that may change at run time prefer parameters ([[core-param-api]]).

## Launch file
```python
import launch
from launch_ros.actions import Node

# How to use Example:
# ros2 launch launch_args_example_pkg start_with_arguments.launch.py timer_period:=0.5


def generate_launch_description():
    return launch.LaunchDescription([
        launch.actions.DeclareLaunchArgument('msg_A', default_value='Tick'),
        launch.actions.DeclareLaunchArgument('msg_B', default_value='Tack'),
        launch.actions.DeclareLaunchArgument('timer_period'),
        launch.actions.LogInfo(msg=launch.substitutions.LaunchConfiguration('msg_A')),
        launch.actions.LogInfo(msg=launch.substitutions.LaunchConfiguration('msg_B')),
        launch.actions.LogInfo(msg=launch.substitutions.LaunchConfiguration('timer_period')),
        # All the arguments have to be strings. Floats will give an error of NonIterable.
        Node(
            package='launch_args_example_pkg',
            executable='arguments_examples_demo',
            output='screen',
            emulate_tty=True,
            arguments=["-name_server", "TestArgumentsDemo",
                       "-timer_period_message", launch.substitutions.LaunchConfiguration('msg_A'),
                       launch.substitutions.LaunchConfiguration('msg_B'),
                       "-timer_period", launch.substitutions.LaunchConfiguration('timer_period')]),
    ])
```

## Node (`arguments_examples.py`)
```python
import argparse

import rclpy
from rclpy.node import Node


class DummyArgumetsExample(Node):

    def __init__(self, args):
        self.timer_flag = True
        super().__init__('dummy_arguments_example')

        # More info here: https://docs.python.org/3/library/argparse.html
        parser = argparse.ArgumentParser(
            description='Dummy Example for Arguments use')

        # All the arguments in this group will only be allowed to pass one of them as argument
        source = parser.add_mutually_exclusive_group(required=True)
        source.add_argument('-file', type=str, metavar='FILE_NAME',
                            help='Load entity xml from file')
        source.add_argument('-name_server', type=str, metavar='ENTITY_NAME',
                            help='Load entity name')

        # Warning: Setting the Nargs makes the variable now a list
        parser.add_argument('-timer_period_message',
                            type=str,
                            nargs=2,
                            help='Time the service will be waiting',
                            required=True)

        # Metvar will replace the default NAME_OF_ARGUMENT with the value shown in the command parser.print_help()
        parser.add_argument('-timer_period',
                            type=float,
                            metavar='TIMEOUT',
                            default=1.0,
                            help="Time period of the callback for timer")

        self.args = parser.parse_args(args[1:])

        # Check length of timer period message is 2
        assert len(self.args.timer_period_message) >= 2, "You have to place two words"

        parser.print_help()

        self.timer = self.create_timer(float(self.args.timer_period), self.timer_callback)

    def timer_callback(self):
        self.print_dummy_msgs()

    def print_dummy_msgs(self):
        if self.timer_flag:
            self.get_logger().info(self.get_source_name()+"---"+self.args.timer_period_message[0])
            self.timer_flag = False
        else:
            self.get_logger().info(self.get_source_name()+"---"+self.args.timer_period_message[1])
            self.timer_flag = True

    def get_source_name(self):
        # -file and -name_server are mutually exclusive: return the one that was given
        return self.args.file or self.args.name_server


def main(args=None):
    # initialize the ROS communication
    rclpy.init(args=args)
    print("args==="+str(args))
    # format the arguments given through ROS to use the arguments
    args_without_ros = rclpy.utilities.remove_ros_args(args)
    print("clean ROS args==="+str(args_without_ros))
    dummy_args_node = DummyArgumetsExample(args_without_ros)
    dummy_args_node.get_logger().info(" Started")
    # parser the program execution and wait for a request to kill the node (ctrl+c)
    rclpy.spin(dummy_args_node)
    # shutdown the ROS communication
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```
Entry point in `setup.py`: `'arguments_examples_demo = launch_args_example_pkg.arguments_examples:main'`.

## What the node receives
```bash
cd ~/ros2_ws
colcon build --packages-select launch_args_example_pkg
source install/setup.bash
ros2 launch launch_args_example_pkg start_with_arguments.launch.py timer_period:=0.5
# Another example
ros2 launch launch_args_example_pkg start_with_arguments.launch.py msg_A:="Sith" msg_B:="Jedi" timer_period:=1.0
```
```text
clean ROS args===['/home/user/ros2_ws/install/launch_args_example_pkg/lib/launch_args_example_pkg/arguments_examples_demo', '-name_server', 'TestArgumentsDemo', '-timer_period_message', 'Sith', 'Jedi', '-timer_period', '1.0']
self.args===['-name_server', 'TestArgumentsDemo', '-timer_period_message', 'Sith', 'Jedi', '-timer_period', '1.0']
[arguments_examples_demo-1] [INFO] [1642516507.539556966] [dummy_arguments_example]: TestArgumentsDemo---Sith
[arguments_examples_demo-1] [INFO] [1642516508.539690047] [dummy_arguments_example]: TestArgumentsDemo---Jedi
```
`args` is `None` in `main()`: `remove_ros_args(None)` reads `sys.argv`. `parser.print_help()` prints the usage, with `metavar` (`TIMEOUT`, `FILE_NAME`) instead of the upper-case argument name.

## argparse in one table
| Call | Effect |
|---|---|
| `add_mutually_exclusive_group(required=True)` | exactly one argument of the group must be given |
| `nargs=2` | the value becomes a list of 2 items (`args.x[0]`, `args.x[1]`) |
| `metavar='TIMEOUT'` | name shown in the help only |
| `type=float`, `default=1.0` | conversion and default |

## Pitfalls
- Do not name a method `get_name()` in a Node subclass: it hides `Node.get_name()` (the node's own name).
- Plain arguments cannot change while the node runs and do not show in `ros2 param list`; that is what parameters are for ([[core-param-api]]).
