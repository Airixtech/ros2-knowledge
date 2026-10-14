---
id: core-action-client
type: reference
owner: equipo-ros2
updated: 2026-10-14
review_by: 2027-04-12
source: manual
confidentiality: internal
title: "Action client (rclpy): feedback, status, timeout-cancel"
domain: core
area: communication
distro: humble
tested: false
audience: dev
summary: "rclpy ActionClient template: send_goal_async, goal response, feedback, result status, timer-based timeout cancel."
tags: [action, ActionClient, send_goal_async, get_result_async, cancel_goal_async, GoalStatus]
see: ["[[core-action-server]]", "[[core-action-cli-status]]", "[[core-nav2-python-client]]"]
requires: []
version_notes: []
---
# Action client (rclpy): feedback, status, timeout-cancel

**TL;DR** `send_goal_async` gives a Future of a goal handle; check `accepted`. `get_result_async()` gives a Future with `.status` + `.result`. Feedback arrives via `feedback_callback`. The client never blocks.

## Client (Python)
```python
import rclpy
from action_msgs.msg import GoalStatus
from action_tutorials_interfaces.action import Fibonacci
from rclpy.action import ActionClient
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node


class FibonacciClient(Node):
    def __init__(self):
        super().__init__('fibonacci_client')
        self._client = ActionClient(self, Fibonacci, 'fibonacci')
        self._goal_handle = None
        self._start = None
        self.timeout_s = 30.0
        self._timer = self.create_timer(0.1, self.check_timeout)

    def send_goal(self, order):
        if not self._client.wait_for_server(timeout_sec=10.0):
            self.get_logger().error('action server not available')
            return False
        goal = Fibonacci.Goal(order=order)
        future = self._client.send_goal_async(goal, feedback_callback=self.on_feedback)
        future.add_done_callback(self.on_goal_response)
        return True

    def on_goal_response(self, future):
        handle = future.result()
        if not handle.accepted:
            self.get_logger().warning('goal rejected')
            rclpy.shutdown()
            return
        self._goal_handle = handle
        self._start = self.get_clock().now()
        handle.get_result_async().add_done_callback(self.on_result)

    def on_feedback(self, feedback_msg):
        self.get_logger().info(f'feedback: {feedback_msg.feedback.partial_sequence}')

    def on_result(self, future):
        wrapped = future.result()                  # .status + .result
        if wrapped.status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info(f'result: {wrapped.result.sequence}')
        elif wrapped.status == GoalStatus.STATUS_CANCELED:
            self.get_logger().warning('goal canceled')
        else:
            self.get_logger().error(f'goal ended with status {wrapped.status}')   # ABORTED=6
        rclpy.shutdown()                           # exit spin in main

    def check_timeout(self):
        if self._goal_handle is None or self._start is None:
            return
        if (self.get_clock().now() - self._start).nanoseconds / 1e9 > self.timeout_s:
            self.get_logger().warning('timeout -> cancel')
            self._goal_handle.cancel_goal_async()
            self._start = None


def main(args=None):
    rclpy.init(args=args)
    node = FibonacciClient()
    if node.send_goal(10):
        try:
            rclpy.spin(node)
        except (KeyboardInterrupt, ExternalShutdownException):
            pass
    node.destroy_node()
    if rclpy.ok():
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```
- Flow: `send_goal_async` → Future[GoalHandle] (accepted?) → `get_result_async()` → Future[(status, result)]. The feedback payload is `msg.feedback`.
- Cancel: `cancel_goal_async()` → Future. If `len(res.goals_canceling) > 0`, the cancel was accepted.
- Script style: `rclpy.spin_until_future_complete(node, send_future)`, then the same for the result future (only outside callbacks).
- Always call `wait_for_server()` before sending. Status codes: [[core-action-cli-status]].
