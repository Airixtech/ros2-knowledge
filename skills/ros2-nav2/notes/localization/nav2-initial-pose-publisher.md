---
id: nav2-initial-pose-publisher
title: "Initial pose from a node: /clicked_point -> /initialpose"
domain: nav2
area: localization
distro: humble
tested: false
audience: dev
summary: "rclpy node that turns RViz Publish Point (/clicked_point, PointStamped) into an AMCL initial pose on /initialpose (PoseWithCovarianceStamped)."
tags: [AMCL, initialpose, clicked_point, PoseWithCovarianceStamped, PointStamped, Publish Point, rclpy, entry_points]
see: ["[[core-nav2-python-client]]", "[[nav2-initial-pose-config]]", "[[nav2-amcl-concepts]]", "[[core-topic-pub-sub-py]]", "[[core-pkg-ament-python]]"]
requires: [ros2-core]
version_notes:
  - "humble: AMCL subscribes to 'initialpose' and strips a leading '/' from the frame_id, so '/map' also works; prefer 'map' — https://github.com/ros-navigation/navigation2/blob/humble/nav2_amcl/src/amcl_node.cpp (NAV2-V34)"
---
# Initial pose from a node: /clicked_point -> /initialpose

**TL;DR** A commercial robot cannot wait for someone to click in RViz. A node can publish the initial pose itself on `/initialpose` (`geometry_msgs/PoseWithCovarianceStamped`, frame `map`). This example takes the point from RViz's **Publish Point** tool; adapt the input to any other interface, the structure stays the same.

## localization_server/initial_pose_pub.py
```python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseWithCovarianceStamped
from geometry_msgs.msg import PointStamped


class Publisher(Node):

    def __init__(self):
        super().__init__('initial_pose_pub_node')
        self.publisher_ = self.create_publisher(PoseWithCovarianceStamped, '/initialpose', 1)
        self.subscriber_ = self.create_subscription(PointStamped, '/clicked_point', self.callback, 1)
        self.subscriber_  # prevent unused variable warning

    def callback(self, msg):
        self.get_logger().info('Received Data:\n X : %f \n Y : %f \n Z : %f' % (msg.point.x, msg.point.y, msg.point.z))
        self.publish(msg.point.x, msg.point.y)

    def publish(self, x, y):
        msg = PoseWithCovarianceStamped()
        msg.header.frame_id = 'map'  # the course used '/map'; AMCL strips the slash
        msg.pose.pose.position.x = x
        msg.pose.pose.position.y = y
        self.get_logger().info('Publishing  Initial Position  \n X= %f \n Y= %f ' % (msg.pose.pose.position.x, msg.pose.pose.position.y))
        self.publisher_.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    publisher = Publisher()
    rclpy.spin(publisher)
    publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```
The orientation is left at its default (`w = 1`, yaw 0) and the covariance at zero. For a real robot set the yaw, a stamp and a small covariance ([[core-nav2-python-client]] shows a complete version).

## Package wiring
- Put the script in `localization_server/localization_server/` and add the entry point in `setup.py` (`<package-name>.<file-name>:main`) ([[core-pkg-ament-python]]):
```python
entry_points={
    'console_scripts': [
        'initial_pose_pub = localization_server.initial_pose_pub:main',
    ],
},
```
- launch/init_robot.launch.py:
```python
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(package='localization_server', executable='initial_pose_pub', output='screen'),
    ])
```
- `colcon build --packages-select localization_server`, launch it with the localization running, then in RViz use **Publish Point** and click on the map.

## Pitfalls
- The topic is `/initialpose` (no underscore); `/initial_pose` is not read by AMCL.
- Publishing before AMCL subscribes loses the message (depth 1, volatile): wait for a subscriber or publish a few times ([[core-nav2-python-client]]).
- Points from RViz are in the RViz fixed frame: keep it `map`.
