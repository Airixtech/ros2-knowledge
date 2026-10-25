---
id: tf-static-python
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "StaticTransformBroadcaster from a Python script with command-line arguments and quaternion_from_euler"
domain: tf
area: broadcast
distro: jazzy
tested: false
audience: dev
summary: "Python StaticTransformBroadcaster taking parent child x y z roll pitch yaw from sys.argv; tf_transformations.quaternion_from_euler (x,y,z,w) or a local function."
tags: [StaticTransformBroadcaster, static transform, sys.argv, tf_transformations, quaternion_from_euler, transforms3d, static_broadcaster_front_turtle_frame.py, my_front_turtle_frame, turtle_chassis]
see: ["[[tf-static-publisher]]", "[[tf-odom-broadcaster]]", "[[core-tf-broadcaster]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: tf_transformations 1.1.1 released (ros-jazzy-tf-transformations, depends on python3-transforms3d); quaternion_from_euler(ai, aj, ak, axes='sxyz') returns (x, y, z, w) — https://github.com/DLu/tf_transformations/blob/main/tf_transformations/__init__.py (TF-V23)"
  - "humble: tf_transformations 1.1.1 released too; lyrical: 1.1.1-3 — https://github.com/ros/rosdistro/blob/master/humble/distribution.yaml (TF-V23)"
  - "jazzy: the official static broadcaster tutorial computes the quaternion with its own function (no extra package) — https://github.com/ros/geometry_tutorials/blob/jazzy/turtle_tf2_py/turtle_tf2_py/static_turtle_tf2_broadcaster.py (TF-V23)"
  - "jazzy: StaticTransformBroadcaster publishes on /tf_static with TRANSIENT_LOCAL durability; late listeners get it only while the node runs (TF-V22, TF-V35)"
  - "course: 0.7 rad is about 40° (45° = 0.785 rad), the 3.1416 value is a yaw, and the assert names the course's solution package (TF-V12); the course kills this node before starting the follower (TF-V35)"
---
# StaticTransformBroadcaster from a Python script

**TL;DR** A static broadcaster in Python is the dynamic one with `StaticTransformBroadcaster` instead of `TransformBroadcaster`: send the transform once, then only spin. The frame stays valid without republishing, but late listeners receive it only while this node is alive.

## `scripts/static_broadcaster_front_turtle_frame.py`
```bash
cd ~/ros2_ws/src/my_tf_ros2_course_pkg/scripts
touch static_broadcaster_front_turtle_frame.py
chmod +x static_broadcaster_front_turtle_frame.py
```
Add it to `install(PROGRAMS …)` ([[tf-odom-broadcaster]]) and `tf_transformations` to `package.xml`.
```python
#! /usr/bin/env python3
import sys
from geometry_msgs.msg import TransformStamped
import rclpy
from rclpy.node import Node
from tf2_ros.static_transform_broadcaster import StaticTransformBroadcaster
import tf_transformations


class StaticFramePublisher(Node):

    def __init__(self):
        super().__init__('static_broadcaster_front_turtle_frame_node')

        # This line creates a `StaticTransformBroadcaster` object.
        # The `StaticTransformBroadcaster` object is used to publish static transforms between frames.
        self._tf_publisher = StaticTransformBroadcaster(self)

        # Publish static transforms once at startup
        self.make_transforms()

        self.get_logger().info("static_broadcaster_front_turtle_frame ready!")

    def make_transforms(self):
        static_transformStamped = TransformStamped()
        static_transformStamped.header.stamp = self.get_clock().now().to_msg()
        static_transformStamped.header.frame_id = sys.argv[1]
        static_transformStamped.child_frame_id = sys.argv[2]
        static_transformStamped.transform.translation.x = float(sys.argv[3])
        static_transformStamped.transform.translation.y = float(sys.argv[4])
        static_transformStamped.transform.translation.z = float(sys.argv[5])
        quat = tf_transformations.quaternion_from_euler(
            float(sys.argv[6]), float(sys.argv[7]), float(sys.argv[8]))
        static_transformStamped.transform.rotation.x = quat[0]
        static_transformStamped.transform.rotation.y = quat[1]
        static_transformStamped.transform.rotation.z = quat[2]
        static_transformStamped.transform.rotation.w = quat[3]

        self._tf_publisher.sendTransform(static_transformStamped)


def main():
    rclpy.init()
    assert len(sys.argv) > 8, "Please add all the arguments: ros2 run tf_ros2_solutions parent_frame child_frame x y z roll pitch yaw"
    node_obj = StaticFramePublisher()
    try:
        rclpy.spin(node_obj)
    except KeyboardInterrupt:
        pass

    rclpy.shutdown()


if __name__ == "__main__":
    main()
```
There is no broadcasting loop, only the spin. The usage text of the `assert` names the course's solution package; run it from yours.

## Run: a camera frame in front of the turtle
```bash
cd ~/ros2_ws && colcon build && source install/setup.bash
ros2 run my_tf_ros2_course_pkg static_broadcaster_front_turtle_frame.py turtle_chassis my_front_turtle_frame 0.4 0 0.4 0 0.7 3.1416
```
| Argument | Value | Meaning |
|---|---|---|
| parent frame | `turtle_chassis` | the frame it hangs from |
| child frame | `my_front_turtle_frame` | any name |
| X, Y, Z | 0.4, 0.0, 0.4 | 0.4 m ahead along x and 0.4 m up along z of the parent |
| roll, pitch, yaw | 0.0, 0.7, 3.1416 | pitch 0.7 rad (about 40°) looking down, yaw π (180°) to face the turtle |

The frame moves with the turtle: "static" means the parent → child transform is constant, and `turtle_chassis` itself moves.

## Without tf_transformations
`tf_transformations` is a separate package (`ros-<distro>-tf-transformations`, needs `python3-transforms3d`). The official tf2 tutorial uses a local function instead (Apache-2.0, Open Source Robotics Foundation; [static_turtle_tf2_broadcaster.py](https://github.com/ros/geometry_tutorials/blob/jazzy/turtle_tf2_py/turtle_tf2_py/static_turtle_tf2_broadcaster.py)); it returns x, y, z, w like `tf_transformations`:
```python
import math
import numpy as np


def quaternion_from_euler(ai, aj, ak):
    ai /= 2.0
    aj /= 2.0
    ak /= 2.0
    ci = math.cos(ai)
    si = math.sin(ai)
    cj = math.cos(aj)
    sj = math.sin(aj)
    ck = math.cos(ak)
    sk = math.sin(ak)
    cc = ci*ck
    cs = ci*sk
    sc = si*ck
    ss = si*sk

    q = np.empty((4, ))
    q[0] = cj*sc - sj*cs
    q[1] = cj*ss + sj*cc
    q[2] = cj*cs - sj*sc
    q[3] = cj*cc + sj*ss

    return q
```

## Pitfalls
- `ModuleNotFoundError: No module named 'tf_transformations'` → install `ros-<distro>-tf-transformations` or use the local function.
- Killing this node and then starting a listener → the listener never gets the frame (TF-V35 `[verify]`); keep it running or start it from the same launch file.
- Fewer than eight arguments → the `assert` stops the script before the node starts.
