---
id: perception-yolo-concepts
type: reference
owner: equipo-ros2
updated: 2026-10-27
review_by: 2027-04-25
source: manual
confidentiality: internal
title: "YOLO: single-stage grid detector, COCO pre-trained models, YOLOv8 sizes n-x and the .pt files"
domain: perception
area: yolo
distro: humble
tested: false
audience: dev
summary: "How YOLO works (grid, boxes, confidence, NMS), COCO's 80 classes, YOLOv8 n-x, -pose and -seg weights, AGPL license."
tags: [YOLO, YOLOv8, Ultralytics, ultralytics, COCO, yolov8n.pt, yolov8n-pose.pt, yolov8n-seg.pt, yolo11, yolo26, non-maximum suppression, IoU, AGPL-3.0, advanced_perception]
see: ["[[perception-yolo-object-detection]]", "[[perception-yolo-pose]]", "[[perception-yolo-segmentation]]", "[[perception-python-deps]]"]
requires: [ros2-core]
version_notes:
  - "ultralytics 8.4.190 (2026-10-26): YOLO('<name>.pt') downloads release assets by name, among them yolov8{n,s,m,l,x}{,-seg,-pose}.pt and the newer yolo11* and yolo26* families; the README example loads yolo26n.pt — https://github.com/ultralytics/ultralytics/blob/main/ultralytics/utils/downloads.py , https://github.com/ultralytics/ultralytics/blob/main/README.md (PERC-V29)"
  - "COCO: 330K images, 200K annotated for detection, segmentation and captioning, 80 categories (Ultralytics' COCO page, the course's source) — https://docs.ultralytics.com/datasets/detect/coco/ (PERC-V29)"
  - "license: Ultralytics is AGPL-3.0; an Enterprise License covers use in business products without the AGPL terms — https://github.com/ultralytics/ultralytics/blob/main/README.md (PERC-V30)"
---
# YOLO concepts and pre-trained models

**TL;DR** YOLO ("You Only Look Once") predicts all boxes and class probabilities of an image in one pass of one CNN, so it runs in real time. Ultralytics ships COCO-trained weights in five sizes (n, s, m, l, x) for detection, pose (`-pose`) and segmentation (`-seg`); the course uses the nano ones. Mind the license: AGPL-3.0.

## How YOLO works
YOLO is a deep-learning model for real-time object detection in images or video. Unlike older methods, it treats detection as a **regression** problem: a single convolutional neural network (CNN) predicts bounding boxes and their probabilities. CNNs suit image recognition, classification and detection because they learn spatial hierarchies of features by themselves through backpropagation. Paper: J. Redmon et al., "You Only Look Once: Unified, Real-Time Object Detection" ([arXiv 1506.02640](https://arxiv.org/pdf/1506.02640.pdf)).
1. **Grid division**: the image is split into an S × S grid; each cell predicts the boxes and confidence scores of the objects whose center falls in it.
2. **Bounding box prediction**: each cell predicts several boxes, each with its dimensions (width, height), a confidence score (how sure the model is that the box holds an object) and class probabilities.
3. **Class prediction**: each cell also predicts class probabilities; box confidence × conditional class probability = a class-specific confidence per box.
4. **Non-max suppression**: overlapping boxes of one object are removed, keeping the most confident box and dropping those with a high overlap (Intersection over Union, IoU) with it (same idea as with HOG, [[perception-hog-human-tracking]]).

What makes it stand out: **speed** (real-time video surveillance, vehicle navigation); **accuracy** usually below slower two-stage detectors such as R-CNN, improved in each version; **single stage** (no separate region proposal + classification), simpler and faster; **good generalization** to scenes unlike the training data, because it sees the whole image at training and test time and so encodes context; **open source**, which drove its adoption.

Tasks used in the course: **object detection** (identify and locate objects in images or video: [[perception-yolo-object-detection]], [[perception-yolo-person-follower]]), **pose estimation** (the orientation and position of objects or humans in a given space, here keypoints of people: [[perception-yolo-pose]]) and **instance segmentation** (detect and segment each object of a scene: [[perception-yolo-segmentation]]).

## Pre-trained models (COCO)
The course trains nothing: the models were trained on **COCO** (Common Objects in Context): 330K images, 200K of them annotated for detection, segmentation and captioning, **80 categories** from cars, bicycles and animals to umbrellas, handbags and sports equipment (class list: `ultralytics/cfg/datasets/coco.yaml`).

| YOLOv8 size | Use |
|---|---|
| `n` (nano) | very constrained devices (mobile, edge): smallest and fastest, least accurate |
| `s` (small) | real-time with a bit more compute than nano; balance of speed and accuracy |
| `m` (medium) | standard applications; higher accuracy, still efficient |
| `l` (large) | high accuracy when compute is less limited |
| `x` (extra large) | highest accuracy and complexity (e.g. cloud servers) |

The course uses **YOLOv8n**: `yolov8n.pt` (detection), `yolov8n-pose.pt` (pose), `yolov8n-seg.pt` (segmentation), downloaded from the "Models" tables (Detection, Pose, Segmentation, all COCO) of the official Ultralytics repository. `YOLO('yolov8n.pt')` also downloads a missing release asset by name; newer families (`yolo11*`, `yolo26*`) are listed the same way (PERC-V29).

## Package for the YOLO nodes
```bash
cd ~/ros2_ws/src/
ros2 pkg create --build-type ament_python advanced_perception
cd ~/ros2_ws/
colcon build
source install/setup.bash
```
```bash
mkdir ~/ros2_ws/src/advanced_perception/data
```
Put the three `.pt` files in `data/`, then create the scripts:
```bash
cd ~/ros2_ws/src/advanced_perception/advanced_perception
touch yolo_object_detection.py yolo_person_follower.py yolo_pose_estimation.py yolo_segmentation.py
chmod +x *.py
cd ~/ros2_ws/
```
Install `data/` with `data_files` and load the weights from the share folder ([[perception-python-deps]]).

## Pitfalls
- License: shipping Ultralytics code or models inside a closed product needs an Enterprise License or compliance with AGPL-3.0 (PERC-V30).
- Small models confuse similar objects at a distance (the course's apple looks like a sports ball until the robot is closer); filter by confidence and class, or use a bigger model.
