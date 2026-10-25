---
id: core-tf-basics
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "TF2 conventions (REP 103/105), CLI & errors"
domain: core
area: tools
distro: humble
tested: false
audience: dev
summary: "Frame conventions and standard tree, who publishes each transform, tf2 CLI tools, static transforms, common TF errors."
tags: [tf2, REP 105, REP 103, view_frames, tf2_echo, static_transform_publisher, extrapolation]
see: ["[[core-tf-broadcaster]]", "[[core-tf-listener]]", "[[core-urdf-basics]]", "[[core-time-timers]]"]
requires: []
version_notes:
  - "lyrical: static_transform_publisher legacy positional args removed (deprecated since Humble) — https://github.com/ros2/geometry2/blob/lyrical/tf2_ros/src/static_transform_broadcaster_program.cpp (V43)"
  - "humble: REP 103, 105, 120 and 147 are in the official REP index; the serial-manipulator frames text is draft REP 199, not accepted — https://github.com/ros-infrastructure/rep (TF-V16, TF-V31)"
---
# TF2 conventions (REP 103/105), CLI & errors

**TL;DR** The tree is `map → odom → base_link → sensors`, with exactly one publisher per transform. Debug with `view_frames` and `tf2_echo`. Extrapolation errors almost always mean a clock or `use_sim_time` mismatch.

## Conventions (REP 103 / 105)
- Right-handed, x forward, y left, z up; meters, radians, seconds. Camera optical frame: z forward, x right, y down (rpy `-π/2, 0, -π/2` from the body frame).
- Tree: `earth → map → odom → base_link → {laser, camera_link, imu_link, wheels}` (`base_footprint` optional, under or above base_link).
- `map`: global and fixed, but may jump (relocalization). `odom`: continuous, drifts. `base_link`: rigidly attached to the robot.
- Axes are drawn x red, y green, z blue. A positive turn rate must turn the robot left, or a drive node does not work with Nav2 and other ROS components; the same holds for car-like robots and drones. Pixel coordinates of images are the usual exception to the right-hand rule.
- Other REPs: 120 (humanoid robots), 147 (aerial vehicles); serial industrial manipulators only have a draft (REP 199, not accepted).

| Transform | Publisher |
|---|---|
| `map → odom` | AMCL / SLAM Toolbox |
| `odom → base_link` | odometry driver / `robot_localization` EKF / sim plugin |
| `base_link → sensors` | `robot_state_publisher` from URDF (static + joint-driven) |

One publisher per transform. Topics: `/tf` (dynamic) and `/tf_static` (TRANSIENT_LOCAL).

## CLI
```bash
ros2 run tf2_tools view_frames                 # listens 5 s -> frames_<date>.pdf/.gv in cwd (run from ~)
ros2 run tf2_ros tf2_echo map base_link        # live transform (translation, quaternion, RPY rad/deg)
ros2 run tf2_ros tf2_monitor [base_link laser] # rates / delays
ros2 run rqt_tf_tree rqt_tf_tree               # interactive tree (pkg ros-humble-rqt-tf-tree)
ros2 topic echo /tf ; ros2 topic echo /tf_static ; ros2 topic hz /tf
# static transform (Humble flag syntax; angles in rad)
ros2 run tf2_ros static_transform_publisher --x 0.1 --y 0 --z 0.2 --yaw 0 --pitch 0 --roll 0 \
  --frame-id base_link --child-frame-id laser
# legacy positional: x y z yaw pitch roll parent child   |   x y z qx qy qz qw parent child
```
The legacy positional form prints a deprecation warning in Humble [changed in Lyrical: removed, flags only]. `view_frames -t <s>` changes how long it listens.

## Errors
| Error | Cause → fix |
|---|---|
| `Lookup would require extrapolation into the future/past` | clock mismatch: `use_sim_time` inconsistent, bag without `--clock`, stale stamps ([[core-time-timers]]) |
| `"X" passed to lookupTransform argument target_frame does not exist` | no publisher for X yet (e.g. `map` before AMCL initial pose) |
| Jittery/ flickering frames | two publishers of the same transform or low rate |
| Laser misaligned with robot in RViz | wrong extrinsic/joint origin in URDF or wrong parent frame |

Code: [[core-tf-broadcaster]] · [[core-tf-listener]] · model: [[core-urdf-basics]]. Each tool in depth (view_frames edge data, tf2_echo argument order, tf2_monitor delays), the RViz TF display and the TF course: skill ros2-tf.
