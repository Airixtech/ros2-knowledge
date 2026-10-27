---
id: perception-yolo-pose
type: reference
owner: equipo-ros2
updated: 2026-10-27
review_by: 2027-04-25
source: manual
confidentiality: internal
title: "YOLOv8 pose estimation node: COCO keypoints, confidence, joint angle from three keypoints"
domain: perception
area: yolo
distro: humble
tested: false
audience: dev
summary: "yolov8n-pose node: keypoints.xy and keypoints.conf of the first person, PoseResult/PoseKeypoint messages, COCO keypoint indices, elbow angle with arccos."
tags: [pose estimation, YOLO, yolov8n-pose, keypoints, keypoints.xy, keypoints.conf, COCO keypoints, PoseKeypoint, PoseResult, yolov8_pose_results, pose_estimation_result, joint angle, np.arccos, yolo_pose_estimation.py]
see: ["[[perception-yolo-object-detection]]", "[[perception-custom-msgs]]", "[[perception-yolo-concepts]]"]
requires: [ros2-core]
version_notes:
  - "ultralytics: COCO pose order 0 nose, 1 left_eye, 2 right_eye, 3 left_ear, 4 right_ear, 5 left_shoulder, 6 right_shoulder, 7 left_elbow, 8 right_elbow, 9 left_wrist, 10 right_wrist, 11 left_hip, 12 right_hip, 13 left_knee, 14 right_knee, 15 left_ankle, 16 right_ankle — https://github.com/ultralytics/ultralytics/blob/main/ultralytics/cfg/datasets/coco-pose.yaml (PERC-V35)"
  - "ultralytics: an empty Keypoints object has length 0 (the `if` skips frames without people); keypoints.conf is None for models without visibility — https://github.com/ultralytics/ultralytics/blob/main/ultralytics/engine/results.py (PERC-V35)"
  - "course: the model was loaded from an absolute path of the course machine; now from the package share folder (PERC-V33)"
---
# YOLOv8 pose estimation node

**TL;DR** With `yolov8n-pose.pt`, `results[0].keypoints.xy` holds the (x, y) pixels of 17 COCO keypoints per person and `.conf` their confidence. The node publishes the first person's keypoints and logs the angle at the left elbow (keypoints 5, 7, 9) from the dot product of the two limb vectors.

## Pose estimation
Pose estimation finds the location of specific points of an image, the **keypoints**: the arrangement of body parts (joints and limbs of people, or points of objects) and how they are placed. The output is a set of points, usually with a confidence score each; use it when you need specific parts of an object and their positions relative to each other.
- **2D pose estimation**: the parts' positions in the image plane (e.g. elbows and knees of a person).
- **3D pose estimation**: adds the depth of the parts relative to the camera; harder.
Applications: human-computer interaction (gesture recognition, intuitive interfaces), sports analytics (movement analysis, injury prevention), animation and gaming (motion capture), robotics (understand human poses and interact better).

Keypoint indices of the COCO pose model ([coco-pose.yaml](https://github.com/ultralytics/ultralytics/blob/main/ultralytics/cfg/datasets/coco-pose.yaml)): 0 nose, 1–2 left/right eye, 3–4 left/right ear, **5** left shoulder, 6 right shoulder, **7** left elbow, 8 right elbow, **9** left wrist, 10 right wrist, 11–12 left/right hip, 13–14 left/right knee, 15–16 left/right ankle.

## `yolo_pose_estimation.py`
```python
#!/usr/bin/env python3

import os
from ament_index_python.packages import get_package_share_directory
from ultralytics import YOLO
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from custom_msgs.msg import PoseKeypoint, PoseResult
import numpy as np
from typing import List


class PoseEstimationNode(Node):

    def __init__(self) -> None:
        super().__init__('pose_estimation_node')
        # Load pre-trained yolov8n-pose model for pose estimation (installed with the package, PERC-V33)
        self.model = YOLO(os.path.join(get_package_share_directory('advanced_perception'), 'data', 'yolov8n-pose.pt'))
        self.subscription = self.create_subscription(Image, '/deepmind_robot1/deepmind_robot1_camera/image_raw', self.image_callback, 10)
        self.pose_publisher = self.create_publisher(PoseResult, "/yolov8_pose_results", 1)
        self.image_publisher = self.create_publisher(Image, "/pose_estimation_result", 1)
        self.bridge = CvBridge()

    def image_callback(self, data: Image) -> None:
        """ Performs the pose estimation by extracting the detected keypoints
            and publishes the annotated image for visualization purposes.
            Additonally, it calculates the angle between specified keypoints for further analysis """
        img = self.bridge.imgmsg_to_cv2(data, "bgr8")
        results = self.model(img)

        pose_result = PoseResult()
        pose_result.header.stamp = self.get_clock().now().to_msg()
        pose_result.header.frame_id = "pose_estimation"

        if results and results[0].keypoints:
            keypoints = results[0].keypoints.xy.cpu().numpy()[0]
            confidence = results[0].keypoints.conf.cpu().numpy()[0]

            for idx, kpt in enumerate(keypoints):
                keypoint = PoseKeypoint()
                keypoint.id = idx
                keypoint.x = float(kpt[0])
                keypoint.y = float(kpt[1])
                keypoint.confidence = float(confidence[idx])
                pose_result.keypoints.append(keypoint)

            # E.g., Left shoulder (5), Left elbow (7), and Left wrist (9)
            self.calculate_angle(pose_result.keypoints, 5, 7, 9)

            self.pose_publisher.publish(pose_result)

        annotated_frame = results[0].plot()
        img_msg = self.bridge.cv2_to_imgmsg(annotated_frame, 'bgr8')
        self.image_publisher.publish(img_msg)

    def calculate_angle(self, keypoints: List[PoseKeypoint], index1: int, index2: int, index3: int) -> None:
        """ Calculate the angle in degrees between three keypoints """
        # Make sure we have enough keypoints
        if len(keypoints) >= 3:
            pt1 = [keypoints[index1].x, keypoints[index1].y]
            pt2 = [keypoints[index2].x, keypoints[index2].y]
            pt3 = [keypoints[index3].x, keypoints[index3].y]

            # Calculate the vectors
            v1 = np.array(pt1) - np.array(pt2)
            v2 = np.array(pt3) - np.array(pt2)

            # Calculate the angle in radians
            angle_rad = np.arccos(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))

            # Convert to degrees
            angle_deg = np.degrees(angle_rad)

            self.get_logger().info(f"The angle between the keypoints {index1}, {index2} and {index3} is equal to {angle_deg:.2f} degrees.")
        else:
            self.get_logger().info(f"Not enough keypoints to calculate the angle ...")


def main(args=None) -> None:
    rclpy.init(args=args)
    pose_estimation = PoseEstimationNode()
    rclpy.spin(pose_estimation)
    pose_estimation.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```
- Messages ([[perception-custom-msgs]]): `PoseKeypoint` = one keypoint (`id`, `x`, `y`, `confidence`); `PoseResult` = `header` + list `keypoints`. Topics: `/yolov8_pose_results` (keypoints) and `/pose_estimation_result` (annotated image).
- `results[0].keypoints.xy` is a tensor (on the GPU if there is one); `.cpu()` moves it to CPU memory, `.numpy()` converts it, `[0]` selects the **first person**; `.conf` gives each keypoint's confidence.
- `calculate_angle()`: `v1` goes from `pt2` to `pt1`, `v2` from `pt2` to `pt3`; the angle at `pt2` is `arccos(v1·v2 / (|v1| |v2|))`, converted to degrees. For 5, 7, 9 that is the left elbow.
- The course's explanation calls the converter `bridge`; the file uses `self.bridge`.

## Launch and test
```bash
cd ~/ros2_ws/
colcon build;source install/setup.bash
ros2 run advanced_perception yolo_pose_estimation
```
Drive around with teleop to both people of the simulation and show `/pose_estimation_result` in RViz. Log for the standing person:
```text
[INFO] [1713841616.193716306] [pose_estimation_node]: The angle between the keypoints 5, 7 and 9 is equal to 96.65 degrees.
```
```bash
ros2 topic echo /yolov8_pose_results
```
```yaml
header:
  stamp:
    sec: 1713838526
    nanosec: 619847301
  frame_id: pose_estimation
keypoints:
- id: 0
  x: 296.20501708984375
  y: 184.19436645507812
  confidence: 0.9856783747673035
# ... ids 1-4 ...
- id: 5
  x: 327.7157897949219
  y: 216.99574279785156
  confidence: 0.997600257396698
# ... id 6 ...
- id: 7
  x: 351.8081359863281
  y: 243.4370880126953
  confidence: 0.9868736863136292
# ... id 8 ...
- id: 9
  x: 328.81292724609375
  y: 268.5673522949219
  confidence: 0.9723747372627258
# ... ids 10-16 (17 keypoints in all) ...
```

## Pitfalls
- All 17 keypoints come back for each person (`kpt_shape: [17, 3]`), hidden or not, each with a confidence: check `keypoint.confidence` of the three points before trusting the angle (PERC-V35).
- Rounding can push the cosine slightly outside [-1, 1] and `np.arccos` returns NaN; two coincident points divide by zero: `np.arccos(np.clip(cos, -1.0, 1.0))` and skip zero-length vectors.
- Only `[0]`, the first person, is published; loop over `results[0].keypoints.xy` for everyone.
- `len(keypoints) >= 3` does not protect indices 5–9; the COCO model always returns 17 keypoints per person, so it works here only.
