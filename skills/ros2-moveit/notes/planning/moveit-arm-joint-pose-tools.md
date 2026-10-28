---
id: moveit-arm-joint-pose-tools
type: reference
owner: equipo-ros2
updated: 2026-10-28
review_by: 2027-04-26
source: manual
confidentiality: internal
title: "Find targets by hand: rqt_joint_trajectory_controller, tf2_echo base_link tool0, /joint_states"
domain: moveit
area: planning
distro: humble
tested: false
audience: dev
summary: "Move joints with rqt_joint_trajectory_controller sliders, read the end-effector pose with tf2_echo base_link tool0 and joint values from /joint_states."
tags: [rqt_joint_trajectory_controller, tf2_echo, tool0, base_link, /joint_states, joint_state_broadcaster, end-effector pose, joint positions, sliders, controller manager]
see: ["[[moveit-cpp-joint-space-goal]]", "[[moveit-cpp-pose-goal]]", "[[core-tf-basics]]", "[[control-jtc-commands]]", "[[core-topic-cli]]"]
requires: [ros2-core, ros2-control]
version_notes:
  - "humble: rqt_joint_trajectory_controller is a console script of ros2_controllers (released 2.54.1; Jazzy 4.43.0, Lyrical 6.10.0) — https://github.com/ros-controls/ros2_controllers/blob/humble/rqt_joint_trajectory_controller/setup.py (MOVEIT-V31)"
  - "humble: /joint_states comes from the joint_state_broadcaster; the course calls it Joint State Controller — https://github.com/ros-controls/ros2_controllers/tree/humble/joint_state_broadcaster (MOVEIT-V13)"
  - "humble: tf2_echo prints more lines than the course shows (MOVEIT-V32)"
---
# Find targets by hand: joint sliders, TF, joint states

**TL;DR** Guessing joint values or end-effector poses with numbers is slow. Move the arm with the `rqt_joint_trajectory_controller` sliders until it is where you want it, then read the pose of the end effector with `tf2_echo` and the joint values from `/joint_states`; paste them into `setup_goal_pose_target()` or `setup_joint_value_target()`.

## Move the joints with sliders
```bash
ros2 run rqt_joint_trajectory_controller rqt_joint_trajectory_controller
```
A GUI with one slider per joint. Choose the **controller manager ns** and the **controller** (the arm's joint trajectory controller, [[control-jtc-commands]]), then press the red ON/OFF button: it turns green and the sliders become active.

## Pose of the end effector
```bash
ros2 run tf2_ros tf2_echo base_link tool0
```
```
At time 1350.570000000
- Translation: [0.457, 0.223, 0.067]
- Rotation: in Quaternion [-0.000, 0.707, 0.707, -0.000]
At time 1351.550000000
```
The pose of `tool0` in `base_link` (any other two frames work too, [[core-tf-basics]]); the course shows only the translation and quaternion lines of each print (MOVEIT-V32).

## Joint values
```bash
ros2 topic echo /joint_states
```
```yaml
header:
  stamp:
    sec: 221
    nanosec: 658000000
  frame_id: ''
name:
- shoulder_pan_joint
- shoulder_lift_joint
- elbow_joint
- wrist_2_joint
- wrist_3_joint
- wrist_1_joint
- robotiq_85_left_knuckle_joint
position:
- 1.5444652730067787e-05
- -1.5700090008239351
- 4.8789799471649076e-06
- -1.938054995598293e-05
- -1.693994438589641e-05
- -1.5699996624648191
- 7.193142447903256e-06
velocity:
- -0.000373574662565984
- 0.001999174211441514
- -0.001199828123609586
- 0.0004902811418939408
- -2.74005972728061e-05
- 0.0003375325463356836
- -0.004076884668536682
effort:
- .nan
- .nan
- .nan
- .nan
- .nan
- .nan
- .nan
```
In ros2_control the `joint_state_broadcaster` publishes `/joint_states` (MOVEIT-V13; the course calls it the "Joint State Controller").

## Pitfalls
- `/joint_states` lists the joints in its own order (here `wrist_2`, `wrist_3`, `wrist_1`), not the planning group's: copy values by name, not by position.
- `tf2_echo` needs the robot's TF (robot_state_publisher and the joint states) running; frame names without a leading `/`.
