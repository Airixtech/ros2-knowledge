---
id: core-recipe-cv-bridge
type: reference
owner: equipo-ros2
updated: 2026-10-27
review_by: 2027-04-25
source: manual
confidentiality: internal
title: "Images with cv_bridge + OpenCV"
domain: core
area: recipes
distro: humble
tested: false
audience: dev
summary: "Convert sensor_msgs/Image to OpenCV and back, HSV color mask, publish debug images, DNN inference pattern, model paths."
tags: [cv_bridge, OpenCV, Image, HSV, DNN, rqt_image_view]
see: ["[[core-exec-callback-groups]]", "[[core-perception-basics]]", "[[core-pkg-workspace]]"]
requires: []
version_notes:
  - "humble+: cv2_to_imgmsg(cvim, encoding='passthrough') writes the OpenCV type ('8UC3'); a later bgr8 conversion raises '[8UC3] is not a color format. but [bgr8] is' — https://github.com/ros-perception/vision_opencv/blob/humble/cv_bridge/python/cv_bridge/core.py (PERC-V32)"
---
# Images with cv_bridge + OpenCV

**TL;DR** `CvBridge().imgmsg_to_cv2(msg, 'bgr8')` gives an OpenCV image, and `cv2_to_imgmsg` converts back (copy the header). Run heavy inference outside the image callback.

## Images (cv_bridge + OpenCV)
```python
import cv2
import numpy as np
from cv_bridge import CvBridge
self.bridge = CvBridge()

def on_image(self, msg):                                       # sensor_msgs/Image
    frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')     # ROS -> OpenCV (BGR)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)                         # feed rgb to DNN/PIL models
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, np.array([34, 84, 0]), np.array([179, 255, 255]))   # "green" range (tune)
    out = self.bridge.cv2_to_imgmsg(cv2.bitwise_and(frame, frame, mask=mask), encoding='bgr8')
    out.header = msg.header
    self.debug_pub.publish(out)
```
- DNN inference pattern: store `self.last_image` in the subscription callback, and run inference in a timer or service in another callback group ([[core-exec-callback-groups]]).
- Model path: use the package share dir (`get_package_share_directory`), never a hard-coded `/home/...` ([[core-pkg-workspace]]).
- View images with `ros2 run rqt_image_view rqt_image_view`.

## Pitfalls
- OpenCV is BGR, while most DNN/PIL models expect RGB. Convert explicitly.
- Subscribe to cameras with sensor QoS. Use compressed transport over Wi-Fi ([[core-perception-basics]]).
- `cv2_to_imgmsg(img)` without an encoding publishes `8UC3`: RViz draws it, but a cv_bridge subscriber asking for `bgr8` raises. Always pass `'bgr8'` (PERC-V32).
- Complete Python pipelines (center-pixel color, HSV blobs and lines, Haar faces, HOG people, YOLO detection, pose and segmentation): the ros2-perception skill.
