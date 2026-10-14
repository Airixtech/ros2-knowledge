---
id: core-learn-inter-unit5-params
type: reference
owner: equipo-ros2
updated: 2026-10-14
review_by: 2027-04-12
source: manual
confidentiality: internal
title: "Intermediate Unit 5: param_vel node, parameter callback, exercises"
domain: core
area: learn-intermediate
distro: humble
tested: false
audience: students
summary: "Unit 5 package parameter_tests: velocity parameter with descriptor, set callback, launch with parameters, exercises 5.1 and 5.2."
tags: [course, unit 5, parameter_tests, param_vel_node, velocity, ParameterDescriptor, add_on_set_parameters_callback, exercise, students]
see: ["[[core-param-api]]", "[[core-param-yaml-cli]]", "[[core-learn-inter-start-here]]", "[[core-recipe-laserscan]]"]
requires: []
version_notes:
  - "jazzy: add_pre_set_parameters_callback / add_post_set_parameters_callback added (Iron) — https://docs.ros.org/en/rolling/Releases/Release-Iron-Irwini.html (V38)"
---
# Intermediate Unit 5: param_vel node, parameter callback, exercises

**TL;DR** `param_vel_node` declares a `velocity` parameter (double, with a description) and publishes it as `linear.x` on `cmd_vel` every 2 s, so `ros2 param set /param_vel_node velocity 0.1` moves the robot (the demo of Unit 1). The CLI session is in [[core-param-yaml-cli]], the API in [[core-param-api]].

## Package and node
```bash
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_python parameter_tests --dependencies rclpy
```
`parameter_tests/parameter_tests_node.py`, final version with the set callback (the first version is the same without the two callback parts):
```python
import rclpy
import rclpy.node
from rcl_interfaces.msg import ParameterDescriptor
from geometry_msgs.msg import Twist
from rclpy.parameter import Parameter
from rcl_interfaces.msg import SetParametersResult


class VelParam(rclpy.node.Node):

    def __init__(self):
        super().__init__('param_vel_node')
        self.timer = self.create_timer(2, self.timer_callback)
        self.publisher = self.create_publisher(Twist, 'cmd_vel', 10)
        self.msg = Twist()
        param_descriptor = ParameterDescriptor(
            description='Sets the velocity (in m/s) of the robot.')
        self.declare_parameter('velocity', 0.0, param_descriptor)
        self.add_on_set_parameters_callback(self.parameter_callback)

    def timer_callback(self):
        self.my_param = self.get_parameter('velocity').value
        self.get_logger().info('Velocity parameter is: %f' % self.my_param)
        self.msg.linear.x = self.my_param
        self.publisher.publish(self.msg)

    def parameter_callback(self, params):
        for param in params:
            if param.name == 'velocity' and param.type_ == Parameter.Type.DOUBLE:
                self.my_param = param.value
                self.get_logger().info('Velocity parameter changed!')
        return SetParametersResult(successful=True)


def main():
    rclpy.init()
    node = VelParam()
    rclpy.spin(node)


if __name__ == '__main__':
    main()
```
- `create_timer(2, …)`: the callback runs once every 2 seconds.
- `ParameterDescriptor(description=…)` is optional but documents the parameter (`ros2 param describe` shows it): useful when a node has many.
- `declare_parameter('velocity', 0.0, param_descriptor)`: name, default value, descriptor.
- `self.get_parameter('velocity').value` in the timer is what makes run-time changes take effect.
- `add_on_set_parameters_callback`: called whenever a parameter of this node is set; it can store the value, change behavior or reject the change.

Entry point: `'param_vel = parameter_tests.parameter_tests_node:main'`.
```bash
cd ~/ros2_ws
colcon build --packages-select parameter_tests
source install/setup.bash
ros2 run parameter_tests param_vel
ros2 param set /param_vel_node velocity 0.1     # Velocity parameter changed! ... is: 0.100000
ros2 param dump /param_vel_node > param_vel_node.yaml
ros2 run parameter_tests param_vel --ros-args --params-file /home/user/param_vel_node.yaml
```

## Parameters from a launch file (set at startup)
```python
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='parameter_tests',
            executable='param_vel',
            name='param_vel_node',
            output='screen',
            emulate_tty=True,
            parameters=[
                {'velocity': 0.2}
            ]
        )
    ])
```
`launch/test_parameters.launch.py`; in `setup.py`: `(os.path.join('share', package_name), glob('launch/*.launch.py'))` (the course installs it in `share/parameter_tests/`, which works because `ros2 launch` searches the whole share folder). `ros2 launch parameter_tests test_parameters.launch.py` → the robot moves at 0.2 m/s.

## Exercises
- **5.1**: a new node with two parameters, `get_laser_data` and `get_odom_data`, both `False` by default. When `True`: print the laser value right in front of the robot, and the robot's \[X, Y\]. Hint: topics `scan` and `odom` ([[core-recipe-laserscan]]).
- **5.2**: a launch file that starts the node of 5.1.

## Pitfalls
- `ros2 param set … velocity 0` fails: `0` is an integer; write `0.0`.
- Without the callback, `ros2 param set` still changes the value; the timer reads it on its next tick.
