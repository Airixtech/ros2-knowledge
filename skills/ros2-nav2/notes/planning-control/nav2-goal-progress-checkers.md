---
id: nav2-goal-progress-checkers
type: reference
owner: equipo-ros2
updated: 2026-10-10
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "Progress and goal checker plugins: SimpleProgressChecker, SimpleGoalChecker, StoppedGoalChecker"
domain: nav2
area: planning-control
distro: humble
tested: false
audience: dev
summary: "controller_server's three plugin kinds; progress checkers (Simple, Pose) and goal checkers (Simple, Stopped, Position) in Humble with their parameters."
tags: [controller_server, progress_checker_plugin, goal_checker_plugins, controller_plugins, SimpleProgressChecker, PoseProgressChecker, SimpleGoalChecker, StoppedGoalChecker, PositionGoalChecker, required_movement_radius, movement_time_allowance, trans_stopped_velocity]
see: ["[[nav2-controller-server]]", "[[nav2-dwb-generators-critics]]", "[[nav2-rpp-controller-params]]", "[[nav2-recovery-flow]]"]
requires: [ros2-core]
version_notes:
  - "humble: progress checkers SimpleProgressChecker, PoseProgressChecker; goal checkers SimpleGoalChecker, StoppedGoalChecker, PositionGoalChecker (course: one and two, 'Galactic'; class StopedGoalChecker misspelled) — https://github.com/ros-navigation/navigation2/blob/humble/nav2_controller/plugins.xml (NAV2-V54)"
  - "jazzy: progress_checker_plugins list (Iron); lyrical: AdaptiveToleranceGoalChecker, AxisGoalChecker and a path handler plugin (FeasiblePathHandler) — https://github.com/ros-navigation/navigation2/blob/lyrical/nav2_controller/plugins.xml (NAV2-V18, NAV2-V67)"
---
# Progress and goal checker plugins

**TL;DR** The `controller_server` is where the velocities of the wheels are computed: master it to solve problems when your robot does not behave correctly. Its behavior is controlled by three kinds of plugins, which you must specify for your navigation task: the `progress_checker_plugin`, the `goal_checker_plugins` and the `controller_plugins`.

## The server block
The beginning of the course's `controller.yaml` is the block of [[nav2-controller-server]] with `controller_frequency: 20.0`; its last three lines select the plugins:
```yaml
    progress_checker_plugin: "progress_checker"
    goal_checker_plugins: ["general_goal_checker"]
    controller_plugins: ["FollowPath"]
```
**IMPORTANT:** the `progress_checker_plugin` takes a single plugin; the `goal_checker_plugins` and the `controller_plugins` can contain more than one. [changed in Jazzy: `progress_checker_plugins` is a list too]

## 1. Progress checker
Checks whether the robot is progressing towards the goal, i.e. making any improvement in reaching it; it is called by the controller server. The `nav2_controller` package provides two plugins in Humble (the course says only one):
```yaml
    # Progress checker parameters
    progress_checker:
      plugin: "nav2_controller::SimpleProgressChecker"
      required_movement_radius: 0.5
      movement_time_allowance: 10.0
```
- `SimpleProgressChecker` checks that the robot has moved at least `required_movement_radius` meters in `movement_time_allowance` seconds. It does not check if the movement makes sense or is towards the goal. When it fails, the controller aborts `FollowPath` and recoveries start ([[nav2-recovery-flow]]).
- `PoseProgressChecker` also counts a rotation of `required_movement_angle` (default 0.5 rad) as progress, so a robot turning in place is not "stuck".
- You can write more complex plugins yourself ([[nav2-plugins-overview]]).

## 2. Goal checkers
Check if the robot has reached the goal pose within specific tolerances. Decreasing the tolerances too much may end with the robot never reaching the goal; increasing them too much ends with the final position far from what is expected. `nav2_controller` provides three in Humble (the course: two, "currently, ROS2 Galactic"):
```yaml
    # Goal checker parameters
    general_goal_checker:
      stateful: True
      plugin: "nav2_controller::SimpleGoalChecker"
      xy_goal_tolerance: 0.25    # m
      yaw_goal_tolerance: 0.25   # rad
```
```yaml
    # Goal checker parameters
    general_goal_checker:
      stateful: True
      plugin: "nav2_controller::StoppedGoalChecker"   # course: StopedGoalChecker (fails to load)
      xy_goal_tolerance: 0.25        # m
      yaw_goal_tolerance: 0.25       # rad
      trans_stopped_velocity: 0.25   # m/s
      rot_stopped_velocity: 0.25     # rad/s
```
- `SimpleGoalChecker`: the robot is within the position and orientation tolerances.
- `StoppedGoalChecker`: the same, and the linear and rotational speeds are below the stopped velocities.
- `PositionGoalChecker`: position only (`xy_goal_tolerance`, `stateful`), any final heading.

## Pitfalls
- A misspelled plugin class → "failed to create goal checker" and the controller server does not configure.
- `progress_checker` too strict for a slow robot → recoveries start while it is still moving.
