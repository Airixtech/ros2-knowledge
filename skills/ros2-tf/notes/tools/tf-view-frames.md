---
id: tf-view-frames
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "view_frames and rqt_tf_tree: draw the TF tree and read its edge data"
domain: tf
area: tools
distro: jazzy
tested: false
audience: dev
summary: "view_frames writes frames_<date>.pdf after listening 5 s; rqt_tf_tree shows the tree live; edge data: broadcaster, rate, buffer length, static 10000/0.0."
tags: [view_frames, tf2_tools, frames.pdf, frames.gv, graphviz, rqt_tf_tree, TF tree, default_authority, average rate, buffer length, most recent transform, static transform]
see: ["[[tf-frames-tree]]", "[[tf-echo]]", "[[tf-monitor-stamps]]", "[[core-tf-basics]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: view_frames -t/--wait-time (default 5.0 s), -o/--output; writes frames_<date>.gv and frames_<date>.pdf with graphviz dot; logs 'Generating graph...' then 'Exporting graph in frames_<date>.pdf file...' — https://github.com/ros2/geometry2/blob/jazzy/tf2_tools/tf2_tools/view_frames.py (TF-V19)"
  - "humble: same options and files; the log says 'Generating graph in frames.pdf file...' whatever the real file name — https://github.com/ros2/geometry2/blob/humble/tf2_tools/tf2_tools/view_frames.py (TF-V19)"
  - "lyrical: view_frames adds --tf_topic and --tf_static_topic — https://github.com/ros2/geometry2/blob/lyrical/tf2_tools/tf2_tools/view_frames.py (TF-V19, TF-V29)"
  - "jazzy: rate = samples / max(time span, 100 µs), so a single static sample shows rate 10000 and most recent 0.0 — https://github.com/ros2/geometry2/blob/jazzy/tf2/src/buffer_core.cpp (TF-V20)"
  - "course text: '/hose/user', 'around 5.2Hz' and '4.93 seconds' do not match its output; its PDF transcription misplaces turtle_attach_frame (TF-V13, TF-V33)"
  - "humble/jazzy/lyrical: rqt_tf_tree released 1.1.1 (branch humble; master for jazzy and later) — https://github.com/ros/rosdistro/blob/master/jazzy/distribution.yaml (TF-V32)"
---
# view_frames and rqt_tf_tree

**TL;DR** `ros2 run tf2_tools view_frames` listens to TF for 5 s and writes the tree as a PDF in the current directory; `ros2 run rqt_tf_tree rqt_tf_tree` shows the same tree live, refreshed with a button. Both tell you, per edge, who broadcasts it, how often, and whether it is static.

## view_frames
```bash
ros2 run tf2_tools view_frames            # -t 10 listens 10 s; -o mytree writes mytree.gv / mytree.pdf
```
```text
[INFO] [1766503787.630028185] [view_frames]: Listening to tf data for 5.0 seconds...
[INFO] [1766503792.637909135] [view_frames]: Generating graph...
[INFO] [1766503792.641426296] [view_frames]: Result:tf2_msgs.srv.FrameGraph_Response(frame_yaml="odom: \n  parent: 'world'\n  broadcaster: 'default_authority'\n  rate: 10000.000\n  most_recent_transform: 0.000000\n  oldest_transform: 0.000000\n  buffer_length: 0.000\ncamera_bot_base_link: \n  parent: 'world'\n  broadcaster: 'default_authority'\n  rate: 50.228\n  most_recent_transform: 2754.860000\n  oldest_transform: 2750.480000\n  buffer_length: 4.380\n ...")
[INFO] [1766503792.649629564] [view_frames]: Exporting graph in frames_2025-12-23_15.29.52.pdf file...
```
The file `frames_<date>.pdf` (and its source `.gv`) lands where you ran the command (`/home/user` in the course); open it in any PDF viewer. The robots must be fully loaded first: the course scene has **16 frames**; fewer means a robot is missing.

## The tree (course scene, shortened)
```text
world
├── camera_bot_base_link      20.136 Hz, buffer 4.42 s
│   └── chassis               static
│       └── rgb_camera_link_frame   static
└── odom                      static
    └── turtle_base_link      100.248 Hz, buffer 4.04 s
        └── turtle_chassis    static
            ├── turtle_attach_frame              static
            ├── back_yaw_link → back_roll_link → back_pitch_link     18.382 Hz each
            ├── front_yaw_link → front_roll_link → front_pitch_link  18.382 Hz each
            ├── left_wheel    18.382 Hz
            └── right_wheel   18.382 Hz
```
`world` is the root.

## Reading an edge
| Field | Meaning |
|---|---|
| Broadcaster | who publishes it (`default_authority` in ROS 2) |
| Average rate | messages per second over the buffer |
| Buffer length | seconds of this transform kept in the listener's buffer |
| Most recent / Oldest transform | stamps of the newest and oldest sample |

**Static transform**: rate **10000.0**, buffer **0.0**, most recent **0.0**. One sample with stamp 0, and the rate formula divides by at least 100 µs.

## rqt_tf_tree
```bash
ros2 run rqt_tf_tree rqt_tf_tree          # package ros-<distro>-rqt-tf-tree
```
Same information as `view_frames`, with one benefit: press the refresh button to see changes in real time without generating a new PDF; zoom with the mouse wheel. Use it while testing a new broadcaster to check that the transform is actively published, not an outdated one.

## Pitfalls
- Fewer frames than expected → a robot or broadcaster is not running yet; reload the simulation and run the tool again.
- Two roots in the drawing → two separate trees ([[tf-frames-tree]]).
- `dot` not found → install graphviz; `view_frames` calls it to make the PDF.
