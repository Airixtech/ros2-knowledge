---
id: core-tf-broadcaster
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "TF broadcasters: dynamic & static (rclpy)"
domain: core
area: tools
distro: humble
tested: false
audience: dev
summary: "Publish odom→base_link with TransformBroadcaster at ≥50 Hz; StaticTransformBroadcaster for fixed frames; yaw→quaternion."
tags: [tf2, TransformBroadcaster, StaticTransformBroadcaster, TransformStamped, odom]
see: ["[[core-tf-basics]]", "[[core-tf-listener]]", "[[core-robot-state-publisher]]"]
requires: []
version_notes:
  - "humble: a transform computed from a message should carry that message's header.stamp; tf2_monitor shows delays as now() − stamp in its own clock — https://github.com/ros2/geometry2/blob/humble/tf2_ros/src/tf2_monitor.cpp (TF-V02, TF-V26)"
---
# TF broadcasters: dynamic & static (rclpy)

**TL;DR** Fill a `TransformStamped` (stamp = node clock, parent `frame_id`, `child_frame_id`, translation + quaternion) and call `sendTransform` from a timer. Fixed extrinsics belong in the URDF, not in broadcasters.

## Dynamic broadcaster (Python)
```python
import math
from geometry_msgs.msg import TransformStamped
from rclpy.node import Node
from tf2_ros import TransformBroadcaster

class OdomTf(Node):
    def __init__(self):
        super().__init__('odom_tf')
        self.br = TransformBroadcaster(self)
        self.timer = self.create_timer(0.02, self.broadcast)     # >= 50 Hz

    def broadcast(self):
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'odom'          # parent
        t.child_frame_id = 'base_link'      # child
        t.transform.translation.x = self.x
        t.transform.translation.y = self.y
        qx, qy, qz, qw = quaternion_from_yaw(self.yaw)
        t.transform.rotation.x, t.transform.rotation.y = qx, qy
        t.transform.rotation.z, t.transform.rotation.w = qz, qw
        self.br.sendTransform(t)

def quaternion_from_yaw(yaw):
    return (0.0, 0.0, math.sin(yaw / 2.0), math.cos(yaw / 2.0))
```

## Static
Publish once; it is latched on `/tf_static`: `from tf2_ros import StaticTransformBroadcaster` → `self.sbr = StaticTransformBroadcaster(self); self.sbr.sendTransform(t)`. Prefer putting fixed sensor extrinsics in the URDF ([[core-robot-state-publisher]]). CLI alternative: `static_transform_publisher` ([[core-tf-basics]]).

## Pitfalls
- Two nodes publishing the same transform (e.g. your node + a sim plugin or EKF) → jittering frames ([[core-tf-basics]]).
- Stamping with `time.time()` instead of the node clock → extrapolation errors under `use_sim_time` ([[core-time-timers]]).
- A transform computed from a message (odometry, a sensor) → copy that message's `header.stamp` into the transform, so data and TF share one clock; `now()` of a node without `use_sim_time` is wall time in a simulation. A complete odometry-to-TF node and `tf2_monitor`: skill ros2-tf.
