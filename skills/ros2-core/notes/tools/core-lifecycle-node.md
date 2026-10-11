---
id: core-lifecycle-node
type: reference
owner: equipo-ros2
updated: 2026-10-09
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "Lifecycle node implementation (rclpy & rclcpp)"
domain: core
area: tools
distro: humble
tested: false
audience: dev
summary: "rclpy.lifecycle LifecycleNode with lifecycle publisher and transition callbacks; rclcpp_lifecycle equivalent."
tags: [lifecycle, rclpy.lifecycle, LifecycleNode, create_lifecycle_publisher, rclcpp_lifecycle, TransitionCallbackReturn]
see: ["[[core-lifecycle-concepts]]", "[[core-node-skeleton]]"]
requires: []
version_notes: []
---
# Lifecycle node implementation (rclpy & rclcpp)

**TL;DR** Subclass `rclpy.lifecycle.Node` (new in Humble) or `rclcpp_lifecycle::LifecycleNode`. Return `SUCCESS` from each `on_*` callback. Call the parent's `on_activate`/`on_deactivate` so lifecycle publishers get enabled or disabled.

## Python (rclpy.lifecycle, Humble)
```python
import rclpy
from rclpy.lifecycle import Node as LifecycleNode
from rclpy.lifecycle import State, TransitionCallbackReturn
from std_msgs.msg import String


class LcTalker(LifecycleNode):
    def __init__(self):
        super().__init__('lc_talker')
        self._pub = None
        self._timer = None

    def on_configure(self, state: State) -> TransitionCallbackReturn:
        self._pub = self.create_lifecycle_publisher(String, 'lifecycle_chatter', 10)
        self._timer = self.create_timer(1.0, self.publish)
        return TransitionCallbackReturn.SUCCESS

    def on_activate(self, state: State) -> TransitionCallbackReturn:
        return super().on_activate(state)            # activates lifecycle publishers

    def on_deactivate(self, state: State) -> TransitionCallbackReturn:
        return super().on_deactivate(state)

    def on_cleanup(self, state: State) -> TransitionCallbackReturn:
        self.destroy_timer(self._timer)
        self.destroy_publisher(self._pub)
        return TransitionCallbackReturn.SUCCESS

    def on_shutdown(self, state: State) -> TransitionCallbackReturn:
        return TransitionCallbackReturn.SUCCESS

    def publish(self):
        if self._pub is not None and self._pub.is_activated:
            self._pub.publish(String(data='hello'))


def main(args=None):
    rclpy.init(args=args)
    node = LcTalker()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
```

## C++ (rclcpp_lifecycle)
```cpp
using CallbackReturn = rclcpp_lifecycle::node_interfaces::LifecycleNodeInterface::CallbackReturn;
class Cam : public rclcpp_lifecycle::LifecycleNode {
public:
  Cam() : LifecycleNode("cam_driver") {}
  CallbackReturn on_configure(const rclcpp_lifecycle::State &) override {
    pub_ = create_publisher<sensor_msgs::msg::Image>("image", 10); return CallbackReturn::SUCCESS; }
  CallbackReturn on_activate(const rclcpp_lifecycle::State & s) override {
    LifecycleNode::on_activate(s); timer_ = create_wall_timer(33ms, [this]{ publish(); });
    return CallbackReturn::SUCCESS; }
  CallbackReturn on_deactivate(const rclcpp_lifecycle::State & s) override {
    timer_.reset(); LifecycleNode::on_deactivate(s); return CallbackReturn::SUCCESS; }
  CallbackReturn on_cleanup(const rclcpp_lifecycle::State &) override {
    pub_.reset(); return CallbackReturn::SUCCESS; }
  // ...
};
```
Rule: configure allocates · activate starts · deactivate stops (keeps) · cleanup frees. Driving the transitions: [[core-lifecycle-concepts]].

## Pitfalls
- The node starts **unconfigured**: nothing publishes until someone runs configure + activate (CLI, launch or lifecycle_manager).
- Overriding `on_activate` without calling the parent keeps lifecycle publishers inactive, so `publish()` does nothing.
