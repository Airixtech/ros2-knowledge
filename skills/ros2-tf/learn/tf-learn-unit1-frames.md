---
id: tf-learn-unit1-frames
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "TF unit 1: the rock frame with static_transform_publisher, TF and RobotModel in RViz2"
domain: tf
area: learn
distro: jazzy
tested: false
audience: students
summary: "TF unit 1: why frames (the rock problem), exercise 1.6.1 rock frame and TF display, exercise 1.7.1 RobotModel and move_head.py."
tags: [unit 1, exercise 1.6.1, exercise 1.7.1, rock, deepmind_robot1_odom, static_transform_publisher, RViz2, TF display, RobotModel, /robot_description, move_head.py, teleop_twist_keyboard]
see: ["[[tf-learn-start-here]]", "[[tf-frames-tree]]", "[[tf-rviz]]", "[[tf-static-publisher]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: static_transform_publisher takes radians with the --roll/--pitch/--yaw flags; the course's first positional form says degrees (TF-V01)"
  - "course: the text calls the new frame rock_frame, the command rock (TF-V37)"
---
# TF unit 1: frames, the rock frame, RViz2

**TL;DR** To send a robot near the big rock you need the rock's position as numbers, and numbers need a fixed reference: a coordinate frame. The unit creates a `rock` frame with `static_transform_publisher`, shows it in RViz2 with the TF display, and shows a robot's many link frames with RobotModel.

## The problem (1.2–1.4)
A human sees where the rock is; a robot needs precise values, and position coordinates have no meaning without a coordinate frame. The theory (frames, global and local frames, transforms, the tree) is in [[tf-frames-tree]]; the conventions (right-hand rule, x red / y green / z blue, a positive turn rate turns left) in [[core-tf-basics]].

## Exercise 1.6.1: the rock frame
1. `rviz2`: only Global Options, Global Status and Grid, and `Fixed Frame:  Frame [map] does not exist.` Choose the fixed frame `deepmind_robot1_odom` (created for you).
2. Add → TF, and look at its options ([[tf-rviz]]).
3. Publish the rock 4 m along y of that frame:
```bash
ros2 run tf2_ros static_transform_publisher --x 0 --y 4.0 --z 0 --roll 0 --pitch 0 --yaw 0 --frame-id deepmind_robot1_odom --child-frame-id rock
```
4. In RViz a new frame `rock` appears (enable Show Names; the course text once calls it `rock_frame`, the command names it `rock`), with an arrow to `deepmind_robot1_odom`: the static transform you just ran. Static transforms are for objects that do not move, and the rock is the most static object there is.
5. Drive the robot with `ros2 run teleop_twist_keyboard teleop_twist_keyboard` and check that all the robot's frames update while `rock` does not move.

## Exercise 1.7.1: the robot's frames
Robot models are written in URDF and xacro (skill ros2-urdf); each joint has one coordinate frame, so you can track where every link is. RViz shows the frames with the 3D meshes: that is not the simulation, it is the coordinate frames drawn with meshes.
1. Add → RobotModel; **Description Source** = Topic, **Description Topic** = `/robot_description`.
2. Move the head (neck left/right angle, up/down angle, whole seconds for the movement):
```bash
ros2 run deepmind_bot_trajectory_sender move_head.py 0.5 0.0 1
```
(after sourcing the course's simulation workspace). Each red-green-blue triad is one frame; even a medium-sized robot uses dozens, and the rest of the course is about tools and methods to manage them.
