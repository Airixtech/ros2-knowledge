---
id: moveit-simple-grasping
type: reference
owner: equipo-ros2
updated: 2026-10-28
review_by: 2027-04-26
source: manual
confidentiality: internal
title: "simple_grasping: object detection from a depth camera point cloud, its two programs, the wrist camera topics"
domain: moveit
area: perception
distro: humble
tested: false
audience: dev
summary: "simple_grasping package: basic_grasping_perception (find_objects action) and object_support_segmentation on a PointCloud2; ros-humble-simple-grasping; wrist_rgbd_depth_sensor topics."
tags: [simple_grasping, basic_grasping_perception, basic_grasping_perception.cpp, object_support_segmentation, find_objects, FindGraspableObjects, depth camera, PointCloud2, /wrist_rgbd_depth_sensor/points, /head_camera/depth_registered/points, grasp planning, perception, pick and place, Mike Ferguson]
see: ["[[moveit-find-objects-action]]", "[[moveit-simple-grasping-code]]", "[[moveit-grasping-msgs]]", "[[moveit-scene-grasp-boxes]]", "[[core-perception-basics]]"]
requires: [ros2-core]
version_notes:
  - "humble: simple_grasping 0.5.0 and grasping_msgs 0.4.0 are released (apt); Jazzy 0.5.0/0.5.0, Kilted and Lyrical 0.6.0/0.5.0 — https://github.com/ros/rosdistro/blob/master/humble/distribution.yaml (MOVEIT-V37)"
  - "humble: the course's modified copy subscribes /wrist_rgbd_depth_sensor/points and sets voxel_limit_min to -1.0; the release subscribes /head_camera/depth_registered/points (voxel_limit_min 0.0) and adds continuous_detection and QoS overrides — https://github.com/mikeferguson/simple_grasping/blob/jazzy/src/basic_grasping_perception.cpp (MOVEIT-V37)"
---
# simple_grasping: find the objects to pick

**TL;DR** A pick needs the object's pose. `simple_grasping` (by Mike Ferguson; original code: https://github.com/mikeferguson/simple_grasping/tree/ros2) takes the point cloud of a 3D (depth) camera, separates the support surface from the objects on it, and can also compute grasp poses for many object shapes. The course uses only the detection part, through the `find_objects` action ([[moveit-find-objects-action]]).

## Get the package
The course clones a copy it modified for its robot (repository given in the course) into `~/ros2_ws/src` and builds it (`cd ~/ros2_ws/src`, `git clone …`, `cd ..`, `colcon build`, `source install/setup.bash`). The original is released:
```bash
sudo apt install ros-humble-simple-grasping
```
(0.5.0 on Humble and Jazzy, 0.6.0 on Kilted and Lyrical; with `grasping_msgs`, MOVEIT-V37). Differences of the course copy: it subscribes `/wrist_rgbd_depth_sensor/points` instead of `/head_camera/depth_registered/points`, its `voxel_limit_min` default is −1.0 instead of 0.0, and it lacks the release's `continuous_detection` parameter and QoS overrides. With the release, a remap and a parameter replace the edits ([[moveit-find-objects-action]]).

## The two programs (in `src/`)
- `basic_grasping_perception.cpp`: the node `basic_grasping_perception_node`; offers the action server `/find_objects` that triggers the detection pipeline ([[moveit-simple-grasping-code]]).
- `object_support_segmentation.cpp`: processes the camera's point cloud to find the support surfaces and the graspable objects on them.

## The depth camera
Spawn a box in front of the arm (x 0.5, y 0.13, [[moveit-scene-grasp-boxes]]) and list the topics:
```bash
ros2 topic list
```
```
...
/wrist_rgbd_depth_sensor/camera_info
/wrist_rgbd_depth_sensor/depth/camera_info
/wrist_rgbd_depth_sensor/depth/image_raw
/wrist_rgbd_depth_sensor/depth/image_raw/compressed
/wrist_rgbd_depth_sensor/depth/image_raw/compressedDepth
/wrist_rgbd_depth_sensor/depth/image_raw/theora
/wrist_rgbd_depth_sensor/image_raw
/wrist_rgbd_depth_sensor/image_raw/compressed
/wrist_rgbd_depth_sensor/image_raw/compressedDepth
/wrist_rgbd_depth_sensor/image_raw/theora
/wrist_rgbd_depth_sensor/points
```
`/wrist_rgbd_depth_sensor/points` carries the depth data as a point cloud: the input of `simple_grasping`. Check it in RViz2 (`rviz2`, add a `PointCloud2` display on that topic). Sensor QoS and optical frames: [[core-perception-basics]]; point clouds read in Python: the ros2-perception skill; simulated depth cameras: the ros2-gazebo skill.

## Pitfalls
- The released node listens on `/head_camera/depth_registered/points`: without the remap it waits for a cloud and the action aborts after 3 s ([[moveit-simple-grasping-code]]).
- The cloud is transformed into `frame_id` (default `base_link`): the camera's TF must be complete.
