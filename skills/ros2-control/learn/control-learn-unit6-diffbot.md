---
id: control-learn-unit6-diffbot
type: reference
owner: equipo-ros2
updated: 2026-10-24
review_by: 2027-04-22
source: manual
confidentiality: internal
title: "Unit 6 exercise 6.7.1: diffbot with diff_drive_controller, spawn_diffbot, list_controllers, topics, circling"
domain: control
area: learn
distro: jazzy
tested: false
audience: students
summary: "Unit 6 exercise 6.7.1: diffbot_description xacro files, spawn_diffbot and diffbot_controllers launches, list_controllers, topic list, TwistStamped command."
tags: [unit 6, exercise 6.7.1, diffbot, diffbot_description, diffbot.ros2_control.xacro, diffbot.gazebo.xacro, spawn_diffbot.launch.py, diffbot_controllers.launch.py, diff_drive_controller, list_controllers, topic list, hands-on]
see: ["[[control-diff-drive-controller]]", "[[control-learn-unit6-controllers]]", "[[control-cli-list]]", "[[control-learn-unit7-custom]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: list_controllers prints columns (name, type, state), not name[type] — https://github.com/ros-controls/ros2_control/blob/jazzy/ros2controlcli/ros2controlcli/verb/list_controllers.py (CONTROL-V10)"
  - "jazzy: the controller manager topics introspection_data (≥ 4.27.0), activity (≥ 4.28.0), statistics (≥ 4.37.0); humble: none — https://github.com/ros-controls/ros2_control/blob/jazzy/controller_manager/CHANGELOG.rst (CONTROL-V71)"
  - "jazzy: the command with -1 is sent once and the robot brakes after 0.5 s (CONTROL-V54); the launch output's 'Sucessfully' is a typo (CONTROL-V72)"
---
# Unit 6 exercise 6.7.1: diffbot with diff_drive_controller, spawn_diffbot, list_controllers, topics, circling

**TL;DR** The last exercise of unit 6 drives a small differential drive robot with one controller for both wheels. The controller, its YAML and the URDF tags: [[control-diff-drive-controller]].

## Files
Package `diffbot_description` in `~/ros2_ws/src/ros2_control_course/unit5`: put the wheels' `<ros2_control>` tags into `robots/diffbot.ros2_control.xacro` and the gz_ros2_control plugin with `<parameters>$(find diffbot_description)/config/diff_drive_controller_config.yaml</parameters>` into `robots/diffbot.gazebo.xacro`, where its code comments show; create `diff_drive_controller_config.yaml` in `config/` (all three: [[control-diff-drive-controller]]).

## Run
Delete the previous robot from Gazebo, then:
```bash
cd ~/ros2_ws && colcon build
source ~/ros2_ws/install/setup.bash
ros2 launch spawn_robot spawn_diffbot.launch.py
ros2 launch diffbot_sim diffbot_controllers.launch.py
```
A small mobile robot appears. The second launch loads both controllers with `ros2 control load_controller --set-state active` and prints, among other lines, `[ros2-1] Successfully loaded controller joint_state_broadcaster into state active` (the course shows "Sucessfully"). Check:
```bash
ros2 control list_controllers
```
It lists `diffbot_base_controller` (`diff_drive_controller/DiffDriveController`) and `joint_state_broadcaster` (`joint_state_broadcaster/JointStateBroadcaster`), both `active`, in three columns: name, type, state (the course shows the older `name[type] state` form).

`ros2 topic list` shows, besides `/clock`, `/parameter_events` and `/rosout`: `/diffbot_base_controller/cmd_vel`, `/diffbot_base_controller/odom`, `/diffbot_base_controller/transition_event`, `/joint_state_broadcaster/transition_event`, `/joint_states`, `/dynamic_joint_states`, `/tf`, `/tf_static`, `/robot_description`, `/diagnostics` and the controller manager's topics:
- `/controller_manager/introspection_data/full`, `/controller_manager/introspection_data/names`, `/controller_manager/introspection_data/values` [≥Jazzy 4.27.0]
- `/controller_manager/activity` [≥Jazzy 4.28.0]
- `/controller_manager/statistics/full`, `/controller_manager/statistics/names`, `/controller_manager/statistics/values` [≥Jazzy 4.37.0]

## Drive
Publish the twist of [[control-diff-drive-controller]] **without** `-1`: the robot drives in a circle until Ctrl+C. With the course's `-1` it stops after half a second.

The unit shows that the included controllers are kept simple: a quick start when the robot must work soon.
