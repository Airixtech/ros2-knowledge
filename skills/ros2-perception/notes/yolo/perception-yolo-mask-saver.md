---
id: perception-yolo-mask-saver
type: reference
owner: equipo-ros2
updated: 2026-10-27
review_by: 2027-04-25
source: manual
confidentiality: internal
title: "Save class-filtered YOLO masks as one colored image and count objects per class"
domain: perception
area: yolo
distro: humble
tested: false
audience: dev
summary: "fruit_mask_saver.py: run yolov8n-seg once, keep apple and banana masks, color them, label counts at centroids, cv2.imwrite combined_masks.png, spin_once loop."
tags: [segmentation masks, masks.data, masks.xy, instance segmentation, YOLO, counting, cv2.imwrite, cv2.moments, cv2.putText, SingleThreadedExecutor, spin_once, combined_masks.png, fruit_mask_saver.py, advanced_perception]
see: ["[[perception-yolo-segmentation]]", "[[perception-custom-msgs]]", "[[core-exec-spin]]"]
requires: [ros2-core]
version_notes:
  - "course: 'YoloSegmentation' is the segmentation node class, not a custom message; the saver builds a second node named `segmentation` (never spun) only to reach its model (PERC-V37)"
  - "course: output_dir was an absolute path of the course machine; now expanded from ~ (PERC-V33)"
  - "ultralytics: masks.data = raw mask tensor at the model input size; masks.xy = segments in original-image pixels — https://github.com/ultralytics/ultralytics/blob/main/ultralytics/engine/results.py (PERC-V38)"
  - "rclpy: `rclpy.executors` is reachable because rclpy.node imports it — https://github.com/ros2/rclpy/blob/humble/rclpy/rclpy/node.py (PERC-V21)"
---
# Save class-filtered YOLO masks and count objects

**TL;DR** Wait until an image and one segmentation message arrived (`spin_once` loop), run the segmentation model once on the image, keep only the `apple` and `banana` masks, paint them (green, yellow) on a black image with a count label at each mask's centroid, save `combined_masks.png`, and exit.

## `fruit_mask_saver.py`
```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from custom_msgs.msg import Yolov8Segmentation
import numpy as np
import cv2
import os
from advanced_perception.yolo_segmentation import YoloSegmentation
import ultralytics

bridge = CvBridge()


class FruitMaskSaver(Node):

    def __init__(self) -> None:
        """Initializes the FruitMaskSaver node."""
        super().__init__('fruit_mask_saver')
        self.subscription = self.create_subscription(Yolov8Segmentation, '/Yolov8_segmentation', self.handle_segmentation, 10)
        self.img_sub = self.create_subscription(Image, '/deepmind_robot1/deepmind_robot1_camera/image_raw', self.image_callback, 10)
        self.output_dir = os.path.expanduser('~/ros2_ws/src/advanced_perception/data/segmentation_results')  # PERC-V33
        os.makedirs(self.output_dir, exist_ok=True)
        self.img = None
        self.yolov8_segmentation = []
        self.image_ready = False
        self.segmentation_ready = False
        # Create an instance of YoloSegmentation
        self.yolo_segmentation_instance = YoloSegmentation()

    def handle_segmentation(self, msg: Yolov8Segmentation) -> None:
        """ Handles incoming segmentation data """
        self.yolov8_segmentation = msg.yolov8_segmentation
        self.segmentation_ready = True

    def image_callback(self, data: Image) -> None:
        """ Callback function for image data received from the camera """
        self.img = bridge.imgmsg_to_cv2(data, "bgr8")
        self.image_ready = True

    def save_masks_as_image(self, results: ultralytics.engine.results.Results, output_dir: str) -> None:
        """ Saves the masks as images in the specified directory """
        if not hasattr(results, 'masks') or results.masks is None:
            self.get_logger().error("No 'masks' attribute found in the results or masks are empty. Please check the model configuration.")
            return

        masks = results.masks.data.cpu().numpy()
        combined_mask = self.combine_masks(masks, results)
        self.save_combined_mask(combined_mask, output_dir)

    def combine_masks(self, masks: np.ndarray, results: ultralytics.engine.results.Results) -> np.ndarray:
        """ Combines individual masks into a single mask image """
        combined_mask = np.zeros((self.img.shape[0], self.img.shape[1], 3), dtype=np.uint8)
        apple_count = 0
        banana_count = 0

        for i, mask in enumerate(masks):
            class_id = int(results.boxes[i].cls)
            class_name = self.yolo_segmentation_instance.model.names[class_id]

            if class_name not in ["apple", "banana"]:
                continue

            mask_data = mask
            if mask_data.size != 0 and mask_data.ndim >= 2:
                if mask_data.shape[0] == 1:
                    mask_data = np.squeeze(mask_data, axis=0)

                mask_data = (mask_data * 255).astype(np.uint8)
                mask_data = cv2.resize(mask_data, (self.img.shape[1], self.img.shape[0]))

                color = [0, 255, 0] if class_name == "apple" else [0, 255, 255]
                combined_mask[mask_data > 0] = color

                M = cv2.moments(mask_data)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    count = apple_count + 1 if class_name == 'apple' else banana_count + 1
                    cv2.putText(combined_mask, f"{class_name[0].upper()}{count}", (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                if class_name == "apple":
                    apple_count += 1
                elif class_name == "banana":
                    banana_count += 1

        self.get_logger().info(f"Total apples: {apple_count}, Total bananas: {banana_count}")
        return combined_mask

    def save_combined_mask(self, combined_mask: np.ndarray, output_dir: str) -> None:
        """ Saves the combined mask image to the specified directory """
        mask_path = os.path.join(output_dir, "combined_masks.png")
        cv2.imwrite(mask_path, combined_mask)
        self.get_logger().info(f"Successfully created and saved the mask image inside {self.output_dir} folder")


def main(args=None) -> None:
    rclpy.init(args=args)
    fruit_mask_saver = FruitMaskSaver()
    executor = rclpy.executors.SingleThreadedExecutor()
    executor.add_node(fruit_mask_saver)

    try:
        while rclpy.ok():
            executor.spin_once()
            if fruit_mask_saver.image_ready and fruit_mask_saver.segmentation_ready:
                if fruit_mask_saver.img is not None and fruit_mask_saver.yolov8_segmentation:
                    results = fruit_mask_saver.yolo_segmentation_instance.model(fruit_mask_saver.img)
                    if results:
                        fruit_mask_saver.save_masks_as_image(results[0], fruit_mask_saver.output_dir)
                        break  # Process only once
            else:
                if fruit_mask_saver.segmentation_ready is False:
                    fruit_mask_saver.get_logger().error("Waiting to subscribe to the Segmentation results ..")
                else:
                    fruit_mask_saver.get_logger().error("Waiting to subscribe to the Image data ..")
    finally:
        fruit_mask_saver.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```
- It runs on top of the segmentation node: subscribes to `/Yolov8_segmentation` and the camera, merges the fruit masks and stores the annotated image.
- `output_dir` is where the image goes; `os.makedirs(..., exist_ok=True)` creates every missing directory and does not fail if it exists. The course hard-coded an absolute path of its machine (PERC-V33).
- `YoloSegmentation()` is **the segmentation node class** of `yolo_segmentation.py` (the course calls it a custom message): the saver creates a second node named `segmentation`, never spun, only for its `model`, which loads the weights a second time (PERC-V37). `YOLO(<path>)` in the saver is enough.
- `handle_segmentation()` stores the received list and sets `segmentation_ready`; `image_callback()` converts the image and sets `image_ready`: processing starts only when both exist.
- `save_masks_as_image()`: checks that the results have masks, moves them to CPU NumPy (`results.masks.data`), combines and saves them.
- `combine_masks()`: an empty 3-channel image of the camera's size and two counters; for each mask, the class from `results.boxes[i].cls`; anything but `apple` and `banana` is skipped; the mask is squeezed if its first dimension is 1, scaled to 8 bits and resized to the image; apples are painted green, bananas yellow (BGR); the mask's moments give its centroid, where a label like `A1`, `B2` is written; the counters are updated and the totals logged.
- `save_combined_mask()`: `cv2.imwrite()` to `<output_dir>/combined_masks.png`, then a log line.
- `main()`: a `SingleThreadedExecutor` with `spin_once()` per loop (one cycle of incoming messages), the model on the last image once both data are there, then `break`; `finally` destroys the node and shuts rclpy down even after an exception.

## Test
With [[perception-yolo-segmentation]] running:
```bash
cd ~/ros2_ws/
colcon build;source install/setup.bash
ros2 run advanced_perception fruit_mask_saver
```
The image appears in `advanced_perception/data/segmentation_results`: apples green, bananas yellow, the sports ball on the left excluded.

## Pitfalls
- `masks.data` is the raw mask tensor at the model's input size, which the code resizes to the image; `results.masks.xy` already gives each segment in original-image pixels (draw it with `cv2.fillPoly`) (PERC-V38).
- The "Waiting…" messages are logged at **error** level on every loop: use `info` or log once.
- The segmentation topic is only a trigger here: the saver runs the model again on its own copy of the image.
- `rclpy.executors` works without `import rclpy.executors` only because `rclpy.node` imports it; import it explicitly (PERC-V21, spin variants: [[core-exec-spin]]).
