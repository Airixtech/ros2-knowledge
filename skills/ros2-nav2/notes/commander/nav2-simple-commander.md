---
id: nav2-simple-commander
title: "nav2_simple_commander BasicNavigator: setInitialPose, goToPose, followWaypoints, feedback, result"
domain: nav2
area: commander
distro: humble
tested: false
audience: dev
summary: "Simple Commander Python API: BasicNavigator, TaskResult, setInitialPose, waitUntilNav2Active, goToPose, goThroughPoses, followWaypoints, isTaskComplete, getFeedback, getResult."
tags: [nav2_simple_commander, Simple Commander API, BasicNavigator, TaskResult, goToPose, goThroughPoses, followWaypoints, isTaskComplete, getFeedback, getResult, waitUntilNav2Active]
see: ["[[nav2-commander-picking-demo]]", "[[nav2-commander-inspection-demo]]", "[[nav2-navigate-to-pose-action]]", "[[nav2-waypoint-follower]]", "[[core-nav2-python-client]]"]
requires: [ros2-core]
version_notes:
  - "humble: isTaskComplete() (isNavComplete() is the Galactic name) returns True when the task ends with any result — https://github.com/ros-navigation/navigation2/blob/humble/nav2_simple_commander/README.md (NAV2-V42)"
  - "jazzy: + driveOnHeading, followGpsWaypoints, docking, clearCostmapAroundRobot; lyrical: getTaskError(), isTaskComplete(task) (Kilted), followWaypoints(poses, number_of_loops, goal_index) — https://github.com/ros-navigation/navigation2/blob/lyrical/nav2_simple_commander/nav2_simple_commander/robot_navigator.py (NAV2-V57)"
---
# nav2_simple_commander BasicNavigator

**TL;DR** The **Nav2 Simple Commander** is a Python API that simplifies interaction with the Nav2 system, enabling you to control and manage robot navigation through Python3 code. It provides a high-level interface to execute navigation tasks without needing to interact directly with lower-level ROS 2 messages and services. Essential methods: **goToPose()** (move to a specific location), **goThroughPoses()** (follow a sequence of poses) and **followWaypoints()** (navigate through predefined waypoints).

## The calls, in the order a script uses them
```python
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult

navigator = BasicNavigator()                 # instantiate the class (it is an rclpy node)
navigator.setInitialPose(initial_pose)       # same as the RViz2 2D Pose Estimate tool; a PoseStamped
navigator.waitUntilNav2Active()              # block until Nav2 is online and its lifecycle nodes are active
navigator.goToPose(shelf_item_pose)          # request navigation to a PoseStamped (NavigateToPose action)
while not navigator.isTaskComplete():        # course text: isNavComplete() (Galactic name)
    feedback = navigator.getFeedback()       # feedback of the NavigateToPose action server
result = navigator.getResult()               # TaskResult.SUCCEEDED / CANCELED / FAILED / UNKNOWN
```
- The `BasicNavigator` class gives you access to the Simple Commander API: import it whenever you want to use the API.
- `goToPose()` requests the robot to navigate to the specified pose; here the pose is in the `shelf_item_pose` variable (it must be of the type `PoseStamped`, like `initial_pose`).
- `isTaskComplete()` returns **True** once the task has finished — succeeded, canceled **or failed** — and **False** while it is still in process (each call waits up to 100 ms). Check `getResult()` for the outcome.
- `setInitialPose()` publishes a `PoseWithCovarianceStamped` on `initialpose`. `waitUntilNav2Active()` waits for `amcl` to be active, re-publishes the stored initial pose every second until `amcl_pose` arrives, then waits for `bt_navigator`.

Other Humble methods: `spin()`, `backup()`, `followPath()`, `cancelTask()`, `clearLocalCostmap()`, `clearGlobalCostmap()`, `clearAllCostmaps()`, `getPath()`, `changeMap()`, `lifecycleStartup()`, `lifecycleShutdown()`. You can review all the Nav2 Simple Commander methods in the [Humble README](https://github.com/ros-navigation/navigation2/blob/humble/nav2_simple_commander/README.md). [≥Jazzy] `driveOnHeading()` and `clearCostmapAroundRobot()` do not exist in Humble: use the clear methods above, or an action client for the `DriveOnHeading` action of the behavior server.

## Pitfalls
- Treating `isTaskComplete() == True` as success: a failed or canceled goal also completes.
- `waitUntilNav2Active()` blocks forever if the localizer node is not called `amcl` (pass `localizer=…`). Call `setInitialPose()` first: otherwise it keeps publishing a default pose with an empty frame.
