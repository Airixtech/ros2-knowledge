---
id: tf-static-publisher
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "static_transform_publisher: rpy and quaternion flags, launch file, /tf_static, joining two trees"
domain: tf
area: broadcast
distro: jazzy
tested: false
audience: dev
summary: "static_transform_publisher --x --y --z --roll --pitch --yaw (radians) or --qx..--qw, --frame-id --child-frame-id; launch Node; /tf_static latched; join two trees."
tags: [static_transform_publisher, tf2_ros, static transform, /tf_static, TRANSIENT_LOCAL, --frame-id, --child-frame-id, roll pitch yaw, radians, quaternion, launch file, publish_static_transform_odom_to_world.launch.py, world, odom]
see: ["[[tf-static-python]]", "[[tf-frames-tree]]", "[[tf-odom-broadcaster]]", "[[core-tf-basics]]", "[[core-launch-basics]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: angles are radians (usage text: 'roll, pitch, yaw euler angles in radians'; tf2 tutorial: 'In ROS 2, roll/pitch/yaw refers to rotation in radians'; REP 103) — https://github.com/ros2/geometry2/blob/jazzy/tf2_ros/src/static_transform_broadcaster_program.cpp, https://docs.ros.org/en/jazzy/Tutorials/Intermediate/Tf2/Writing-A-Tf2-Static-Broadcaster-Py.html (TF-V01)"
  - "humble/jazzy/kilted: the positional form 'x y z yaw pitch roll frame_id child_frame_id' still works with 'Old-style arguments are deprecated'; lyrical: not parsed, exits 'Frame id must not be empty' — https://github.com/ros2/geometry2/blob/lyrical/tf2_ros/src/static_transform_broadcaster_program.cpp (TF-V01)"
  - "jazzy: rpy and quaternion flags cannot be mixed ('Cannot specify both quaternion and Euler rotations'); /tf_static is TRANSIENT_LOCAL, published once and kept for late listeners while the publisher runs (TF-V22)"
  - "jazzy: without name= the node is static_transform_publisher_<random> (TF-V30)"
  - "humble: same flags — https://docs.ros.org/en/humble/Tutorials/Intermediate/Tf2/Writing-A-Tf2-Static-Broadcaster-Py.html (TF-V01)"
  - "course: 1.5 gives the positional form 'in degrees' (TF-V01); the 3.7 reminders swap parent and child (TF-V06)"
---
# static_transform_publisher: CLI, launch file, joining two trees

**TL;DR** Static transforms are for TFs that do **not** change over time. They go on `/tf_static`, published once and kept (latched) for late listeners, so they cost almost nothing. Publish one from the command line, a launch file or a program ([[tf-static-python]]). Angles are **radians**.

## Command line
```bash
# Option 1: XYZ + roll-pitch-yaw (radians)
ros2 run tf2_ros static_transform_publisher --x x --y y --z z --yaw yaw --pitch pitch --roll roll --frame-id frame_id --child-frame-id child_frame_id
# Option 2: XYZ + quaternion (XYZW)
ros2 run tf2_ros static_transform_publisher --x x --y y --z z --qx qx --qy qy --qz qz --qw qw --frame-id frame_id --child-frame-id child_frame_id
```
`--frame-id` is the parent, `--child-frame-id` the new frame; with no translation or orientation flags the identity transform is published. Do not mix rpy and quaternion flags. Every frame has six degrees of freedom: three translations (meters) and three rotations (radians). The old positional form `x y z yaw pitch roll frame_id child_frame_id`, which the course shows first "in degrees", takes **radians** too and is deprecated; Lyrical no longer accepts it.

Example: a frame for the rock, 4 m along y from the robot's odometry frame:
```bash
ros2 run tf2_ros static_transform_publisher --x 0 --y 4.0 --z 0 --roll 0 --pitch 0 --yaw 0 --frame-id deepmind_robot1_odom --child-frame-id rock
```
```text
[INFO] [1702566939.440495975] [static_transform_publisher_BXol3vQrgh8yCw89]: Spinning until stopped - publishing transform
translation: ('0.000000', '4.000000', '0.000000')
rotation: ('0.000000', '0.000000', '0.000000', '1.000000')
from 'deepmind_robot1_odom' to 'rock'
```
The node keeps running ("spinning"); the `rock` frame appears in RViz linked to `deepmind_robot1_odom` by an arrow, and it stays put while the robot moves.

## Launch file: join the two robots' trees
```bash
cd ~/ros2_ws/src/my_tf_ros2_course_pkg
mkdir launch
touch launch/publish_static_transform_odom_to_world.launch.py
chmod +x launch/publish_static_transform_odom_to_world.launch.py
```
Install the folder with `install(DIRECTORY launch DESTINATION share/${PROJECT_NAME}/)` ([[tf-odom-broadcaster]]).
```python
#! /usr/bin/env python3
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    static_tf_pub = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_transform_publisher_turtle_odom',
        output='screen',
        arguments=['--x', '0', '--y', '0', '--z', '0',
                   '--roll', '0', '--pitch', '0', '--yaw', '0',
                   '--frame-id', 'world', '--child-frame-id', 'odom', ],
    )

    return LaunchDescription([static_tf_pub])
```
The node publishes the static transform `world` (parent) → `odom` (child): the root of the Cam_bot tree becomes the parent of the turtle's tree. With the odometry broadcaster running too (`world → camera_bot_base_link`):
```bash
ros2 run my_tf_ros2_course_pkg cam_bot_odom_to_tf_pub_late_tf_fixed.py
ros2 launch my_tf_ros2_course_pkg publish_static_transform_odom_to_world.launch.py
ros2 run rqt_tf_tree rqt_tf_tree
```
the tree has one root, `world`, with `odom → turtle_base_link → …` and `camera_bot_base_link → chassis → rgb_camera_link_frame` below it; RViz places both robots, and they move correctly when driven.

## Pitfalls
- Degrees instead of radians → `--yaw 90` means 90 rad: 14 full turns plus 2.035 rad, a 116.6° rotation instead of 90° (use 1.5708).
- A frame that moves published as static → it never updates; use a broadcaster ([[tf-odom-broadcaster]]).
- Stopping the publisher → listeners that start later never get the frame ([[tf-static-python]]).
