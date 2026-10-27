---
id: perception-yolo-object-detection
type: reference
owner: equipo-ros2
updated: 2026-10-27
review_by: 2027-04-25
source: manual
confidentiality: internal
title: "YOLOv8 object detection node: results boxes (xyxy, cls, names), inference messages and annotated image"
domain: perception
area: yolo
distro: humble
tested: false
audience: dev
summary: "rclpy node running Ultralytics YOLO on camera images: boxes.xyxy, cls, model.names, InferenceResult/Yolov8Inference messages, results[0].plot() image."
tags: [YOLO, YOLOv8, ultralytics, object detection, results, boxes, xyxy, cls, model.names, plot, InferenceResult, Yolov8Inference, Yolov8_Inference, inference_result, yolo_object_detection.py, advanced_perception]
see: ["[[perception-yolo-concepts]]", "[[perception-custom-msgs]]", "[[perception-yolo-person-follower]]", "[[perception-python-deps]]"]
requires: [ros2-core]
version_notes:
  - "course: the comment said '(top, left, bottom, right)' for xyxy; it is [x1, y1, x2, y2] = (left, top, right, bottom); the code's assignments were right — https://github.com/ultralytics/ultralytics/blob/main/ultralytics/engine/results.py (PERC-V31)"
  - "course: the model was loaded from an absolute path of the course machine; now from the package share folder (PERC-V33)"
  - "ultralytics: NumPy input is HWC BGR uint8; results.plot() returns a BGR NumPy array — https://docs.ultralytics.com/modes/predict/ (PERC-V34)"
  - "ultralytics: `verbose: True` is a default of the shared configuration that predict() keyword arguments override — https://github.com/ultralytics/ultralytics/blob/main/ultralytics/cfg/default.yaml"
  - "humble+: cv2_to_imgmsg(annotated_frame) without an encoding publishes '8UC3' (passthrough) — https://github.com/ros-perception/vision_opencv/blob/humble/cv_bridge/python/cv_bridge/core.py (PERC-V32)"
---
# YOLOv8 object detection node

**TL;DR** Load `YOLO(<weights>)` once, call `self.model(img)` on each BGR frame, and read `r.boxes`: `box.xyxy[0]` (left, top, right, bottom in pixels), `box.cls` (class id → `self.model.names[int(c)]`). Publish the results as a custom message and `results[0].plot()` as an annotated image.

## `yolo_object_detection.py`
```python
#!/usr/bin/env python3

import os
from ament_index_python.packages import get_package_share_directory
from ultralytics import YOLO
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from custom_msgs.msg import InferenceResult, Yolov8Inference

bridge = CvBridge()


class YoloObjectDetection(Node):

    def __init__(self) -> None:
        super().__init__('object_detection')
        # Load a pre-trained YOLOv8 object detection model (installed with the package, PERC-V33)
        self.model = YOLO(os.path.join(get_package_share_directory('advanced_perception'), 'data', 'yolov8n.pt'))
        self.yolov8_inference = Yolov8Inference()
        self.subscription = self.create_subscription(Image, '/deepmind_robot1/deepmind_robot1_camera/image_raw', self.camera_callback, 10)
        self.yolov8_pub = self.create_publisher(Yolov8Inference, "/Yolov8_Inference", 1)
        self.img_pub = self.create_publisher(Image, "/inference_result", 1)

    def camera_callback(self, msg: Image) -> None:
        """ Performs object detection using the loaded YOLO model
            and processes the detection results. The image with
            annotated detections is also published for visualization """
        img = bridge.imgmsg_to_cv2(msg, "bgr8")
        results = self.model(img)

        self.yolov8_inference.header.frame_id = "inference"
        self.yolov8_inference.header.stamp = self.get_clock().now().to_msg()

        for r in results:
            boxes = r.boxes
            for box in boxes:
                self.inf_result = InferenceResult()
                # get box coordinates in (left, top, right, bottom) format (PERC-V31)
                b = box.xyxy[0].to('cpu').detach().numpy().copy()
                c = box.cls
                self.inf_result.class_name = self.model.names[int(c)]
                self.inf_result.left = int(b[0])
                self.inf_result.top = int(b[1])
                self.inf_result.right = int(b[2])
                self.inf_result.bottom = int(b[3])
                self.inf_result.box_width = (self.inf_result.right - self.inf_result.left)
                self.inf_result.box_height = (self.inf_result.bottom - self.inf_result.top)
                self.inf_result.x = self.inf_result.left + (self.inf_result.box_width/2.0)
                self.inf_result.y = self.inf_result.top + (self.inf_result.box_height/2.0)
                self.yolov8_inference.yolov8_inference.append(self.inf_result)

        annotated_frame = results[0].plot()
        img_msg = bridge.cv2_to_imgmsg(annotated_frame)
        self.img_pub.publish(img_msg)

        self.yolov8_pub.publish(self.yolov8_inference)
        self.yolov8_inference.yolov8_inference.clear()


def main(args=None) -> None:
    rclpy.init(args=args)
    object_detection = YoloObjectDetection()
    rclpy.spin(object_detection)
    object_detection.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```
- `from ultralytics import YOLO` loads and runs the model; `InferenceResult` holds one detection (`class_name`, `top`, `left`, `bottom`, `right`, `box_width`, `box_height`, center `x`, `y`) and `Yolov8Inference` a `header` plus the list `yolov8_inference` ([[perception-custom-msgs]]).
- `YOLO(...)` loads the trained weights of `yolov8n.pt`. The course passed an absolute path of its own machine; the share folder works on any install once `data/` is in `data_files` (PERC-V33, [[perception-python-deps]]).
- The subscription feeds the camera image; `/Yolov8_Inference` carries the detections, `/inference_result` the annotated image for RViz.
- `bridge.imgmsg_to_cv2(msg, "bgr8")`: YOLO takes the BGR NumPy image directly. `results` holds the detected objects, boxes, confidence scores and class ids.
- The header gets the frame id `"inference"` and the current time, so subscribers can interpret timing and context.
- For each box: `box.xyxy` = (xmin, ymin, xmax, ymax), top-left and bottom-right corners; `.to('cpu').detach().numpy().copy()` moves the tensor to CPU memory, detaches it from the computation graph (gradients), converts it to NumPy and copies it; `box.cls` is the class id, turned into a name with `self.model.names`. Width, height and center follow from the corners. The course's comment said "(top, left, bottom, right)" (PERC-V31).
- `results[0].plot()` draws the boxes on the frame (BGR); it is converted and published on `/inference_result`. Then the detections are published and the list is cleared for the next frame.

## Launch and test
Tilt the head down (`move_head.py 0.0 0.5 1`), restart the simulation, spawn a banana and an apple on a bench (`ros2 launch perception_ros2 spawn_fruits.launch.py`, course simulation, [[perception-learn-start-here]]), drive close with teleop, then:
```bash
cd ~/ros2_ws/
colcon build;source install/setup.bash
ros2 run advanced_perception yolo_object_detection
```
Show `/inference_result` in RViz's `Image` display: both fruits are detected. From far away the apple is first labeled `sports ball` and the banana sometimes `frisbee`; closer, the labels become right.

## Pitfalls
- `cv2_to_imgmsg(annotated_frame)` without an encoding publishes `8UC3`: RViz shows it, a cv_bridge subscriber asking for `bgr8` raises; pass `'bgr8'` (PERC-V32).
- `self.model(img)` prints a log line per frame; `self.model(img, verbose=False)` silences it.
- Inference in the image callback blocks the executor while it runs, and the depth-10 subscription queues up to 10 stale frames; subscribe with depth 1 (KEEP_LAST 1 keeps only the newest), or store the last image and run inference in a timer ([[core-recipe-cv-bridge]]).
- `box.conf` (confidence) is ignored here: filter low-confidence boxes before acting on them.
