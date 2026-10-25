---
id: tf-echo
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "Read transforms: ros2 topic echo /tf vs tf2_echo between any two connected frames"
domain: tf
area: tools
distro: jazzy
tested: false
audience: dev
summary: "ros2 topic echo /tf shows only direct transforms; tf2_echo source_frame target_frame computes any connected pair: target's pose in source."
tags: [tf2_echo, ros2 topic echo /tf, /tf, /tf_static, lookupTransform, source_frame, target_frame, indirect transform, Waiting for transform, teleop_twist_keyboard]
see: ["[[tf-frames-tree]]", "[[tf-view-frames]]", "[[core-tf-listener]]", "[[core-tf-basics]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: tf2_echo source_frame target_frame [-r rate] [-t time] [-p precision] runs lookupTransform(source, target): 'the transform to get data from target_frame into the source_frame'; logs 'Waiting for transform A ->  B: …' each second until it exists — https://github.com/ros2/geometry2/blob/jazzy/tf2_ros/src/tf2_echo.cpp (TF-V21)"
  - "humble: same usage and output; -t and -p since tf2_ros 0.25.15 — https://github.com/ros2/geometry2/blob/humble/tf2_ros/src/tf2_echo.cpp (TF-V21)"
  - "jazzy: frame ids must not start with '/' ('in tf2 frame_ids cannot start with a /') — https://github.com/ros2/geometry2/blob/jazzy/tf2/src/buffer_core.cpp"
---
# Read transforms: `ros2 topic echo /tf` vs `tf2_echo`

**TL;DR** Transforms are plain topics: `/tf` and `/tf_static` carry every published transform, but only from each frame to the next connected one. `tf2_echo` filters one pair and, more importantly, **computes an indirect transform** between two connected frames that are not directly linked.

## Raw topic
```bash
ros2 topic echo /tf          # add --once for one message
```
```yaml
transforms:
- header:
    stamp:
      sec: 4501
      nanosec: 299000000
    frame_id: odom
  child_frame_id: turtle_base_link
  transform:
    translation:
      x: -0.0026619430167396235
      y: -1.0362233570186838
      z: 0.05966079087107041
    rotation:
      x: -0.0033527500224697616
      y: -2.7084494229150955e-05
      z: 0.008117683583956063
      w: 0.9999614300296525
```
A lot of data arrives every second, and none of it relates frames that are not neighbours.

## tf2_echo
```bash
ros2 run tf2_ros tf2_echo [reference_frame] [target_frame]     # usage: tf2_echo source_frame target_frame [-r rate]
ros2 run tf2_ros tf2_echo rgb_camera_link_frame turtle_chassis
```
- It prints, once per second (`-r` changes the rate), the position and orientation of the **second** frame expressed in the **first** one: `lookupTransform(source_frame, target_frame)`, "the transform to get data from target_frame into the source_frame". Output: `At time <sec>.<nanosec>`, `- Translation: [x, y, z]`, `- Rotation: in Quaternion (xyzw) [...]`, `- Rotation: in RPY (radian) [...]` and `(degree)`, `- Matrix:`.
- Behind the result is the chain through the tree: here `rgb_camera_link_frame → chassis → camera_bot_base_link → world → odom → turtle_base_link → turtle_chassis` ([[tf-frames-tree]]).
- Until both frames are connected and buffered it logs `Waiting for transform rgb_camera_link_frame ->  turtle_chassis: …` with the reason (often "does not exist") every second; in the course scene the first values come after about 10 seconds.
- Move the turtle and watch the values change:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args --remap cmd_vel:=/turtle_cmd_vel
```
Keys: `u i o / j k l / m , .` move and turn (shift = holonomic), `t`/`b` up/down in z, `q/z` all speeds ±10 %, `w/x` linear only, `e/c` angular only, anything else stops, CTRL-C quits.

## Pitfalls
- A leading slash (`/turtle_chassis`) → invalid frame id in tf2; write `turtle_chassis`.
- Arguments swapped → you get the inverse transform; the first argument is the frame you express the result in.
- Endless "Waiting for transform" → the two frames are in different trees or one is not published; check with [[tf-view-frames]].
