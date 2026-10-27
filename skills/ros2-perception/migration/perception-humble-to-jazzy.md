---
id: perception-humble-to-jazzy
type: reference
owner: equipo-ros2
updated: 2026-10-27
review_by: 2027-04-25
source: manual
confidentiality: internal
title: "The course's perception code on Jazzy and Lyrical: Python and pip rules, numpy, cv_bridge, PCL binding, YOLO"
domain: perception
area: migration
distro: humble
tested: false
audience: dev
summary: "Porting the perception nodes: python-pcl only on Humble, PEP 668 pip rules, numpy<2 with cv_bridge, logger.warn removed in Lyrical."
tags: [migration, Jazzy, Kilted, Lyrical, Ubuntu 24.04, Ubuntu 26.04, python3-pcl, PEP 668, externally-managed-environment, numpy 2, cv_bridge, logger.warn, OpenCV 4.6, OpenCV 4.10, Ultralytics]
see: ["[[perception-python-deps]]", "[[perception-pcl-python]]", "[[perception-opencv-cv-bridge]]", "[[core-logging]]"]
requires: [ros2-core]
version_notes:
  - "Ubuntu indexes (archive.ubuntu.com, 2026-10-26): python3 3.10.4 / 3.12.3 / 3.14.3; python3-numpy 1.21.5 / 1.26.4 / 2.3.5; python3-opencv 4.5.4 / 4.6.0 / 4.10.0; python3-pcl only in 22.04; EXTERNALLY-MANAGED from 24.04 (PERC-V16, PERC-V39, PERC-V40, PERC-V46)"
  - "rosdistro: vision_opencv 3.2.1 (humble), 4.1.0 (jazzy, kilted, lyrical); perception_pcl 2.4.5 / 2.6.5 / 2.10.0 — https://github.com/ros/rosdistro (PERC-V16)"
  - "lyrical: rclpy removed the deprecated RcutilsLogger.warn (rclpy #1456) — https://github.com/ros2/rclpy/blob/lyrical/rclpy/CHANGELOG.rst (PERC-V47)"
  - "humble+: a second rclpy.shutdown() raises RCLError on humble, jazzy and lyrical — https://github.com/ros2/rclpy/blob/lyrical/rclpy/rclpy/context.py (PERC-V03)"
---
# The perception code on Jazzy and Lyrical

**TL;DR** The rclpy, cv_bridge, sensor_msgs_py and tf2 calls of the course work unchanged on Jazzy, Kilted and Lyrical. What breaks is around them: no `python3-pcl` after Ubuntu 22.04, pip refused outside a virtualenv from Ubuntu 24.04, NumPy 2 versus modules built for NumPy 1, and `get_logger().warn()` gone in Lyrical.

## What changes
| Item | Humble (22.04) | Jazzy / Kilted (24.04) | Lyrical (26.04) |
|---|---|---|---|
| Python | 3.10 | 3.12 | 3.14 |
| `import pcl` (python-pcl) | `sudo apt install python3-pcl` | **no package** | **no package** |
| `pip install` system / `--user` | allowed | refused (PEP 668): use a venv or rosdep/apt keys | refused |
| apt NumPy | 1.21.5 | 1.26.4 | 2.3.5 |
| `pip install ultralytics` | add `"numpy<2"` | add `"numpy<2"` | system NumPy is already 2.x |
| apt OpenCV (`python3-opencv`) | 4.5.4 | 4.6.0 | 4.10.0 |
| cv_bridge release | 3.2.1 | 4.1.0 | 4.1.0 |
| `get_logger().warn()` | deprecated alias | deprecated alias | **removed**: `AttributeError` |
| Haar cascades from apt | `opencv-data` → `/usr/share/opencv4/haarcascades/` | same | `opencv-data` 4.10.0 (path not checked) |

Details: [[perception-python-deps]] (pip, venv, NumPy), [[perception-pcl-python]] (PCL).

## What does not change
- `CvBridge().imgmsg_to_cv2()` / `cv2_to_imgmsg()` signatures and the `passthrough` default (`8UC3` without an encoding) ([[perception-opencv-cv-bridge]]).
- `sensor_msgs_py.point_cloud2.read_points` / `read_points_numpy`, `from tf2_sensor_msgs import do_transform_cloud`, `TransformListener(..., spin_thread=...)`, `lookup_transform(..., timeout)` behavior ([[perception-cloud-to-base-link]]).
- `rclpy.try_shutdown()` exists in all of them; a second `rclpy.shutdown()` raises `RCLError` in all of them.
- The message definitions used (`LaserScan`, `Image`, `PointCloud2`, `Marker`, `Trigger`).
- Ultralytics and face_recognition are pip packages with their own release lines, independent of the distro.

## Porting checklist
1. Replace every `get_logger().warn(` with `warning(` (PERC-V47, [[core-logging]]).
2. PCL nodes: on Jazzy and later move the plane/cluster step to C++ (`pcl_ros`, `pcl_conversions`, released for all three) or to another library; the TF and point parsing parts stay in Python ([[perception-cloud-to-base-link]]).
3. Create the venv of the official guide, install `ultralytics "numpy<2"` (Jazzy, Kilted) and the other pip libraries in it; add `COLCON_IGNORE` in the venv folder ([[perception-python-deps]]).
4. Check `numpy.__version__` once in the environment the nodes run in.
5. Rebuild the custom interface package and the Python packages on the new distro ([[perception-custom-msgs]]).
