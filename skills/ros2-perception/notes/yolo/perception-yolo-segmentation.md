---
id: perception-yolo-segmentation
type: reference
owner: equipo-ros2
updated: 2026-10-27
review_by: 2027-04-25
source: manual
confidentiality: internal
title: "YOLOv8 instance segmentation node: semantic vs instance vs panoptic, per-object results and annotated image"
domain: perception
area: yolo
distro: humble
tested: false
audience: dev
summary: "Segmentation types; yolov8n-seg node publishing SegmentationResult/Yolov8Segmentation (class, center, size) and the annotated image on segmentation_result."
tags: [segmentation, instance segmentation, semantic segmentation, panoptic segmentation, YOLO, yolov8n-seg, masks, SegmentationResult, Yolov8Segmentation, Yolov8_segmentation, segmentation_result, yolo_segmentation.py, advanced_perception]
see: ["[[perception-yolo-mask-saver]]", "[[perception-yolo-object-detection]]", "[[perception-custom-msgs]]", "[[perception-yolo-concepts]]"]
requires: [ros2-core]
version_notes:
  - "course: `clear()` of the result list was commented out, so every frame appended to the same message (unbounded growth); restored (PERC-V36)"
  - "course: the model was loaded from an absolute path of the course machine (now the package share folder), and its comment said yolov8n-pose for the -seg model (PERC-V33, PERC-V05)"
  - "humble+: cv2_to_imgmsg(annotated_frame) without an encoding publishes '8UC3' (PERC-V32)"
---
# YOLOv8 instance segmentation node

**TL;DR** `yolov8n-seg.pt` returns boxes **and** a mask per object. This node publishes each object's class, box center and size as `SegmentationResult` items of one `Yolov8Segmentation` message per frame, plus the annotated image; the masks themselves are used by [[perception-yolo-mask-saver]].

## Segmentation
Segmentation partitions an image into segments (sets of pixels, also called superpixels) so that it is simpler to analyze; it locates objects and boundaries (lines, curves).
- **Semantic segmentation**: every pixel gets a class (car, building, person, road…), with no distinction between instances of one class; understanding at pixel level.
- **Instance segmentation**: every pixel gets a class **and** the instances are told apart (each car separately).
- **Panoptic segmentation**: both: every pixel is labeled, instances are separated for discrete objects, and areas like sky or road are one entity.
Uses: medical imaging (regions of interest in scans), autonomous vehicles (lanes, obstacles, objects), robotics (telling objects apart to manipulate them), agricultural automation (crop growth, weed areas to treat). The course uses **instance segmentation**: a set of masks or contours, one per object, with class labels and confidence scores, for when you need where each object is and its exact shape.

Course goal: a precise **inventory count** of fruits: segment each fruit from its surroundings and from other objects, count them, and save an image with only the fruit masks (fruits in artworks). Two nodes: this segmentation node and the mask saver.
```bash
cd ~/ros2_ws/src/advanced_perception/advanced_perception
touch fruit_mask_saver.py
chmod +x *.py
cd ~/ros2_ws/
mkdir ~/ros2_ws/src/advanced_perception/data/segmentation_results
```
(`yolo_segmentation.py` was created with the other YOLO scripts, [[perception-yolo-concepts]].)

## `yolo_segmentation.py`
```python
#!/usr/bin/env python3

import os
from ament_index_python.packages import get_package_share_directory
from ultralytics import YOLO
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from custom_msgs.msg import SegmentationResult, Yolov8Segmentation

bridge = CvBridge()


class YoloSegmentation(Node):
    """ This node publishes segmentation results of YOLOv8 on ROS2 """

    def __init__(self) -> None:
        super().__init__('segmentation')
        # Load pre-trained yolov8n-seg model for instance segmentation (package share folder, PERC-V33)
        self.model = YOLO(os.path.join(get_package_share_directory('advanced_perception'), 'data', 'yolov8n-seg.pt'))
        self.yolov8_segmentation = Yolov8Segmentation()
        self.subscription = self.create_subscription(Image, '/deepmind_robot1/deepmind_robot1_camera/image_raw', self.camera_callback, 10)
        self.yolov8_pub = self.create_publisher(Yolov8Segmentation, "/Yolov8_segmentation", 1)
        self.img_pub = self.create_publisher(Image, "/segmentation_result", 1)

    def camera_callback(self, data: Image) -> None:
        img = bridge.imgmsg_to_cv2(data, "bgr8")
        results = self.model(img)

        self.yolov8_segmentation.header.stamp = self.get_clock().now().to_msg()
        self.yolov8_segmentation.header.frame_id = "segmentation"

        for r in results:
            boxes = r.boxes
            for box in boxes:
                self.segmentation_result = SegmentationResult()
                b = box.xyxy[0].to('cpu').detach().numpy().copy()
                c = box.cls
                self.segmentation_result.class_id = int(c)
                self.segmentation_result.class_name = self.model.names[int(c)]
                self.segmentation_result.x = (b[0] + b[2]) / 2
                self.segmentation_result.y = (b[1] + b[3]) / 2
                self.segmentation_result.width = float(b[2] - b[0])
                self.segmentation_result.height = float(b[3] - b[1])
                self.yolov8_segmentation.yolov8_segmentation.append(self.segmentation_result)

        annotated_frame = results[0].plot()
        img_msg = bridge.cv2_to_imgmsg(annotated_frame)
        self.img_pub.publish(img_msg)

        self.yolov8_pub.publish(self.yolov8_segmentation)
        self.yolov8_segmentation.yolov8_segmentation.clear()  # PERC-V36: commented out in the course


def main(args=None) -> None:
    rclpy.init(args=args)
    segmentation = YoloSegmentation()
    rclpy.spin(segmentation)
    segmentation.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```
- Messages ([[perception-custom-msgs]]): `SegmentationResult` = class id (`class_id`), `class_name`, center `x`, `y`, `width`, `height`; `Yolov8Segmentation` = `header` + list `yolov8_segmentation`.
- `yolov8n-seg.pt` predicts boxes and segmentation masks per object, a more precise shape than contours alone. The loop over `r.boxes` is the one of the detection node ([[perception-yolo-object-detection]]): xyxy corners, class id and name, plus center and size.
- `/segmentation_result` carries the annotated image (masks drawn by `plot()`) for RViz, `/Yolov8_segmentation` the per-object data.
- The course left `clear()` commented out: the list kept every object of every frame since start (PERC-V36).

## Launch
Restart the simulation, spawn several models on a bench (`ros2 launch perception_ros2 spawn_models.launch.py`, course simulation), tilt the head (`move_head.py 0.0 0.7 1`), RViz with `/segmentation_result`, drive to the bench, then:
```bash
cd ~/ros2_ws/
colcon build;source install/setup.bash
ros2 run advanced_perception yolo_segmentation
```
It segments and labels three kinds of objects: apples, bananas and a sports ball. Saving the fruit masks: [[perception-yolo-mask-saver]].

## Pitfalls
- A message that grows every frame (memory, bandwidth, stale objects) → the list of a reused message object was never cleared (PERC-V36).
- The published data has no masks: subscribers that need the shape must run the model themselves or receive the masks some other way ([[perception-yolo-mask-saver]]).
- Publish the annotated image with `'bgr8'` (PERC-V32).
