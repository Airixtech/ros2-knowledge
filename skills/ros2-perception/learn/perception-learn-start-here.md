---
id: perception-learn-start-here
type: reference
owner: equipo-ros2
updated: 2026-10-27
review_by: 2027-04-25
source: manual
confidentiality: internal
title: "Perception course map: units 2-7, the robot and its topics, head tilt tool, packages per unit, exercises"
domain: perception
area: learn
distro: humble
tested: false
audience: students
order: 1
summary: "Perception course map: units 1-7, DeepMind robot topics in the museum simulation, move_head.py tilts, packages per unit, exercises, reading order."
tags: [course, perception course, units, DeepMind robot, museum, move_head.py, deepmind_bot_trajectory_sender, teleop_twist_keyboard, basics_sensor_data, blob_tracking, line_following, bench_detector, hri, advanced_perception, final_project, exercises]
see: ["[[perception-laserscan-msg]]", "[[perception-blob-detect]]", "[[perception-surface-detection]]", "[[perception-face-eye-detection]]", "[[perception-yolo-concepts]]", "[[perception-learn-project]]"]
requires: [ros2-core]
version_notes:
  - "course: `move_head.py` is described as 'Pitch and Yaw', but the commands tilt the head with the second value and the project solution moves [head_base_joint, head_joint]: first value = turn (yaw), second = tilt (pitch) (PERC-V14) [verify]"
---
# Perception course map

**TL;DR** Seven units, practice from the start: sensor messages (2), OpenCV image processing (3), point clouds with PCL (4), faces and people (5), YOLO (6), an inventory project (7). Everything runs on a "DeepMind" robot in a museum simulation of the course platform; the code is Python (rclpy).

## Goals (unit 1)
Perception lets robots understand and interact with their surroundings. By the end: integrate and process sensor data in ROS 2; implement image processing with OpenCV; work with point clouds and the Point Cloud Library (PCL); human-robot interaction techniques (face detection and recognition); deep-learning frameworks for AI perception; a real-world project on intelligent inventory management. Theory and hands-on practice.

| Unit | Topics | Notes |
|---|---|---|
| 1 | course intro, objectives, perception demo | this note |
| 2 | sensor integration: `LaserScan`, `Image`, `PointCloud2` | [[perception-laserscan-msg]], [[perception-image-msg]], [[perception-pointcloud2-msg]], [[perception-pointcloud-markers]], [[perception-rviz-sensors]] |
| 3 | image processing, OpenCV, blob tracking, line following | [[perception-opencv-cv-bridge]], [[perception-hsv-color-ranges]], [[perception-blob-detect]], [[perception-blob-follow]], [[perception-line-follower]], [[perception-door-follower]] |
| 4 | point cloud processing, PCL, surface and object detection | [[perception-pcl-python]], [[perception-cloud-to-base-link]], [[perception-pcl-plane-clusters]], [[perception-surface-detection]], [[perception-object-detection-pcl]] |
| 5 | human-robot interaction: face detection, recognition, human tracking | [[perception-haar-cascades]], [[perception-face-eye-detection]], [[perception-face-recognition]], [[perception-hog-human-tracking]] |
| 6 | YOLO: object detection, person following, pose estimation, segmentation | [[perception-yolo-concepts]], [[perception-yolo-object-detection]], [[perception-yolo-person-follower]], [[perception-yolo-pose]], [[perception-yolo-segmentation]], [[perception-yolo-mask-saver]] |
| 7 | project: intelligent inventory management | [[perception-learn-project]], [[perception-learn-project-inventory]], [[perception-learn-project-detection-solution]], [[perception-learn-project-inventory-solution]] |

Prerequisites (optional, take them when needed): ROS 2 basics in Python, Python 3, OpenCV basics, and the PCL documentation ([pointclouds.org](https://pointclouds.org/)). Setup of the libraries: [[perception-python-deps]].

## Demo (unit 1)
The robot detects a person and drives to them ([[perception-yolo-person-follower]]): if the robot does not appear, restart the simulation; drive near the starting point with `ros2 run teleop_twist_keyboard teleop_twist_keyboard`; source the course simulation workspace and run `ros2 launch advanced_perception launch_yolo_person_follower.launch.py`. The terminal shows `Moving towards person with error_x: 9.5, angular velocity: -0.0095, linear velocity: 0.1, box_width = 93` and, at the end, `[INFO] [yolo_person_follower]: Arrived at destination...`. Afterwards clean the workspace:
```bash
rm -rf ~/ros2_ws/src/advanced_perception/
```

## The robot and its topics
| What | Name |
|---|---|
| base frame (RViz Fixed Frame) | `deepmind_robot1_base_link` |
| robot description | `/deepmind_robot1_robot_description` |
| laser | `/deepmind_robot1/laser_scan` |
| camera (640 × 480, `rgb8`) | `/deepmind_robot1/deepmind_robot1_camera/image_raw` |
| depth camera cloud (frame `deepmind_robot1_camera_depth_optical_frame`) | `/deepmind_robot1_depth_sensor/points` |
| velocity commands | `cmd_vel` |

Course tools (in the course simulation workspace): `ros2 run deepmind_bot_trajectory_sender move_head.py <a> <b> <seconds>` moves the head in a given duration (integer seconds). The course describes the two floats as pitch and yaw, but its commands tilt the head down by raising the **second** value (PERC-V14 `[verify]`). Values used: `0.0 0.7 1` (color detector, cloud markers, segmentation), `0.0 0.5 1` (blob, line follower, YOLO detection), `0.0 0.9 1` (door and project line followers), `0.0 0.3 1` (PCL units, and the static TF), `0.0 0.0 1` (faces, people, YOLO follower). Other course pieces: the HSV trackbar tool `range_detector` ([[perception-hsv-color-ranges]]), launch files that spawn objects on the benches (`spawn_cube.launch.py`, `spawn_fruits.launch.py`, `spawn_models.launch.py` of `perception_ros2`), and RViz configurations for units 5 and 6 (`face_detection.rviz`, `face_recognition.rviz`, `human_tracking.rviz`, `yolo_object_detection.rviz`, `yolo_person_follower.rviz`, `yolo_pose_estimation.rviz`, `yolo_segmentation.rviz`).

## Packages created (all `ament_python` in `~/ros2_ws/src`)
`basics_sensor_data` (unit 2, with an `rviz` folder) · `blob_tracking`, `line_following` (3) · `bench_detector` + the given `custom_msgs` (4, [[perception-custom-msgs]]) · `hri` with a `data` folder (5) · `advanced_perception` with a `data` folder (6) · `final_project` (7). Every executable needs a `console_scripts` entry ([[perception-python-deps]]).

## Exercises
- 2.1 Step of a 2 × 2 `bgr8` image: 2 × 3 = 6 bytes ([[perception-image-msg]]).
- 2.2 Height, width and encoding of the course camera: 480, 640, `rgb8` (`ros2 topic echo` on the image topic, [[perception-image-msg]]).
- 3.1 HSV range of the orange blob near the exit door: 3, 0, 233 – 9, 255, 255 ([[perception-hsv-color-ranges]]).
- 3.2 HSV range of the yellow line: 20, 100, 100 – 40, 255, 255 ([[perception-hsv-color-ranges]]).

## Reading order
Units 2 → 7 in the order of the table; the programs of a unit build on the previous one (blob detector before the follower, surface before objects, detection node before the person follower). Distro differences: [[perception-humble-to-jazzy]].
