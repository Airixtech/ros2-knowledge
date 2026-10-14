---
id: core-srv-client-async
type: reference
owner: equipo-ros2
updated: 2026-10-09
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "Service client patterns (async)"
domain: core
area: core-api
distro: humble
tested: false
audience: dev
summary: "Three rclpy client patterns (one-shot script, done-callback, async/await) and why sync calls in callbacks deadlock."
tags: [service, call_async, spin_until_future_complete, deadlock, add_done_callback, await]
see: ["[[core-srv-server]]", "[[core-exec-callback-groups]]", "[[core-exec-spin]]"]
requires: []
version_notes: []
---
# Service client patterns (async)

**TL;DR** Use `call_async()`, which returns a Future. Block on it only from `main` (pattern A). Inside a running node, use a done-callback (B) or `async def` + `await` (C). A blocking call inside a callback deadlocks.

## Client A — one-shot script (simplest, blocks main only)
```python
import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts


def main(args=None):
    rclpy.init(args=args)
    node = Node('add_client')
    cli = node.create_client(AddTwoInts, 'add_two_ints')
    while not cli.wait_for_service(timeout_sec=1.0):
        node.get_logger().info('waiting for service...')
    req = AddTwoInts.Request(a=5, b=3)
    future = cli.call_async(req)
    rclpy.spin_until_future_complete(node, future, timeout_sec=5.0)
    if future.done() and future.exception() is None:
        node.get_logger().info(f'sum = {future.result().sum}')
    else:
        node.get_logger().error(f'call failed: {future.exception()}')
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```
Equivalent course form: `future = cli.call_async(req)` then `while rclpy.ok(): rclpy.spin_once(node); if future.done(): res = future.result(); break`.

## Client B — inside a running node (non-blocking callback chain)
```python
class Caller(Node):
    def __init__(self):
        super().__init__('caller')
        self.cli = self.create_client(Trigger, '/get_robot_status')
        self.timer = self.create_timer(2.0, self.on_timer)

    def on_timer(self):
        if not self.cli.service_is_ready():
            self.get_logger().warning('service not ready', throttle_duration_sec=5.0)
            return
        future = self.cli.call_async(Trigger.Request())
        future.add_done_callback(self.on_response)     # never block inside a callback

    def on_response(self, future):
        try:
            res = future.result()
            self.get_logger().info(f'{res.success}: {res.message}')
        except Exception as e:
            self.get_logger().error(f'service call failed: {e}')
```

## Client C — `async def` callback with await
```python
    async def on_timer(self):                      # rclpy executors run coroutine callbacks
        res = await self.cli.call_async(Trigger.Request())
        self.get_logger().info(res.message)
```

## Sync vs async (critical)
- `call_async()` returns a Future immediately. It is safe and recommended (the ROS 2 default; ROS 1 was sync).
- Blocking inside a callback (`cli.call()`, `spin_until_future_complete`, `while not future.done()`) causes a **deadlock**. The response cannot be processed because the executor thread is busy. Fix: patterns B/C, or a `MultiThreadedExecutor` with the client in a separate callback group ([[core-exec-callback-groups]]).
- Call `cli.call(req)` (sync) only from a thread other than the spinning one.
