---
id: core-learn-inter-unit6-executor
type: reference
owner: equipo-ros2
updated: 2026-10-14
review_by: 2027-04-12
source: manual
confidentiality: internal
title: "Intermediate Unit 6: same program with an explicit executor and two nodes"
domain: core
area: learn-intermediate
distro: humble
tested: false
audience: students
summary: "Unit 6 example 6.2 (subscriber and publisher nodes in a SingleThreadedExecutor, still blocked) and exercise 6.3: three groups, MultiThreadedExecutor."
tags: [course, unit 6, exercise42, SingleThreadedExecutor, MultiThreadedExecutor, ReentrantCallbackGroup, MutuallyExclusiveCallbackGroup, num_threads, students]
see: ["[[core-exec-model]]", "[[core-exec-callback-groups]]", "[[core-learn-inter-unit6-blocking]]", "[[core-learn-inter-unit6-exercises]]"]
requires: []
version_notes:
  - "humble: MultiThreadedExecutor() uses multiprocessing.cpu_count() threads; Jazzy counts the CPUs available to the process — https://github.com/ros2/rclpy/blob/jazzy/rclpy/rclpy/executors.py (V85)"
---
# Intermediate Unit 6: same program with an explicit executor and two nodes

**TL;DR** Executors run the callbacks (SingleThreadedExecutor: in the thread that calls `spin()`; MultiThreadedExecutor: in a thread pool) and callback groups say which callbacks may run together (Reentrant: any; MutuallyExclusive: one at a time). The base class `CallbackGroup` is not used directly: a group type implements `can_execute()`, `beginning_execution()` and `ending_execution()`. Example 6.2 only makes the structure explicit: one Reentrant group but a **single** thread, so it behaves exactly like [[core-learn-inter-unit6-blocking]]. Exercise 6.3 fixes it. Rules: [[core-exec-model]].

## exercise42.py (added to `exercise41_pkg`)
```python
import rclpy
from rclpy.node import Node
import time
import numpy as np
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import SingleThreadedExecutor
from rclpy.qos import ReliabilityPolicy, QoSProfile


class SubscriberClass(Node):

    def __init__(self):
        super().__init__('sub_node')
        rclpy.logging.set_logger_level('sub_node', rclpy.logging.LoggingSeverity.DEBUG)
        self.group = ReentrantCallbackGroup()
        self.odom_sub = self.create_subscription(
            Odometry, 'odom', self.odom_callback, 10, callback_group=self.group)
        self.scan_sub = self.create_subscription(LaserScan, 'scan', self.scan_callback, QoSProfile(
            depth=10, reliability=ReliabilityPolicy.BEST_EFFORT), callback_group=self.group)
        self.timer = self.create_timer(0.5, self.timer_callback, callback_group=self.group)
        self.laser_msg = LaserScan()
        self.odom_msg = Odometry()
        self.roll = 0.0
        self.pitch = 0.0
        self.yaw = 0.0
        self.publisher = PublisherClass()

    def odom_callback(self, msg):
        self.get_logger().debug("Odom CallBack")
        orientation_q = msg.pose.pose.orientation
        orientation_list = [orientation_q.x, orientation_q.y, orientation_q.z, orientation_q.w]
        (self.roll, self.pitch, self.yaw) = self.euler_from_quaternion(orientation_list)

    def scan_callback(self, msg):
        self.get_logger().debug("Scan CallBack")
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

    def timer_callback(self):
        self.get_logger().info("Timer CallBack")
        try:
            self.get_logger().warning(">>>>>>>>>>>>>>RANGES Value="+str(self.laser_msg.ranges[360]))
            if not self.laser_msg.ranges[360] < 0.8:
                self.publisher.move_straight()
            else:
                self.publisher.stop_robot()
                self.publisher.rotate()
        except:
            pass


class PublisherClass(Node):

    def __init__(self, seconds_sleeping=10):
        super().__init__('pub_node')
        self._seconds_sleeping = seconds_sleeping
        rclpy.logging.set_logger_level('pub_node', rclpy.logging.LoggingSeverity.DEBUG)
        self.vel_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.cmd = Twist()

    def stop_robot(self):
        self.get_logger().info("Ex2 MOVE STOP")
        self.cmd.linear.x = 0.0
        self.cmd.angular.z = 0.0
        self.vel_pub.publish(self.cmd)

    def move_straight(self):
        self.get_logger().info("Ex2 MOVE STRAIGHT")
        self.cmd.linear.x = 0.15
        self.cmd.angular.z = 0.0
        self.vel_pub.publish(self.cmd)

    def rotate(self):
        self.get_logger().info("Ex2 MOVE ROTATE")
        self.cmd.angular.z = -0.2
        self.cmd.linear.x = 0.0
        self.get_logger().info("PUBLISH COMMAND...")
        self.vel_pub.publish(self.cmd)
        self.get_logger().info("PUBLISH COMMAND...FINISHED")

        self.get_logger().info("Ex2 Rotating for "+str(self._seconds_sleeping)+" seconds")
        for i in range(self._seconds_sleeping):
            self.get_logger().info("Ex2 SLEEPING=="+str(i)+" seconds")
            time.sleep(1)

        self.stop_robot()


def main(args=None):
    rclpy.init(args=args)
    try:
        subs_node = SubscriberClass()
        pub_node = PublisherClass()

        executor = SingleThreadedExecutor()
        executor.add_node(subs_node)
        executor.add_node(pub_node)

        try:
            executor.spin()
        finally:
            executor.shutdown()
            subs_node.destroy_node()
            pub_node.destroy_node()
    finally:
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```
Launch file `exercise42_pkg_launch_file.launch.py`: as in Unit 6.1 with `executable='exercise42'`; entry point `'exercise42 = exercise41_pkg.exercise42:main'`. The output is the same as in example 6.1, as expected: one thread, so nothing changed but the structure.

## Exercise 6.3
Copy `exercise42.py` to `exercise43.py`; use **three** `MutuallyExclusiveCallbackGroup`s, one per callback, and a `MultiThreadedExecutor`; add a launch file `exercise43_pkg_launch_file.launch.py` and the entry point; build, run and watch the subscribers.
```python
executor = MultiThreadedExecutor(num_threads=4)
```
```python
self.group1 = MutuallyExclusiveCallbackGroup()
self.group2 = MutuallyExclusiveCallbackGroup()
self.group3 = MutuallyExclusiveCallbackGroup()
```
Without `num_threads`, Humble uses `multiprocessing.cpu_count()` threads (`python3 -c "import multiprocessing; print(multiprocessing.cpu_count())"` → 8). Use only the threads you need: every thread costs resources, and more groups need more threads. Executor reference: [executors (humble)](https://docs.ros.org/en/humble/Concepts/Intermediate/About-Executors.html).

## Why both threads and groups
Threads are **workers**, callback groups are **conveyor belts** (queues), callbacks are the **boxes** on them.
- Several groups but one thread: one worker for three belts, working on one at a time.
- Several threads but one MutuallyExclusive group: many workers, one belt with one chair: they wait for each other.
- You need several workers **and** several belts. Use the fewest threads that keep data flowing without losses or slowdowns ([[core-learn-inter-unit6-exercises]]).

## Pitfalls
- `SubscriberClass` creates its own `PublisherClass` and `main()` creates another: two nodes named `pub_node` (`ros2 node list` warns that nodes share an exact name). Pass the same instance instead.
- Reentrant + one thread = still sequential: groups only matter with enough threads.
