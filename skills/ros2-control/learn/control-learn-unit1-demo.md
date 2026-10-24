---
id: control-learn-unit1-demo
type: reference
owner: equipo-ros2
updated: 2026-10-24
review_by: 2027-04-22
source: manual
confidentiality: internal
title: "Unit 1 demo: load the controllers, publish forward commands, switch to the trajectory controller"
domain: control
area: learn
distro: jazzy
tested: false
audience: students
summary: "Unit 1 exercises 1.1.1–1.1.3: course packages, load_controllers.launch.py output, forward command topic, switch_controllers to position_trajectory_controller, joint_trajectory_publisher."
tags: [unit 1, rrbot, rrbot_sim, load_controllers.launch.py, forward_position_controller, position_trajectory_controller, switch_controllers, joint_trajectory_demo, joint_trajectory_publisher.launch.py, Float64MultiArray]
see: ["[[control-learn-start-here]]", "[[control-cli-state-changes]]", "[[control-cli-list]]", "[[control-jtc-parameters]]", "[[control-learn-unit2-setup]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: 'Successfully loaded controller X into state active' is ros2 control load_controller --set-state (CONTROL-V41)"
---
# Unit 1 demo: load the controllers, publish forward commands, switch to the trajectory controller

**TL;DR** A preview of the course: the rrbot arm in Gazebo Sim, three controllers loaded for you, one topic to move the joints, then a switch to a controller that follows whole trajectories.

## Start
Start the unit's simulation with the course's script and wait until the arm is visible and the view can be moved with the mouse: before that, the controllers fail to load.

## Exercise 1.1.1: course packages and controllers
```bash
cd ~/ros2_ws/src
git clone -b jazzy <course repository>      # link given in the course
cd ~/ros2_ws/ && colcon build
source install/setup.bash
ros2 launch rrbot_sim load_controllers.launch.py   # after sourcing the course's simulation workspace
```
```text
[ros2-1] Successfully loaded controller joint_state_broadcaster
[ros2-3] Successfully loaded controller position_trajectory_controller
[ros2-1] Successfully loaded controller joint_state_broadcaster into state active
[ros2-3] Successfully loaded controller position_trajectory_controller into state inactive
[ros2-2] Successfully loaded controller forward_position_controller
[ros2-2] Successfully loaded controller forward_position_controller into state active
```
These are `ros2 control load_controller --set-state …` messages ([[control-cli-state-changes]]): the broadcaster and the forward controller active, the trajectory controller inactive (both claim the same joints). `ros2 topic list` shows the topics the controllers subscribe to:
```text
/forward_position_controller/commands
/position_trajectory_controller/joint_trajectory
```

## Exercise 1.1.2: publish joint commands
```bash
ros2 topic pub /forward_position_controller/commands std_msgs/msg/Float64MultiArray "data:
- 1.57
- -1.57" -1
```
One value per joint in radians; try other values.

## Exercise 1.1.3: follow a trajectory
```bash
ros2 control switch_controllers --deactivate forward_position_controller --activate position_trajectory_controller
```
```text
Successfully switched controllers!
Deactivated controllers: [ forward_position_controller ]
Activated controllers: [ position_trajectory_controller ]
```
```bash
ros2 launch joint_trajectory_demo joint_trajectory_publisher.launch.py
```
The arm follows a sequence of movements. Stop everything with Ctrl+C before the next unit.
