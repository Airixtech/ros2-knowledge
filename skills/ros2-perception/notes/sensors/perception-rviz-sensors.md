---
id: perception-rviz-sensors
type: reference
owner: equipo-ros2
updated: 2026-10-27
review_by: 2027-04-25
source: manual
confidentiality: internal
title: "RViz2 for perception: Fixed Frame, RobotModel, LaserScan, Image (QoS), PointCloud2, MarkerArray, saved .rviz"
domain: perception
area: sensors
distro: humble
tested: false
audience: dev
summary: "RViz2 setup for perception: Fixed Frame, RobotModel topic, LaserScan/PointCloud2 Size and Style, Image display QoS, MarkerArray topics, rviz2 -d config."
tags: [RViz2, rviz2 -d, Fixed Frame, RobotModel, LaserScan display, Image display, PointCloud2 display, MarkerArray display, QoS, Reliable, .rviz]
see: ["[[core-debug-tools]]", "[[perception-laserscan-msg]]", "[[perception-image-msg]]", "[[perception-pointcloud2-msg]]", "[[core-qos-usage]]"]
requires: [ros2-core]
version_notes: []
---
# RViz2 for perception

**TL;DR** Set the Fixed Frame to the robot's base frame, add one display per sensor topic, match the Image display's QoS to the publisher, and save the layout as a `.rviz` file inside your package so `rviz2 -d` reopens it. General RViz2 use: [[core-debug-tools]].

## One saved setup for the whole course
1. Start `rviz2` (source the workspace that holds the robot's meshes first).
2. **Fixed Frame**: `deepmind_robot1_base_link`.
3. **RobotModel** display, description topic `/deepmind_robot1_robot_description`: the robot appears.
4. Add the three sensor displays:
   - `LaserScan` on `/deepmind_robot1/laser_scan`. `Size` makes the points bigger, `Style` changes how they are drawn.
   - `Image` on `/deepmind_robot1/deepmind_robot1_camera/image_raw`. Set its QoS to History `Keep Last`, Reliability `Reliable`, Durability `Volatile` (it must be compatible with the publisher, [[core-qos-usage]]). The display opens a new render window with the image.
   - `PointCloud2` on `/deepmind_robot1_depth_sensor/points`, with the same `Size` and `Style` options.
5. Save it as `basics_sensor_data.rviz` in the package's `rviz` folder, then close RViz with Ctrl + C in its terminal.

Reopen it any time:
```bash
rviz2 -d ~/ros2_ws/src/basics_sensor_data/rviz/basics_sensor_data.rviz
```
A file in `src/` works from the source tree; to start it from an installed package, install the folder with `data_files` and use `$(ros2 pkg prefix <pkg>)/share/<pkg>/rviz/…` ([[core-debug-tools]], [[perception-python-deps]]).

## Topics the later nodes add
| Display | Topic | Node |
|---|---|---|
| `MarkerArray` | `/visualization_marker_array` | sampled cloud points ([[perception-pointcloud-markers]]) |
| `MarkerArray` | `/bench_markers`, `/object_markers` | surfaces and objects from the cloud ([[perception-surface-detection]], [[perception-object-detection-pcl]]) |
| `Image` | `/detected_faces/faces`, `/detected_faces/eyes` | Haar face and eye detection ([[perception-face-eye-detection]]) |
| `Image` | `/detected_human` | HOG people detection ([[perception-hog-human-tracking]]) |
| `Image` | `/inference_result`, `/pose_estimation_result`, `/segmentation_result` | YOLO nodes ([[perception-yolo-object-detection]], [[perception-yolo-pose]], [[perception-yolo-segmentation]]) |

## Pitfalls
- Nothing drawn and a "No transform" status → the Fixed Frame does not exist in TF yet, or the data's frame is not connected to it.
- An empty Image window → QoS mismatch with the camera (a Reliable display does not receive a Best Effort camera): check `ros2 topic info -v <topic>`.
- Annotated images published with cv_bridge's default encoding show as `8UC3`; RViz draws them like `bgr8`, but other subscribers may reject them: publish with `'bgr8'` ([[perception-yolo-object-detection]]).
