---
id: tf-rviz
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "TF in RViz2: Fixed Frame, the TF display options, white robot models, several roots"
domain: tf
area: frames
distro: jazzy
tested: false
audience: dev
summary: "RViz2 and TF: existing Fixed Frame, TF display options (Frame Timeout, Marker Scale), RobotModel description topic, white models, image QoS."
tags: [RViz2, rviz2, Fixed Frame, TF display, Show Names, Show Axes, Show Arrows, Marker Scale, Update Interval, Frame Timeout, RobotModel, Description Topic, Image display, QoS, rviz2 -d]
see: ["[[tf-frames-tree]]", "[[tf-view-frames]]", "[[urdf-frames-rviz]]", "[[core-debug-tools]]"]
requires: [ros2-core, ros2-urdf]
version_notes:
  - "jazzy: TF display defaults Show Names off, Show Axes and Show Arrows on, Marker Scale 1, Update Interval 0, Frame Timeout 15 s (min 1); frames whose latest stamp is 0 (static) never fade — https://github.com/ros2/rviz/blob/jazzy/rviz_default_plugins/src/rviz_default_plugins/displays/tf/tf_display.cpp (TF-V18)"
  - "humble: same options and defaults, but no Filter (whitelist) / Filter (blacklist) regex fields: untick frames under Frames — https://github.com/ros2/rviz/blob/humble/rviz_default_plugins/src/rviz_default_plugins/displays/tf/tf_display.cpp (TF-V18)"
---
# TF in RViz2: Fixed Frame, TF display, robot models

**TL;DR** RViz2 draws everything relative to the **Fixed Frame**, which must exist in the TF tree (`world`, `map` or `odom` are the usual choices). Add a **TF** display to see the frames, a **RobotModel** per robot description topic, and remember: a model drawn white means there is no transform from the Fixed Frame to its root link.

## Fixed Frame
A fresh `rviz2` shows only Global Options, Global Status and Grid, with the error `Fixed Frame:  Frame [map] does not exist.` Pick an existing frame in the Global Options dropdown (the course uses `deepmind_robot1_odom`, later `world`). RViz2 has a built-in TransformListener on `/tf` and `/tf_static`; nothing that needs TF (sensor data, models) renders when the Fixed Frame is wrong or the tree is broken into several roots, a common issue with several robots.

## TF display (Add → TF)
| Option | Default | Effect |
|---|---|---|
| Show Names | off | 3D labels with the frame names |
| Show Axes | on | the frame axes: x red, y green, z blue |
| Show Arrows | on | arrows from child to parent |
| Marker Scale | 1 | size of names, axes and arrows (the course uses 1.0 and 5) |
| Update Interval | 0 | seconds between updates; 0 = every update cycle |
| Frame Timeout | 15 s | a frame not updated for 1/3 of it is drawn normally, fades to grey in the second third, then disappears; static frames never fade |
| Frames | all enabled | one checkbox per frame, with details on click |
| Tree | — | the whole tree with parent/child relations |
| Filter (whitelist / blacklist) | empty | regex on frame names [≥Jazzy] |

Showing only the frames of the current task keeps the view readable. A frame that stops being published turns grey and disappears, which tells you a broadcaster died.

## Robot models and images
- Add → RobotModel, **Description Source** = Topic, **Description Topic** = `/robot_description` (one RobotModel per robot: the course uses `/turtle_robot_description` and `/cam_bot_robot_description`; rename each display with Rename). Check its QoS settings.
- Source the workspace that installs the meshes before starting `rviz2`, or the models have no meshes.
- Add → Image, topic `/camera/image_raw`; read the publisher's reliability with `ros2 topic info -v /camera/image_raw` and set the display's QoS to match.
- Save the configuration (for example `~/ros2_ws/src/unit3_config.rviz`) and start with `rviz2 -d ~/ros2_ws/src/unit3_config.rviz`.

## White models
Both robot models white and overlapping at the origin = no transform from the Fixed Frame (`world`) to the root link of either model. Setting the Fixed Frame to a frame of one robot's own tree (`chassis`, `turtle_chassis`) shows that robot with its textures, but it no longer moves in the 3D view even when the camera image shows it moving. The fix is the missing transform ([[tf-odom-broadcaster]], [[tf-static-publisher]]).

## Pitfalls
- `Frame [map] does not exist` → choose an existing Fixed Frame, or start the node that publishes it.
- No image although the topic publishes → the display's reliability does not match the publisher's.
- Models white → missing link to the Fixed Frame; check the roots with [[tf-view-frames]].
