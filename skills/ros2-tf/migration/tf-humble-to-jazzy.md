---
id: tf-humble-to-jazzy
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "TF course on Humble (+ Fortress) and Lyrical: what changes"
domain: tf
area: migration
distro: jazzy
tested: false
audience: dev
summary: "TF differences Humble/Jazzy/Lyrical: static_transform_publisher positional form, view_frames log and topics, RViz TF filters, listener topics, logger.warn, type hashes, Gazebo."
tags: [migration, humble, jazzy, kilted, lyrical, fortress, static_transform_publisher, view_frames, tf2_echo, TransformListener, tf_topic, StaticTransformListener, RViz TF display, logger.warn, Topic type hash, tf_transformations]
see: ["[[tf-static-publisher]]", "[[tf-view-frames]]", "[[tf-rviz]]", "[[tf-echo]]", "[[core-humble-to-jazzy]]", "[[core-jazzy-to-lyrical]]"]
requires: [ros2-core]
version_notes:
  - "humble: tf2 tutorials — https://docs.ros.org/en/humble/Tutorials/Intermediate/Tf2/Tf2-Main.html; lyrical: https://docs.ros.org/en/lyrical/ROS-Framework/client-libraries/Working-with-Client-Libraries/Tf2/Tf2-Main.html"
  - "lyrical: positional static_transform_publisher arguments not parsed — https://github.com/ros2/geometry2/blob/lyrical/tf2_ros/src/static_transform_broadcaster_program.cpp (TF-V01)"
  - "lyrical: TransformListener(tf_topic=, tf_static_topic=), tf2_ros.static_transform_listener, view_frames --tf_topic/--tf_static_topic — https://github.com/ros2/geometry2/blob/lyrical/tf2_ros_py/tf2_ros/transform_listener.py (TF-V29)"
  - "humble: no regex filters in the RViz TF display — https://github.com/ros2/rviz/blob/humble/rviz_default_plugins/src/rviz_default_plugins/displays/tf/tf_display.cpp (TF-V18)"
  - "humble: no Topic type hash in ros2 topic info -v, no get_type_description service — https://github.com/ros2/rclpy/blob/humble/rclpy/rclpy/topic_endpoint_info.py (TF-V28)"
  - "lyrical: get_logger().warn() removed (V22) (TF-V36)"
  - "humble/fortress: ros_gz_sim create options, bridge type names (gz.msgs accepted, GZ-V26) and the SetEntityPose service bridge are available — https://github.com/gazebosim/ros_gz/blob/humble/ros_gz_bridge/README.md (TF-V24, TF-V25)"
---
# TF course on Humble (+ Fortress) and Lyrical

**TL;DR** The TF code of the course runs unchanged on Humble: the tf2 Python API, the tools and robot_state_publisher are the same, and the Gazebo parts work with Fortress. What differs is small: some tool outputs and options, RViz filters, and on Lyrical the removal of old forms (positional `static_transform_publisher`, `logger.warn`).

| Topic | Humble (+ Fortress) | Jazzy (course) | Lyrical (+ Jetty) |
|---|---|---|---|
| `static_transform_publisher` | flags; positional form warns "Old-style arguments are deprecated" | same | flags only: positional arguments ignored, "Frame id must not be empty" |
| `view_frames` | same options (`-t`, `-o`); log "Generating graph in frames.pdf file..." whatever the file name | "Generating graph...", "Exporting graph in frames_<date>.pdf file..." | adds `--tf_topic`, `--tf_static_topic` |
| `tf2_echo` | `-r`; `-t` and `-p` since tf2_ros 0.25.15 | `-r`, `-t`, `-p` | same |
| RViz2 TF display | no Filter (whitelist/blacklist) | regex filters | same |
| `TransformListener` topics | fixed `/tf`, `/tf_static` | fixed | `tf_topic=`, `tf_static_topic=`; module `tf2_ros.static_transform_listener` |
| `get_logger().warn()` | deprecated alias | deprecated alias | removed: use `warning()` |
| `ros2 topic info -v`, `ros2 node info` | no `Topic type hash`, no `get_type_description` | both | both |
| `tf_transformations` | released 1.1.1 | released | released |
| Gazebo parts (create, bridge, `set_pose`) | same commands with Fortress; the bridge accepts the `gz.msgs` names | Harmonic | Jetty |

## Humble alternatives
- Regex filters of the TF display → untick frames one by one under **Frames** (the category exists in Humble).
- Other TF topics for a listener or `view_frames` → remap `/tf` and `/tf_static` with `--ros-args -r` `[verify]`.

Platform-wide changes (Python, Ubuntu, removed APIs): [[core-humble-to-jazzy]], [[core-jazzy-to-lyrical]].
