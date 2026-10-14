---
id: core-action-server
type: reference
owner: equipo-ros2
updated: 2026-10-14
review_by: 2027-04-12
source: manual
confidentiality: internal
title: "Action server (rclpy) with feedback & cancel"
domain: core
area: communication
distro: humble
tested: false
audience: dev
summary: "rclpy ActionServer template with goal/cancel callbacks, feedback, terminal states, Reentrant group and MultiThreadedExecutor."
tags: [action, ActionServer, feedback, cancel, GoalResponse, ReentrantCallbackGroup]
see: ["[[core-action-client]]", "[[core-action-cli-status]]", "[[core-exec-callback-groups]]", "[[core-nav2-python-client]]"]
requires: []
version_notes:
  - "lyrical: action_tutorials_interfaces removed in Kilted; use example_interfaces/action/Fibonacci (feedback 'sequence') — https://github.com/ros2/demos/tree/kilted/action_tutorials (V29)"
---
# Action server (rclpy) with feedback & cancel

**TL;DR** Every `execute_cb` path must end with `succeed()`, `abort()` or `canceled()`. A `ReentrantCallbackGroup` + `MultiThreadedExecutor` lets cancel requests run while the goal executes.

## Server (Python) — feedback + cancel support
```python
import time

import rclpy
from action_tutorials_interfaces.action import Fibonacci
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node


class FibonacciServer(Node):
    def __init__(self):
        super().__init__('fibonacci_server')
        self._server = ActionServer(
            self, Fibonacci, 'fibonacci',
            execute_callback=self.execute_cb,
            goal_callback=self.goal_cb,              # optional: accept/reject
            cancel_callback=self.cancel_cb,          # optional: accept/reject cancel
            callback_group=ReentrantCallbackGroup())  # lets cancel requests run during execute

    def goal_cb(self, goal_request):
        return GoalResponse.ACCEPT if goal_request.order > 0 else GoalResponse.REJECT

    def cancel_cb(self, goal_handle):
        return CancelResponse.ACCEPT

    def execute_cb(self, goal_handle):
        feedback = Fibonacci.Feedback()
        feedback.partial_sequence = [0, 1]
        for i in range(1, goal_handle.request.order):
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                return Fibonacci.Result(sequence=feedback.partial_sequence)
            feedback.partial_sequence.append(
                feedback.partial_sequence[i] + feedback.partial_sequence[i - 1])
            goal_handle.publish_feedback(feedback)
            time.sleep(0.5)                          # OK here: reentrant group + MT executor
        goal_handle.succeed()                        # ALWAYS end with succeed()/abort()/canceled()
        return Fibonacci.Result(sequence=feedback.partial_sequence)


def main(args=None):
    rclpy.init(args=args)
    node = FibonacciServer()
    executor = MultiThreadedExecutor()
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
- `execute_cb` may be `async def` and `await` other futures, e.g. a Nav2 goal ([[core-nav2-python-client]]).
- Returning without succeed/abort/canceled → rclpy logs "Goal state not set, assuming aborted" and the status is ABORTED.
- `action_tutorials_interfaces` [changed in Lyrical: removed in Kilted → `example_interfaces.action.Fibonacci`, whose feedback field is `sequence`].

## Pitfalls
- A long blocking `execute_cb` in the default group with a single-threaded executor starves cancel requests and every other callback. Use a ReentrantCallbackGroup + MultiThreadedExecutor (as above).
- Client and server must use the same interface package ([[core-iface-package]]).
