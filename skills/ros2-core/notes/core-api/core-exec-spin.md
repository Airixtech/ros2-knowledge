---
id: core-exec-spin
title: "Spin variants, self-exit & several nodes per process"
domain: core
area: core-api
distro: humble
tested: false
audience: dev
summary: "spin vs spin_once vs spin_until_future_complete, clean self-exit loop, init-time spin_once, several nodes in one executor."
tags: [spin, spin_once, spin_until_future_complete, executor, add_node, shutdown]
see: ["[[core-exec-model]]", "[[core-node-skeleton]]", "[[core-srv-client-async]]"]
requires: []
version_notes: []
---
# Spin variants, self-exit & several nodes per process

**TL;DR** Use `spin` to run forever, `spin_once` for a loop you control, and `spin_until_future_complete` only from `main` (never inside callbacks). Several nodes can share one executor.

## Spin variants
```python
rclpy.spin(node)                                      # forever (until shutdown)
rclpy.spin_once(node, timeout_sec=0.1)                # process ≤1 ready callback, return
rclpy.spin_until_future_complete(node, future, timeout_sec=5.0)   # NOT inside callbacks
executor.spin() / executor.spin_once(timeout_sec=0.1) / executor.spin_until_future_complete(f)
```

## Clean self-exit (the node decides when to stop)
```python
node = RobotStatus()
while rclpy.ok():
    rclpy.spin_once(node)
    if node.shutdown_flag:          # set inside a callback
        break
node.destroy_node()
rclpy.shutdown()
```
Init-time check pattern: call `rclpy.spin_once(node)` once to receive the first odom message before deciding on a goal, then `rclpy.spin(node)`.

## Several nodes in one executor (one process)
```python
plant = PlantDetectorNode()
green = GreenDetectorNode(plant)            # pass reference -> reuse plant.last_image, no extra subscription
executor = MultiThreadedExecutor(num_threads=2)
executor.add_node(plant)
executor.add_node(green)
try:
    executor.spin()
finally:
    plant.destroy_node(); green.destroy_node(); rclpy.shutdown()
```
Benefits: shared threads, fewer resources and faster intra-process data access. C++ zero-copy composition: [[core-composition]].

## Pitfalls
- `spin_once` without a timeout can block until an event arrives. Pass `timeout_sec` when the loop must stay responsive.
- `spin_until_future_complete` inside a callback deadlocks ([[core-srv-client-async]]).
