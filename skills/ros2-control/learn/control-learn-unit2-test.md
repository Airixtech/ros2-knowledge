---
id: control-learn-unit2-test
type: reference
owner: equipo-ros2
updated: 2026-10-24
review_by: 2027-04-22
source: manual
confidentiality: internal
title: "Unit 2 exercises 2.6–2.7: test the pipeline, add joint2"
domain: control
area: learn
distro: jazzy
tested: false
audience: students
summary: "Unit 2 exercises 2.6.1–2.7.1: launch my_robot.launch.py, publish one-joint commands, add joint2 to YAML and xacro, publish two-joint commands."
tags: [unit 2, exercise 2.6.1, exercise 2.7.1, my_robot.launch.py, forward_position_controller, Float64MultiArray, joint2, hands-on]
see: ["[[control-learn-unit2-setup]]", "[[control-controller-config]]", "[[control-urdf-tag]]", "[[control-bringup-sim-launch]]", "[[control-learn-unit3-manager]]"]
requires: [ros2-core]
version_notes: []
---
# Unit 2 exercises 2.6–2.7: test the pipeline, add joint2

**TL;DR** With a few setup steps and no development, the robot moves by publishing on a topic. Then extend the files so that ros2_control drives both joints.

## Exercise 2.6.1: test
```bash
ros2 launch my_robot_bringup my_robot.launch.py
```
The console confirms that `joint_state_broadcaster` and `forward_position_controller` were loaded, configured and started. The robot appears in Gazebo; one segment stands up and the other falls: intended, only `joint1` is controlled. `ros2 topic list` shows `/forward_position_controller/commands`. The topic takes the positions of the rotary joints in radians:
```bash
ros2 topic pub /forward_position_controller/commands std_msgs/msg/Float64MultiArray "data:
- 0.79" -1
ros2 topic pub /forward_position_controller/commands std_msgs/msg/Float64MultiArray "data:
- -0.79" -1
```
Stop the launched processes with Ctrl+C before the next exercise.

## Exercise 2.7.1: control joint2 too
Why does the second arm swirl? Nobody controls `joint2`. Add it:
- `controller_configuration.yaml`: `joint2` under `joints` of both controllers (the full file: [[control-controller-config]]).
- `rrbot.xacro`: a second `<joint name="joint2">` block inside `<ros2_control>`, the same as `joint1` (the full block: [[control-urdf-tag]]).

Remove the robot from the simulation before launching again, or the updated model does not appear. Then:
```bash
ros2 launch my_robot_bringup my_robot.launch.py
ros2 topic pub /forward_position_controller/commands std_msgs/msg/Float64MultiArray "data:
- 1.57
- -1.57" -1
ros2 topic pub /forward_position_controller/commands std_msgs/msg/Float64MultiArray "data:
- -1.57
- 0.79" -1
```
Both joints move to each pair of positions. The unit has covered: configuring controllers, updating the robot description, and starting and commanding ros2_control.
