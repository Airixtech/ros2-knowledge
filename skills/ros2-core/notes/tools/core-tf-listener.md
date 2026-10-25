---
id: core-tf-listener
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "TF listener & lookup_transform (rclpy, rclcpp)"
domain: core
area: tools
distro: humble
tested: false
audience: dev
summary: "Buffer + TransformListener, lookup_transform semantics and timeout, transforming poses, rclcpp essentials with .hpp headers."
tags: [tf2, Buffer, TransformListener, lookup_transform, tf2_geometry_msgs, lookupTransform]
see: ["[[core-tf-basics]]", "[[core-tf-broadcaster]]", "[[core-message-filters]]"]
requires: []
version_notes:
  - "lyrical: tf2_ros/*.h headers deprecated and tf2/LinearMath/Quaternion.h removed (deprecated in Kilted); use .hpp (exists since Humble) — https://github.com/ros2/geometry2/tree/lyrical/tf2/include/tf2/LinearMath (V44)"
  - "jazzy: tf2_geometry_msgs.h, tf2_eigen.h etc. removed; Buffer.wait_for_transform_async returns the transform — https://docs.ros.org/en/rolling/Releases/Release-Jazzy-Jalisco.html (V44)"
  - "humble: TransformListener subscribes /tf VOLATILE and /tf_static TRANSIENT_LOCAL (depth 100) — https://github.com/ros2/geometry2/blob/humble/tf2_ros_py/tf2_ros/transform_listener.py (TF-V14, TF-V35)"
---
# TF listener & lookup_transform (rclpy, rclcpp)

**TL;DR** Create one `Buffer` + `TransformListener` and keep both alive. `lookup_transform(target, source, Time())` returns the pose of `source` expressed in `target`. Always catch `TransformException`.

## Listener (Python)
```python
import rclpy
from rclpy.duration import Duration
from rclpy.node import Node
from tf2_ros import Buffer, TransformException, TransformListener

class Lookup(Node):
    def __init__(self):
        super().__init__('tf_lookup')
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)   # keep reference
        self.timer = self.create_timer(0.1, self.on_timer)

    def on_timer(self):
        try:
            t = self.tf_buffer.lookup_transform(
                'map', 'base_link',            # target_frame, source_frame
                rclpy.time.Time(),             # latest available
                timeout=Duration(seconds=0.1))
        except TransformException as e:
            self.get_logger().warning(f'no transform: {e}', throttle_duration_sec=2.0)
            return
        self.get_logger().info(f'x={t.transform.translation.x:.2f}')
```
`lookup_transform(target, source, time)` returns the pose of `source` expressed in `target`: "where is `source` with respect to `target` right now?" when `time` is `Time()`. The listener subscribes `/tf` (volatile) and `/tf_static` (transient local, depth 100): a node only knows the dynamic transforms published since it started, but receives static ones published earlier, as long as their publisher still runs. To transform a point or pose: `import tf2_geometry_msgs`, then `self.tf_buffer.transform(pose_stamped, 'map')`.

## C++ essentials
```cpp
#include "tf2_ros/transform_broadcaster.hpp"
#include "tf2_ros/buffer.hpp"
#include "tf2_ros/transform_listener.hpp"
#include "tf2/LinearMath/Quaternion.hpp"
tf_buffer_ = std::make_unique<tf2_ros::Buffer>(get_clock());
tf_listener_ = std::make_shared<tf2_ros::TransformListener>(*tf_buffer_);
auto t = tf_buffer_->lookupTransform("map", "base_link", tf2::TimePointZero);
tf2::Quaternion q; q.setRPY(0, 0, yaw);   // msg: tf2::toMsg(q)
```
- Headers: `.hpp` exist in Humble and are the only safe choice up to Lyrical. [changed in Lyrical: `tf2_ros/*.h` deprecated, `tf2/LinearMath/Quaternion.h` removed]
- Quaternion order in msgs is x, y, z, w. The Eigen constructor is (w, x, y, z), so use the tf2 converters.

## Pitfalls
- A `TransformListener` that is not stored in `self` stops filling the buffer.
- Blocking lookups (long `timeout`) inside a single-threaded callback can wait for TF data that is never processed ([[core-exec-model]]).
