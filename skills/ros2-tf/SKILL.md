---
name: ros2-tf
description: "TF2 on ROS 2 (Jazzy; Humble noted): frames, TF tree, static_transform_publisher, broadcasters, timestamps, view_frames, tf2_echo, tf2_monitor, RViz2 TF display."
---
# ros2-tf — coordinate frames and transforms with TF2

Atomic notes for publishing, inspecting and debugging TF. **Jazzy is canonical** (the TF course's code and outputs); Humble, Kilted and Lyrical differences are marked, never substituted, and every Humble difference names the official `humble` source. The tf2 Python API is the same on Humble. Paths are relative to this skill's folder. `[[note-id]]` means the file `<note-id>.md`; find it via the area index or a glob `**/<note-id>.md`.

## Golden rules (always apply)
1. Check the user's distro first. **Humble**: same tf2 API and tools; no `Topic type hash` in CLI outputs, no regex filters in RViz's TF display. **Lyrical**: `static_transform_publisher` no longer parses positional arguments, `get_logger().warn()` is gone (use `warning()`), `TransformListener` takes `tf_topic`/`tf_static_topic` ([[tf-humble-to-jazzy]]).
2. Every frame has exactly **one parent**: `header.frame_id` is the parent (the reference), `child_frame_id` the frame being located. Frames exist only as names in `/tf` and `/tf_static`; two unconnected roots mean no transform between them ([[tf-frames-tree]]).
3. Angles are **radians** (REP 103): `static_transform_publisher --x --y --z --roll --pitch --yaw` or `--qx --qy --qz --qw`, then `--frame-id` (parent) and `--child-frame-id`; never mix rpy and quaternion flags ([[tf-static-publisher]]).
4. Static means a constant parent → child relation, published once on latched `/tf_static`; a listener that starts later gets it only while the publisher runs [verify], so keep static broadcasters alive or in the launch file ([[tf-static-python]]).
5. Stamp a transform with the time of the data it comes from (copy the odometry `header.stamp`) and keep every node on one clock (`use_sim_time:=true` with a simulator); mixing wall and sim time makes RViz and filters drop data ([[tf-monitor-stamps]], [[tf-odom-broadcaster]]).
6. A moving relation needs a dynamic broadcaster: `TransformBroadcaster(node)` adds a `/tf` publisher to your node; set the frame ids once, send on every source message ([[tf-odom-broadcaster]]).
7. Debug in this order: the tree (`view_frames`, `rqt_tf_tree`: roots, rates, static = rate 10000 and stamp 0.0), one transform (`tf2_echo A B` = pose of B in A, frame ids without a leading `/`), then delays (`tf2_monitor`, delay = its clock − stamp) ([[tf-view-frames]], [[tf-echo]], [[tf-monitor-stamps]]).
8. RViz2 needs an existing Fixed Frame; white robot models mean no transform from the Fixed Frame to their root link; a frame that stops being published fades after Frame Timeout (15 s) unless it is static ([[tf-rviz]]).
9. Links of a URDF become frames through robot_state_publisher (fixed joints on `/tf_static`, movable joints from `/joint_states`); in a simulator the joint states come from the simulator, never from the `joint_state_publisher` node, and a remapped description topic must be used by RViz and the spawner ([[tf-learn-unit4-rsp]]).
10. Course code: add every Python import to `package.xml` (`rclpy`, `tf_transformations`, `ros_gz_interfaces`); `tf_transformations` is a separate package, or compute the quaternion with a local function like the official tf2 tutorial ([[tf-learn-start-here]], [[tf-static-python]]).

## Retrieval protocol
1. Pick the area from the **Areas** table below (column "Covers").
2. Open that area's `_index.md` and choose notes by their summary.
3. Open 1–3 notes. Use their code and commands as the template: keep the structure, adapt the names.
4. No clear match → `grep -ril "<keyword>" notes/` (tool and API names work best: `tf2_echo`, `tf2_monitor`, `view_frames`, `StaticTransformBroadcaster`, `Frame Timeout`) and open the top hits.
5. Follow a note's `see:` links **one hop** at most. Listener code, conventions (REP 103/105) and robot_state_publisher launch files live in ros2-core; links and joints in ros2-urdf.
6. Do not open `learn/` unless the question is about the TF course (Cam_bot, turtle, unicycle; units 1–4).
7. Humble, Kilted, Lyrical or porting → open `migration/` and apply the version marks.
8. Simulation → answer with modern Gazebo (Gazebo Sim); spawning, bridging and moving models (`set_pose`) are in the ros2-gazebo skill.
If the notes do not cover the question, read the official source for the user's distro (below) or say that you answer from standard knowledge. Never invent APIs, flags or frames.

## Version marks and official sources
`[Humble]` what Humble needs instead · `[≥Jazzy]` added in Jazzy · `[changed in Lyrical: …]` what to use there · `[verify]` not confirmed by a source or a build: tell the user. Each note's `version_notes` holds the source URL and audit ID of every difference (`reports/version_audit_tf.md`).

| Distro | geometry2 / rviz2 | Read first |
|---|---|---|
| Humble | 0.25 / 11.2 | docs.ros.org/en/humble Tutorials/Intermediate/Tf2; branches `humble` of geometry2 and rviz |
| Jazzy | 0.36 / 14.1 | docs.ros.org/en/jazzy Tutorials/Intermediate/Tf2; branches `jazzy` |
| Kilted | 0.41 / — | branches `kilted` |
| Lyrical | 0.45 / 15.2 | docs.ros.org/en/lyrical ROS-Framework/client-libraries/Working-with-Client-Libraries/Tf2; branches `lyrical` |

## Areas
<!-- INDEX:START -->
<!-- generated by tools/build_index.py — do not edit by hand -->
| Area | Notes | Open | Covers |
|---|---|---|---|
| frames | 2 | `notes/frames/_index.md` | Coordinate frames, transforms, the TF tree (frame_id, child_frame_id, roots), /tf and /tf_static, TF and RobotModel in RViz2 (Fixed Frame, TF display options) |
| tools | 3 | `notes/tools/_index.md` | Introspect TF: view_frames, rqt_tf_tree, ros2 topic echo /tf, tf2_echo, tf2_monitor delays and transform timestamps (sim time vs wall clock) |
| broadcast | 3 | `notes/broadcast/_index.md` | Publish TF: TransformBroadcaster from odometry, static_transform_publisher (CLI, launch), StaticTransformBroadcaster from a Python script, tf_transformations |
| learn | 5 | `learn/_index.md` | TF course for students (Cam_bot and turtle, unicycle in Gazebo Sim): course map and units 1–4; open only for course questions |
| migration | 1 | `migration/_index.md` | TF course on Humble (+ Fortress) and Lyrical: tool outputs, RViz options, static_transform_publisher, TF topics; open for other distros |
<!-- INDEX:END -->

## Related skills
ros2-core (required): nodes, launch, sim time, the short TF overview and conventions, broadcaster and listener basics (`lookup_transform`), robot_state_publisher. ros2-urdf (required): links and joints as frames. ros2-gazebo: spawning a URDF, ros_gz_bridge, moving a model to a TF frame with `set_pose`. Install ros2-core and ros2-urdf with this skill.
