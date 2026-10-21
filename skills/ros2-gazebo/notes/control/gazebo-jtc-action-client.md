---
id: gazebo-jtc-action-client
type: reference
owner: equipo-ros2
updated: 2026-10-21
review_by: 2027-04-19
source: manual
confidentiality: internal
title: "Move a joint with a FollowJointTrajectory action client (Python)"
domain: gazebo
area: control
distro: jazzy
tested: false
audience: dev
summary: "Python ActionClient for /joint_trajectory_controller/follow_joint_trajectory: JointTrajectoryPoint, time_from_start, goal_time_tolerance; install in ament_cmake; CLI checks."
tags: [FollowJointTrajectory, control_msgs, ActionClient, joint_trajectory_controller, JointTrajectoryPoint, trajectory_msgs, time_from_start, goal_time_tolerance, move_laser.py, install PROGRAMS]
see: ["[[gazebo-ros2-control-controllers]]", "[[gazebo-ros2-control-urdf]]", "[[core-action-client]]", "[[core-pkg-ament-cmake]]"]
requires: [ros2-core, ros2-urdf]
version_notes:
  - "jazzy/harmonic: same structure as the official action client tutorial (rclpy.shutdown() in the result callback, rclpy.spin in main) — https://docs.ros.org/en/jazzy/Tutorials/Intermediate/Writing-an-Action-Server-Client/Py.html (GZ-V33)"
  - "jazzy/harmonic: a rejected goal returns without shutdown, so the script keeps spinning (GZ-V51)"
---
# Move a joint with a FollowJointTrajectory action client (Python)

**TL;DR** joint_trajectory_controller offers the action `/joint_trajectory_controller/follow_joint_trajectory` (`control_msgs/action/FollowJointTrajectory`). A goal is a trajectory: joint names plus points, each with positions and a `time_from_start`. This script sends one point taken from the command line.

## scripts/move_laser.py
```python
#! /usr/bin/env python3
import sys
import rclpy
from rclpy.duration import Duration
from rclpy.action import ActionClient
from rclpy.node import Node
from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectoryPoint

# ros2 action list -t
# ros2 action info /joint_trajectory_controller/follow_joint_trajectory -t
# ros2 interface show control_msgs/action/FollowJointTrajectory


class SteeringActionClient(Node):

    def __init__(self):
        super().__init__('move_laser_actionclient')
        self._action_client = ActionClient(self, FollowJointTrajectory, '/joint_trajectory_controller/follow_joint_trajectory')

    def send_goal(self, position_value):
        goal_msg = FollowJointTrajectory.Goal()

        # Fill in data for trajectory
        joint_names = ["laser_scan_link_joint"]

        points = []
        point_to_move_to = JointTrajectoryPoint()
        point_to_move_to.time_from_start = Duration(seconds=1, nanoseconds=0).to_msg()
        point_to_move_to.positions = [position_value]
        points.append(point_to_move_to)

        goal_msg.goal_time_tolerance = Duration(seconds=1, nanoseconds=0).to_msg()
        goal_msg.trajectory.joint_names = joint_names
        goal_msg.trajectory.points = points

        self._action_client.wait_for_server()
        self._send_goal_future = self._action_client.send_goal_async(goal_msg, feedback_callback=self.feedback_callback)
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
        pass  # feedback_msg.feedback holds desired, actual and error of the trajectory (unused here)


def main(args=None):
    rclpy.init()
    action_client = SteeringActionClient()
    position_value = float(sys.argv[1])
    action_client.send_goal(position_value)
    rclpy.spin(action_client)


if __name__ == '__main__':
    main()
```
- One joint, one point; add more points (each with a later `time_from_start`) for a path. `goal_time_tolerance`: how late the joint may reach the end.
- `send_goal` returns nothing: the course stores its result in an unused `future` variable (always `None`), and its feedback callback keeps an unused `feedback` variable; both are left out here.

## Install and run (ament_cmake package)
```cmake
install(PROGRAMS scripts/move_laser.py DESTINATION lib/${PROJECT_NAME})
```
`chmod +x scripts/move_laser.py`, keep the shebang, rebuild, then:
```bash
ros2 run my_box_bot_gazebo move_laser.py 0.0     # highest position (upper limit 0.0)
ros2 run my_box_bot_gazebo move_laser.py -0.05   # lowest commanded position
```
Declare `rclpy`, `control_msgs` and `trajectory_msgs` as `<exec_depend>` in `package.xml`. Generic action clients: [[core-action-client]].

## Pitfalls
- Goal rejected → the script logs it and keeps spinning (no shutdown on that path): stop it with Ctrl+C, or call `rclpy.shutdown()` there too. Typical cause: a joint name the controller does not handle (log: "Incoming joint … doesn't match the controller's joints.").
- `wait_for_server()` blocks forever → the controller is not active (`ros2 control list_controllers`).
- "Exceeded goal_time_tolerance: holding position..." → the joint could not reach the point in `time_from_start` + tolerance (too slow, blocked, or effort too low).
