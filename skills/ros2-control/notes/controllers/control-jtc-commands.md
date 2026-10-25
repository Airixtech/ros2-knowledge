---
id: control-jtc-commands
type: reference
owner: equipo-ros2
updated: 2026-10-24
review_by: 2027-04-22
source: manual
confidentiality: internal
title: "joint_trajectory_controller: trajectories, interpolation, tolerances, ~/joint_trajectory topic and FollowJointTrajectory action"
domain: control
area: controllers
distro: jazzy
tested: false
audience: dev
summary: "JTC follows time-stamped waypoints for a joint group: ~/joint_trajectory topic vs follow_joint_trajectory action, tolerances, controller_state, test publisher node."
tags: [joint_trajectory_controller, JointTrajectoryController, JTC, trajectory_msgs/JointTrajectory, joint_trajectory, follow_joint_trajectory, FollowJointTrajectory, controller_state, tolerances, goal tolerance, interpolation, MoveIt, ros2_controllers_test_nodes, publisher_joint_trajectory_controller]
see: ["[[control-jtc-parameters]]", "[[control-controller-config]]", "[[control-builtin-forward]]", "[[control-learn-unit6-controllers]]", "[[control-learn-unit8-solution]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: tolerances default to 0.0 (not enforced); a violation aborts an action goal and tells the client; on the topic interface nobody is told and a violated state tolerance aborts the trajectory and holds the position — https://github.com/ros-controls/ros2_controllers/blob/jazzy/joint_trajectory_controller/doc/userdoc.rst (CONTROL-V65)"
  - "jazzy: ~/joint_trajectory, <name>/follow_joint_trajectory, state on ~/controller_state; humble: also the older ~/state — https://github.com/ros-controls/ros2_controllers/blob/humble/joint_trajectory_controller/src/joint_trajectory_controller.cpp (CONTROL-V66)"
  - "jazzy: JointTrajectoryControllerState has reference/feedback/error/output; humble: also desired/actual — https://github.com/ros-controls/control_msgs/blob/jazzy/control_msgs/msg/JointTrajectoryControllerState.msg (CONTROL-V66)"
  - "jazzy: official test node publisher_joint_trajectory_controller in ros2_controllers_test_nodes — https://github.com/ros-controls/ros2_controllers/blob/jazzy/ros2_controllers_test_nodes/ros2_controllers_test_nodes/publisher_joint_trajectory_controller.py (CONTROL-V66)"
---
# joint_trajectory_controller: trajectories, interpolation, tolerances, ~/joint_trajectory topic and FollowJointTrajectory action

**TL;DR** The joint trajectory controller (JTC) moves a group of joints together along waypoints that each carry a time. It interpolates between them, so the joints move smoothly and arrive in sync. It is the controller MoveIt drives on position-controlled arms. Send it trajectories on a topic (no feedback) or through an action (result, feedback and tolerances).

## Trajectories
A trajectory is a list of points, each with joint positions (optionally velocities and accelerations) and the time from the start at which they must be reached. The controller interpolates between the points and follows them as closely as it can. Planners such as MoveIt generate the trajectories.

```yaml
position_trajectory_controller:
  type: joint_trajectory_controller/JointTrajectoryController
```
Declare it under `controller_manager` like any controller; its `command_interfaces` must exist in the joints' `<ros2_control>` tags. Parameters and their defaults: [[control-jtc-parameters]].

## Interfaces
| Name | Kind | Type | Use |
|---|---|---|---|
| `~/joint_trajectory` | topic | `trajectory_msgs/msg/JointTrajectory` | fire and forget: no result |
| `<controller>/follow_joint_trajectory` | action | `control_msgs/action/FollowJointTrajectory` | result, feedback, per-goal tolerances (MoveIt) |
| `~/controller_state` | topic | `control_msgs/msg/JointTrajectoryControllerState` | fields `reference`, `feedback`, `error`, `output` [Humble: also `desired` and `actual`, and the older topic `~/state`] |

Only one action goal is active at a time, and none while a trajectory from the topic is running.

## Tolerances
The `constraints` parameters ([[control-jtc-parameters]]) give default tolerances; an action goal can send its own. A tolerance of 0.0 means **not enforced**, which is the default. When a tolerance is violated during an action goal, the goal is aborted, the client is told and the current position is held. With the topic there is nobody to tell: a violated state tolerance aborts the trajectory and holds the position, and goal tolerances are not used.

## Which topic does a test script use?
The course's test programs publish trajectories; find their target before writing your configuration:
```bash
ros2 topic list
ros2 topic info /position_trajectory_controller/joint_trajectory
```
```text
Type: trajectory_msgs/msg/JointTrajectory
Publisher count: 1
Subscription count: 0
```
That is the topic interface of a JTC named `position_trajectory_controller`: name your controller the same, or it never receives them. `Subscription count: 0` means no such controller is running yet.

## Official test publisher
`ros2_controllers_test_nodes` has `publisher_joint_trajectory_controller`, which sends a list of goals in turn to `/<controller_name>/joint_trajectory`. Its parameters, adapted from ros2_control_demos example_1 (`rrbot_joint_trajectory_publisher.yaml`, Apache-2.0) [verify]:
```yaml
publisher_joint_trajectory_controller:
  ros__parameters:
    controller_name: "position_trajectory_controller"
    wait_sec_between_publish: 6
    goal_names: ["pos1", "pos2"]
    pos1:
      positions: [0.785, 0.785]
    pos2:
      positions: [0.0, 0.0]
    joints:
      - joint1
      - joint2
```
```bash
ros2 run ros2_controllers_test_nodes publisher_joint_trajectory_controller --ros-args --params-file <file>.yaml
```
An action client in Python (FollowJointTrajectory): ros2-gazebo skill, `gazebo-jtc-action-client`.

## Pitfalls
- JTC has no `interface_name` parameter: list `command_interfaces` and `state_interfaces` instead.
- Topic interface: no success or failure is reported; use the action when the sender must know whether the motion finished.
- A controller with another name than the publisher expects receives nothing, without an error.
