---
id: perception-pcl-python
type: reference
owner: equipo-ros2
updated: 2026-10-27
review_by: 2027-04-25
source: manual
confidentiality: internal
title: "PCL for ROS 2 Python nodes: filtering, segmentation, clustering and which Python binding the code uses"
domain: perception
area: pointcloud
distro: humble
tested: false
audience: dev
summary: "Point Cloud Library roles (filter, segment, cluster); python-pcl (import pcl, apt python3-pcl on Humble only) vs pclpy; C++ pcl_ros alternative."
tags: [PCL, Point Cloud Library, python-pcl, python3-pcl, import pcl, pclpy, pcl_ros, pcl_conversions, filtering, segmentation, clustering, bench_detector]
see: ["[[perception-cloud-to-base-link]]", "[[perception-pcl-plane-clusters]]", "[[perception-surface-detection]]", "[[core-perception-basics]]", "[[perception-humble-to-jazzy]]"]
requires: [ros2-core]
version_notes:
  - "course: pclpy is not ROS-specific (conda only, Python 3.6-3.8, PCL 1.9.1) and the course code does not use it: `import pcl`, make_segmenter() and make_EuclideanClusterExtraction() are python-pcl's API — https://github.com/davidcaron/pclpy , https://github.com/strawlab/python-pcl , https://docs.ros.org/en/humble/How-To-Guides/Using-Python-Packages.html (PERC-V15)"
  - "humble: Ubuntu 22.04 universe has python3-pcl 0.3.0~rc1+dfsg-12; jazzy/kilted (24.04) and lyrical (26.04): no package; upstream archived; no rosdep key — Ubuntu archive indexes, https://github.com/ros/rosdistro/blob/master/rosdep/python.yaml (PERC-V16)"
  - "all distros: C++ perception_pcl (pcl_ros, pcl_conversions) released: humble 2.4.5, jazzy 2.6.5, lyrical 2.10.0 — https://github.com/ros/rosdistro/blob/master/jazzy/distribution.yaml (PERC-V16)"
---
# PCL from Python nodes

**TL;DR** PCL is a C++ library; the course's Python code uses the **python-pcl** binding (`import pcl`), which Ubuntu 22.04 packages as `python3-pcl` and later Ubuntu releases do not. On Humble: `sudo apt install python3-pcl`. On Jazzy and later: do the PCL part in C++ (`pcl_ros`, `pcl_conversions`) or without PCL ([[perception-humble-to-jazzy]]).

## What PCL does
The Point Cloud Library is a large open project for processing 2D/3D images and point clouds, with state-of-the-art algorithms for:
- **Filtering**: removing noise and outliers to make the data cleaner and more reliable.
- **Segmentation**: splitting the data into meaningful regions by spatial proximity, color, intensity or geometric properties.
- **Clustering**: grouping points by similar properties (spatial proximity, geometric features) for pattern recognition and analysis.
These serve noise reduction, merging of 3D clouds, finding the relevant parts of a scene, keypoint extraction, descriptors for geometric object recognition, and surface generation. With ROS 2, PCL makes point-cloud pipelines for perception and decision-making.

The course builds two workflows in a package `bench_detector`: **surface detection** (the flat tops of the museum's benches, [[perception-surface-detection]]) and **object detection** (objects standing on them, [[perception-object-detection-pcl]]).

## Which Python binding
PCL is primarily C++. The course text recommends **pclpy** "designed for ROS 2"; that is wrong twice (PERC-V15): pclpy is a general binding released only through conda for Python 3.6–3.8 and PCL 1.9.1 (its README), and the ROS 2 guide warns that a conda interpreter is likely incompatible with ROS 2 binaries ([Using Python Packages](https://docs.ros.org/en/humble/How-To-Guides/Using-Python-Packages.html)). The course code uses the API of **python-pcl** instead: `pcl.PointCloud`, `from_array()`, `extract()`, `make_segmenter()`, `make_kdtree()`, `make_EuclideanClusterExtraction()`.

| Distro (Ubuntu) | python-pcl | C++ PCL in ROS |
|---|---|---|
| Humble (22.04) | `sudo apt install python3-pcl` (0.3.0rc1, universe) | `pcl_ros`, `pcl_conversions` 2.4.5 |
| Jazzy, Kilted (24.04) | no package | `pcl_ros`, `pcl_conversions` 2.6.5 / 2.10.0 |
| Lyrical (26.04) | no package | `pcl_ros`, `pcl_conversions` 2.10.0 |

python-pcl's repository is archived ("no longer maintained") and rosdep has no key for it, so `package.xml` cannot declare it for `rosdep install`: document the apt step instead.

## Pitfalls
- `ModuleNotFoundError: No module named 'pcl'` on Jazzy → there is no package; building python-pcl yourself against a newer PCL is not covered here (PERC-V16).
- The course's `from_ros_msg()` loops over every point in Python (307,200 per message); `sensor_msgs_py` reads them in one NumPy call ([[perception-cloud-to-base-link]]).
- Frames: PCL works on raw coordinates; transform the cloud to `base_link` first so that heights mean something ([[perception-cloud-to-base-link]]).
