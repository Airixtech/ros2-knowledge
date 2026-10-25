---
id: cpp-learn-unit9-debugging
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "C++ unit 9: logs_test logger example, RViz2 with the rover laser, view_frames, ros2 doctor"
domain: cpp
area: learn
distro: humble
tested: false
audience: students
summary: "Course unit 9 in C++: logs_test logger example and levels, RViz2 with the rover laser, view_frames, ros2 doctor report."
tags: [course, unit 9, debugging, logs_test, logger_example, RViz2, LaserScan, view_frames, tf2_tools, ros2 doctor, students]
see: ["[[cpp-learn-start-here]]", "[[cpp-logging]]", "[[core-debug-tools]]", "[[core-debug-triage]]", "[[core-tf-basics]]", "[[core-learn-unit8-debugging]]"]
requires: [ros2-core]
version_notes:
  - "course: '`ros2 doctor` belongs to the ros2cli package' — it is the package ros2doctor, in the ros2cli repository — https://github.com/ros2/ros2cli/blob/humble/ros2doctor/setup.py (CPP-V14)"
---
# C++ unit 9: debugging tools

**TL;DR** Unit 9 in C++ (the Python twin, which is its unit 8: [[core-learn-unit8-debugging]]): log levels in a C++ node, RViz2 to see the robot and its laser, `view_frames` for the TF tree, `ros2 doctor` for the whole setup. The tools themselves are language-neutral: [[core-debug-tools]], [[core-tf-basics]], [[core-debug-triage]].

## Exercises 9.1 and 9.2 (pkg `logs_test`, dependency `rclcpp`)
`src/logger_example.cpp`, launch `logger_example.launch.py`, CMakeLists and package.xml → [[cpp-logging]]. Then change the level in the `rcutils_logging_set_logger_level("logger_name", RCUTILS_LOG_SEVERITY_<LOG_LEVEL>)` line (rebuild each time), or start with `ros2 run logs_test logger_example --ros-args --log-level DEBUG`, and add `emulate_tty=True` to the launch Node for colours.

## Example 9.1: RViz2 and the laser
- `ros2 topic echo /laser_scan --once`: `frame_id: _laser_scan_frame`, `angle_min: -2.200000047683716`, `angle_max: 2.200000047683716`, `angle_increment: 0.022110553458333015`, `range_min: 0.10000000149011612`, `range_max: 20.0`, then the `ranges` (`.inf` … `16.342742919921875`) and `intensities` arrays: too many numbers to read by eye.
- Source the simulation workspace (meshes), run `rviz2`. Add **TF** (Fixed Frame `base_link` in Global Options), **RobotModel** (Description Topic `/robot_description`) and **LaserScan** (Topic `/laser_scan`, Reliability Policy `Best Effort`, Size `0.1`). Mouse: left button rotates, middle button moves, right button zooms.
- Drive with `ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.2, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.4}}"` and watch the scan points follow the terrain. RViz2 is **not** a simulator: it shows what a simulator or a real robot publishes.
- A scan that does not line up with the robot points at a TF problem → `view_frames`.

## Example 9.2: `view_frames`
```bash
cd                                   # it writes the PDF in the current folder
source /opt/ros/humble/setup.bash
ros2 run tf2_tools view_frames       # Listening to tf data for 5.0 seconds... Generating graph in frames.pdf file...
ls                                   # frames_2024-09-05_19.41.06.gv  frames_2024-09-05_19.41.06.pdf
```
The printed `frame_yaml` lists each frame with parent, broadcaster, rate, most recent and oldest transform and buffer length (e.g. `wheel_FR_link` with parent `rocker_R_link`, `rocker_R_link` with parent `base_footprint`). The PDF shows the tree: missing links between a map and the robot, or between a sensor frame and the base, show up at once.

## `ros2 doctor` (unit 9.5)
- The scenario: `ros2 topic pub /robot/cmd_vel …` prints `publishing #1 …` without error, yet the robot does not move (wrong topic; the controller listens on `/cmd_vel`).
- `ros2 doctor` runs the checks (Humble: platform, network, topic, QoS compatibility, package) and ends `All 5 checks passed` or `N/5 checks failed` with the failed modules. `UserWarning` lines have the form `<path>: <line>: UserWarning: <message>`: `<pkg> has been updated to a new version. local: … < latest: …` (an outdated package, informational) or `Publisher without subscriber detected on /odom.` (normal for sensors nobody listens to).
- `ros2 doctor --report`: NETWORK CONFIGURATION (interfaces, addresses, MTU; the course's `lo` line shows `128.0.0.1`, the loopback is `127.0.0.1`, CPP-V18), PACKAGE VERSIONS, PLATFORM INFORMATION, QOS COMPATIBILITY LIST, RMW MIDDLEWARE (`rmw_fastrtps_cpp`), ROS 2 INFORMATION (`distribution name: humble`, `distribution status: active`), TOPIC LIST with publisher and subscriber counts.
- `ros2 doctor` is the package `ros2doctor` of the ros2cli repository (the course says "the ros2cli package", CPP-V14).
