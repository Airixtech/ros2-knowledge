---
id: nav2-waypoint-follower
title: "waypoint_follower: FollowWaypoints action, task executor plugins, launch"
domain: nav2
area: commander
distro: humble
tested: false
audience: dev
summary: "FollowWaypoints action and the waypoint_follower server: waypoint_follower.yaml (loop_rate, stop_on_failure, WaitAtWaypoint pause in ms), task executor plugins, launch and lifecycle."
tags: [waypoint_follower, nav2_waypoint_follower, FollowWaypoints, follow_waypoints, TaskExecutor, WaitAtWaypoint, PhotoAtWaypoint, InputAtWaypoint, waypoint_pause_duration, stop_on_failure, missed_waypoints]
see: ["[[nav2-simple-commander]]", "[[nav2-commander-inspection-demo]]", "[[nav2-single-launch]]", "[[nav2-lifecycle-manager]]", "[[nav2-behavior-server]]"]
requires: [ros2-core]
version_notes:
  - "humble: the course launch names the behavior server recoveries_server; a params YAML applies only if its key equals the node name — https://github.com/ros2/rcl/blob/humble/rcl_yaml_param_parser/src/parse.c (NAV2-V01)"
  - "humble: defaults loop_rate 20, stop_on_failure true, wait_at_waypoint, pause 0 ms; nav2_bringup starts waypoint_follower — https://github.com/ros-navigation/navigation2/blob/humble/nav2_waypoint_follower/src/waypoint_follower.cpp (NAV2-V60)"
  - "jazzy: goal number_of_loops, goal_index; result MissedWaypoint[], error_code, error_msg; params action_server_result_timeout, global_frame_id; lyrical: WaypointStatus[] — https://github.com/ros-navigation/navigation2/blob/jazzy/nav2_msgs/action/FollowWaypoints.action (NAV2-V59, NAV2-V60)"
---
# waypoint_follower: FollowWaypoints action, task executor plugins, launch

**TL;DR** The **FollowWaypoints** action is most suitable for simple autonomy tasks where you wish to stop at each waypoint and execute a behavior (e.x. pausing for 2 seconds, taking a picture, waiting for someone to place a box on it, etc.). The Nav2 waypoint follower server contains `TaskExecutor` plugins to execute a task at each waypoint.

## FollowWaypoints.action (Humble)
```yaml
#goal definition
geometry_msgs/PoseStamped[] poses
---
#result definition
int32[] missed_waypoints
---
#feedback definition
uint32 current_waypoint
```
It takes in the set of poses, where the last pose is the final goal. The feedback is the current waypoint ID it is executing, and it returns a vector of missed waypoint IDs at the end should any be unnavigable. [changed in Jazzy: loops and error codes; in Humble, repeat a route by calling `followWaypoints()` again]

## config/waypoint_follower.yaml (package `path_planner_server`)
The **FollowWaypoints** action is not started by the course's `navigation.launch.py`, so add it (Nav2's own `navigation_launch.py` does start it). Begin by creating a configuration file for it: in the **config** folder of your **path_planner_server** package, add a new configuration file named **waypoint_follower.yaml**.
```yaml
waypoint_follower:
  ros__parameters:
    loop_rate: 20
    stop_on_failure: false
    waypoint_task_executor_plugin: "wait_at_waypoint"
    wait_at_waypoint:
      plugin: "nav2_waypoint_follower::WaitAtWaypoint"
      enabled: True
      waypoint_pause_duration: 200
```
- `WaitAtWaypoint` (default plugin) pauses the robot for a specified time after reaching each waypoint: `waypoint_pause_duration`, in **milliseconds** (default 0).
- There are other plugins available, such as **PhotoAtWaypoint** (takes a photo at each waypoint and saves it to a directory) or **InputAtWaypoint** (waits for an external input, with a timeout). To learn more about them, review the official documentation: [waypoint follower](https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/configuration_guide/core_servers/waypoint_follower/index.md).
- `stop_on_failure: false` continues with the next waypoint when one fails (default `true`: the action fails).

## Add it to navigation.launch.py
```python
waypoint_follower_yaml = os.path.join(get_package_share_directory('path_planner_server'), 'config', 'waypoint_follower.yaml')
```
```python
Node(package='nav2_waypoint_follower', executable='waypoint_follower', name='waypoint_follower',
     output='screen', parameters=[waypoint_follower_yaml]),
```
Finally, and important, add the new node to the nodes started by the lifecycle manager:
```python
Node(package='nav2_lifecycle_manager', executable='lifecycle_manager', name='lifecycle_manager',
     output='screen',
     parameters=[{'autostart': True},
                 {'node_names': ['map_server', 'amcl', 'controller_server', 'planner_server',
                                 'recoveries_server', 'bt_navigator', 'waypoint_follower']}])
```
Compile and check with `ros2 action list` that **`/follow_waypoints`** is listed. The course launch names the behavior server `recoveries_server`, so its YAML key must be `recoveries_server:` ([[nav2-behavior-server]], [[nav2-single-launch]]).

## Pitfalls
- Node missing from `node_names` → it stays unconfigured and `/follow_waypoints` never appears ([[nav2-lifecycle-manager]]).
- `waypoint_pause_duration: 2` is 2 ms, not 2 s.
