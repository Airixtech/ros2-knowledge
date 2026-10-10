---
id: nav2-send-goal-action-client
title: "NavigateToPose action client triggered by /clicked_point"
domain: nav2
area: planning-control
distro: humble
tested: false
audience: dev
summary: "rclpy node: each RViz Publish Point (/clicked_point) becomes a NavigateToPose goal on /navigate_to_pose, with feedback and result callbacks."
tags: [NavigateToPose, ActionClient, rclpy, clicked_point, PointStamped, send_goal_async, feedback_callback, nav2_msgs]
see: ["[[core-nav2-python-client]]", "[[core-action-client]]", "[[nav2-send-goal-cli]]", "[[core-pkg-ament-python]]"]
requires: [ros2-core]
version_notes:
  - "humble: the course put theta in pose.position.z and printed 'Result: {0}'; fixed below (orientation from yaw) — https://github.com/ros-navigation/navigation2/blob/humble/nav2_msgs/action/NavigateToPose.action (NAV2-V14)"
---
# NavigateToPose action client triggered by /clicked_point

**TL;DR** Most of the time you send goals from a program: an `ActionClient` for `nav2_msgs/action/NavigateToPose` on `/navigate_to_pose`. Here a click with RViz's **Publish Point** (`/clicked_point`) becomes the goal.

## path_planner_server/nav_to_pose_action_client.py
```python
import math

import rclpy
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient
from rclpy.node import Node
from geometry_msgs.msg import PointStamped


class NavToPoseActionClient(Node):

    def __init__(self):
        super().__init__('Nav_To_Pose_Action_Client')
        self._action_client = ActionClient(self, NavigateToPose, '/navigate_to_pose')
        self.subscriber_ = self.create_subscription(PointStamped, 'clicked_point', self.callback, 1)
        self.subscriber_  # prevent unused variable warning

    def callback(self, msg):
        self.get_logger().info('Received Data:\n X : %f \n Y : %f \n Z : %f' % (msg.point.x, msg.point.y, msg.point.z))
        self.send_goal(msg.point.x, msg.point.y, 0.0)

    def send_goal(self, x, y, theta):
        self.get_logger().info('sending goal to action server')
        goal_pose = NavigateToPose.Goal()
        goal_pose.pose.header.frame_id = 'map'
        goal_pose.pose.pose.position.x = x
        goal_pose.pose.pose.position.y = y
        goal_pose.pose.pose.orientation.z = math.sin(theta / 2.0)  # yaw -> quaternion
        goal_pose.pose.pose.orientation.w = math.cos(theta / 2.0)
        self.get_logger().info('waiting for action server')
        self._action_client.wait_for_server()
        self.get_logger().info('action server detected')
        self._send_goal_future = self._action_client.send_goal_async(
            goal_pose, feedback_callback=self.feedback_callback)
        self.get_logger().info('goal sent')
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected :(')
            return
        self.get_logger().info('Goal accepted :)')
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        result = future.result().result
        self.get_logger().info('Result: ' + str(result))
        rclpy.shutdown()

    def feedback_callback(self, feedback_msg):
        feedback = feedback_msg.feedback
        self.get_logger().info('FEEDBACK:' + str(feedback))


def main(args=None):
    rclpy.init(args=args)
    action_client = NavToPoseActionClient()
    rclpy.spin(action_client)


if __name__ == '__main__':
    main()
```
Wiring: script in the package's module folder, `setup.py` entry point, a launch file, `colcon build` ([[core-pkg-ament-python]]). Then click **Publish Point** in RViz.

## Notes
- The node shuts down after the first result: remove `rclpy.shutdown()` to keep accepting clicks.
- `wait_for_server()` blocks the callback until bt_navigator is active.
- `async`/`await` version with initial pose and status check, and `nav2_simple_commander`: [[core-nav2-python-client]].

## Pitfalls
- Heading in `position.z` (as in the course) is ignored: the robot always ends at yaw 0.
- The goal must be in the `map` frame; RViz's fixed frame must be `map` for the clicked point to match.
