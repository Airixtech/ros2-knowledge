---
id: nav2-commander-inspection-demo
type: reference
owner: equipo-ros2
updated: 2026-10-10
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "Simple Commander demo: shelf inspection with followWaypoints"
domain: nav2
area: commander
distro: humble
tested: false
audience: dev
summary: "follow_waypoints.py: BasicNavigator followWaypoints over shelf inspection points, current_waypoint feedback, TaskResult, return to the staging point."
tags: [nav2_simple_commander, followWaypoints, inspection demo, follow_waypoints.py, current_waypoint, TaskExecutor, warehouse, deepcopy]
see: ["[[nav2-waypoint-follower]]", "[[nav2-simple-commander]]", "[[nav2-commander-picking-demo]]", "[[nav2-learn-adv-unit1-features]]"]
requires: [ros2-core]
version_notes:
  - "humble: older revision of upstream demo_inspection.py; lyrical adds followWaypoints(poses, number_of_loops, goal_index) — https://github.com/ros-navigation/navigation2/blob/humble/nav2_simple_commander/nav2_simple_commander/demo_inspection.py (NAV2-V57, NAV2-V59)"
---
# Simple Commander demo: shelf inspection with followWaypoints

**TL;DR** In this demo, use the **`FollowWaypoints`** action to have your robot drive from its staging point to a set of inspection points. The Nav2 waypoint follower **`TaskExecutor`** plugin takes images and RFID scans of the shelves that can be analyzed for inventory management. The `waypoint_follower` server must be running ([[nav2-waypoint-follower]]).

## scripts/follow_waypoints.py (package `nav2_new_features`)
Create a new Python script named **follow_waypoints.py** next to `navigate_to_pose.py` ([[nav2-commander-picking-demo]]):
```python
#! /usr/bin/env python3
# Copyright 2021 Samsung Research America
# Licensed under the Apache License, Version 2.0 (SPDX: Apache-2.0): http://www.apache.org/licenses/LICENSE-2.0
from copy import deepcopy

from geometry_msgs.msg import PoseStamped
import rclpy

from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult


def main():
    rclpy.init()

    navigator = BasicNavigator()

    # Inspection route, probably read in from a file for a real application
    # from either a map or drive and repeat.
    inspection_route = [
        [3.461, -0.450],
        [3.461, -2.200],
        [3.661, -4.121],
        [3.661, -5.850]]

    # Set your demo's initial pose
    initial_pose = PoseStamped()
    initial_pose.header.frame_id = 'map'
    initial_pose.header.stamp = navigator.get_clock().now().to_msg()
    initial_pose.pose.position.x = 3.45
    initial_pose.pose.position.y = 2.15
    initial_pose.pose.orientation.z = 1.0
    initial_pose.pose.orientation.w = 0.0
    navigator.setInitialPose(initial_pose)

    # Wait for navigation to activate fully
    navigator.waitUntilNav2Active()

    # Send your route
    inspection_points = []
    inspection_pose = PoseStamped()
    inspection_pose.header.frame_id = 'map'
    inspection_pose.header.stamp = navigator.get_clock().now().to_msg()
    inspection_pose.pose.orientation.z = 1.0
    inspection_pose.pose.orientation.w = 0.0
    for pt in inspection_route:
        inspection_pose.pose.position.x = pt[0]
        inspection_pose.pose.position.y = pt[1]
        inspection_points.append(deepcopy(inspection_pose))
    navigator.followWaypoints(inspection_points)

    # Do something during your route (e.x. AI to analyze stock information or upload to the cloud)
    # Print the current waypoint ID for the demonstration
    i = 0
    while not navigator.isTaskComplete():
        i = i + 1
        feedback = navigator.getFeedback()
        if feedback and i % 5 == 0:
            print('Executing current waypoint: ' +
                  str(feedback.current_waypoint + 1) + '/' + str(len(inspection_points)))

    result = navigator.getResult()
    if result == TaskResult.SUCCEEDED:
        print('Inspection of shelves complete! Returning to start...')
    elif result == TaskResult.CANCELED:
        print('Inspection of shelving was canceled. Returning to start...')
        exit(1)
    elif result == TaskResult.FAILED:
        print('Inspection of shelving failed! Returning to start...')

    # go back to start
    initial_pose.header.stamp = navigator.get_clock().now().to_msg()
    navigator.goToPose(initial_pose)
    while not navigator.isTaskComplete():
        pass

    exit(0)


if __name__ == '__main__':
    main()
```
Code adapted from the official [demo_inspection.py (humble)](https://github.com/ros-navigation/navigation2/blob/humble/nav2_simple_commander/nav2_simple_commander/demo_inspection.py). The course version also imported `time` and `Duration` and stored an unused `nav_start`.

## Code review
- `navigator.followWaypoints(inspection_points)` requests the robot to follow a set of waypoints (list of `PoseStamped` messages) and executes the chosen TaskExecutor plugin at each pose.
- The `while` loop prints the robot's current waypoint (`feedback.current_waypoint` is 0-based); you could do other, more meaningful tasks there.
- `deepcopy` is needed: appending the same `PoseStamped` object would leave every waypoint at the last position.

## Pitfalls
- `/follow_waypoints` missing from `ros2 action list` → the waypoint follower is not launched or not in the lifecycle manager's `node_names`.
- With `stop_on_failure: true` (default) one unreachable waypoint fails the whole task. The action result lists `missed_waypoints`; `getResult()` only returns the `TaskResult`.
