# Version audit — ros2-perception (Phase 1)

> Date: 2026-10-26. Scope: every version-dependent or checkable statement of the perception course (course wiki,
> not published; units 1–7, Python/rclpy) that lands in `ros2-perception`: the sensor messages read by hand
> (`LaserScan`, `Image`, `PointCloud2`), RViz2 displays, OpenCV with `cv_bridge` (HSV masks, blob tracking, line
> following), point clouds with a Python PCL binding (region filter, RANSAC plane, Euclidean clusters), Haar cascades,
> `face_recognition`, HOG people detection, Ultralytics YOLOv8 (detection, person follower, pose, segmentation, masks)
> and the inventory project. The course's project solutions (repository given in the course, commit `1c188e9`,
> 2024-06-19: `line_follower.py`, `go_to_aoi.py`, `object_detection.py`, `inventory_checking.py`) were read as
> evidence. Section IDs = the course's section numbers.
> Baseline: **Humble is canonical** (decision of 2026-10-26; the course does not name its distro and its code is plain
> rclpy). Jazzy, Kilted and Lyrical are annotated. Most differences between distros come from the Python libraries
> and Ubuntu's packaging, not from rclpy. Generic ROS 2 rows are in [version_audit.md](version_audit.md) (`Vnn`).

## Method
- Primary sources, read on the matching branch with grep: `ros2/rclpy` (humble, jazzy, lyrical: `__init__.py`,
  `context.py`, `utilities.py`, `time.py`, `node.py`), `ros2/rcl` (humble, jazzy, lyrical: `init.c`),
  `ros2/geometry2` (humble, jazzy, lyrical: `tf2_ros_py/tf2_ros/buffer.py`, `transform_listener.py`, `__init__.py`,
  `tf2_py/src/tf2_py.cpp`, `tf2_sensor_msgs/tf2_sensor_msgs/`), `ros2/common_interfaces` (humble, jazzy:
  `sensor_msgs/msg/*.msg`, `sensor_msgs_py/point_cloud2.py`, `std_srvs/srv/Trigger.srv`),
  `ros-perception/vision_opencv` (humble, rolling = Jazzy/Kilted/Lyrical release branch: `cv_bridge/python/cv_bridge/core.py`,
  `src/cv_bridge.cpp`, `src/module.cpp`), `ros2/rviz` (humble: `ros_image_texture.cpp`), `opencv/opencv` (4.x:
  `objdetect.hpp`, `imgproc.hpp`, `imgproc/doc/colors.markdown`, `features2d.hpp`, `data/haarcascades/`, the Python
  people-detector test), `opencv/opencv_contrib` (4.x: `xfeatures2d/src/surf.cpp`), `ultralytics/ultralytics` (main,
  8.4.190: `engine/results.py`, `utils/downloads.py`, `cfg/datasets/coco*.yaml`, `pyproject.toml`, `README.md`,
  `docs/en/modes/predict.md`, `docs/en/datasets/detect/coco.md`), `ageitgey/face_recognition` (master:
  `face_recognition/api.py`, `README.md`), `PyImageSearch/imutils` (master: `object_detection.py`),
  `strawlab/python-pcl` (master, archived), `davidcaron/pclpy` (master), `ros/rosdistro` (released versions,
  `rosdep/python.yaml`, `rosdep/base.yaml`), `ros2/ros2_documentation` (humble, jazzy: `Using-Python-Packages.rst`),
  `numpy/numpy` (main: `doc/source/dev/depending_on_numpy.rst`).
- Ubuntu packaging: the `Packages.xz` and `Contents-amd64.gz` indexes of `archive.ubuntu.com` for jammy (22.04,
  Humble), noble (24.04, Jazzy and Kilted) and resolute (26.04, Lyrical); Debian's `opencv-data.install` on
  sources.debian.org.
- Origin of the course text: the COCO paragraph of 6.4 follows Ultralytics' COCO dataset page; no public origin was
  found for the YOLO nodes and their `custom_msgs` (a web search found no repository with `Yolov8Inference` /
  `InferenceResult`). The other programs are the course's own.
- Course logic was reviewed too: each variable followed from the code that writes it to the code that reads it, index
  arithmetic, slicing, empty-list cases, exceptions inside callbacks, the order of the course commands, explanations
  against their code. Contradictions are **fix** rows ("course mistake").
- Actions: **keep** = correct for Humble · **annotate** = correct, add marks (Jazzy, Lyrical) or a precise wording ·
  **fix** = wrong for Humble itself. Confidence: High (read in code or the official file) · Medium (docs, or
  inferred) · `[verify]` (needs a run).

## Baseline
| | Humble | Jazzy | Kilted | Lyrical |
|---|---|---|---|---|
| Ubuntu / EOL | 22.04 jammy / May 2027 | 24.04 noble / May 2029 | 24.04 noble / Dec 2026 | 26.04 resolute / May 2031 |
| System Python (`python3`) | 3.10.4 | 3.12.3 | 3.12.3 | 3.14.3 |
| PEP 668 marker (`EXTERNALLY-MANAGED`) / `python3-pip` | no / 22.0.2 | yes (`/usr/lib/python3.12/`) / 24.0 | yes / 24.0 | yes (`/usr/lib/python3.14/`) / 25.1.1 (pip reads the marker since 23.0, [pip NEWS][pip-news]) |
| `python3-numpy` (apt) | 1.21.5 | 1.26.4 | 1.26.4 | 2.3.5 |
| `python3-opencv` / `opencv-data` (apt) | 4.5.4 | 4.6.0 | 4.6.0 | 4.10.0 |
| `vision_opencv` (cv_bridge) release | 3.2.1 | 4.1.0 | 4.1.0 | 4.1.0 |
| `common_interfaces` (sensor_msgs, `sensor_msgs_py`) | 4.9.2 | 5.3.8 | 5.5.3 | 5.9.4 |
| `geometry2` (tf2_ros, `tf2_sensor_msgs` Python) | 0.25.24 | 0.36.23 | 0.41.10 | 0.45.10 |
| rclpy | 3.3.22 | 7.1.12 | 9.1.7 | 10.0.11 |
| `python3-pcl` (python-pcl 0.3.0rc1, apt universe) | 0.3.0~rc1+dfsg-12 | none | none | none |
| `perception_pcl` (C++ `pcl_ros`, `pcl_conversions`) | 2.4.5 | 2.6.5 | 2.10.0 | 2.10.0 |
| Ultralytics (pip, not a ROS package) | 8.4.190 on 2026-10-26: `numpy>=1.23.0`, `opencv-python>=4.7.0`, `torch>=1.8.0`; AGPL-3.0 or Enterprise license | same | same | same |

## Real Humble errors (fix)
| ID | Section | Origin | Error | Correct statement |
|---|---|---|---|---|
| PERC-V01 | 2.3, 2.5, 2.7, 7.5.1 | course mistake (ROS 1 links) | The message definitions of `LaserScan`, `Image`, `PointCloud2` and the `Trigger` service link to the documentation of two ROS 1 distributions | Use the ROS 2 definitions of the canonical branch: [LaserScan][ls-h], [Image][img-h], [PointCloud2][pc2-h], [PointField][pf-h], [Trigger][trig-h] (`common_interfaces`, humble). |
| PERC-V02 | 2.4 | course mistake | `mona_lisa_approach.py`: the 0.5 s timer compares `self.mona_lisa_distance > 0.5` while the value is still `None` (set only by the first scan) | `None > 0.5` raises `TypeError` in Python 3 and ends `rclpy.spin` if the timer fires before the first scan; return early while the value is `None`. |
| PERC-V03 | 2.4; project solution `go_to_aoi.py` | course mistake | `rclpy.shutdown()` is called inside a callback and again at the end of `main()` | The second call raises: `Context.shutdown()` calls `rcl_shutdown`, which returns "rcl_shutdown already called on the given context", and rclpy raises `RCLError` (Humble, Jazzy, Lyrical: [context.py][ctx-h], [init.c][rcl-init-h]). Use `rclpy.try_shutdown()` in `main()` (exported since Humble, [__init__.py][rclpy-init-h]) or stop with a flag. |
| PERC-V05 | 2.5, 3.8, 3.11, 4.3, 5.7, 6.13 | course typos | `heigth`; "`rgb8` similar to `b0gr8`"; `sensors_msgs/Image`; `crop_top_image` in the 3.11 review (the file uses `crop_top_img`); `extract_bench_clusters()` in the 4.3 text (the method is `extract_clusters`); `image_callback(self, msg: None)`; "yolov8n-pose model for instance segmentation" (the file loads `yolov8n-seg.pt`); `ultralytics.engine.results` used as a type (it is a module; the class is `Results`); "non-maximam" | `height`; `bgr8`; `sensor_msgs/Image`; `crop_top_img`; `extract_clusters()`; `msg: Image`; "yolov8n-seg model"; `ultralytics.engine.results.Results`; "non-maximum". |
| PERC-V06 | 2.6 | course mistake | `color_detector.py`: `center_index = ((height // 2) * width + (width // 2)) * byte_depth`, then three branches on `center_index % byte_depth`; for `rgb8` the blue byte is `center_index - 1` | `center_index` is always a multiple of 3, so only the first branch runs and "blue" is the last byte of the **previous** pixel (works only on uniform areas). For `rgb8` the bytes are R = `i`, G = `i + 1`, B = `i + 2`. Index rows with `msg.step` ("Full row length in bytes", [Image.msg][img-h]): `i = (height // 2) * msg.step + (width // 2) * 3`, and check `msg.encoding` (`rgb8` vs `bgr8`). |
| PERC-V07 | 2.8 | course mistake | `point_cloud_marker.py`: `step_size = len(msg.data) // num_points` and every read starts at `i` | The start of a read must be a multiple of `point_step`; here it is only by chance (9,830,400 / 50 = 196,608 = 6,144 × 32 B). Step by points: `stride = (msg.width * msg.height // 50) * msg.point_step`, and read `x/y/z` at the offsets of `msg.fields`. |
| PERC-V11 | 3.6 | course mistake (explanation vs code) | "If no blob is detected, it rotates the robot continuously until an orange blob is found" | `no_blob_detected` starts `True` and is never set back: the node rotates only **before the first** detection. Later, `blob_point_pub.py` publishes nothing when no contour is found, and the tracker sends no new command. |
| PERC-V12 | 3.9, 3.10, 3.11; project solution `line_follower.py` | course mistake | `crop_img = cv_image[height*3//4:height*3//4 + rows_to_watch][1:width]` (and `cv_image[1:cols_to_watch][1:width]` for the door crop) | The second `[...]` slices the **rows** of the 20-row crop again (it drops row 0); the columns are not cropped. Use one 2D index: `cv_image[r0:r1, 0:width]`, as the course's own project solution `go_to_aoi.py` does ([NumPy indexing][np-index]). |
| PERC-V13 | 3.10, 3.11; project solution `line_follower.py` | course mistake | `most_right_centroid = max(centres, key=...)` before the `try`, whose `except` should fall back to the image center | With no contour, `max()` of an empty list raises `ValueError` before the `try`, and the exception ends the node (an exception in an rclpy callback leaves `spin`). The project solution `go_to_aoi.py` guards it with `if centres:`. |
| PERC-V14 | 2.6 (and every `move_head.py` call) | course mistake | "adjust the robot's head in Pitch (float value) and Yaw (float value) within a specified duration" | The commands tilt the head down by changing the **second** value (`0.0 0.5 1`, `0.0 0.9 1`), and the project solution moves the joints `[deepmind_robot1_head_base_joint, deepmind_robot1_head_joint]` with `[0.0, -0.2]` (up) and `[0.0, 0.7]` (down): the first value turns the head (yaw), the second tilts it (pitch) `[verify]` (`move_head.py` is not shown). |
| PERC-V15 | 4.2 | course mistake | "the most recommended option … would be to use pclpy … Python bindings specifically designed for ROS 2" | pclpy is a general PCL binding installed with conda, for Python 3.6–3.8 and PCL 1.9.1 (its [README][pclpy]; last commit 2021); nothing in it is ROS-specific, and the official ROS 2 guide warns that a conda interpreter is likely incompatible with ROS 2 binaries ([Using Python Packages][pypkg-h]). The course code does not use it: `import pcl`, `make_segmenter()`, `make_EuclideanClusterExtraction()` are the API of **python-pcl** ([python-pcl][pypcl], archived). |
| PERC-V22 | 5.2 | course mistake (source attribution) | "The OpenCV library manages a repository containing all popular haar cascades", linking a third-party fork | The cascades live in `data/haarcascades` of [opencv/opencv][cv-haar] (17 files, among them `haarcascade_frontalface_default.xml` and `haarcascade_eye.xml`). On Ubuntu 22.04 and 24.04, `sudo apt install opencv-data` puts them in `/usr/share/opencv4/haarcascades/` (Contents index of jammy and noble; Debian's [opencv-data.install][deb-ocvdata]). |
| PERC-V23 | 5.2 | course mistake | "A higher `scaleFactor` increases sensitivity but also increases processing time, while a lower `scaleFactor` decreases sensitivity but speeds up processing" | Reversed. `scaleFactor` is "how much the image size is reduced at each image scale" ([objdetect.hpp][cv-objdetect]): a higher value means fewer scales, so it is faster and may miss faces between two scales; a lower value (e.g. 1.05) means more scales, slower and more detections. |
| PERC-V25 | 5.5 | course mistake | `face_recognition.py`: after a match, `break` | `break` leaves only the inner loop over one person's encodings; the outer loop goes on with the other people, so one face can get several labels. Stop both loops (e.g. a flag or a function that returns the first match). |
| PERC-V31 | 6.5; project solution `object_detection.py` | course mistake | `# get box coordinates in (top, left, bottom, right) format` above `b = box.xyxy[0]…` | `xyxy` is `[x1, y1, x2, y2]` = (left, top, right, bottom) ([results.py][ul-results]); the code assigns `left = b[0]`, `top = b[1]`, `right = b[2]`, `bottom = b[3]` correctly, only the comment is wrong. |
| PERC-V33 | 6.5, 6.10, 6.13; project solution `object_detection.py` | course mistake (platform paths) | `YOLO('/home/user/ros2_ws/src/advanced_perception/data/yolov8n.pt')` and `output_dir = '/home/user/…'`; the solution uses `YOLO('~/ros2_ws/src/final_project/data/yolov8n.pt')` | Absolute paths of the course machine. Python does not expand `~`: `attempt_download_asset` finds no such file, sees that `yolov8n.pt` is a release asset and **downloads a new copy** to `./~/ros2_ws/…` under the current directory ([downloads.py][ul-dl]), ignoring the file you placed. Install the models with the package (`data_files`) and build the path with `get_package_share_directory`, or pass it as a parameter; `os.path.expanduser` if you keep a home path. |
| PERC-V36 | 6.13 | course mistake | `yolo_segmentation.py`: `#self.yolov8_segmentation.yolov8_segmentation.clear()` (commented out) | The same message object is reused, so every frame **appends** to the list and the published message grows without bound (memory, bandwidth, stale objects). Clear it after publishing, as the detection node of 6.5 does, or build a new message per frame. |
| PERC-V37 | 6.13 | course mistake | "This line initializes an instance of the `YoloSegmentation` custom ROS message" | `YoloSegmentation` is the segmentation **node** class imported from `yolo_segmentation.py`: the saver builds a second node named `segmentation` (with its own subscription and publishers, never spun) only to reach its `model`, and loads the weights a second time. Loading `YOLO(<path>)` in the saver is enough. |
| PERC-V44 | project solution `inventory_checking.py` | course mistake | `missing_items = {item: expected_counts[item] - total_count[item] for item in expected_counts if item not in total_count or total_count[item] < expected_counts[item]}` | When a class is missing entirely, the condition is true and the value reads `total_count[item]` → `KeyError`, caught by `main()` as "Error during inventory". Use `total_count.get(item, 0)`. |

## Full table
| # | Section | Statement | Humble | Jazzy | Lyrical | Action | Source | Confidence |
|---|---|---|---|---|---|---|---|---|
| PERC-V01 | 2.3, 2.5, 2.7, 7.5.1 | message docs linked to ROS 1 | ✗ use ROS 2 msg files | ✗ same | ✗ same | **fix** | [ls-h], [img-h], [pc2-h], [trig-h] | High |
| PERC-V02 | 2.4 | timer compares `None > 0.5` | ✗ TypeError | ✗ same | ✗ same | **fix** | Python 3 semantics | High |
| PERC-V03 | 2.4; solution | second `rclpy.shutdown()` | ✗ RCLError; `try_shutdown()` | ✗ same | ✗ same (`_cleanup` calls shutdown again) | **fix** | [ctx-h], [rcl-init-h], [rclpy-init-h], [ctx-l] | High |
| PERC-V04 | 2.3, 2.4 | `len(ranges)//2` is the front; discard values outside `range_min`/`range_max`; `intensities` may be empty | ✓ front only for symmetric scans: angle 0 is at index `round(-angle_min / angle_increment)` (angles around +Z, zero along +X); the two notes match the msg comments | ✓ | ✓ | annotate | [ls-h] | High |
| PERC-V05 | several | typos and wrong names | ✗ | ✗ | ✗ | **fix** | course files | High |
| PERC-V06 | 2.6 | center-pixel component indices | ✗ blue = previous pixel; use `step` and encoding | ✗ | ✗ | **fix** | [img-h] | High |
| PERC-V07 | 2.8 | 50 reads every `len(data)//50` bytes | ✗ aligned by chance | ✗ | ✗ | **fix** | [pc2-h] | High |
| PERC-V08 | 2.7, 2.8 | parse `PointCloud2` bytes by hand; `is_dense` = "dense or sparse" | ✓ works for this layout; `sensor_msgs_py.point_cloud2.read_points` / `read_points_numpy(cloud, field_names, skip_nans)` read any layout and byte order (Humble+); `is_dense` = "True if there are no invalid points"; `datatype 7` = `FLOAT32` | ✓ same API | ✓ same API | annotate | [pc2py-h], [pc2py-j], [pc2-h], [pf-h] | High |
| PERC-V09 | 3.2 | OpenCV offers SIFT, SURF and ORB | ✓ SIFT and ORB are in the main `features2d` module (4.x); SURF is in `opencv_contrib` `xfeatures2d` and needs a build with `OPENCV_ENABLE_NONFREE` ("This algorithm is patented") | ✓ | ✓ | annotate | [cv-f2d], [cv-surf] | High |
| PERC-V10 | 3.4 | Hue "is measured in degrees on a color wheel" | ✓ for 8-bit images OpenCV stores H/2: `COLOR_BGR2HSV` gives H in 0..180, S and V in 0..255 (the course's ranges are in this scale) | ✓ | ✓ | annotate | [cv-imgproc], [cv-colors] | High |
| PERC-V11 | 3.6 | tracker rotates whenever no blob | ✗ only before the first detection | ✗ | ✗ | **fix** | course code | High |
| PERC-V12 | 3.9–3.11; solution | `img[a:b][1:width]` crops columns | ✗ rows twice | ✗ | ✗ | **fix** | [np-index], course solution | High |
| PERC-V13 | 3.10, 3.11; solution | `max(centres)` falls back in `except` | ✗ ValueError first | ✗ | ✗ | **fix** | course code and solution | High |
| PERC-V14 | 2.6 | `move_head.py` args "pitch and yaw" | ✗ yaw then pitch | ✗ | ✗ | **fix** | course commands, project solution | Medium, `[verify]` |
| PERC-V15 | 4.2 | pclpy "designed for ROS 2" and used by the code | ✗ conda-only, Python 3.6–3.8; code is python-pcl | ✗ | ✗ | **fix** | [pclpy], [pypcl], [pypkg-h] | High |
| PERC-V16 | 4.2, 4.3 | python-pcl as the PCL binding | ✓ `sudo apt install python3-pcl` (jammy universe 0.3.0~rc1+dfsg-12); no rosdep key; upstream archived ("no longer maintained") | ✗ no Ubuntu 24.04 package; C++ `pcl_ros`/`pcl_conversions` released (2.6.5) | ✗ no 26.04 package; C++ released (2.10.0) | annotate | Ubuntu indexes, [pypcl], [rosdep-py], [distro-j], [distro-l] | High |
| PERC-V17 | 4.3 | Python loop over every point + hand-written quaternion matrix | ✓ correct (standard rotation matrix); a Python loop over 307,200 points per message is slow; official alternatives: `from tf2_sensor_msgs import do_transform_cloud` and `read_points_numpy(cloud, field_names=('x', 'y', 'z'), skip_nans=True)` (Humble) | ✓ same | ✓ same | annotate | [tf2sm-h], [pc2py-h] | High (API), Medium (speed) |
| PERC-V18 | 4.3 | "problems with transformations that result in the disappearance of the transforms" | ✓ the workaround works; in rclpy, `lookup_transform(..., timeout=…)` inside a callback waits on the executor thread (`sleep(0.02)` loop), and `TransformListener` has `spin_thread=False` by default, so no new TF is received during the wait; `TransformListener(buffer, node, spin_thread=True)` gives it a thread. The course's cause is not shown | ✓ same code | ✓ same code | annotate | [tf2buf-h], [tf2lis-h], [tf2buf-j], [tf2buf-l] | High (code), `[verify]` (cause) |
| PERC-V19 | 4.3 | static TF base_link → camera optical frame from one `tf2_echo` | ✓ valid only for the head pose of the measurement (`move_head.py 0.0 0.3 1`): the camera moves with the head joints, so another tilt gives wrong points | ✓ | ✓ | annotate | course commands and output | High |
| PERC-V20 | 4.3 | `DetectedSurfaces.height` / `width` | ✓ `height` holds the x extent (logged as "Length"), `width` the y extent | ✓ | ✓ | annotate | course code | High |
| PERC-V21 | 4.3, 6.13 | `tf2_ros.ConnectivityException`, `rclpy.time.Duration`, `rclpy.executors.SingleThreadedExecutor` without import | ✓ tf2_ros re-exports tf2's exceptions; `rclpy.time` imports `Duration` (its home is `rclpy.duration`); `rclpy.node` imports `rclpy.executors`, so the attribute exists | ✓ | ✓ | keep | [tf2py-h], [rclpy-time-h], [rclpy-node-h] | High |
| PERC-V22 | 5.2 | cascades "managed by OpenCV" in a fork | ✗ official repo; `opencv-data` path | ✗ same path (noble) | official repo | **fix** | [cv-haar], Contents indexes, [deb-ocvdata] | High |
| PERC-V23 | 5.2 | `scaleFactor` effect | ✗ reversed | ✗ | ✗ | **fix** | [cv-objdetect] | High |
| PERC-V24 | 5.2, 5.5 | missing cascade file: log and `return` in `__init__` | ✓ the node keeps running without `self.face_cascade`, and every image raises `AttributeError`; raise or shut down instead | ✓ | ✓ | annotate | course code | High |
| PERC-V25 | 5.5 | `break` after the first match | ✗ inner loop only | ✗ | ✗ | **fix** | course code | High |
| PERC-V26 | 5.5 | `face_encodings(rgb_face_image)` on the Haar crop | ✓ without `known_face_locations` the library runs its own face detector again on the crop (`_raw_face_landmarks`); pass the crop as one box in (top, right, bottom, left) order: `known_face_locations=[(0, w, h, 0)]`. `compare_faces` default `tolerance=0.6` ("lower is more strict"); `load_image_file` returns RGB | ✓ | ✓ | annotate | [fr-api] | High (code), `[verify]` (crops that fail) |
| PERC-V27 | 5.5 | "the face_recognition library built into Python" | ✓ it is a pip package (1.4.0) built on dlib: install dlib first (README); rosdep has `python3-dlib-pip`, no key for face_recognition | ✓ (pip in a venv, V40) | ✓ (same) | annotate | [fr-readme], [rosdep-py] | High |
| PERC-V28 | 5.7 | HOG people detector, NMS 0.65, angular command | ✓ `cv2.HOGDescriptor_getDefaultPeopleDetector()` is used by OpenCV 4.x's own Python test; imutils `non_max_suppression(boxes, probs=None, overlapThresh=0.3)` (the course passes 0.65); the node publishes `angular.z` only when a person is found, never a stop | ✓ | ✓ | annotate | [cv-hog-test], [imutils-nms] | High |
| PERC-V29 | 6.4 | COCO 330K images, 200K annotated, 80 classes; YOLOv8 n–x from the README "Models" table | ✓ text from Ultralytics' COCO page; `YOLO('yolov8n.pt')` downloads release assets by name (`yolov8{n,s,m,l,x}{,-seg,-pose}.pt`); newer families `yolo11*` and `yolo26*` are listed too, and the README example uses `yolo26n.pt` | ✓ | ✓ | annotate | [ul-coco], [ul-dl], [ul-readme] | High |
| PERC-V30 | 6.4 | Ultralytics "open source" | ✓ AGPL-3.0; an Enterprise License is required to ship it in business products without the AGPL terms (README) | ✓ | ✓ | annotate | [ul-readme], [ul-license] | High |
| PERC-V31 | 6.5; solution | `xyxy` comment "(top, left, bottom, right)" | ✗ (left, top, right, bottom) | ✗ | ✗ | **fix** | [ul-results] | High |
| PERC-V32 | 6.5, 6.13 | `bridge.cv2_to_imgmsg(annotated_frame)` without encoding | ✓ RViz shows it, but the default `passthrough` sets `encoding = '8UC3'`: RViz treats `8UC3` like `bgr8`, while a cv_bridge subscriber asking for `bgr8` gets "[8UC3] is not a color format. but [bgr8] is"; pass `'bgr8'` (`plot()` returns BGR) | ✓ same (rolling branch) | ✓ same | annotate | [cvb-core-h], [cvb-cpp-h], [rviz-tex-h], [ul-predict] | High |
| PERC-V33 | 6.5–6.13; solution | `/home/user/…` and `~/…` model paths | ✗ platform paths; `~` → new download | ✗ | ✗ | **fix** | [ul-dl] | High |
| PERC-V34 | 6.5 | `self.model(img)` with a `bgr8` image; `results[0].plot()` | ✓ NumPy input is HWC BGR uint8; `plot()` returns a BGR NumPy array | ✓ | ✓ | keep | [ul-predict], [ul-results] | High |
| PERC-V35 | 6.10 | keypoints 5, 7, 9 = left shoulder, elbow, wrist; `if results and results[0].keypoints` | ✓ COCO order (0 nose … 16 right_ankle); an empty `Keypoints` has length 0, so the check skips frames without people; `[0]` takes only the first person; `keypoints.conf` is `None` for models without visibility; clip the cosine to [-1, 1] before `np.arccos` (NaN outside) and check each keypoint's confidence | ✓ | ✓ | annotate | [ul-coco-pose], [ul-results], [np-arccos] | High |
| PERC-V36 | 6.13 | segmentation list cleared each frame | ✗ `clear()` commented out | ✗ | ✗ | **fix** | course code | High |
| PERC-V37 | 6.13 | `YoloSegmentation()` "custom ROS message" | ✗ a second node | ✗ | ✗ | **fix** | course code | High |
| PERC-V38 | 6.13 | `results.masks.data` resized with `cv2.resize` to the image | ✓ `masks.data` is the raw mask tensor at the model's input size; `masks.xy` gives each segment in original-image pixels | ✓ | ✓ | annotate | [ul-results] | High |
| PERC-V39 | setup (beyond source) | `pip install ultralytics` on a ROS machine | ✓ Ultralytics needs `numpy>=1.23.0` and Ubuntu 22.04 ships 1.21.5, so pip installs a newer NumPy; NumPy 2 changed the C ABI ("Wheels built against NumPy 1.xx will not work with NumPy 2.0 or later") and cv_bridge's `cv_bridge_boost` module, apt's OpenCV and `python3-pcl` are built against 1.x: keep `"numpy<2"` (1.x minor releases stay compatible) | ✓ same rule (noble has 1.26.4) | ✓ system NumPy 2.3.5, cv_bridge built against 2.x | annotate | [ul-pyproject], [np-abi], [cvb-module-h] | Medium, `[verify]` (run) |
| PERC-V40 | setup (beyond source) | `pip install` of the course libraries | ✓ allowed (no PEP 668 marker); the official guide lists rosdep keys, apt, `pip --user` and a virtualenv made with the system interpreter (`touch venv/COLCON_IGNORE`) | ✗ `EXTERNALLY-MANAGED` present: pip refuses system **and** `--user` installs (PEP 668: both show up on the system interpreter's `sys.path`), although the Jazzy guide still shows `pip install --user`; use rosdep/apt keys or the guide's virtualenv (`--break-system-packages` is the PEP's opt-out) | ✗ same | annotate | [pypkg-h], [pypkg-j], [pep668], Contents indexes | High |
| PERC-V41 | setup (beyond source) | rosdep keys for the course libraries | ✓ `python3-opencv`, `python3-numpy`, `cv_bridge`, `sensor_msgs_py`, `tf2_ros`, `python3-ultralytics-pip`, `python3-imutils-pip`, `python3-dlib-pip`; none for face_recognition or python-pcl | ✓ | ✓ | keep | [rosdep-py] | High |
| PERC-V42 | 7.5.1 | `Trigger`: empty request, `bool success`, `string message` | ✓ | ✓ | ✓ | keep | [trig-h] | High |
| PERC-V43 | 7.5.1; solution | excluded classes `dining table, keyboard, umbrella, remote`; cell phones under 100 px filtered | ✓ the solution also excludes `chair`; counts are kept only for classes not excluded | ✓ | ✓ | annotate | project solution | High |
| PERC-V44 | solution | `missing_items` comprehension | ✗ KeyError when a class is absent | ✗ | ✗ | **fix** | project solution | High |
| PERC-V45 | solution | "Wait the detection to complete" with `time.sleep(10)` | ✓ callbacks run only while the node spins: during the sleep no count is processed; the next `spin_until_future_complete` (the stop call) runs the queued `ObjectCount` callbacks, the first one stores the count and clears `detected_objects`. Spin or use a timer instead of sleeping | ✓ | ✓ | annotate | project solution, rclpy executor | Medium |
| PERC-V46 | setup (beyond source) | OpenCV versions | ✓ apt `python3-opencv` 4.5.4; `pip install ultralytics` also installs the `opencv-python` wheel (`>=4.7.0`) next to it | ✓ apt 4.6.0, same | ✓ apt 4.10.0, same | annotate | Ubuntu indexes, [ul-pyproject] | Medium |

## Canonical alternatives (features of a later distro)
None: every API the notes use exists in Humble (`sensor_msgs_py.point_cloud2.read_points_numpy`, `tf2_sensor_msgs.do_transform_cloud`, `TransformListener(spin_thread=True)`, `rclpy.try_shutdown`). The other way round, python-pcl exists only on Humble (PERC-V16).

## Open `[verify]` (Phase 5 or a real machine)
- PERC-V14: argument order of `move_head.py` (course tool, not shown).
- PERC-V18: the real cause of the "disappearing transforms" in 4.3 (blocked executor, sim time, or the head joints).
- PERC-V26: how often `face_encodings` finds no face in a tight Haar crop without `known_face_locations`.
- PERC-V39: `pip install ultralytics` on Humble upgrading NumPy to 2.x and breaking `cv_bridge` imports.

## Sources
[ls-h]: https://github.com/ros2/common_interfaces/blob/humble/sensor_msgs/msg/LaserScan.msg
[img-h]: https://github.com/ros2/common_interfaces/blob/humble/sensor_msgs/msg/Image.msg
[pc2-h]: https://github.com/ros2/common_interfaces/blob/humble/sensor_msgs/msg/PointCloud2.msg
[pf-h]: https://github.com/ros2/common_interfaces/blob/humble/sensor_msgs/msg/PointField.msg
[trig-h]: https://github.com/ros2/common_interfaces/blob/humble/std_srvs/srv/Trigger.srv
[pc2py-h]: https://github.com/ros2/common_interfaces/blob/humble/sensor_msgs_py/sensor_msgs_py/point_cloud2.py
[pc2py-j]: https://github.com/ros2/common_interfaces/blob/jazzy/sensor_msgs_py/sensor_msgs_py/point_cloud2.py
[ctx-h]: https://github.com/ros2/rclpy/blob/humble/rclpy/rclpy/context.py
[ctx-l]: https://github.com/ros2/rclpy/blob/lyrical/rclpy/rclpy/context.py
[rcl-init-h]: https://github.com/ros2/rcl/blob/humble/rcl/src/rcl/init.c
[rclpy-init-h]: https://github.com/ros2/rclpy/blob/humble/rclpy/rclpy/__init__.py
[rclpy-time-h]: https://github.com/ros2/rclpy/blob/humble/rclpy/rclpy/time.py
[rclpy-node-h]: https://github.com/ros2/rclpy/blob/humble/rclpy/rclpy/node.py
[tf2buf-h]: https://github.com/ros2/geometry2/blob/humble/tf2_ros_py/tf2_ros/buffer.py
[tf2buf-j]: https://github.com/ros2/geometry2/blob/jazzy/tf2_ros_py/tf2_ros/buffer.py
[tf2buf-l]: https://github.com/ros2/geometry2/blob/lyrical/tf2_ros_py/tf2_ros/buffer.py
[tf2lis-h]: https://github.com/ros2/geometry2/blob/humble/tf2_ros_py/tf2_ros/transform_listener.py
[tf2py-h]: https://github.com/ros2/geometry2/blob/humble/tf2_py/src/tf2_py.cpp
[tf2sm-h]: https://github.com/ros2/geometry2/blob/humble/tf2_sensor_msgs/tf2_sensor_msgs/tf2_sensor_msgs.py
[cvb-core-h]: https://github.com/ros-perception/vision_opencv/blob/humble/cv_bridge/python/cv_bridge/core.py
[cvb-cpp-h]: https://github.com/ros-perception/vision_opencv/blob/humble/cv_bridge/src/cv_bridge.cpp
[cvb-module-h]: https://github.com/ros-perception/vision_opencv/blob/humble/cv_bridge/src/module.cpp
[rviz-tex-h]: https://github.com/ros2/rviz/blob/humble/rviz_default_plugins/src/rviz_default_plugins/displays/image/ros_image_texture.cpp
[cv-objdetect]: https://github.com/opencv/opencv/blob/4.x/modules/objdetect/include/opencv2/objdetect.hpp
[cv-haar]: https://github.com/opencv/opencv/tree/4.x/data/haarcascades
[cv-hog-test]: https://github.com/opencv/opencv/blob/4.x/modules/objdetect/misc/python/test/test_peopledetect.py
[cv-imgproc]: https://github.com/opencv/opencv/blob/4.x/modules/imgproc/include/opencv2/imgproc.hpp
[cv-colors]: https://github.com/opencv/opencv/blob/4.x/modules/imgproc/doc/colors.markdown
[cv-f2d]: https://github.com/opencv/opencv/blob/4.x/modules/features2d/include/opencv2/features2d.hpp
[cv-surf]: https://github.com/opencv/opencv_contrib/blob/4.x/modules/xfeatures2d/src/surf.cpp
[deb-ocvdata]: https://sources.debian.org/src/opencv/4.6.0+dfsg-12/debian/opencv-data.install/
[ul-results]: https://github.com/ultralytics/ultralytics/blob/main/ultralytics/engine/results.py
[ul-dl]: https://github.com/ultralytics/ultralytics/blob/main/ultralytics/utils/downloads.py
[ul-pyproject]: https://github.com/ultralytics/ultralytics/blob/main/pyproject.toml
[ul-readme]: https://github.com/ultralytics/ultralytics/blob/main/README.md
[ul-license]: https://github.com/ultralytics/ultralytics/blob/main/LICENSE
[ul-predict]: https://docs.ultralytics.com/modes/predict/
[ul-coco]: https://docs.ultralytics.com/datasets/detect/coco/
[ul-coco-pose]: https://github.com/ultralytics/ultralytics/blob/main/ultralytics/cfg/datasets/coco-pose.yaml
[fr-api]: https://github.com/ageitgey/face_recognition/blob/master/face_recognition/api.py
[fr-readme]: https://github.com/ageitgey/face_recognition/blob/master/README.md
[imutils-nms]: https://github.com/PyImageSearch/imutils/blob/master/imutils/object_detection.py
[pypcl]: https://github.com/strawlab/python-pcl
[pclpy]: https://github.com/davidcaron/pclpy
[pypkg-h]: https://docs.ros.org/en/humble/How-To-Guides/Using-Python-Packages.html
[pypkg-j]: https://docs.ros.org/en/jazzy/How-To-Guides/Using-Python-Packages.html
[rosdep-py]: https://github.com/ros/rosdistro/blob/master/rosdep/python.yaml
[distro-j]: https://github.com/ros/rosdistro/blob/master/jazzy/distribution.yaml
[distro-l]: https://github.com/ros/rosdistro/blob/master/lyrical/distribution.yaml
[np-abi]: https://numpy.org/doc/stable/dev/depending_on_numpy.html
[np-index]: https://numpy.org/doc/stable/user/basics.indexing.html
[np-arccos]: https://numpy.org/doc/stable/reference/generated/numpy.arccos.html
[pep668]: https://peps.python.org/pep-0668/
[pip-news]: https://github.com/pypa/pip/blob/main/NEWS.rst
