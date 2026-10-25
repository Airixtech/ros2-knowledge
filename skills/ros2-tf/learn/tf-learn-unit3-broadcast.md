---
id: tf-learn-unit3-broadcast
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "TF unit 3: two trees, odometry broadcaster, tf2_monitor fix, static frames, follow a frame"
domain: tf
area: learn
distro: jazzy
tested: false
audience: students
summary: "TF unit 3: two-tree scene, exercise 3.2.1, examples 3.2.1, 3.3.2, 3.4.1, tf2_monitor fix, world→odom launch, start_tf_fixes.launch.xml."
tags: [unit 3, exercise 3.2.1, example 3.2.1, example 3.3.2, example 3.4.1, two trees, camera_bot_base_link, cam_bot_teleop.py, unit3_config.rviz, start_tf_fixes.launch.xml, move_generic_model.py, my_front_turtle_frame]
see: ["[[tf-learn-start-here]]", "[[tf-odom-broadcaster]]", "[[tf-monitor-stamps]]", "[[tf-static-publisher]]", "[[tf-static-python]]"]
requires: [ros2-core]
version_notes:
  - "course: the scene text says cam_bot_base_link; the frame is camera_bot_base_link (TF-V11)"
  - "course: killing the static broadcaster before the follower starts leaves the follower without my_front_turtle_frame (TF-V35, [verify])"
  - "course: the 3.7 reminders swap parent and child (TF-V06)"
---
# TF unit 3: broadcasting and listening

**TL;DR** The scene starts broken on purpose: the Cam_bot publishes no `world → camera_bot_base_link`, and the turtle's `odom` tree is not connected to `world`, so there are **two trees**, one per robot. You fix it step by step: an odometry broadcaster for the Cam_bot, a timestamp fix found with `tf2_monitor`, a static `world → odom` transform, a static frame in front of the turtle, and a listener that makes the Cam_bot follow it.

## The scene (3.2) and exercise 3.2.1
1. Source the simulation workspace and run `rviz2`. Add two RobotModel displays (`/cam_bot_robot_description` and the turtle's topic), TF, Fixed Frame `world`, and an Image display on `/camera/image_raw` with the QoS read from `ros2 topic info -v /camera/image_raw`.
2. Save the configuration as `~/ros2_ws/src/unit3_config.rviz` and reopen it later with `rviz2 -d ~/ros2_ws/src/unit3_config.rviz`.
3. Both models are white and overlap: no transform from `world` to either root ([[tf-rviz]]). Fixed Frame `chassis` shows the Cam_bot correctly, `turtle_chassis` the turtle.
4. Drive the Cam_bot: `ros2 run turtle_tf_3d_ros2 cam_bot_teleop.py` (W/S ±X, A/D ±Y, R/F ±Z, Q/E ±yaw, X resets the pose, Ctrl+C exits). The camera image moves, the model in RViz does not.
5. `ros2 run rqt_tf_tree rqt_tf_tree`: two roots, `camera_bot_base_link` and `odom`, and no `world`. Close RViz and rqt_tf_tree before going on.

## Example 3.2.1: odometry → TF
Restart the simulation, create `my_tf_ros2_course_pkg` and `scripts/cam_bot_odom_to_tf_pub.py`, which subscribes to `/cam_bot_odom` and broadcasts `world → camera_bot_base_link` ([[tf-odom-broadcaster]]). The course calls it a static transform; it is a dynamic one on `/tf`. Build, run, open `unit3_config.rviz`, drive the Cam_bot: it now moves in RViz, and rqt_tf_tree shows `world → camera_bot_base_link` next to the separate `odom` tree.

## 3.4: the timestamp fix
`tf2_monitor` shows huge delays for the static camera frames and 4.4 ms for `world → camera_bot_base_link`; the fixed script `cam_bot_odom_to_tf_pub_late_tf_fixed.py` stamps the transform with the odometry time:
```bash
cd ~/ros2_ws/src
touch my_tf_ros2_course_pkg/scripts/cam_bot_odom_to_tf_pub_late_tf_fixed.py
chmod +x my_tf_ros2_course_pkg/scripts/cam_bot_odom_to_tf_pub_late_tf_fixed.py
```
Add it to `install(PROGRAMS …)`, build, run it instead of the first script, and open `unit3_config.rviz` again. Why, and what the numbers really mean: [[tf-monitor-stamps]].

## 3.5–3.7: join the trees
Static transforms through the command line, a program or a launch file ([[tf-static-publisher]]). With `cam_bot_odom_to_tf_pub_late_tf_fixed.py` running, launch `publish_static_transform_odom_to_world.launch.py`: it publishes the static `world` (parent) → `odom` (child), so the tree has a single root `world`. Drive both robots (`cam_bot_teleop.py` and the turtle teleop with `--remap cmd_vel:=/turtle_cmd_vel`): RViz shows them where the simulation has them.

## Example 3.3.2: a frame in front of the turtle
`static_broadcaster_front_turtle_frame.py turtle_chassis my_front_turtle_frame 0.4 0 0.4 0 0.7 3.1416` ([[tf-static-python]]). The frame moves with the turtle because its parent does.

## Example 3.4.1: follow the frame
A TF listener reads `odom → my_front_turtle_frame` and moves the Cam_bot there through Gazebo's `set_pose` service (`scripts/move_generic_model.py`; the program and the service bridge are in the note `gazebo-tf-follow-frame` of the skill ros2-gazebo). A launch file starts everything the follower needs:
```bash
cd ~/ros2_ws/src/my_tf_ros2_course_pkg/launch/
touch start_tf_fixes.launch.xml
```
```xml
<?xml version="1.0" encoding="UTF-8"?>
<launch>
  <include file="$(find-pkg-share my_tf_ros2_course_pkg)/launch/publish_static_transform_odom_to_world.launch.py"/>
  <node pkg="my_tf_ros2_course_pkg" exec="cam_bot_odom_to_tf_pub_late_tf_fixed.py" name="cam_bot_odom_to_tf_pub_late_tf_fixed_node"></node>
  <node pkg="my_tf_ros2_course_pkg" exec="move_generic_model.py" name="move_generic_model_node"></node>
</launch>
```
Order of the course: build; run `static_broadcaster_front_turtle_frame.py …` (see above); `ros2 launch my_tf_ros2_course_pkg start_tf_fixes.launch.xml`; after some seconds the Cam_bot sits at `my_front_turtle_frame`; open `unit3_config.rviz`; drive the turtle and the Cam_bot follows. The course stops the static broadcaster with CTRL+C before the launch: keep it running instead, since a listener that starts later cannot receive a static frame whose publisher is gone (TF-V35 `[verify]`).
