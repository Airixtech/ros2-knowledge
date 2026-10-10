---
id: nav2-send-goal-cli
title: "Sending goals from the CLI: navigate_to_pose action and /goal_pose"
domain: nav2
area: planning-control
distro: humble
tested: false
audience: dev
summary: "Nav2 goal from the terminal: ros2 action send_goal /navigate_to_pose (feedback, result) or ros2 topic pub /goal_pose."
tags: [navigate_to_pose, NavigateToPose, goal_pose, PoseStamped, ros2 action send_goal, ros2 topic pub, quaternion, Publish Point]
see: ["[[nav2-send-goal-action-client]]", "[[core-nav2-python-client]]", "[[core-action-cli-status]]", "[[nav2-bt-navigator]]"]
requires: [ros2-core]
version_notes:
  - "humble: bt_navigator serves navigate_to_pose and subscribes to goal_pose; same in Jazzy and Lyrical — https://github.com/ros-navigation/navigation2/blob/humble/nav2_bt_navigator/src/navigators/navigate_to_pose.cpp (NAV2-V39)"
---
# Sending goals from the CLI: navigate_to_pose action and /goal_pose

**TL;DR** RViz sends goals through the `/navigate_to_pose` action; you can do the same from a terminal. Publishing on `/goal_pose` also works but gives you no feedback or result.

## With the action server
```bash
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose "pose: {header: {frame_id: map}, pose: {position: {x: 1.52, y: 1.92, z: 0.0}, orientation:{x: 0.0, y: 0.0, z: 0, w: 1.0000000}}}"
```
- Change `position` and `orientation` to where you want the robot to go. The orientation is a quaternion: for a yaw θ, `z = sin(θ/2)`, `w = cos(θ/2)`.
- Add `--feedback` (`-f`) to print the feedback (current pose, distance remaining, recoveries) ([[core-action-cli-status]]).
- Use RViz to find coordinates: the **Publish Point** tool prints the clicked point in the RViz terminal.

## With the topic
```bash
ros2 topic pub -1 /goal_pose geometry_msgs/PoseStamped "{header: {stamp: {sec: 0}, frame_id: 'map'}, pose: {position: {x: 2.2, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}"
```
`bt_navigator` subscribes to `goal_pose` and starts a NavigateToPose with it (this is what RViz's **2D Goal Pose** tool publishes). `-1` publishes once and exits.

| | Action `/navigate_to_pose` | Topic `/goal_pose` |
|---|---|---|
| Feedback and result | yes | no |
| Cancel | yes (Ctrl+C / cancel request) | send a new goal |
| Typical use | scripts, programs | quick tests, RViz tool |

From a program: [[nav2-send-goal-action-client]], [[core-nav2-python-client]].

## Pitfalls
- `frame_id` empty or not `map` → the goal is interpreted in the wrong frame.
- A quaternion with all zeros is invalid; give at least `w: 1.0`.
- Goals are rejected until the lifecycle manager reports the stack active and AMCL has an initial pose.
