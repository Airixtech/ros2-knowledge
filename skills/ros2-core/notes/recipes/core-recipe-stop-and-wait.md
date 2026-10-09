---
id: core-recipe-stop-and-wait
title: "Stop on exit, bounded loops & waiting for readiness"
domain: core
area: recipes
distro: humble
tested: false
audience: dev
summary: "Publish a zero Twist on Ctrl+C (SignalHandlerOptions.NO), time-bounded loops with ROS clock, wait for subscribers/topics, teleop."
tags: [SignalHandlerOptions, Ctrl+C, stop robot, Duration, count_subscribers, teleop]
see: ["[[core-node-skeleton]]", "[[core-exec-callback-groups]]", "[[core-nav2-python-client]]"]
requires: []
version_notes: []
---
# Stop on exit, bounded loops & waiting for readiness

**TL;DR** To publish a final zero Twist on Ctrl+C, init rclpy with `SignalHandlerOptions.NO` so the context survives the signal. Bound long loops with the ROS clock. Wait for subscribers or topics before spinning, never inside callbacks.

## Stop the robot on exit (Ctrl+C)
```python
import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from rclpy.signals import SignalHandlerOptions


class MoveNode(Node):                                   # minimal example node
    def __init__(self):
        super().__init__('move_node')
        self.cmd_pub = self.create_publisher(Twist, 'cmd_vel', 10)


def main(args=None):
    rclpy.init(args=args, signal_handler_options=SignalHandlerOptions.NO)   # keep context alive on Ctrl+C
    node = MoveNode()                                   # your node; has self.cmd_pub (Twist)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.cmd_pub.publish(Twist())                    # zero velocity
    finally:
        node.destroy_node()
        rclpy.shutdown()
```
Course alternative: `signal.signal(signal.SIGINT, handler)`, where the handler publishes `Twist()`, destroys the node and calls `rclpy.shutdown()`. Manual stop: `ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{}"`.

## Time-bounded loop inside a callback (ROS clock)
```python
from rclpy.duration import Duration
start = self.get_clock().now()
while (self.get_clock().now() - start) < Duration(seconds=10) and not found:
    found = self.check(self.last_image)       # last_image must be updated by ANOTHER group (core-exec-callback-groups)
    time.sleep(0.1)
```
This only works if the callback runs in its own group with a MultiThreadedExecutor ([[core-exec-callback-groups]]).

## Wait for system readiness
```python
while self.count_subscribers('/initialpose') == 0: time.sleep(1.0)     # someone listening
names = [n for n, _ in self.get_topic_names_and_types()]                 # topic exists?
ok = '/amcl_pose' in names
```
Do this before spinning (in the constructor or `main`), not inside callbacks.

## Teleop for testing
`ros2 run teleop_twist_keyboard teleop_twist_keyboard` (`k` = stop; remap with `--ros-args -r cmd_vel:=/robot1/cmd_vel`).

## Pitfalls
- With the default signal handler, the context is already shut down inside `except KeyboardInterrupt`, so the zero Twist is never sent.
- With `SignalHandlerOptions.NO`, `rclpy.ok()` is still True after Ctrl+C, so call `rclpy.shutdown()` yourself (as above).
