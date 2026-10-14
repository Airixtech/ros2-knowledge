---
id: core-topic-pub-sub-py
type: reference
owner: equipo-ros2
updated: 2026-10-14
review_by: 2027-04-12
source: manual
confidentiality: internal
title: "Publisher & subscriber templates (rclpy) & topic pitfalls"
domain: core
area: communication
distro: humble
tested: false
audience: dev
summary: "Complete rclpy publisher (timer + Twist) and subscriber (LaserScan, sensor QoS) nodes; queue depth, name resolution, pitfalls."
tags: [publisher, subscriber, create_publisher, create_subscription, Twist, LaserScan]
see: ["[[core-qos-policies]]", "[[core-topic-cli]]", "[[core-recipe-laserscan]]", "[[core-exec-callback-groups]]"]
requires: []
version_notes: []
---
# Publisher & subscriber templates (rclpy)

**TL;DR** `create_publisher(Type, topic, qos)` plus a timer to publish. `create_subscription(Type, topic, cb, qos)` where `cb(self, msg)` should store the message or react quickly. The publisher sets the QoS, and the subscriber must be compatible ([[core-qos-policies]]).

## Publisher (Python)
```python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class MovePublisher(Node):
    def __init__(self):
        super().__init__('move_publisher')
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)   # (type, topic, qos|depth)
        self.timer = self.create_timer(0.5, self.on_timer)         # publish periodically

    def on_timer(self):
        msg = Twist()
        msg.linear.x = 0.5          # forward m/s
        msg.angular.z = 0.5         # yaw rate rad/s (+ = left/CCW)
        self.pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = MovePublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
```
Depth `10` = a KEEP_LAST queue of 10. The oldest message is dropped if consumers lag.

## Subscriber (Python)
```python
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan


class ScanListener(Node):
    def __init__(self):
        super().__init__('scan_listener')
        self.sub = self.create_subscription(
            LaserScan, '/scan', self.on_scan, qos_profile_sensor_data)  # BEST_EFFORT matches any pub
        self.last_scan = None

    def on_scan(self, msg: LaserScan):                 # signature: (self, msg)
        self.last_scan = msg                           # store-latest pattern
        finite = [r for r in msg.ranges if msg.range_min < r < msg.range_max]
        if finite:
            self.get_logger().info(f'min: {min(finite):.2f} m', throttle_duration_sec=1.0)


def main(args=None):
    rclpy.init(args=args)
    node = ScanListener()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
```
Keep a reference (`self.sub = ...`), or the subscription is garbage-collected.
To share data between callbacks (e.g. odom + image), store the latest message in `self.x` in one callback and read it in another. A pub+sub "sense → act" node: [[core-recipe-laserscan]].

## Pitfalls
- Topic listed but `echo` silent → QoS mismatch ([[core-qos-usage]]), or the wrong domain or namespace.
- Topic names: relative names (`cmd_vel`) get the node namespace, absolute names (`/cmd_vel`) do not. Prefer relative names plus remaps.
- `inf`/`nan` in `ranges` → filter them before `min()`.
- Heavy processing in a subscription callback blocks the node. Move it to a timer or another callback group ([[core-exec-callback-groups]]).
