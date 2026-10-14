---
id: nav2-navigate-to-pose-action
type: reference
owner: equipo-ros2
updated: 2026-10-10
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "NavigateToPose action: goal, feedback and result fields"
domain: nav2
area: commander
distro: humble
tested: false
audience: dev
summary: "nav2_msgs/action/NavigateToPose: goal pose and optional behavior_tree, feedback (current_pose, navigation_time, ETA, recoveries, distance), result per distro."
tags: [NavigateToPose, NavigateToPose.action, nav2_msgs, navigate_to_pose, behavior_tree, estimated_time_remaining, distance_remaining, number_of_recoveries, error_code]
see: ["[[nav2-simple-commander]]", "[[nav2-bt-navigator]]", "[[nav2-send-goal-cli]]", "[[nav2-send-goal-action-client]]", "[[core-nav2-python-client]]"]
requires: [ros2-core]
version_notes:
  - "humble: result is std_msgs/Empty; the outcome is the goal status — https://github.com/ros-navigation/navigation2/blob/humble/nav2_msgs/action/NavigateToPose.action (NAV2-V58)"
  - "jazzy: result has uint16 error_code and string error_msg — https://github.com/ros-navigation/navigation2/blob/jazzy/nav2_msgs/action/NavigateToPose.action (NAV2-V58)"
  - "lyrical: error codes UNKNOWN=9000, FAILED_TO_LOAD_BEHAVIOR_TREE=9001, TF_ERROR=9002, TIMEOUT=9003 (Kilted), GOAL_REJECTED=1, SEND_GOAL_FAILURE=2; feedback adds position_tracking_error, heading_tracking_error — https://github.com/ros-navigation/navigation2/blob/lyrical/nav2_msgs/action/NavigateToPose.action (NAV2-V58)"
---
# NavigateToPose action: goal, feedback and result fields

**TL;DR** The **NavigateToPose** action is most suitable for point-to-point navigation requests or other tasks that can be represented in a behavior tree with a boundary condition pose, such as dynamic object following. `bt_navigator` serves it on `navigate_to_pose` ([[nav2-bt-navigator]]); `BasicNavigator.goToPose()` sends it ([[nav2-simple-commander]]).

## NavigateToPose.action (Humble)
```yaml
#goal definition
geometry_msgs/PoseStamped pose
string behavior_tree
---
#result definition
std_msgs/Empty result
---
# feedback definition
geometry_msgs/PoseStamped current_pose
builtin_interfaces/Duration navigation_time
builtin_interfaces/Duration estimated_time_remaining
int16 number_of_recoveries
float32 distance_remaining
```
- **Goal**: the `pose` you would like the robot to navigate to and the (optional) `behavior_tree` to use. If none is specified, the default behavior tree of the BT Navigator is used.
- **Feedback** during the execution: the robot's pose, how much time has elapsed, the estimated time remaining, the distance remaining, and the number of recoveries executed while navigating to the goal. Use it to make good autonomy decisions or track progress (e.g. print the ETA, [[nav2-commander-picking-demo]]).
- **Result** in Humble: empty. Success or failure is the goal status (`TaskResult` in the Simple Commander).

## Result in later distros
| Distro | Result fields |
|---|---|
| Humble | `std_msgs/Empty result` |
| [≥Jazzy] | `uint16 error_code`, `string error_msg` |
| [Lyrical] | named codes (9000–9003 from Kilted, `GOAL_REJECTED`, `SEND_GOAL_FAILURE`); feedback also `position_tracking_error`, `heading_tracking_error` |

Humble has no error code: read the goal status and the `bt_navigator` log to know why a goal failed.

## Pitfalls
- `pose.header.frame_id` must be the global frame (`map`), and the orientation a valid quaternion (`w: 1.0` for yaw 0).
- An empty `behavior_tree` uses the navigator's default tree; a wrong path fails the goal at once.
- Feedback `distance_remaining` is along the current path, not the straight-line distance.
