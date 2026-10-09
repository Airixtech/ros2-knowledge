---
id: core-nav2-python-client
title: "Nav2 goals from Python (NavigateToPose, initial pose)"
domain: core
area: architecture
distro: humble
tested: false
audience: dev
summary: "Publish the AMCL initial pose and send NavigateToPose goals with an rclpy ActionClient (async/await); CLI test; simple commander."
tags: [Nav2, NavigateToPose, initialpose, ActionClient, nav2_simple_commander, AMCL]
see: ["[[core-action-client]]", "[[core-action-server]]", "[[core-nav2-overview]]", "[[core-learn-unit7-actions]]"]
requires: []
version_notes:
  - "lyrical: Nav2 cmd_vel defaults to TwistStamped (Kilted); goal API unchanged — https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/migration_guides/jazzy/Jazzy.md (V54)"
---
# Nav2 goals from Python (NavigateToPose, initial pose)

**TL;DR** Publish `/initialpose` (frame `map`) a few times once AMCL subscribes. Then send a `NavigateToPose` goal to `navigate_to_pose` and `await` the goal handle and the result status.

## Nav2 from Python (ActionClient to /navigate_to_pose)
```python
import math
import time
from action_msgs.msg import GoalStatus
from geometry_msgs.msg import PoseWithCovarianceStamped
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient
from rclpy.node import Node

def yaw_to_quat(yaw):
    return 0.0, 0.0, math.sin(yaw / 2.0), math.cos(yaw / 2.0)

class Navigator(Node):
    def __init__(self):
        super().__init__('navigator')
        self.nav = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        self.init_pub = self.create_publisher(PoseWithCovarianceStamped, '/initialpose', 10)

    def set_initial_pose(self, x, y, yaw):            # AMCL needs it before map->odom exists
        while self.count_subscribers('/initialpose') == 0:
            time.sleep(0.5)
        msg = PoseWithCovarianceStamped()
        msg.header.frame_id = 'map'
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.pose.pose.position.x, msg.pose.pose.position.y = x, y
        (msg.pose.pose.orientation.x, msg.pose.pose.orientation.y,
         msg.pose.pose.orientation.z, msg.pose.pose.orientation.w) = yaw_to_quat(yaw)
        for _ in range(5):                                # publish a few times (discovery race)
            self.init_pub.publish(msg)
            time.sleep(0.1)

    async def go_to(self, x, y, yaw):                 # call from an async callback / execute_cb
        goal = NavigateToPose.Goal()
        goal.pose.header.frame_id = 'map'
        goal.pose.header.stamp = self.get_clock().now().to_msg()
        goal.pose.pose.position.x, goal.pose.pose.position.y = x, y
        (goal.pose.pose.orientation.x, goal.pose.pose.orientation.y,
         goal.pose.pose.orientation.z, goal.pose.pose.orientation.w) = yaw_to_quat(yaw)
        self.nav.wait_for_server()
        handle = await self.nav.send_goal_async(goal)
        if not handle.accepted:
            return False
        result = await handle.get_result_async()
        return result.status == GoalStatus.STATUS_SUCCEEDED
```
To wrap it in your own action server, use an `async def execute_cb` that awaits `go_to`, and a `cancel_callback` that forwards `handle.cancel_goal_async()` ([[core-action-server]]).

## CLI test
```bash
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
  "{pose: {header: {frame_id: 'map'}, pose: {position: {x: 2.0, y: 1.0}, orientation: {w: 1.0}}}}" -f
```
- Simpler API: `nav2_simple_commander` (`BasicNavigator`: `setInitialPose`, `waitUntilNav2Active`, `goToPose`, `isTaskComplete`, `getResult`).
- The startup log `Timed out waiting for transform from base_link to map` is normal until the initial pose is set.
- `set_initial_pose` blocks with `time.sleep`, so call it before spinning, not inside a callback ([[core-recipe-stop-and-wait]]).
