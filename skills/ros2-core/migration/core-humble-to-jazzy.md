---
id: core-humble-to-jazzy
type: reference
owner: equipo-ros2
updated: 2026-10-09
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "Humble → Jazzy changes (core)"
domain: core
area: migration
distro: jazzy
tested: false
audience: dev
summary: "What changes for user code from Humble to Jazzy (includes Iron): platform, discovery, rclpy/rclcpp, launch, tf2, CLI, rosbag2, Nav2, ros2_control."
tags: [migration, jazzy, iron, deprecations, breaking changes]
see: ["[[core-jazzy-to-lyrical]]", "[[core-migration-checklist]]"]
requires: []
version_notes:
  - "sources: https://docs.ros.org/en/rolling/Releases/Release-Iron-Irwini.html · https://docs.ros.org/en/rolling/Releases/Release-Jazzy-Jalisco.html · https://www.ros.org/reps/rep-2000.html"
---
# Humble → Jazzy changes (core)

**TL;DR** Jazzy (LTS, May 2024 – May 2029) includes everything from Iron. The breaking items for most projects are Ubuntu 24.04 + PEP 668, the rosbag2 CLI, non-const C++ callbacks, removed `tf2_*.h` headers, Nav2 BT.CPP 4, and ros2_control reading `robot_description` from a topic. `Vxx` = row in the repo's `reports/version_audit.md`.

| Area | Humble | Jazzy | Ref |
|---|---|---|---|
| Platform | Ubuntu 22.04, Python 3.10 | Ubuntu 24.04, Python 3.12; `pip install` into system Python blocked (PEP 668) → apt or venv | V04, V13, V42 |
| Gazebo | Fortress (`ign gazebo`, `ignition.msgs`) | Harmonic (`gz sim`, `gz.msgs`), `gz_*_vendor` packages; no Gazebo Classic | V64, V65 |
| Discovery | `ROS_LOCALHOST_ONLY=1` | deprecated (still honored) → `ROS_AUTOMATIC_DISCOVERY_RANGE`, `ROS_STATIC_PEERS` | V01, V70 |
| setup.py | `tests_require` (old template) | `extras_require={'test': ['pytest']}` | V07 |
| rclpy | `logger.warn()` deprecated alias | still deprecated (removed in Lyrical) → `warning()` | V22 |
| rclpy params | typed declare without default allowed | rejected; pre/post set-param callbacks added | V37, V38 |
| rclpy misc | MT executor fallback 1 thread; Time vs other type raises | fallback 2; comparisons return False; KEEP_LAST depth 0 warns | V31, V34 |
| rclcpp callbacks | `shared_ptr<MsgT>` (non-const) deprecated | **removed** → `ConstSharedPtr` | V27 |
| rclcpp executors | — | WaitSet-based; callback order not consistent; `rclcpp/qos_event.hpp` removed; EventsExecutor (exp.) | V30, V33 |
| launch | `PushRosNamespace`, `LaunchConfigurationEquals` | `PushROSNamespace` (alias kept); `Equals`/`NotEquals` substitutions; `LifecycleTransition` action | V15 |
| tf2 | `tf2_geometry_msgs.h`, `tf2_eigen.h`… deprecated | **removed** → `.hpp`; `wait_for_transform_async` returns the transform | V44 |
| CLI | `param dump --print/--output-dir` deprecated | removed; `topic echo --timeout`, `pub --max-wait-time`, `now`/`auto`; hz/bw/pub honor sim time; `ros2 action type`; `--log-file-name` | V26, V39, V78 |
| rosbag2 | sqlite3 default; `-a` = topics; `-x/--exclude` | **mcap** default; `-a` = topics **+ services**; `--exclude-regex` (no `-x` in record); service record/play; `--topic-types` | V46, V47, V49 |
| Tracing | no tracepoints in binaries | instrumentation built in; `ros2 trace start/stop/pause/resume` | V40 |
| Nav2 | velocity_smoother → cmd_vel; BT.CPP 3; mixed plugin names | collision_monitor in chain; **BT.CPP 4.5** (XML migration); `::` names; `enable_stamped_cmd_vel` (opt-in); docking | V48, V54, V56, V57 |
| ros2_control | `robot_description` parameter; `--start/--stop` aliases | CM subscribes to `/robot_description`; `--start/--stop` removed | V60, V62 |
| MoveIt2 | OMPL/Pilz/CHOMP | + parallel planning, STOMP | V53 |
| message_filters | — | `ApproximateEpsilonTime`, `LatestTime` policies (C++) | V72 |

Step-by-step procedure: [[core-migration-checklist]]. Next hop: [[core-jazzy-to-lyrical]].
