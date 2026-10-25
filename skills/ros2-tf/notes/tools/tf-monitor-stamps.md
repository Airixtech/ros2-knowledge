---
id: tf-monitor-stamps
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "tf2_monitor delays and transform timestamps: stamp with the data's time, sim time vs wall clock"
domain: tf
area: tools
distro: jazzy
tested: false
audience: dev
summary: "tf2_monitor chain and per-frame delay now−stamp; static stamps are 0; stamp TF with the data's time; use_sim_time in simulation."
tags: [tf2_monitor, delay, Net delay, Chain is, timestamp, header.stamp, use_sim_time, sim time, wall clock, get_clock().now(), odometry stamp, extrapolation]
see: ["[[tf-odom-broadcaster]]", "[[tf-view-frames]]", "[[core-time-timers]]", "[[core-tf-basics]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: tf2_monitor delay = its node clock now() − header.stamp; the authority is always '<no authority available>' (the course export shows it empty) — https://github.com/ros2/geometry2/blob/jazzy/tf2_ros/src/tf2_monitor.cpp (TF-V02)"
  - "humble: same code; ROS arguments such as --ros-args -p use_sim_time:=true are accepted — https://github.com/ros2/geometry2/blob/humble/tf2_ros/src/tf2_monitor.cpp (TF-V02)"
  - "jazzy: get_clock().now() is wall time unless the node's use_sim_time is true (V69) (TF-V26)"
---
# tf2_monitor delays and transform timestamps

**TL;DR** `tf2_monitor` shows how late each transform of a chain arrives: delay = `now()` of the monitor's own clock − `header.stamp`. Sensor data must be consistent with the TF stamps, otherwise consumers such as RViz discard it. Stamp a transform with the time of the data it comes from, and keep every node on the same clock (`use_sim_time:=true` with a simulator).

## Command and output
```bash
ros2 run tf2_ros tf2_monitor camera_bot_base_link rgb_camera_link_frame
ros2 run tf2_ros tf2_monitor world camera_bot_base_link
ros2 run tf2_ros tf2_monitor world camera_bot_base_link --ros-args -p use_sim_time:=true   # simulation clock [verify]
```
```text
RESULTS: for camera_bot_base_link to rgb_camera_link_frame
Chain is: rgb_camera_link_frame -> chassis -> camera_bot_base_link
Net delay     avg = 3.23952e+08: max = 1.70257e+09

Frames:
Frame: camera_bot_base_link, published by <no authority available>, Average Delay: 0.000354682, Max Delay: 0.00420332
Frame: chassis, published by <no authority available>, Average Delay: 1.70257e+09, Max Delay: 1.70257e+09
Frame: rgb_camera_link_frame, published by <no authority available>, Average Delay: 1.70257e+09, Max Delay: 1.70257e+09

All Broadcasters:
Node:  155.869 Hz, Average Delay: 1.28033e+09 Max Delay: 1.70257e+09
```
For `world camera_bot_base_link` the first broadcaster gives `Net delay     avg = 0.00443906: max = 0.0457809`. Frames directly connected show the time between them; for a longer chain the delays accumulate from the first frame to the last.

## Reading the numbers
| Case | Delay | Why |
|---|---|---|
| static transforms (`chassis`, `rgb_camera_link_frame`) | ≈ 1.70e9 s | stamp 0: the "delay" is the current Unix time; ignore it |
| `world → camera_bot_base_link` stamped with `get_clock().now()` | 4.4 ms | stamp and monitor both on the wall clock: only transport time |
| the same, stamped with the odometry header | ≈ 1.67e9 s | stamp in simulation time, monitor on the wall clock: the number is the gap between the clocks |

The course reads these numbers differently (TF-V02): 4 ms is not "too much for the image module in RVIZ", and the last case does not "behave like a static transform". The real error was the clock: the first broadcaster stamped with wall time while the camera images carried simulation time, so RViz found no transform at the image stamps [verify]. The course's code fix is right.

## The fix: stamp with the data's time
```python
# Get the current odometry data.
time_header = self.cam_bot_odom.header
...
# The timestamp of the TF message is set to the odom message time.
self.transform_stamped.header.stamp = time_header.stamp     # instead of self.get_clock().now().to_msg()
```
Whole program: [[tf-odom-broadcaster]]. The other way is to start the broadcaster with `use_sim_time:=true`, so that `now()` returns simulation time ([[core-time-timers]]).

## Pitfalls
- Huge delays on static frames → expected (stamp 0).
- Extrapolation errors or sensor data never shown → TF and data stamped from different clocks; check `use_sim_time` of every node ([[core-tf-basics]]).
- Monitoring a simulation without `use_sim_time` → every delay includes the wall-to-sim gap.
