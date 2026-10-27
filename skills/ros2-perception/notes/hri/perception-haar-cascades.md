---
id: perception-haar-cascades
type: reference
owner: equipo-ros2
updated: 2026-10-27
review_by: 2027-04-25
source: manual
confidentiality: internal
title: "Haar cascades (Viola-Jones): how they work, OpenCV's pre-trained XML files, detectMultiScale parameters"
domain: perception
area: hri
distro: humble
tested: false
audience: dev
summary: "Viola-Jones Haar cascade classifiers, OpenCV's pre-trained XML cascades (opencv-data path), CascadeClassifier.detectMultiScale scaleFactor and minNeighbors."
tags: [Haar cascade, Viola-Jones, cv2.CascadeClassifier, detectMultiScale, scaleFactor, minNeighbors, haarcascade_frontalface_default.xml, haarcascade_eye.xml, opencv-data, face detection, hri]
see: ["[[perception-face-eye-detection]]", "[[perception-face-recognition]]", "[[perception-python-deps]]", "[[perception-opencv-cv-bridge]]"]
requires: [ros2-core]
version_notes:
  - "opencv 4.x: the 17 pre-trained cascades are in data/haarcascades of opencv/opencv (no mouth cascade; haarcascade_smile.xml exists) — https://github.com/opencv/opencv/tree/4.x/data/haarcascades (PERC-V22)"
  - "humble (22.04) and jazzy (24.04): `sudo apt install opencv-data` installs them in /usr/share/opencv4/haarcascades/ — Ubuntu Contents index, https://sources.debian.org/src/opencv/4.6.0+dfsg-12/debian/opencv-data.install/ (PERC-V22)"
  - "course: the scaleFactor explanation was reversed; scaleFactor is 'how much the image size is reduced at each image scale' — https://github.com/opencv/opencv/blob/4.x/modules/objdetect/include/opencv2/objdetect.hpp (PERC-V23)"
---
# Haar cascades (Viola-Jones)

**TL;DR** A Haar cascade is a pre-trained XML classifier; `cv2.CascadeClassifier(path).detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)` returns `(x, y, w, h)` boxes. Take the XML files from OpenCV itself (`opencv-data` on Ubuntu, or the official repository). A higher `scaleFactor` is **faster** and may miss faces; a lower one finds more and costs more.

## How the detector works
**Haar feature-based cascade classifiers** are the object detection method of Paul Viola and Michael Jones (2001): a machine-learning approach where a cascade function is trained from many positive images (with faces) and negative images (without), and then detects the object in other images. A window slides over the image and features are computed in each window to decide whether it can hold the object. Each Haar feature is a single value: the sum of the pixels under the white rectangle minus the sum under the black rectangle. The algorithm scans an image fast, finds the regions likely to contain faces and returns bounding boxes around them. It is simple and efficient, a good choice for **resource-constrained** hardware. Training needs a large, carefully curated set of positive and negative examples; pre-trained cascades avoid that work.

Reference: P. Viola, M. Jones, "Rapid Object Detection using a Boosted Cascade of Simple Features" (CVPR 2001; mathematical and machine-learning detail).

## Pre-trained cascades from OpenCV
Haar cascades are **XML files** OpenCV loads to detect a given object: `haarcascade_frontalface_default.xml` holds the set of features and weights that describe the typical characteristics of frontal faces. OpenCV ships 17 in `data/haarcascades` of its repository ([opencv/opencv 4.x](https://github.com/opencv/opencv/tree/4.x/data/haarcascades)): frontal faces (`haarcascade_frontalface_default.xml`, trained on many positive and negative face images, plus `_alt`, `_alt2`, `_alt_tree`), eyes (`haarcascade_eye.xml`, `haarcascade_eye_tree_eyeglasses.xml`, left/right eye), profile face, smile, full/upper/lower body, cat faces, license plates. The course says "mouth detection"; there is no mouth cascade in OpenCV 4.x (PERC-V22).

On Ubuntu 22.04 and 24.04:
```bash
sudo apt install opencv-data
ls /usr/share/opencv4/haarcascades/
```
The course instead puts copies in a `data` folder of its `hri` package and installs them with `data_files` ([[perception-python-deps]]):
```bash
mkdir ~/ros2_ws/src/hri/data
```

## `detectMultiScale` parameters
```python
faces = self.face_cascade.detectMultiScale(gray_image, scaleFactor=1.3, minNeighbors=5)
```
- Input: a grayscale image. Converting to gray simplifies the pipeline, saves computation and can improve detection.
- `scaleFactor`: how much the image size is reduced at each image scale ([objdetect.hpp](https://github.com/opencv/opencv/blob/4.x/modules/objdetect/include/opencv2/objdetect.hpp)). Bigger steps (1.3) = fewer scales: faster, but faces whose size falls between two scales can be missed. Smaller steps (1.05) = more scales: slower, more detections. The course states the opposite (PERC-V23).
- `minNeighbors`: how many neighboring detections a candidate needs to be kept. Higher = more conservative and better quality; lower = more liberal, more false positives.
- Output: a list of rectangles `(x, y, w, h)`: top-left corner, width, height.

## Pitfalls
- `cv2.CascadeClassifier` with a wrong path does not raise: `load()` just fails, `empty()` is true, and `detectMultiScale` raises later (`CV_Assert(!empty())`, [cascadedetect.cpp](https://github.com/opencv/opencv/blob/4.x/modules/objdetect/src/cascadedetect.cpp)). Check `os.path.isfile()` (as the course does) and stop the node if it is missing ([[perception-face-eye-detection]]).
- Frontal-face cascades miss profiles and tilted heads; combine with `haarcascade_profileface.xml` or use a DNN or YOLO model ([[perception-yolo-concepts]]).
