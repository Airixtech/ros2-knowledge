---
id: tf-learn-unit2-tools
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "TF unit 2: Cam_bot and turtle, view_frames, rqt_tf_tree, tf2_echo, RViz2 and the follower"
domain: tf
area: learn
distro: jazzy
tested: false
audience: students
summary: "TF unit 2: Cam_bot and turtle scene, examples 2.3.1–2.6.1 with view_frames, rqt_tf_tree, tf2_echo, RViz2 and cam_bot_follower.py."
tags: [unit 2, example 2.3.1, example 2.4.1, example 2.5.1, example 2.6.1, Cam_bot, turtle, turtle_attach_frame, cam_bot_follower.py, turtle_tf_3d_ros2, /turtle_cmd_vel, tf_ros2_course.rviz]
see: ["[[tf-learn-start-here]]", "[[tf-view-frames]]", "[[tf-echo]]", "[[tf-rviz]]"]
requires: [ros2-core]
version_notes:
  - "course: the command passes offset_xyz:=\"[0.0, 0.0, 0.0]\", the explanation shows 0.6 (TF-V09); cam_bot_follower.py is the program written in unit 3 as move_generic_model.py (TF-V10)"
---
# TF unit 2: tools and visualization

**TL;DR** Two robots, the Cam_bot and the turtle, and one question: where is the turtle? The unit answers it with the TF tools: `view_frames` (PDF), `rqt_tf_tree` (live tree), `tf2_echo` (any transform) and RViz2, and ends with the Cam_bot following a frame attached to the turtle.

## The scene (2.2–2.3)
The **Cam_bot** has a camera on its front, moves anywhere in space with any orientation, and follows whatever robot frame you tell it to. The **turtle** behaves like a 3D turtlesim (forward/backward and turn, not sideways). To make the Cam_bot follow the turtle you must know where the turtle is, place the Cam_bot at a fixed pose relative to it, and compute the motion when the turtle moves: all of it is transforms between frames ([[tf-frames-tree]]). A camera only says that it sees a turtle, not where it is.

## Examples
| Example | Do | Note |
|---|---|---|
| 2.3.1 | wait until both robots are loaded (zoom out), `ros2 run tf2_tools view_frames`, open `frames_<date>.pdf`: 16 frames, root `world` | [[tf-view-frames]] |
| 2.4.1 | `ros2 run rqt_tf_tree rqt_tf_tree`, refresh, zoom with the wheel | [[tf-view-frames]] |
| 2.5.1 | `ros2 topic echo /tf`, then `ros2 run tf2_ros tf2_echo rgb_camera_link_frame turtle_chassis` while driving the turtle | [[tf-echo]] |
| 2.6.1 | RViz2 with both robots, the camera image and TF; then the follower | below |

Drive the turtle in every example with:
```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args --remap cmd_vel:=/turtle_cmd_vel
```

## Example 2.6.1
1. Source the simulation workspace, start `rviz2`, Fixed Frame `/world` (RViz strips the leading slash; tf2 tools need plain `world`).
2. Two RobotModel displays, renamed `TurtleRobotModel` and `CamBotRobotModel`, reading `turtle_robot_description` and `cam_bot_robot_description`; check their QoS.
3. An Image display on `/camera/image_raw` with the right QoS; a TF display with Marker Scale 1.0.
4. Save the configuration in `/home/user/ros2_ws/src/` as `tf_ros2_course.rviz`.
5. A frame, `turtle_attach_frame`, always follows the turtle. Tell the Cam_bot to copy its position and orientation:
```bash
ros2 run turtle_tf_3d_ros2 cam_bot_follower.py --ros-args -p model_name:=cam_bot -p fixed_frame:=world -p target_frame:=turtle_attach_frame -p offset_xyz:="[0.0, 0.0, 0.0]" -p rate_hz:=30.0
```
`model_name` = Gazebo model to move, `fixed_frame` = reference TF frame, `target_frame` = frame to follow, `offset_xyz` = offset in meters in the target frame (for example `"[0.0, 0.0, 0.6]"` to stay above it), `rate_hz` = update rate. The Cam_bot now follows the turtle and its camera always sees it. How the program works: note `gazebo-tf-follow-frame` of the skill ros2-gazebo (it is the `move_generic_model.py` of unit 3).

RViz2 also tells you about problems: a transform that stops being published turns grey and disappears, and nothing that needs TF is drawn with a wrong fixed frame or a tree broken into several roots ([[tf-rviz]]).
