---
id: tf-odom-broadcaster
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "Broadcast odometry as TF: a TransformBroadcaster node in an ament_cmake package with Python scripts"
domain: tf
area: broadcast
distro: jazzy
tested: false
audience: dev
summary: "Python node subscribing nav_msgs/Odometry and broadcasting world→camera_bot_base_link with TransformBroadcaster; ament_cmake package with scripts/ and install(PROGRAMS)."
tags: [TransformBroadcaster, sendTransform, TransformStamped, nav_msgs/Odometry, odom to tf, cam_bot_odom_to_tf_pub_late_tf_fixed.py, my_tf_ros2_course_pkg, ament_cmake, install(PROGRAMS), scripts, BEST_EFFORT]
see: ["[[tf-monitor-stamps]]", "[[tf-frames-tree]]", "[[tf-static-publisher]]", "[[core-tf-broadcaster]]", "[[core-pkg-ament-cmake]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: TransformBroadcaster(node) creates a /tf publisher (depth 100) on that node; it is not a node itself — https://github.com/ros2/geometry2/blob/jazzy/tf2_ros_py/tf2_ros/transform_broadcaster.py (TF-V34)"
  - "humble: same Python API — https://github.com/ros2/geometry2/blob/humble/tf2_ros_py/tf2_ros/transform_broadcaster.py"
  - "course: the task calls this a static transform; it is dynamic, on /tf (TF-V03); its explained snippet names the callback listener_callback (TF-V04); the package lacks exec dependencies (TF-V05)"
---
# Broadcast odometry as TF

**TL;DR** When a robot publishes odometry but no transform, a small node can do it: subscribe to the `nav_msgs/msg/Odometry` topic and, for every message, send a `TransformStamped` from the fixed frame to the robot's base frame with a `TransformBroadcaster`. Stamp it with the odometry's own stamp ([[tf-monitor-stamps]]). It is a **dynamic** transform on `/tf`, sent on every message.

## Where the script lives
A Python script in an ament_cmake package: shebang, `chmod +x`, and an entry in `install(PROGRAMS ...)` ([[core-pkg-ament-cmake]]). The course package `my_tf_ros2_course_pkg`, its `CMakeLists.txt` and the dependencies its `package.xml` needs: [[tf-learn-start-here]].

## `scripts/cam_bot_odom_to_tf_pub_late_tf_fixed.py`
```python
#! /usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.qos import ReliabilityPolicy, DurabilityPolicy, QoSProfile
import tf2_ros
from geometry_msgs.msg import TransformStamped
from nav_msgs.msg import Odometry


class CamBotOdomToTF(Node):

    def __init__(self, robot_base_frame="camera_bot_base_link"):
        super().__init__('odom_to_tf_broadcaster_node')

        self._robot_base_frame = robot_base_frame

        # Create a new `TransformStamped` object.
        # A `TransformStamped` object is a ROS message that represents a transformation between two frames.
        self.transform_stamped = TransformStamped()
        # This line sets the `header.frame_id` attribute of the `TransformStamped` object.
        # The `header.frame_id` attribute specifies the frame in which the transformation is defined.
        # In this case, the transformation is defined in the `world` frame.
        self.transform_stamped.header.frame_id = "world"
        # This line sets the `child_frame_id` attribute of the `TransformStamped` object.
        # The `child_frame_id` attribute specifies the frame that is being transformed to.
        # In this case, the robot's base frame is being transformed to the `world` frame.
        self.transform_stamped.child_frame_id = self._robot_base_frame

        self.subscriber = self.create_subscription(
            Odometry,
            '/cam_bot_odom',
            self.odom_callback,
            QoSProfile(depth=1, durability=DurabilityPolicy.VOLATILE, reliability=ReliabilityPolicy.BEST_EFFORT))

        # This line creates a new `TransformBroadcaster` object.
        # A `TransformBroadcaster` object adds a /tf publisher to this node (TF-V34).
        self.br = tf2_ros.TransformBroadcaster(self)

        self.get_logger().info("odom_to_tf_broadcaster_node ready!")

    def odom_callback(self, msg):
        self.cam_bot_odom = msg
        # print the log info in the terminal
        self.get_logger().debug('Odom VALUE: "%s"' % str(self.cam_bot_odom))
        self.broadcast_new_tf()

    def broadcast_new_tf(self):
        """
        This function broadcasts a new TF message to the TF network.
        """
        # Get the current odometry data.
        time_header = self.cam_bot_odom.header
        position = self.cam_bot_odom.pose.pose.position
        orientation = self.cam_bot_odom.pose.pose.orientation

        # Set the timestamp of the TF message.
        # The timestamp of the TF message is set to the odom message time.
        self.transform_stamped.header.stamp = time_header.stamp

        # Set the translation of the TF message.
        # The translation of the TF message should be set to the current position of the robot.
        self.transform_stamped.transform.translation.x = position.x
        self.transform_stamped.transform.translation.y = position.y
        self.transform_stamped.transform.translation.z = position.z

        # Set the rotation of the TF message.
        # The rotation of the TF message should be set to the current orientation of the robot.
        self.transform_stamped.transform.rotation.x = orientation.x
        self.transform_stamped.transform.rotation.y = orientation.y
        self.transform_stamped.transform.rotation.z = orientation.z
        self.transform_stamped.transform.rotation.w = orientation.w

        # Send (broadcast) the TF message.
        self.br.sendTransform(self.transform_stamped)


def main(args=None):
    rclpy.init()
    odom_to_tf_obj = CamBotOdomToTF()
    rclpy.spin(odom_to_tf_obj)


if __name__ == '__main__':
    main()
```
The course's first version, `cam_bot_odom_to_tf_pub.py`, is the same file with `self.transform_stamped.header.stamp = self.get_clock().now().to_msg()` and without `time_header`; that stamp is the error that [[tf-monitor-stamps]] explains. The values that do not change (`frame_id`, `child_frame_id`) are set once in the constructor.

## Run
```bash
cd ~/ros2_ws && colcon build && source install/setup.bash
ros2 run my_tf_ros2_course_pkg cam_bot_odom_to_tf_pub_late_tf_fixed.py
```
`[INFO] [1677838571.448821430] [odom_to_tf_broadcaster_node]: odom_to_tf_broadcaster_node ready!` Then `world → camera_bot_base_link` appears in `rqt_tf_tree` (with an epoch-like stamp in the first version), and the Cam_bot moves in RViz with `world` as Fixed Frame. The turtle's `odom` tree is still separate until [[tf-static-publisher]] joins it.

## Pitfalls
- A transform built from data → stamp it with the data's stamp, not `now()` of a node without sim time ([[tf-monitor-stamps]]).
- Copying the explained snippet of the course → it passes `self.listener_callback`, which does not exist; the callback is `odom_callback`.
- Scripts in an ament_cmake package run only if listed in `install(PROGRAMS …)` and executable (`chmod +x`, shebang).
