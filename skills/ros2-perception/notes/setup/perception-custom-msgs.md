---
id: perception-custom-msgs
type: reference
owner: equipo-ros2
updated: 2026-10-27
review_by: 2027-04-25
source: manual
confidentiality: internal
title: "The course's custom_msgs interfaces: detected surfaces and objects, YOLO inference, pose, segmentation, counts"
domain: perception
area: setup
distro: humble
tested: false
audience: dev
summary: "Nine custom .msg files: DetectedSurfaces, DetectedObjects, InferenceResult, Yolov8Inference, PoseKeypoint, PoseResult, SegmentationResult, Yolov8Segmentation, ObjectCount."
tags: [custom_msgs, interface package, msg, DetectedSurfaces, DetectedObjects, InferenceResult, Yolov8Inference, PoseKeypoint, PoseResult, SegmentationResult, Yolov8Segmentation, ObjectCount, rosidl_generate_interfaces]
see: ["[[core-iface-package]]", "[[perception-surface-detection]]", "[[perception-yolo-object-detection]]", "[[perception-learn-project-detection-solution]]"]
requires: [ros2-core]
version_notes:
  - "course: the SegmentationResult text names the class-id field `id`; the file has `class_id` (PERC-V05)"
  - "vision_msgs released: humble 4.1.1, jazzy 4.1.1, lyrical 4.2.0; Detection2DArray = header + Detection2D[] detections — https://github.com/ros/rosdistro/blob/master/humble/distribution.yaml , https://github.com/ros-perception/vision_msgs/blob/ros2/vision_msgs/msg/Detection2DArray.msg"
---
# The course's `custom_msgs` interfaces

**TL;DR** One interface package, `custom_msgs`, holds every message the course's nodes publish. The course copies it ready-made into `~/ros2_ws/src`; to rebuild it, create an ament_cmake interface package ([[core-iface-package]]) with the nine files below and depend on `std_msgs` and `geometry_msgs`.

## Point clouds ([[perception-surface-detection]], [[perception-object-detection-pcl]])
`DetectedSurfaces.msg` (`height` = x extent, `width` = y extent of the cluster)
```text
uint32 surface_id
geometry_msgs/Point position
float32 height
float32 width
```
`DetectedObjects.msg`
```text
uint32 object_id
geometry_msgs/Point position
float32 height
float32 width
float32 thickness
```

## YOLO detection ([[perception-yolo-object-detection]], [[perception-yolo-person-follower]])
`InferenceResult.msg`: one detection: class name, box corners, box size, box center.
```text
string class_name
int64 top
int64 left
int64 bottom
int64 right
int64 box_width
int64 box_height
float64 x
float64 y
```
`Yolov8Inference.msg`: the detections of one frame.
```text
std_msgs/Header header
InferenceResult[] yolov8_inference
```

## YOLO pose ([[perception-yolo-pose]])
`PoseKeypoint.msg`
```text
int64 id
float32 x
float32 y
float32 confidence
```
`PoseResult.msg`
```text
std_msgs/Header header
PoseKeypoint[] keypoints
```

## YOLO segmentation ([[perception-yolo-segmentation]])
`SegmentationResult.msg`
```text
int64 class_id
string class_name
float64 x
float64 y
float64 width
float64 height
```
`Yolov8Segmentation.msg`
```text
std_msgs/Header header
SegmentationResult[] yolov8_segmentation
```

## Project counts ([[perception-learn-project-inventory]])
`ObjectCount.msg`: `header`, the detected class names and, at the same index, their counts.
```text
std_msgs/Header header
string[] classes
int32[] counts
```

## Rebuilding the package
Following [[core-iface-package]] (`[verify]`, not built here):
```cmake
find_package(rosidl_default_generators REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/DetectedSurfaces.msg" "msg/DetectedObjects.msg"
  "msg/InferenceResult.msg" "msg/Yolov8Inference.msg"
  "msg/PoseKeypoint.msg" "msg/PoseResult.msg"
  "msg/SegmentationResult.msg" "msg/Yolov8Segmentation.msg"
  "msg/ObjectCount.msg"
  DEPENDENCIES std_msgs geometry_msgs)
```
`package.xml`: `<depend>std_msgs</depend>`, `<depend>geometry_msgs</depend>`, `rosidl_default_generators` as buildtool dependency, `rosidl_default_runtime` as exec dependency, `<member_of_group>rosidl_interface_packages</member_of_group>`. Every Python package that imports `custom_msgs.msg` adds `<exec_depend>custom_msgs</exec_depend>`.

## Pitfalls
- `float32` fields hold numpy `float64` values with lost precision; harmless for centroids in meters, but the YAML echo shows the float32 digits.
- `Yolov8Inference` and `Yolov8Segmentation` reuse one message object per node: clear the list after publishing (PERC-V36, [[perception-yolo-segmentation]]).
- The standard alternative for detections is `vision_msgs` (`Detection2DArray`), which other ROS tools understand; the course keeps its own messages.
