---
id: core-node-skeleton
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "Node skeleton and main() (rclpy & rclcpp)"
domain: core
area: core-api
distro: humble
tested: false
audience: dev
summary: "Canonical rclpy Node subclass with timer and safe main() shutdown; minimal rclcpp node; node-level pitfalls."
tags: [rclpy, rclcpp, Node, main, spin, ExternalShutdownException, destroy_node]
see: ["[[core-time-timers]]", "[[core-logging]]", "[[core-exec-spin]]", "[[core-ros-args]]"]
requires: []
version_notes: []
---
# Node skeleton and main() (rclpy & rclcpp)

**TL;DR** A Python node is a `Node` subclass. `main()` follows `rclpy.init` → node → `spin` inside try/except (`KeyboardInterrupt`, `ExternalShutdownException`) → `destroy_node()` → `rclpy.shutdown()` if `rclpy.ok()`.

## Canonical rclpy node (copy this)
```python
#!/usr/bin/env python3
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node


class MyNode(Node):
    def __init__(self):
        super().__init__('my_node')                      # node name (snake_case)
        self.declare_parameter('rate_hz', 10.0)
        rate = self.get_parameter('rate_hz').value
        self.timer = self.create_timer(1.0 / rate, self.on_timer)   # never time.sleep loops
        self.get_logger().info('my_node ready')

    def on_timer(self):
        now = self.get_clock().now()                     # ROS time (honors use_sim_time)
        self.get_logger().info(f'tick {now.nanoseconds}', throttle_duration_sec=2.0)


def main(args=None):
    rclpy.init(args=args)
    node = MyNode()
    try:
        rclpy.spin(node)                                 # process callbacks until shutdown
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
```
Life of a script: `rclpy.init()` → create node(s) → `spin` → `destroy_node()` → `rclpy.shutdown()`.
A minimal non-class form is only for throwaway tests: `node = rclpy.create_node('n')` or `Node('n')` inside `main`.

## C++ skeleton
```cpp
#include <chrono>
#include "rclcpp/rclcpp.hpp"
using namespace std::chrono_literals;

class MyNode : public rclcpp::Node {
public:
  MyNode() : Node("my_node") {
    timer_ = create_wall_timer(100ms, [this]() { RCLCPP_INFO(get_logger(), "tick"); });
  }
private:
  rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char ** argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<MyNode>());
  rclcpp::shutdown();
  return 0;
}
```
Build setup: [[core-pkg-ament-cmake]]. C++ nodes in depth (classes, timers and clocks, logging, launch): the ros2-cpp skill.

## Pitfalls
- Two nodes with the same name → undefined behavior. Rename one with `__node` ([[core-ros-args]]).
- Blocking work (`time.sleep`, long loops) inside a callback freezes the node ([[core-exec-model]]).
- To shut down from inside a callback, set a flag and leave a `spin_once` loop in `main` ([[core-exec-spin]]), or call `rclpy.shutdown()` (then `spin` returns).
