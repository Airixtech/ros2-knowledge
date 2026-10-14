---
id: core-learn-inter-unit6-blocking
type: reference
owner: equipo-ros2
updated: 2026-10-14
review_by: 2027-04-12
source: manual
confidentiality: internal
title: "Intermediate Unit 6: a blocking timer starves the sensor callbacks"
domain: core
area: learn-intermediate
distro: humble
tested: false
audience: students
summary: "Unit 6 example 6.1: obstacle-avoid node whose 10 s rotation inside the timer callback blocks odom and scan callbacks."
tags: [course, unit 6, exercise41_pkg, blocking callback, time.sleep, single thread, euler_from_quaternion, students]
see: ["[[core-exec-model]]", "[[core-learn-inter-unit6-executor]]", "[[core-learn-inter-unit6-exercises]]", "[[core-recipe-laserscan]]"]
requires: []
version_notes:
  - "humble: MultiThreadedExecutor() uses multiprocessing.cpu_count() threads; Jazzy counts the CPUs available to the process — https://github.com/ros2/rclpy/blob/jazzy/rclpy/rclpy/executors.py (V85)"
---
# Intermediate Unit 6: a blocking timer starves the sensor callbacks

**TL;DR** One node subscribes to `odom` and `scan` and decides in a 0.5 s timer. When an obstacle is closer than 0.5 m, the timer callback rotates for 10 s with `time.sleep()`: with the default single thread, no scan or odom callback runs meanwhile, so the decision repeats with stale data. The fix is executors plus callback groups ([[core-exec-model]], [[core-learn-inter-unit6-executor]]).

## Package
```bash
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_python exercise41_pkg --dependencies rclpy std_msgs sensor_msgs geometry_msgs nav_msgs
```

## exercise41_pkg/exercise41.py
```python
import rclpy
from rclpy.node import Node
import time
import numpy as np
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist
from rclpy.qos import ReliabilityPolicy, QoSProfile


class ControlClass(Node):

    def __init__(self, seconds_sleeping=10):
        super().__init__('sub_node')
        self._seconds_sleeping = seconds_sleeping
        self.vel_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.cmd = Twist()
        self.odom_sub = self.create_subscription(
            Odometry, 'odom', self.odom_callback, 10)
        self.scan_sub = self.create_subscription(LaserScan, 'scan', self.scan_callback, QoSProfile(
            depth=10, reliability=ReliabilityPolicy.BEST_EFFORT))
        self.timer = self.create_timer(0.5, self.timer_callback)
        self.laser_msg = LaserScan()
        self.odom_msg = Odometry()
        self.roll = 0.0
        self.pitch = 0.0
        self.yaw = 0.0

    def odom_callback(self, msg):
        self.get_logger().info("Odom CallBack")
        orientation_q = msg.pose.pose.orientation
        orientation_list = [orientation_q.x, orientation_q.y, orientation_q.z, orientation_q.w]
        (self.roll, self.pitch, self.yaw) = self.euler_from_quaternion(orientation_list)

    def scan_callback(self, msg):
        self.get_logger().info("Scan CallBack")
        self.laser_msg = msg

    def get_front_laser(self):
        return self.laser_msg.ranges[360]

    def get_yaw(self):
        return self.yaw

    def euler_from_quaternion(self, quaternion):
        """
        Converts quaternion (w in last place) to Euler roll, pitch, yaw
        quaternion = [x, y, z, w]
        Below should be replaced when porting for ROS2 Python tf_conversions is done.
        """
        x = quaternion[0]
        y = quaternion[1]
        z = quaternion[2]
        w = quaternion[3]

        sinr_cosp = 2 * (w * x + y * z)
        cosr_cosp = 1 - 2 * (x * x + y * y)
        roll = np.arctan2(sinr_cosp, cosr_cosp)

        sinp = 2 * (w * y - z * x)
        pitch = np.arcsin(sinp)

        siny_cosp = 2 * (w * z + x * y)
        cosy_cosp = 1 - 2 * (y * y + z * z)
        yaw = np.arctan2(siny_cosp, cosy_cosp)

        return roll, pitch, yaw

    def stop_robot(self):
        self.cmd.linear.x = 0.0
        self.cmd.angular.z = 0.0
        self.vel_pub.publish(self.cmd)

    def move_straight(self):
        self.cmd.linear.x = 0.08
        self.cmd.angular.z = 0.0
        self.vel_pub.publish(self.cmd)

    def rotate(self):
        self.cmd.angular.z = -0.2
        self.cmd.linear.x = 0.0
        self.vel_pub.publish(self.cmd)

        self.get_logger().info("Rotating for "+str(self._seconds_sleeping)+" seconds")
        for i in range(self._seconds_sleeping):
            self.get_logger().info("SLEEPING=="+str(i)+" seconds")
            time.sleep(1)

        self.stop_robot()

    def timer_callback(self):
        self.get_logger().info("Timer CallBack")
        try:
            self.get_logger().warning(">>>>>>>>>>>>>>RANGES Value="+str(self.laser_msg.ranges[360]))
            if not self.laser_msg.ranges[360] < 0.5:
                self.get_logger().info("MOVE STRAIGHT")
                self.move_straight()
            else:
                self.get_logger().info("STOP ROTATE")
                self.stop_robot()
                self.rotate()
        except:
            pass


def main(args=None):
    rclpy.init(args=args)
    try:
        control_node = ControlClass()
        try:
            rclpy.spin(control_node)
        finally:
            control_node.destroy_node()
    finally:
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Launch and setup
```bash
cd ~/ros2_ws/src/exercise41_pkg
mkdir launch
touch launch/exercise41_pkg_launch_file.launch.py
chmod +x launch/exercise41_pkg_launch_file.launch.py
```
```python
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='exercise41_pkg',
            executable='exercise41',
            output='screen',
            emulate_tty=True),
    ])
```
`setup.py`: install `launch/*.launch.py` and add `'exercise41 = exercise41_pkg.exercise41:main'`. Then `colcon build --packages-select exercise41_pkg`, source, and `ros2 launch exercise41_pkg exercise41_pkg_launch_file.launch.py`.

## What you see
```text
[sub_node]: Odom CallBack
[sub_node]: Scan CallBack
# Here comes the timer and gets inside the STOP ROTATE
[sub_node]: Timer CallBack
[sub_node]: >>>>>>>>>>>>>>RANGES Value=0.43359941244125366
[sub_node]: STOP ROTATE
[sub_node]: Rotating for 10 seconds
[sub_node]: SLEEPING==0 seconds ... SLEEPING==9 seconds
# When it finishes, it executes again: the sensor value is the same, the scan callback has not run yet
[sub_node]: Timer CallBack
[sub_node]: >>>>>>>>>>>>>>RANGES Value=0.43359941244125366
[sub_node]: STOP ROTATE
...
# Only now the scan callback runs and the value is updated: the timer can move straight
[sub_node]: Scan CallBack
[sub_node]: >>>>>>>>>>>>>>RANGES Value=13.314866065979004
[sub_node]: MOVE STRAIGHT
```
1. The timer callback overtakes the scan callback, which is queued behind it.
2. While the robot turns, no other callback runs. The timer runs twice in a row because its next tick was already due.
In a car this is unacceptable: sensors must keep updating while the controller acts, and the controller must stay regular; real systems stop when sensor data gets too old. You need several threads, each behaving according to its task.

Stop the robot from a shell: `ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"`; reset it: `ros2 service call /reset_world std_srvs/srv/Empty "{}"`.

## Pitfalls
- `ranges[360]` assumes the MP-400 laser; another laser has another front index ([[core-recipe-laserscan]]).
- The bare `except: pass` also hides the `IndexError` of the empty `LaserScan()` before the first scan arrives: log it instead.
