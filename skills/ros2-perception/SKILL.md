---
name: ros2-perception
description: "ROS 2 perception in Python (Humble): LaserScan, Image, PointCloud2, cv_bridge, OpenCV HSV, blob and line following, PCL, Haar, face_recognition, HOG, YOLO. Jazzy/Lyrical notes."
---
# ros2-perception — perception nodes in Python (rclpy)

Atomic notes for writing perception nodes and debugging them. **Humble is canonical**; differences for later versions are marked, never substituted. Most differences come from the Python libraries and Ubuntu's packaging, not from rclpy. Paths are relative to this skill's folder. `[[note-id]]` means the file `<note-id>.md`; find it via the area index or a glob `**/<note-id>.md`.

## Golden rules (always apply)
1. Check the distro first. Humble (Ubuntu 22.04): apt `python3-opencv`, `python3-pcl`, pip allowed. Jazzy, Kilted, Lyrical (24.04/26.04): no `python3-pcl`, pip refused outside a virtualenv (PEP 668), and `get_logger().warn()` is gone in Lyrical (use `warning()`). With pip libraries (Ultralytics) keep `"numpy<2"` on Humble and Jazzy: cv_bridge, apt OpenCV and python-pcl are built for NumPy 1 ([[perception-humble-to-jazzy]], [[perception-python-deps]]).
2. Images: `CvBridge().imgmsg_to_cv2(msg, 'bgr8')` in, `cv2_to_imgmsg(img, 'bgr8')` out; always name the encoding (the default `passthrough` publishes `8UC3`). OpenCV is BGR; face_recognition and PIL want RGB. Reading raw `data` by hand: row stride is `msg.step`, byte order follows `msg.encoding` ([[perception-opencv-cv-bridge]], [[perception-image-msg]]).
3. LaserScan: beam `i` is at `angle_min + i * angle_increment` (0 = forward, + = left); the front index is `round(-angle_min / angle_increment)`, the middle only for symmetric scans; discard values outside `[range_min, range_max]` and `inf`/`nan` ([[perception-laserscan-msg]]).
4. PointCloud2: read it with `sensor_msgs_py.point_cloud2.read_points_numpy(cloud, field_names=('x','y','z'), skip_nans=True)` (offsets, `point_step`, byte order, NaN), and bring it to `base_link` with `tf2_sensor_msgs.do_transform_cloud` before using heights. A fixed static TF to a camera on a moving head is valid for one pose only ([[perception-pointcloud2-msg]], [[perception-cloud-to-base-link]]).
5. Color segmentation: HSV with OpenCV's 8-bit scale (H 0–180, S and V 0–255), ranges tuned with trackbars on the real camera, red split in two ranges; crop with one 2D index `img[r0:r1, c0:c1]` (`img[a:b][c:d]` slices rows twice) ([[perception-hsv-color-ranges]], [[perception-line-follower]]).
6. Contours to motion: guard empty lists before `max()`, skip `m00 == 0`, steer with the normalized offset of the centroid, clamp the angular speed, and stop or search again when the target is lost (no message = no new command) ([[perception-blob-detect]], [[perception-blob-follow]], [[perception-door-follower]]).
7. Classic detectors: grayscale input; Haar `detectMultiScale(gray, scaleFactor, minNeighbors)`: a bigger `scaleFactor` is faster and may miss faces, a higher `minNeighbors` gives fewer false positives; HOG people detector + non-maximum suppression. Cascades come from `opencv-data` or the package's `data/` installed with `data_files` and found with `get_package_share_directory` ([[perception-haar-cascades]], [[perception-face-eye-detection]], [[perception-hog-human-tracking]]).
8. YOLO (Ultralytics): load the weights from the package share folder (never an absolute path; `~` is not expanded and triggers a new download); `box.xyxy` = left, top, right, bottom; `results[0].plot()` is BGR; clear a reused result list after each publish; filter by `box.conf` and keypoint confidence. License: AGPL-3.0 unless an Enterprise License covers the product ([[perception-yolo-object-detection]], [[perception-yolo-concepts]], [[perception-yolo-pose]]).
9. Heavy work in a callback blocks the executor: subscribe to cameras with depth 1, or keep the last frame and process it in a timer; replace per-point Python loops by NumPy ([[perception-yolo-object-detection]], [[perception-cloud-to-base-link]]).
10. Ending a node: a second `rclpy.shutdown()` raises `RCLError` (after Ctrl + C, or after a callback that shut down): use `rclpy.try_shutdown()` or check `rclpy.ok()` ([[perception-laserscan-msg]]; the `main()` pattern is ros2-core's `core-node-skeleton`).

## Retrieval protocol
1. Pick the area from the **Areas** table below (column "Covers").
2. Open that area's `_index.md` and choose notes by their summary.
3. Open 1–3 notes. Use their code as the template: keep the structure, adapt the names, topics and color ranges.
4. No clear match → `grep -ril "<keyword>" notes/` (API names work best: `imgmsg_to_cv2`, `inRange`, `findContours`, `moments`, `read_points_numpy`, `make_segmenter`, `CascadeClassifier`, `face_encodings`, `HOGDescriptor`, `YOLO(`, `keypoints`, `masks`) and open the top hits.
5. Follow a note's `see:` links **one hop** at most. Perception basics (sensor QoS, optical frames, calibration, image transport), cv_bridge in short, TF listeners, interface packages and `setup.py` live in ros2-core.
6. Do not open `learn/` unless the question is about the perception course (DeepMind robot in a museum, inventory project).
7. Jazzy, Kilted, Lyrical or installing the libraries → open `migration/` and `setup/` and apply the version marks.
8. Simulated cameras and lidars → answer with modern Gazebo (Gazebo Sim, the ros2-gazebo skill); the same pipelines in C++ (cv_bridge, PCL) → the ros2-cpp skill; TF in depth → the ros2-tf skill.
If the notes do not cover the question, read the official source for the user's distro (below) or say that you answer from standard knowledge. Never invent APIs, parameters or model files.

## Version marks and official sources
`[Humble]` Humble-only · `[≥Jazzy]` added in Jazzy (or later) · `[changed in Jazzy: …]` / `[changed in Lyrical: …]` what to use there instead · `[verify]` not confirmed by a source or a build: tell the user. Each note's `version_notes` holds the source URL and audit ID of every difference (`reports/version_audit_perception.md`).

| Distro | Ubuntu / Python | apt OpenCV / NumPy | cv_bridge | python-pcl | Read first |
|---|---|---|---|---|---|
| Humble | 22.04 / 3.10 | 4.5.4 / 1.21.5 | 3.2.1 | `python3-pcl` | docs.ros.org/en/humble; branches `humble` of vision_opencv, common_interfaces, geometry2 |
| Jazzy, Kilted | 24.04 / 3.12 | 4.6.0 / 1.26.4 | 4.1.0 | none | docs.ros.org/en/jazzy; vision_opencv `rolling` |
| Lyrical | 26.04 / 3.14 | 4.10.0 / 2.3.5 | 4.1.0 | none | docs.ros.org/en/lyrical (pages under `ROS-Framework/`) |

Ultralytics, face_recognition and imutils are pip packages with their own versions (checked 2026-10-26: Ultralytics 8.4.190).

## Areas
<!-- INDEX:START -->
<!-- generated by tools/build_index.py — do not edit by hand -->
| Area | Notes | Open | Covers |
|---|---|---|---|
| sensors | 5 | `notes/sensors/_index.md` | Sensor messages read by hand in rclpy: sensor_msgs/LaserScan (ranges, angles), Image (encoding, step, data bytes), PointCloud2 (fields, offsets, point_step), MarkerArray from points, RViz2 displays for perception |
| image | 6 | `notes/image/_index.md` | OpenCV with cv_bridge in Python: imgmsg_to_cv2, HSV color ranges (inRange, trackbar tuning), blob detection (contours, moments), blob following, line following (crop, centroid error), door/area following |
| pointcloud | 5 | `notes/pointcloud/_index.md` | Point clouds in Python: PCL bindings (python-pcl, pclpy), PointCloud2 to base_link with TF, region filter, RANSAC plane segmentation, Euclidean clustering, surface and object-on-surface detection, markers |
| hri | 4 | `notes/hri/_index.md` | Human-robot interaction perception: Haar cascades (face, eye detection, detectMultiScale), face_recognition encodings, HOG + SVM people detection, non-maximum suppression, turning toward a person |
| yolo | 6 | `notes/yolo/_index.md` | Ultralytics YOLO (YOLOv8) in ROS 2 nodes: models and COCO, object detection results (boxes, classes), person follower, pose keypoints and joint angles, instance segmentation masks and counts |
| setup | 2 | `notes/setup/_index.md` | Python perception packages: custom detection messages (custom_msgs), data_files for models and cascades, package share paths, installing OpenCV, PCL, face_recognition, Ultralytics (rosdep, apt, pip, venv, numpy<2) |
| learn | 5 | `learn/_index.md` | Perception course for students (DeepMind robot in a museum): course map, exercises, inventory-management project and its solution; open only for course questions |
| migration | 1 | `migration/_index.md` | The course's perception code on Jazzy, Kilted and Lyrical: Python and pip rules (PEP 668), NumPy 2 and cv_bridge, python-pcl availability, Ultralytics; open for other distros |
<!-- INDEX:END -->

## Related skills
ros2-core (required): nodes, topics, QoS, TF basics, interface packages, `setup.py`, the short cv_bridge and LaserScan recipes and the perception basics note; install it with this skill. Named in plain text, never required: ros2-cpp (cv_bridge and image pipelines in C++), ros2-tf (static and dynamic broadcasters), ros2-gazebo (simulated cameras, depth sensors and lidars).
