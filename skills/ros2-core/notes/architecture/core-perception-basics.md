---
id: core-perception-basics
type: reference
owner: equipo-ros2
updated: 2026-10-27
review_by: 2027-04-25
source: manual
confidentiality: internal
title: "Perception basics: timing, frames, calibration, transport"
domain: core
area: architecture
distro: humble
tested: false
audience: dev
summary: "Sensor QoS, optical frames and IMU conventions, where calibration lives, image/point-cloud transport, composed pipelines, Isaac ROS NITROS."
tags: [perception, camera, calibration, image_transport, point_cloud_transport, NITROS]
see: ["[[core-message-filters]]", "[[core-qos-usage]]", "[[core-composition]]", "[[core-recipe-cv-bridge]]"]
requires: []
version_notes:
  - "jazzy: Isaac ROS 4.x targets Jazzy; Isaac ROS 3.2 is the Humble line (Jetson Orin) [verify] — https://forums.developer.nvidia.com/t/roadmap-for-isaac-ros-jazzy-on-orin-devices/375982 (V68)"
---
# Perception basics: timing, frames, calibration, transport

**TL;DR** Stamp as close to the hardware as possible and use sensor QoS. Optical frames are z-forward. Extrinsics go in the URDF and intrinsics in `camera_info` YAML. Compress over Wi-Fi, and compose pipelines in one container. Perception nodes in Python (OpenCV, PCL, Haar/HOG, YOLO) in detail: the ros2-perception skill.

## Checklist
- Sync quality: hardware trigger > PTP > NTP > software sync ([[core-message-filters]]).
- QoS: camera/lidar/IMU BEST_EFFORT VOLATILE (depth 1–5 / 5 / 10–50); odom RELIABLE; /tf_static & /map TRANSIENT_LOCAL ([[core-qos-usage]]).
- Frames: body x-fwd/y-left/z-up; camera optical z-fwd/x-right/y-down; quaternions x,y,z,w. IMU `linear_acceleration` includes gravity (+9.81 on z at rest).
- Calibration: extrinsics in URDF/xacro (`*_description` pkg); intrinsics YAML via `camera_info_manager` (K/D/R/P); hand-eye: `easy_handeye2` (not released as a Humble binary, build it from source).
- Transport: `image_transport` (compressed/theora/h264) over Wi-Fi; `point_cloud_transport` (draco, zstd); `cv_bridge` share vs copy ([[core-recipe-cv-bridge]]); `pcl_conversions` (`fromROSMsg`/`toROSMsg`).
- Pipelines: composable nodes in one `component_container_mt` with `use_intra_process_comms=True` ([[core-composition]]).
- Isaac ROS NITROS (GPU zero-copy, type adaptation REP 2007/2009): all NITROS nodes go in the same `component_container_mt`. GEMs: `isaac_ros_visual_slam`, `isaac_ros_apriltag`, `isaac_ros_yolov8`, `isaac_ros_ess`. Versions: Isaac ROS 3.2 = Humble, 4.x = Jazzy [verify].

## Pitfalls
- Ignoring gravity in IMU acceleration → a "falling" robot in filters that expect it removed (or the reverse).
- Using the body frame instead of the optical frame for camera data → point clouds rotated 90°.
