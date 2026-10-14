---
id: core-debug-tools
type: reference
owner: equipo-ros2
updated: 2026-10-14
review_by: 2027-04-12
source: manual
confidentiality: internal
title: "rqt, RViz2, teleop & ros2_tracing"
domain: core
area: tools
distro: humble
tested: false
audience: dev
summary: "rqt plugins, RViz2 setup and displays, teleop/joystick tools, and ros2_tracing (enabling it on Humble, CLI, launch Trace action)."
tags: [rqt, rqt_graph, rviz2, teleop, ros2_tracing, ros2 trace, LTTng]
see: ["[[core-debug-triage]]", "[[core-qos-usage]]", "[[core-exec-model]]", "[[core-learn-unit5-callbacks]]"]
requires: []
version_notes:
  - "humble: binaries ship WITHOUT tracepoints; install LTTng and build tracetools from source; Iron+ includes instrumentation — https://github.com/ros2/ros2_tracing/blob/humble/README.md (V40)"
  - "jazzy: ros2 trace start/stop/pause/resume verbs; lyrical: snapshot mode, dual session, runtime opt-out — https://docs.ros.org/en/rolling/Releases/Release-Lyrical-Luth.html (V40)"
---
# rqt, RViz2, teleop & ros2_tracing

**TL;DR** `rqt_graph` shows who talks to whom. RViz2 only displays topics: set the Fixed Frame and the QoS. ros2_tracing shows callback timelines, but on Humble it needs a rebuilt `tracetools`.

## rqt tools
```bash
rqt                                         # dashboard (Plugins menu); --perspective-file x.perspective
rqt_graph                                   # nodes <-> topics graph (most useful)
ros2 run rqt_console rqt_console            # log viewer with filters
ros2 run rqt_plot rqt_plot /odom/pose/pose/position/x    # live numeric plot (PlotJuggler is better for heavy use)
ros2 run rqt_reconfigure rqt_reconfigure    # params at runtime
ros2 run rqt_image_view rqt_image_view /camera/image_raw
ros2 run rqt_tf_tree rqt_tf_tree
ros2 run rqt_bag rqt_bag
ros2 run rqt_service_caller rqt_service_caller
```

## RViz2 (visualizer, NOT a simulator)
```bash
rviz2                       # source the ws containing robot meshes first
rviz2 -d my_config.rviz
ros2 run rviz2 rviz2 -d $(ros2 pkg prefix my_pkg)/share/my_pkg/rviz/view.rviz
```
Steps: Global Options → Fixed Frame (it must exist in TF: `map`/`odom`/`base_link`) → Add displays → set topic + QoS. Save with Ctrl+S.
| Display | For |
|---|---|
| TF | all frames |
| RobotModel | URDF (Description Topic `/robot_description`) |
| LaserScan | 2D lidar (Reliability: Best Effort; Size ~0.1) |
| PointCloud2 / Image / Camera | 3D points / images |
| Map / Path / Odometry / Pose | nav data |
| Marker / MarkerArray | custom debug shapes |

Nothing shown → check the Fixed Frame, topic, QoS and TF.

## Other tools
```bash
ros2 run turtlesim turtlesim_node ; ros2 run turtlesim turtle_teleop_key     # sandbox
ros2 run teleop_twist_keyboard teleop_twist_keyboard
ros2 run joy joy_node ; ros2 run teleop_twist_joy teleop_node                # joystick
ros2 run tf2_ros tf2_monitor base_link laser                                 # TF latency
```

## ros2_tracing (callback timelines)
- **Humble**: the binaries are built without tracepoints. Install LTTng (`sudo apt install lttng-tools liblttng-ust-dev python3-babeltrace python3-lttng`) plus `ros-humble-ros2trace ros-humble-tracetools-launch`. Then clone `ros2_tracing` (humble branch) into the workspace, run `colcon build --packages-up-to tracetools`, source it, and check that `ros2 run tracetools status` prints `Tracing enabled`. [changed in Jazzy: instrumentation included by default since Iron]
- CLI: `ros2 trace --session-name my_session` (interactive: Enter to start/stop; `-p` path, `-u`/`-k` events, `-l` list). [≥Jazzy: `ros2 trace start|stop|pause|resume`] [≥Lyrical: snapshot mode, dual sessions]
- Launch: `from tracetools_launch.action import Trace` → `Trace(session_name='my_session')`. Output goes to `$ROS_TRACE_DIR`, or `~/.ros/tracing/my_session` by default.
- Analyze callback durations with tracetools_analysis / Trace Compass. Course exercise: [[core-learn-unit5-callbacks]].
