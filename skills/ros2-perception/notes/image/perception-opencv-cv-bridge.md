---
id: perception-opencv-cv-bridge
type: reference
owner: equipo-ros2
updated: 2026-10-27
review_by: 2027-04-25
source: manual
confidentiality: internal
title: "OpenCV and cv_bridge in rclpy: what OpenCV offers, imgmsg_to_cv2 / cv2_to_imgmsg, encodings"
domain: perception
area: image
distro: humble
tested: false
audience: dev
summary: "OpenCV filtering, features (SIFT, ORB, SURF in contrib), detectors; CvBridge imgmsg_to_cv2 and cv2_to_imgmsg with desired_encoding, passthrough, CvBridgeError."
tags: [OpenCV, cv2, cv_bridge, CvBridge, imgmsg_to_cv2, cv2_to_imgmsg, desired_encoding, passthrough, bgr8, 8UC3, CvBridgeError, SIFT, ORB, SURF, opencv_contrib]
see: ["[[core-recipe-cv-bridge]]", "[[perception-image-msg]]", "[[perception-hsv-color-ranges]]", "[[perception-python-deps]]"]
requires: [ros2-core]
version_notes:
  - "humble: imgmsg_to_cv2(img_msg, desired_encoding='passthrough') and cv2_to_imgmsg(cvim, encoding='passthrough', header=None); passthrough sets encoding to the OpenCV type (8UC3); same on the rolling branch released for jazzy, kilted, lyrical — https://github.com/ros-perception/vision_opencv/blob/humble/cv_bridge/python/cv_bridge/core.py (PERC-V32)"
  - "humble: '[8UC3] is not a color format. but [bgr8] is' when converting 8UC3 to a color encoding — https://github.com/ros-perception/vision_opencv/blob/humble/cv_bridge/src/cv_bridge.cpp (PERC-V32)"
  - "opencv 4.x: SIFT and ORB in features2d; SURF only in opencv_contrib xfeatures2d built with OPENCV_ENABLE_NONFREE — https://github.com/opencv/opencv/blob/4.x/modules/features2d/include/opencv2/features2d.hpp , https://github.com/opencv/opencv_contrib/blob/4.x/modules/xfeatures2d/src/surf.cpp (PERC-V09)"
  - "humble: apt python3-opencv 4.5.4 (Ubuntu 22.04); jazzy/kilted 4.6.0 (24.04); lyrical 4.10.0 (26.04) — Ubuntu archive indexes (PERC-V46)"
---
# OpenCV and cv_bridge in rclpy

**TL;DR** OpenCV works on NumPy arrays; ROS works on `sensor_msgs/Image`. `CvBridge().imgmsg_to_cv2(msg, desired_encoding='bgr8')` converts in, `cv2_to_imgmsg(img, encoding='bgr8')` converts out. Always name the encoding: the default `passthrough` keeps the raw type and loses the color order. Short recipe: [[core-recipe-cv-bridge]].

## OpenCV
OpenCV (Open Source Computer Vision Library) is an open-source computer vision and machine learning library for images and videos: image recognition, object detection, facial recognition, video tracking. Families of functions the course relies on:
- **Filtering**: Gaussian, median and bilateral blur for noise reduction and smoothing.
- **Feature extraction**: keypoint detectors and descriptors such as SIFT and ORB (main `features2d` module of 4.x), used for object recognition and tracking. SURF is patented: it lives in `opencv_contrib` (`xfeatures2d`) and exists only in builds with `OPENCV_ENABLE_NONFREE` (PERC-V09).
- **Object detection**: pre-trained Haar cascades ([[perception-haar-cascades]]), HOG descriptors ([[perception-hog-human-tracking]]) and deep-learning methods.
OpenCV functions apply directly to the image data of a `sensor_msgs/Image` once it is converted.

## cv_bridge
`cv_bridge` converts between ROS 2 `sensor_msgs/Image` messages and OpenCV images (`cv::Mat` in C++, a NumPy array in Python) both ways, so image-processing code fits into ROS nodes. The course builds two pipelines on it: blob tracking ([[perception-blob-detect]]) and line following ([[perception-line-follower]]); a short intro to color spaces comes first ([[perception-hsv-color-ranges]]).
```python
from cv_bridge import CvBridge

self.cv_bridge = CvBridge()

def image_callback(self, msg: Image) -> None:
    try:
        # Convert ROS Image message to OpenCV format
        cv_image = self.cv_bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
    except Exception as e:
        self.get_logger().error("Error converting ROS Image to OpenCV format: {0}".format(e))
        return
    # ... OpenCV processing on cv_image (H x W x 3, uint8, BGR) ...
    out = self.cv_bridge.cv2_to_imgmsg(cv_image, 'bgr8')
    out.header = msg.header
```
- `imgmsg_to_cv2` uses the message's `step`, so padded rows are fine; `desired_encoding` converts the color order (an `rgb8` camera comes out as BGR, OpenCV's order).
- `cv2_to_imgmsg(img)` without an encoding writes `encoding: 8UC3`. RViz draws `8UC3` like `bgr8`, but a cv_bridge subscriber that asks for `bgr8` raises `[8UC3] is not a color format. but [bgr8] is` (PERC-V32).
- Conversion errors raise `cv_bridge.CvBridgeError`; catching it (or `Exception`, as the course does) keeps one bad frame from ending the node.

## Pitfalls
- Feeding a BGR image to a library that expects RGB (`face_recognition`, PIL): convert with `cv2.cvtColor(img, cv2.COLOR_BGR2RGB)` ([[perception-face-recognition]]).
- `cv2.imshow` + `cv2.waitKey(1)` inside a callback needs a display; on a headless robot publish the debug image instead.
- Installing `opencv-python` with pip next to apt's `python3-opencv` gives two OpenCV builds on one machine; prefer one route ([[perception-python-deps]]).
