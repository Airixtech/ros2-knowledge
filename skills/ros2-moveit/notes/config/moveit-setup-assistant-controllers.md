---
id: moveit-setup-assistant-controllers
type: reference
owner: equipo-ros2
updated: 2026-10-28
review_by: 2027-04-26
source: manual
confidentiality: internal
title: "MoveIt Setup Assistant (2/2): find the controllers' actions, auto-add controllers, author info, generate and edit the package"
domain: moveit
area: config
distro: humble
tested: false
audience: dev
summary: "ros2 action list/info -t for FollowJointTrajectory and GripperCommand servers, Auto Add controllers, Author Information, Generate Package my_moveit_config, SRDF group_state."
tags: [MoveIt Setup Assistant, MoveIt Controllers, Auto Add FollowJointsTrajectory, ros2 action list, ros2 action info, FollowJointTrajectory, GripperCommand, joint_trajectory_controller, gripper_controller, Author Information, Generate Package, my_moveit_config, SRDF, group_state, Edit Existing MoveIt Configuration Package]
see: ["[[moveit-setup-assistant-model]]", "[[moveit-config-controllers-yaml]]", "[[moveit-config-joint-limits]]", "[[control-jtc-commands]]", "[[core-action-cli-status]]"]
requires: [ros2-core, ros2-control]
version_notes:
  - "humble: 'Auto Add FollowJointsTrajectory Controllers For Each Planning Group' names each controller <group>_controller; the ROS 2 Controllers tab has its own 'Auto Add JointTrajectoryController Controllers For Each Planning Group' — https://github.com/moveit/moveit2/blob/humble/moveit_setup_assistant/moveit_setup_controllers/src/controllers.cpp (MOVEIT-V22)"
  - "humble: the configuration is read when move_group, RViz2 and the programs start: after a change rebuild and restart them; the course says restart the simulation (MOVEIT-V29)"
---
# MoveIt Setup Assistant (2/2): controllers, author, generate, edit

**TL;DR** MoveIt executes plans through the robot's controller **action servers**. Find their names and types with `ros2 action list` / `ros2 action info -t`, let the Setup Assistant add one controller per planning group, then fill in the author and generate the package into `~/ros2_ws/src/my_moveit_config`. The generated controller file needs fixes ([[moveit-config-controllers-yaml]]), and so does `joint_limits.yaml` ([[moveit-config-joint-limits]]).

## Find the controllers of the robot (simulation running)
```bash
ros2 action list
```
```
/gripper_controller/gripper_cmd
/joint_trajectory_controller/follow_joint_trajectory
```
```bash
ros2 action info /joint_trajectory_controller/follow_joint_trajectory -t
```
```
Action: /joint_trajectory_controller/follow_joint_trajectory
Action clients: 0
Action servers: 1
    /joint_trajectory_controller [control_msgs/action/FollowJointTrajectory]
```
The arm controller is a joint trajectory controller (JTC, [[control-jtc-commands]]): name `joint_trajectory_controller`, type `FollowJointTrajectory`. The gripper server is of another type (`GripperCommand`, [[moveit-config-controllers-yaml]]).

## Remaining tabs
1. **MoveIt Controllers**: click **Auto Add FollowJointsTrajectory Controllers For Each Planning Group**. It adds one `FollowJointTrajectory` controller per group, named `<group>_controller` (`ur_manipulator_controller`, `gripper_controller`, MOVEIT-V22); both are adjusted later by hand. (The **ROS 2 Controllers** tab has its own auto-add button for `ros2_controllers.yaml`.)
2. **Author Information**: your name and e-mail (required).
3. **Configuration Files**: **Browse**, go to `ros2_ws/src`, create a folder `my_moveit_config`, choose it, click **Generate Package**.
4. Build:
```bash
cd ~/ros2_ws
colcon build
source install/setup.bash
```

## Edit the package later
- A missed named pose (or a new one) goes into the SRDF, `config/<robot_name>.srdf` (the course's robot is called `name`, so `name.srdf`), inside `<robot>`:
```xml
<!--GROUP STATES: Purpose: Define a named state for a particular group, in terms of joint values. This is useful to define states like 'folded arms'-->
<group_state name="home" group="ur_manipulator">
    <joint name="elbow_joint" value="1.5"/>
    <joint name="shoulder_lift_joint" value="-2.5"/>
    <joint name="shoulder_pan_joint" value="0"/>
    <joint name="wrist_1_joint" value="-1.5"/>
    <joint name="wrist_2_joint" value="-1.55"/>
    <joint name="wrist_3_joint" value="0"/>
</group_state>
```
- To fix any setting, start the Setup Assistant and choose **Edit Existing MoveIt Configuration Package**, then your package.
- After a change, rebuild and restart `move_group` (and RViz2 and your programs): they read the configuration only when they start (MOVEIT-V29; the course says to restart the simulation).

## Pitfalls
- The generated controller names (`ur_manipulator_controller`) rarely match the robot's: the arm then plans but never moves ([[moveit-config-controllers-yaml]]).
- Run `ros2 action list` with the simulation (or the real robot's driver) running, or there is nothing to list.
