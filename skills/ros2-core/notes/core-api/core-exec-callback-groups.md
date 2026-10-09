---
id: core-exec-callback-groups
title: "Callback groups: long callbacks & same-process deadlock"
domain: core
area: core-api
distro: humble
tested: false
audience: dev
summary: "Templates: long service that reads live sensor data, timer calling a service in the same process without deadlock; rclcpp groups."
tags: [callback group, MutuallyExclusiveCallbackGroup, MultiThreadedExecutor, deadlock, callback_group]
see: ["[[core-exec-model]]", "[[core-srv-client-async]]", "[[core-recipe-cv-bridge]]"]
requires: []
version_notes: []
---
# Callback groups: long callbacks & same-process deadlock

**TL;DR** Put the long callback and the callback that feeds it data in **different** groups, and spin a `MultiThreadedExecutor` with enough threads. The same applies to a client called from a timer in the same process.

## Template: long service + live sensor updates
```python
import rclpy
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_srvs.srv import Trigger


class Detector(Node):
    def __init__(self):
        super().__init__('detector')
        self.sensor_group = MutuallyExclusiveCallbackGroup()
        self.service_group = MutuallyExclusiveCallbackGroup()
        self.last_image = None
        self.sub = self.create_subscription(
            Image, '/camera/image_raw', self.on_image, 10, callback_group=self.sensor_group)
        self.srv = self.create_service(
            Trigger, 'detect', self.on_detect, callback_group=self.service_group)

    def on_image(self, msg):
        self.last_image = msg                  # keeps updating while on_detect runs

    def on_detect(self, request, response):
        # long loop (e.g. rotate until detection, max 10 s) reading self.last_image
        response.success = self.last_image is not None
        return response


def main(args=None):
    rclpy.init(args=args)
    node = Detector()
    executor = MultiThreadedExecutor(num_threads=2)
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
```
`callback_group=` exists on `create_subscription`, `create_timer`, `create_service`, `create_client`, `ActionServer`, `ActionClient`.

## Deadlock: timer/callback calling a service of the same process
Cause: the client response is handled by the same blocked thread or group. Fix it with either:
```python
self.cb_timer = MutuallyExclusiveCallbackGroup()
self.cb_client = MutuallyExclusiveCallbackGroup()      # different group!
self.cli = self.create_client(Trigger, 'srv', callback_group=self.cb_client)
self.timer = self.create_timer(1.0, self.on_timer, callback_group=self.cb_timer)
# + MultiThreadedExecutor; inside on_timer a blocking self.cli.call(req) is now OK
```
or a non-blocking `call_async().add_done_callback(...)` / `async def` + `await` ([[core-srv-client-async]]).

## C++
```cpp
auto group = create_callback_group(rclcpp::CallbackGroupType::MutuallyExclusive);
rclcpp::SubscriptionOptions opts; opts.callback_group = group;
sub_ = create_subscription<Image>("image", 10, cb, opts);
timer_ = create_wall_timer(100ms, cb2, other_group);
rclcpp::executors::MultiThreadedExecutor exec; exec.add_node(node); exec.spin();
```
Which combinations actually run in parallel: [[core-exec-model]].
