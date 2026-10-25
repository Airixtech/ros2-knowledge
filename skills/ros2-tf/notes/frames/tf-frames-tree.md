---
id: tf-frames-tree
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "Coordinate frames, transforms and the TF tree: frame_id, child_frame_id, one parent, roots"
domain: tf
area: frames
distro: jazzy
tested: false
audience: dev
summary: "Coordinate frames and transforms in TF2: frame_id parent, child_frame_id, TransformStamped, one parent per frame, roots, two trees, /tf and /tf_static."
tags: [coordinate frame, reference frame, TF frame, global frame, local frame, transform, TF tree, root, frame_id, child_frame_id, TransformStamped, TFMessage, /tf, /tf_static]
see: ["[[tf-rviz]]", "[[tf-echo]]", "[[tf-static-publisher]]", "[[core-tf-basics]]", "[[urdf-frames-rviz]]"]
requires: [ros2-core, ros2-urdf]
version_notes:
  - "humble: same concepts, messages (tf2_msgs/msg/TFMessage of geometry_msgs/msg/TransformStamped) and topics /tf, /tf_static — https://docs.ros.org/en/humble/Concepts/Intermediate/About-Tf2.html"
---
# Coordinate frames, transforms and the TF tree

**TL;DR** Position coordinates have no meaning without the coordinate frame they are measured in. TF2 stores every frame's position and orientation relative to exactly **one parent** frame, so the frames form a tree, and any two connected frames are related by chaining the transforms between them. Transforms travel on `/tf` (changing) and `/tf_static` (fixed).

## Words
- **Coordinate frame**: a set of orthogonal axes that intersect at an origin and describe positions relative to it. "Coordinate system" and "reference frame" mean the same; ROS says **TF frame** (transform frame).
- In 2D a point is (X, Y): the course's rock is zero units right and four units up from the origin, (0.0, 4.0). In 3D a third coordinate, Z, gives the height above or below the plane (measured at the rock's base: 0.0 m).
- **Global coordinate frame**: an arbitrary frame placed in the environment so that any point of interest can be located from it (`world`, `map`, `odom`; in the course, the robot's starting location).
- **Local coordinate frames** are added for convenience: to know where the head is with respect to the neck, define `neck_frame` (the local frame) and `head_frame`.
- Each frame needs a unique **name**, its `frame_id`, and every new frame is placed with respect to an existing one: that relation is the **transform**.

## The message
| `geometry_msgs/msg/TransformStamped` field | Meaning |
|---|---|
| `header.frame_id` | parent: the frame the transform is defined in |
| `child_frame_id` | child: the frame being located |
| `header.stamp` | time the transform is valid for ([[tf-monitor-stamps]]) |
| `transform.translation` | child origin in parent coordinates (m) |
| `transform.rotation` | child orientation as a quaternion x, y, z, w |

`/tf` and `/tf_static` carry `tf2_msgs/msg/TFMessage`: a list `transforms` of these.

## The tree
- One parent per frame, any number of children. The topmost frame is the **root**.
- Frames that are not directly connected are related through the chain: from `rgb_camera_link_frame` to `turtle_chassis` it is `rgb_camera_link_frame → chassis → camera_bot_base_link → world → odom → turtle_base_link → turtle_chassis` ([[tf-echo]]).
- To place a turtle seen by a camera you need the camera robot's position in space, the distance from its body center (`base_link`) to the camera sensor, and the distance from the camera to the turtle: frames plus the transforms between them.
- Two robots whose roots are not connected make **two trees**: no transform exists between them, and RViz cannot place one in the other's fixed frame ([[tf-rviz]]). One transform between the roots joins them; the course publishes `world → odom` as a static transform ([[tf-static-publisher]]).
- A robot model has one frame per link: each URDF joint places its child link in the parent link, and robot_state_publisher publishes those transforms ([[urdf-frames-rviz]], [[core-robot-state-publisher]]). Even a medium-sized robot has dozens of frames.

## Frames are only names
Broadcasting a transform is all it takes to "create" its frames: TF data is just a topic of transforms between names, with no built-in connection to the real or simulated robot. If both frames already exist, your transform interferes with the one someone else publishes; if one exists, the other appears attached to it; if neither exists, both appear.

## Pitfalls
- Two nodes publishing the same child frame → the frame jumps between their values ([[core-tf-basics]]).
- Two roots → no transform between the trees and robot models drawn white in RViz; find the missing link with [[tf-view-frames]].
- `frame_id` and `child_frame_id` swapped → the inverse transform; `frame_id` is the reference, `child_frame_id` is what is located.
