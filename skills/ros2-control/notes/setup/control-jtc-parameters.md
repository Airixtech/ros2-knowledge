---
id: control-jtc-parameters
type: reference
owner: equipo-ros2
updated: 2026-10-24
review_by: 2027-04-22
source: manual
confidentiality: internal
title: "joint_trajectory_controller parameters of the course YAML: defaults, goal_time, removed and deprecated keys"
domain: control
area: setup
distro: jazzy
tested: false
audience: dev
summary: "JTC parameters: joints, command/state_interfaces, action_monitor_rate, allow_partial_joints_goal, goal_time semantics, state_publish_rate and open_loop_control per distro."
tags: [joint_trajectory_controller, JointTrajectoryController, JTC, action_monitor_rate, allow_partial_joints_goal, allow_integration_in_goal_trajectories, stopped_velocity_tolerance, goal_time, state_publish_rate, open_loop_control, interpolate_from_desired_state, controller_state]
see: ["[[control-controller-config]]", "[[control-cli-state-changes]]", "[[control-learn-unit1-demo]]", "[[control-humble-to-jazzy]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: state_publish_rate is not a JointTrajectoryController parameter (ignored); humble: default 50.0 — https://github.com/ros-controls/ros2_controllers/blob/jazzy/joint_trajectory_controller/src/joint_trajectory_controller_parameters.yaml (CONTROL-V06)"
  - "jazzy: goal_time 0.0 means no time limit, not 'start immediately'; lyrical: default 10.0, 0.0 = on time, negative = no limit — https://github.com/ros-controls/ros2_controllers/blob/master/doc/migration.rst (CONTROL-V07)"
  - "jazzy: open_loop_control deprecated (use interpolate_from_desired_state and zero feedback gains); lyrical: removed — https://github.com/ros-controls/ros2_controllers/blob/jazzy/doc/migration.rst (CONTROL-V28)"
---
# joint_trajectory_controller parameters of the course YAML: defaults, goal_time, removed and deprecated keys

**TL;DR** The course's trajectory controller block ([[control-controller-config]]) comes from the official Humble demo. On Jazzy one key is no longer a parameter, one is deprecated and one comment is wrong; on Lyrical the meaning of `goal_time` changes.

## The parameters used
| Parameter | Course value | Default (Jazzy) | Meaning |
|---|---|---|---|
| `joints` | `joint1`, `joint2` | — | joints to control (URDF names) |
| `command_interfaces` / `state_interfaces` | `position` / `position` | — | interfaces claimed and read; they must exist in `<ros2_control>` |
| `action_monitor_rate` | 20.0 | 20.0 | rate to monitor status changes while executing a `FollowJointTrajectory` action |
| `allow_partial_joints_goal` | false | false | accept goals for only some joints |
| `open_loop_control` | true | false | [changed in Jazzy: deprecated, use `interpolate_from_desired_state` and zero feedback gains; removed in Lyrical] |
| `allow_integration_in_goal_trajectories` | true | false | accept goals without position or velocity, which are then integrated |
| `constraints.stopped_velocity_tolerance` | 0.01 | 0.01 | velocity below which the system counts as stopped at the end of the trajectory |
| `constraints.goal_time` | 0.0 | 0.0 | time tolerance for reaching the goal before or after the commanded time |

## goal_time
The course (and the official Humble demo file) comment `goal_time: 0.0 # Defaults to 0.0 (start immediately)` is wrong: on Humble and Jazzy 0.0 means **no time limit** (the controller may wait indefinitely for the goal). [changed in Lyrical: default 10.0; 0.0 now means the goal must be reached on time and a negative value waits indefinitely: set `goal_time: -1.0` to keep the old behaviour].

## state_publish_rate
The course sets `state_publish_rate: 200.0 # Hz, Defaults to 50`. [Humble] a parameter, default 50.0. [changed in Jazzy: not a parameter, the line is ignored; JTC publishes its state on `~/controller_state` in every `update()`, so at the controller's update rate]. With the course's `update_rate: 10`, 200 Hz could not be reached in any case.

## Pitfalls
- Keys that are not parameters are ignored without an error: check the controller's `*_parameters.yaml` on your distro's branch, not an old tutorial.
- Lyrical: a YAML that relied on `goal_time: 0.0` for "no timeout" now aborts goals that arrive late.
