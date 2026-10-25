# Version audit — ros2-tf (Phase 1)

> Date: 2026-10-25. Scope: every version-dependent or checkable statement of the TF course (course wiki, not
> published; units 1–4) that lands in `ros2-tf`, and the course lines that become unions in `ros2-core` and
> `ros2-gazebo`: coordinate frames and conventions, `static_transform_publisher`, RViz2's TF display, `view_frames`,
> `rqt_tf_tree`, `tf2_echo`, `tf2_monitor`, transform broadcasters (dynamic from odometry, static from a script),
> a TF listener that moves a Gazebo model, and `robot_state_publisher` with and without a spawned robot.
> Section IDs = the course's section numbers.
> Baseline: **Jazzy (+ Gazebo Harmonic) is canonical** for this skill (decision of 2026-10-25): the course code and its
> outputs are Jazzy's (bridge types `gz.msgs.*`, `Topic type hash` in `ros2 topic info -v`, the `get_type_description`
> service). **Humble (+ Fortress)** is annotated with the official `humble` sources, Kilted and **Lyrical (+ Jetty)**
> too. Unions written into `ros2-core` keep that skill's canonical Humble. Generic ROS 2 rows are in
> [version_audit.md](version_audit.md) (`Vnn`), Gazebo rows in [version_audit_gazebo.md](version_audit_gazebo.md)
> (`GZ-Vnn`, e.g. GZ-V26 bridge type names).

## Method
- Primary sources, read on the matching branch with grep: `ros2/geometry2` (humble, jazzy, kilted, lyrical:
  `tf2_ros/src/static_transform_broadcaster_program.cpp`, `tf2_echo.cpp`, `tf2_monitor.cpp`,
  `tf2/src/buffer_core.cpp`, `tf2_tools/view_frames.py`, `tf2_ros_py/tf2_ros/*.py`), `ros2/rviz` (humble, jazzy,
  lyrical: `rviz_default_plugins/.../displays/tf/tf_display.cpp`, `frame_info.cpp`), `ros/robot_state_publisher`
  (humble, jazzy, lyrical), `ros/joint_state_publisher` (humble), `gazebosim/ros_gz` (humble, jazzy, lyrical:
  `ros_gz_sim/src/create.cpp`, `ros_gz_bridge/README.md`, `ros_gz_interfaces`), `gazebosim/gz-sim` (gz-sim8 =
  Harmonic: `UserCommands.cc`), `ros-visualization/rqt_tf_tree` (humble, master), `DLu/tf_transformations` (main),
  `ros2/rclpy` (humble, jazzy: `topic_endpoint_info.py`), `ros/rosdistro` (released versions),
  `ros-infrastructure/rep` (REP index).
- Origin of the course code: the static broadcaster of 3.8 follows the official tf2 tutorial
  `static_turtle_tf2_broadcaster.py` of `ros/geometry_tutorials` (Apache-2.0, OSRF; [tutorial code][tut-static-j],
  [docs][docs-static-j]), which defines its own `quaternion_from_euler` instead of the `tf_transformations` package.
  The other programs (odometry broadcaster, follower, launch files) and the simulations are the course's own.
- Course logic was reviewed too: explanations against the printed outputs and the code, explained snippets against
  the files, remappings against the topics the next step uses. Contradictions are **fix** rows ("course mistake").
- Actions: **keep** = correct for Jazzy · **annotate** = correct, add marks (Humble, Lyrical) or a precise wording ·
  **fix** = wrong for Jazzy itself. Confidence: High (read in code) · Medium (docs, or inferred) · `[verify]` (needs a run).

## Baseline
| | Humble | Jazzy (canonical) | Kilted | Lyrical |
|---|---|---|---|---|
| Ubuntu / EOL | 22.04 / May 2027 | 24.04 / May 2029 | 24.04 / Dec 2026 | 26.04 / May 2031 |
| Gazebo | Fortress | Harmonic | Ionic | Jetty |
| geometry2 (tf2_ros) branch head | 0.25.24 | 0.36.23 | 0.41.10 | 0.45.10 |
| rviz2 | 11.2.29 | 14.1.24 | — | 15.2.7 |
| robot_state_publisher | 3.0.3 | 3.3.4 | — | 3.5.6 |
| ros_gz (ros_gz_sim) | 0.244.27 | 1.0.25 | — | 3.0.12 |
| tf_transformations (rosdistro) | 1.1.1-1 | 1.1.1-1 | 1.1.1-2 | 1.1.1-3 |
| Official docs | [tf2 tutorials (Humble)][docs-tf2-h] | [tf2 tutorials (Jazzy)][docs-tf2-j] | — | [tf2 tutorials (Lyrical)][docs-tf2-l] |

## Real Jazzy errors (fix)
| ID | Section | Origin | Error | Correct statement |
|---|---|---|---|---|
| TF-V01 | 1.5 | course mistake (older syntax) | `static_transform_publisher x y z yaw pitch roll frame_id child_frame_id` with "the three rotational degrees of freedom (in degrees)" | Angles are **radians** (the program's usage text: "roll, pitch, yaw euler angles in radians"; 3.6 of the course says so). Use the flags `--x --y --z --roll --pitch --yaw` (or `--qx --qy --qz --qw`) `--frame-id --child-frame-id`. The positional form prints "Old-style arguments are deprecated" in Humble, Jazzy and Kilted; Lyrical no longer parses it and exits with "Frame id must not be empty". Official docs: the tf2 static broadcaster tutorial ("In ROS 2, roll/pitch/yaw refers to rotation in radians about the x/y/z-axis, respectively", [Humble][docs-static-h], [Jazzy][docs-static-j]) and REP 103 (angle unit: radian, [REP 103][rep-103]). Sources: [program (jazzy)][stp-j], [program (lyrical)][stp-l]. |
| TF-V02 | 3.4 | course mistake | `tf2_monitor`: the huge delay of the static chain "reflects" a zero delay; 4.4 ms "is too much for the image module in RVIZ"; after the fix, 1.67e9 s "indicates that it behaves like a static transform" | `tf2_monitor` prints `now() − header.stamp` with **its own node clock** (wall time unless `use_sim_time:=true`). Static transforms carry stamp 0, so their "delay" is the current Unix time. The first broadcaster stamped with `get_clock().now()` of a node without sim time (wall time), so the monitor saw ~4 ms; RViz, however, looks up the camera images (sim-time stamps) and found no transform at those times (inferred from the stamps, `[verify]`). Stamping with the odometry header puts the transform in sim time: the data and the TF agree, and the 1.67e9 s is only the wall-clock − sim-time difference of the monitor. Run it with `--ros-args -p use_sim_time:=true` for real delays [verify]. Sources: [tf2_monitor.cpp (jazzy)][mon-j]. |
| TF-V03 | 3.3 | course mistake | Example 3.2.1: the script "publishes a **static** TF transform from camera_bot_base_link to world" | It publishes a **dynamic** transform (`TransformBroadcaster`, topic `/tf`) on every odometry message; static transforms use `StaticTransformBroadcaster` and `/tf_static` (3.8). Source: the course code; [tf2_ros_py (jazzy)][tb-py-j]. |
| TF-V04 | 3.3 | course mistake | Explained snippet subscribes with `self.listener_callback` | The program defines and uses `self.odom_callback`; `listener_callback` does not exist (AttributeError). The file wins. |
| TF-V05 | 3.3, 3.8, 3.9 | course mistake | Package created with `--dependencies tf2_ros geometry_msgs nav_msgs` | The scripts also import `rclpy`, `tf_transformations` (3.8) and `ros_gz_interfaces` (3.9): declare them in `package.xml` (`<exec_depend>`) so `rosdep install` brings them on another machine; `tf_transformations` itself depends on `python3-transforms3d` ([package.xml][tft-pkg]). |
| TF-V06 | 3.7 | course mistake | Reminders: "publishing the TF from `camera_bot_base_link` to `odom`" and "the **static** TF from `odom` to `world`" | Running at that point: the dynamic transform `world` (parent) → `camera_bot_base_link` (child) from the odometry script, and the static `world` (parent) → `odom` (child) of the launch file (its arguments `--frame-id world --child-frame-id odom`). |
| TF-V07 | 4.2 | course mistake | "we spawn the robot passing directly the URDF contents using the `-file` argument" | `-file` takes a **file path** ("Load XML from a file"); `-string` takes the XML text, `-topic` reads it from a topic, `-param` from a parameter. Sources: [create.cpp (jazzy)][create-j], [(humble)][create-h]. |
| TF-V08 | 4.3 | course mistake | RViz: "set the topic to `/unicycle_robot_description`" | The launch file remaps the description to `/unicycle_bot_robot_description` (the node info output of the same section lists it): use that topic. |
| TF-V09 | 2.7 | course mistake | The command passes `offset_xyz:="[0.0, 0.0, 0.0]"`; the parameter list explains `offset_xyz:="[0.0, 0.0, 0.6]"` | The command (zero offset: the camera sits on `turtle_attach_frame`) is what runs; 0.6 is an example of the offset in the target frame. |
| TF-V10 | 2.7, 2.9, 3.9 | course mistake | 2.7 runs `cam_bot_follower.py`, 2.9 asks "How does `move_generic_model.py` work?", 3.9 writes `move_generic_model.py` with the node name `cam_bot_follower` | One program under two file names: the course's prebuilt `turtle_tf_3d_ros2/cam_bot_follower.py` and the exercise copy `my_tf_ros2_course_pkg/move_generic_model.py` (same parameters, node `cam_bot_follower`). |
| TF-V11 | 3.2 | course mistake | "Cam_bot does not publish its TF from `cam_bot_base_link` to `world`" | The frame is `camera_bot_base_link` (TF trees, code and commands). |
| TF-V12 | 3.8 | course mistake | "Pitch = 0.7 (… 45 degrees/0.7 radians pitch down)", "Yaw = 3.1416 (… 180 degrees/3.1416 radians **pitch** down)" | 45° = 0.785 rad; 0.7 rad ≈ 40°. 3.1416 rad = 180° is the **yaw** (turn around z), not a pitch. |
| TF-V13 | 2.4 | course mistake | "`/hose/user/frames_XXXXX.pdf`"; "average rate … around 5.2Hz"; "4.93 seconds of data" | The file is written in the directory where `view_frames` runs (`/home/user` there). The shown tree says 20.136 Hz and 4.42 s for `world → camera_bot_base_link`: the printed output wins. |
| TF-V14 | 3.9 | course claim | "each node is only aware of transforms published since that node started" | True for `/tf`. `/tf_static` is subscribed TRANSIENT_LOCAL (depth 100) and published latched, so a late listener still receives the static transforms. Sources: [transform_listener.py (jazzy)][tl-py-j], [static_transform_broadcaster.py][stb-py-j]. |
| TF-V15 | 4.3 | course claim | "In Gazebo, start the `joint_state_publisher` node or use a Gazebo Plugin" | `joint_state_publisher` publishes default positions (0, or the middle of the limits) for every movable joint, not the simulated ones; in Gazebo Sim the JointStatePublisher system publishes the real joint states, bridged to `/joint_states` (`sensor_msgs/msg/JointState[gz.msgs.Model`). Never run both: two publishers of `/joint_states`. Sources: [joint_state_publisher.py (humble)][jsp-h], GZ-V26. |
| TF-V16 | 1.4 | course claim | "Coordinate Frames for Serial Industrial Manipulators (ROS.org)" linked as a REP | It is a **draft** (REP 199) published in a personal repository, not in the official REP index (`ros-infrastructure/rep` has no `rep-0199`); REP 103, 105, 120 and 147 are official. Source: [REP repository][rep-repo]. |
| TF-V17 | 4.2 | course mistake | The explained snippet stores the path in `urdf` and spawns with `"-file", urdf` | The launch file names it `urdf_path`; the file wins. |

## Full table
| # | Section | Statement | Humble (Fortress) | Jazzy (Harmonic) | Lyrical (Jetty) | Action | Source | Confidence |
|---|---|---|---|---|---|---|---|---|
| TF-V01 | 1.5 | positional args, angles in degrees | ✗ radians; positional deprecated (warning) | ✗ same | ✗ radians; positional not parsed | **fix** | [stp-h], [stp-j], [stp-l], [docs-static-h], [docs-static-j], [rep-103] | High |
| TF-V02 | 3.4 | reading of the tf2_monitor delays | ✗ monitor clock − stamp | ✗ same | ✗ same | **fix** | [mon-j] | High (formula), `[verify]` (sim-time run) |
| TF-V03 | 3.3 | odometry → TF called "static" | ✗ dynamic `/tf` | ✗ same | ✗ same | **fix** | course code | High |
| TF-V04 | 3.3 | `self.listener_callback` in the snippet | ✗ | ✗ | ✗ | **fix** | course code | High |
| TF-V05 | 3.3–3.9 | package dependencies | ✗ missing rclpy, tf_transformations, ros_gz_interfaces | ✗ same | ✗ same | **fix** | [tft-pkg] | High |
| TF-V06 | 3.7 | parent/child in the reminders | ✗ | ✗ | ✗ | **fix** | course launch file | High |
| TF-V07 | 4.2 | `-file` = URDF contents | ✗ path | ✗ path | ✗ path | **fix** | [create-h], [create-j] | High |
| TF-V08 | 4.3 | RViz topic `/unicycle_robot_description` | ✗ remapped name | ✗ same | ✗ same | **fix** | course launch file and output | High |
| TF-V09 | 2.7 | `offset_xyz` 0.0 vs 0.6 | — | ✗ command wins | — | **fix** | course command | High |
| TF-V10 | 2.7–3.9 | follower file names | — | ✗ one program, two names | — | **fix** | course code | High |
| TF-V11 | 3.2 | `cam_bot_base_link` | — | ✗ `camera_bot_base_link` | — | **fix** | course trees | High |
| TF-V12 | 3.8 | 0.7 rad = 45°, yaw "pitch down" | ✗ | ✗ | ✗ | **fix** | arithmetic | High |
| TF-V13 | 2.4 | `/hose/user`, 5.2 Hz, 4.93 s | — | ✗ output wins | — | **fix** | course output | High |
| TF-V14 | 3.9 | listener only knows transforms since it started | ✗ statics arrive late (transient local) | ✗ same | ✗ same | **fix** | [tl-py-h], [tl-py-j] | High |
| TF-V15 | 4.3 | joint_state_publisher node in Gazebo | ✗ default positions | ✗ same | ✗ same | **fix** | [jsp-h] | High |
| TF-V16 | 1.4 | manipulator frames REP | ✗ draft REP 199 | ✗ | ✗ | **fix** | [rep-repo] | High |
| TF-V17 | 4.2 | `urdf` vs `urdf_path` | — | ✗ file wins | — | **fix** | course launch file | High |
| TF-V18 | 1.6 | RViz2 TF display: Show Names/Axes/Arrows (child → parent), Marker Scale, Update Interval (0 = every cycle), Frame Timeout (1/3 normal, 1/3 grey, then gone; static frames never fade), Frames, Tree | ✓ same options; no regex filters | ✓ defaults: names off, axes and arrows on, scale 1, interval 0, timeout 15 s (min 1); `Filter (whitelist)` / `Filter (blacklist)` regex | ✓ same as Jazzy | **annotate** ([≥Jazzy] filters) | [tfd-h], [tfd-j], [fi-j] | High |
| TF-V19 | 2.4 | `view_frames`: listens 5 s, writes the tree, prints the frame YAML | ✓ `-t/--wait-time` (5 s), `-o`; writes `frames_<date>.gv` + `.pdf` (needs graphviz `dot`); logs "Generating graph in frames.pdf file..." | ✓ same; logs "Generating graph..." and "Exporting graph in frames_<date>.pdf file..." | ✓ + `--tf_topic`, `--tf_static_topic` | **annotate** | [vf-h], [vf-j], [vf-l] | High |
| TF-V20 | 2.4, 2.5 | edge data: rate 10000 and most recent 0.0 = static | ✓ | ✓ `rate = samples / max(span, 100 µs)`: one sample → 10000; static stamps are 0 | ✓ | **annotate** (why 10000) | [bc-j] | High |
| TF-V21 | 2.6 | `tf2_echo [reference_frame] [target_frame]`, wait until it appears | ✓ `tf2_echo source_frame target_frame [-r rate]` = `lookupTransform(source, target)`: the pose of the second frame in the first; logs "Waiting for transform A -> B: …" each second until available; prints translation, quaternion, RPY (rad and deg), matrix | ✓ same | ✓ same | **annotate** (argument meaning) | [echo-j] | High |
| TF-V22 | 3.5, 3.6 | static transforms on `/tf_static`, "only published when they change"; flags rpy (radians) or quaternion | ✓ | ✓ latched (TRANSIENT_LOCAL); rpy and quaternion flags cannot be mixed ("Cannot specify both quaternion and Euler rotations") | ✓ | **annotate** (latched, not "on change") | [stb-py-j], [stp-j] | High |
| TF-V23 | 3.8 | `import tf_transformations`, `quaternion_from_euler(roll, pitch, yaw)` | ✓ released 1.1.1 (`ros-humble-tf-transformations`, depends `python3-transforms3d`) | ✓ same; returns `(x, y, z, w)` | ✓ released | **annotate** (extra package; official tutorial computes the quaternion itself) | [tft], [tft-pkg], [rd-h], [rd-j], [rd-l], [tut-static-j] | High |
| TF-V24 | 3.9 | follower calls `/world/<world>/set_pose` (`SetEntityPose`), `ENTITY_MODEL = 2` | ✓ same service and bridge line (Fortress; the README lists `SetEntityPose`) | ✓ Gazebo's UserCommands system offers `/world/<world>/set_pose`; a ROS client needs `ros2 run ros_gz_bridge parameter_bridge /world/<world>/set_pose@ros_gz_interfaces/srv/SetEntityPose`; `Entity.MODEL = 2` is a constant of `ros_gz_interfaces/msg/Entity`; parameter `world` must match the world name | ✓ | **annotate** (bridge step, constant) | [sep-j], [entity-j], [uc-8], [bridge-j], [bridge-h] | High (API), Medium (the course sim bridged it) |
| TF-V25 | 4.2, 4.3 | `ros_gz_sim create -name -allow_renaming -file/-topic -Y`; bridge `/tf@…[gz.msgs.Pose_V`, `/joint_states@…[gz.msgs.Model`, `/clock` | ✓ same options (Fortress); the bridge accepts the `gz.msgs` names (GZ-V26) | ✓ | ✓ | **keep** | [create-h], [create-j], GZ-V26 | High |
| TF-V26 | 3.3, 3.4 | broadcaster stamps with `self.get_clock().now()` | ✓ wall time unless the node has `use_sim_time:=true` | ✓ same | ✓ same | **annotate** (with a simulator: sim time, or the source message stamp) | [mon-j], V69 of [version_audit.md](version_audit.md) (`use_sim_time` rules) | High |
| TF-V27 | 4.3 | robot_state_publisher: description topic, fixed joints on `/tf_static`, movable from `/joint_states` on `/tf`; subscribes `/clock` with sim time; `remappings` rename the description topic | ✓ | ✓ | ✓ | **keep** | [rsp-j] | High |
| TF-V28 | 2.6, 4.2, 4.3 | `ros2 topic info -v` shows `Topic type hash`; `ros2 node info` lists `…/get_type_description` | ✗ neither exists in Humble (type hashes came in Iron) | ✓ | ✓ | **annotate** ([Humble: …] output without them) | [tei-h], [tei-j] | High |
| TF-V29 | — (Lyrical) | listener and tools always use `/tf` and `/tf_static` | ✓ fixed names | ✓ fixed names | ✓ `TransformListener(..., tf_topic=, tf_static_topic=)`, module `tf2_ros.static_transform_listener`, `view_frames --tf_topic/--tf_static_topic` | **annotate** ([≥Lyrical]) | [tl-py-l], [stl-py-l], [vf-l] | High |
| TF-V30 | 1.6 | `static_transform_publisher` output: node `static_transform_publisher_<random>`, "Spinning until stopped - publishing transform", translation and rotation as strings | ✓ | ✓ | ✓ | **keep** | [stp-j] | High |
| TF-V32 | 2.5 | `ros2 run rqt_tf_tree rqt_tf_tree`, refresh button | ✓ released (branch `humble`, 1.1.1) | ✓ released (`master`, 1.1.1) | ✓ released | **keep** | [rd-h], [rd-j], [rd-l] | High |
| TF-V31 | 1.4 | right-handed frames, x red / y green / z blue, positive turn rate turns left; REP 103, 105, 120, 147 | ✓ | ✓ | ✓ | **keep** | [rep-103], [rep-105], [rep-120], [rep-147] | High |

## Canonical alternatives (features of a later distro)
| Feature | First distro | Humble/Jazzy alternative | Checked |
|---|---|---|---|
| Regex filters in the TF display | Jazzy | Humble: untick frames one by one under `Frames` (the category exists in Humble) | [tfd-h] |
| `tf_topic` / `tf_static_topic` of `TransformListener`, `view_frames --tf_topic` | Lyrical | remap `/tf` and `/tf_static` with `--ros-args -r` on the process `[verify]` | not run |

## Open `[verify]` (Phase 5 or a real machine)
- TF-V02: `tf2_monitor world camera_bot_base_link --ros-args -p use_sim_time:=true` with the fixed broadcaster gives delays of milliseconds; with the first broadcaster RViz drops the camera images (needs the course simulation or any Gazebo world with a camera).
- Canonical alternative of TF-V29: remapping `/tf` and `/tf_static` for `view_frames` and a Python `TransformListener` on Humble/Jazzy.

## Sources
[stp-h]: https://github.com/ros2/geometry2/blob/humble/tf2_ros/src/static_transform_broadcaster_program.cpp
[stp-j]: https://github.com/ros2/geometry2/blob/jazzy/tf2_ros/src/static_transform_broadcaster_program.cpp
[stp-l]: https://github.com/ros2/geometry2/blob/lyrical/tf2_ros/src/static_transform_broadcaster_program.cpp
[vf-h]: https://github.com/ros2/geometry2/blob/humble/tf2_tools/tf2_tools/view_frames.py
[vf-j]: https://github.com/ros2/geometry2/blob/jazzy/tf2_tools/tf2_tools/view_frames.py
[vf-l]: https://github.com/ros2/geometry2/blob/lyrical/tf2_tools/tf2_tools/view_frames.py
[echo-j]: https://github.com/ros2/geometry2/blob/jazzy/tf2_ros/src/tf2_echo.cpp
[mon-j]: https://github.com/ros2/geometry2/blob/jazzy/tf2_ros/src/tf2_monitor.cpp
[bc-j]: https://github.com/ros2/geometry2/blob/jazzy/tf2/src/buffer_core.cpp
[tl-py-h]: https://github.com/ros2/geometry2/blob/humble/tf2_ros_py/tf2_ros/transform_listener.py
[tl-py-j]: https://github.com/ros2/geometry2/blob/jazzy/tf2_ros_py/tf2_ros/transform_listener.py
[tl-py-l]: https://github.com/ros2/geometry2/blob/lyrical/tf2_ros_py/tf2_ros/transform_listener.py
[stl-py-l]: https://github.com/ros2/geometry2/blob/lyrical/tf2_ros_py/tf2_ros/static_transform_listener.py
[tb-py-j]: https://github.com/ros2/geometry2/blob/jazzy/tf2_ros_py/tf2_ros/transform_broadcaster.py
[stb-py-j]: https://github.com/ros2/geometry2/blob/jazzy/tf2_ros_py/tf2_ros/static_transform_broadcaster.py
[tfd-h]: https://github.com/ros2/rviz/blob/humble/rviz_default_plugins/src/rviz_default_plugins/displays/tf/tf_display.cpp
[tfd-j]: https://github.com/ros2/rviz/blob/jazzy/rviz_default_plugins/src/rviz_default_plugins/displays/tf/tf_display.cpp
[fi-j]: https://github.com/ros2/rviz/blob/jazzy/rviz_default_plugins/src/rviz_default_plugins/displays/tf/frame_info.cpp
[create-h]: https://github.com/gazebosim/ros_gz/blob/humble/ros_gz_sim/src/create.cpp
[create-j]: https://github.com/gazebosim/ros_gz/blob/jazzy/ros_gz_sim/src/create.cpp
[bridge-h]: https://github.com/gazebosim/ros_gz/blob/humble/ros_gz_bridge/README.md
[bridge-j]: https://github.com/gazebosim/ros_gz/blob/jazzy/ros_gz_bridge/README.md
[sep-j]: https://github.com/gazebosim/ros_gz/blob/jazzy/ros_gz_interfaces/srv/SetEntityPose.srv
[entity-j]: https://github.com/gazebosim/ros_gz/blob/jazzy/ros_gz_interfaces/msg/Entity.msg
[uc-8]: https://github.com/gazebosim/gz-sim/blob/gz-sim8/src/systems/user_commands/UserCommands.cc
[tft]: https://github.com/DLu/tf_transformations/blob/main/tf_transformations/__init__.py
[tft-pkg]: https://github.com/DLu/tf_transformations/blob/main/package.xml
[jsp-h]: https://github.com/ros/joint_state_publisher/blob/humble/joint_state_publisher/joint_state_publisher/joint_state_publisher.py
[rsp-j]: https://github.com/ros/robot_state_publisher/tree/jazzy
[tei-h]: https://github.com/ros2/rclpy/blob/humble/rclpy/rclpy/topic_endpoint_info.py
[tei-j]: https://github.com/ros2/rclpy/blob/jazzy/rclpy/rclpy/topic_endpoint_info.py
[tut-static-j]: https://github.com/ros/geometry_tutorials/blob/jazzy/turtle_tf2_py/turtle_tf2_py/static_turtle_tf2_broadcaster.py
[docs-static-h]: https://docs.ros.org/en/humble/Tutorials/Intermediate/Tf2/Writing-A-Tf2-Static-Broadcaster-Py.html
[docs-static-j]: https://docs.ros.org/en/jazzy/Tutorials/Intermediate/Tf2/Writing-A-Tf2-Static-Broadcaster-Py.html
[docs-tf2-h]: https://docs.ros.org/en/humble/Tutorials/Intermediate/Tf2/Tf2-Main.html
[docs-tf2-j]: https://docs.ros.org/en/jazzy/Tutorials/Intermediate/Tf2/Tf2-Main.html
[docs-tf2-l]: https://docs.ros.org/en/lyrical/ROS-Framework/client-libraries/Working-with-Client-Libraries/Tf2/Tf2-Main.html
[rd-h]: https://github.com/ros/rosdistro/blob/master/humble/distribution.yaml
[rd-j]: https://github.com/ros/rosdistro/blob/master/jazzy/distribution.yaml
[rd-l]: https://github.com/ros/rosdistro/blob/master/lyrical/distribution.yaml
[rep-repo]: https://github.com/ros-infrastructure/rep
[rep-103]: https://www.ros.org/reps/rep-0103.html
[rep-105]: https://www.ros.org/reps/rep-0105.html
[rep-120]: https://www.ros.org/reps/rep-0120.html
[rep-147]: https://www.ros.org/reps/rep-0147.html
