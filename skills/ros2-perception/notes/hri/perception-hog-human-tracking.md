---
id: perception-hog-human-tracking
type: reference
owner: equipo-ros2
updated: 2026-10-27
review_by: 2027-04-25
source: manual
confidentiality: internal
title: "People detection with HOG + linear SVM, non-maximum suppression and turning toward the person"
domain: perception
area: hri
distro: humble
tested: false
audience: dev
summary: "cv2.HOGDescriptor with the default people SVM, detectMultiScale winStride padding scale, imutils non_max_suppression, angular velocity toward the person."
tags: [HOG, histogram of oriented gradients, SVM, cv2.HOGDescriptor, getDefaultPeopleDetector, detectMultiScale, winStride, padding, scale, non-maximum suppression, imutils, human tracking, detected_human, human_tracking.py, hri]
see: ["[[perception-yolo-person-follower]]", "[[perception-haar-cascades]]", "[[perception-python-deps]]"]
requires: [ros2-core]
version_notes:
  - "opencv 4.x: cv.HOGDescriptor_getDefaultPeopleDetector() is used by OpenCV's own Python test — https://github.com/opencv/opencv/blob/4.x/modules/objdetect/misc/python/test/test_peopledetect.py (PERC-V28)"
  - "imutils (master): non_max_suppression(boxes, probs=None, overlapThresh=0.3), returns [] for no boxes; the course passes 0.65 — https://github.com/PyImageSearch/imutils/blob/master/imutils/object_detection.py (PERC-V28)"
  - "course: `image_callback(self, msg: None)` type hint (msg: Image) (PERC-V05); 'non-maximam' typo"
---
# People detection with HOG + SVM

**TL;DR** `hog = cv2.HOGDescriptor(); hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())`, then `hog.detectMultiScale(img, winStride=(8, 8), padding=(8, 8), scale=1.05)` gives person boxes; merge overlaps with non-maximum suppression and turn the robot so the first box stays centered (`angular.z = -0.001 * offset_x`).

## Histograms and HOG
Histogram-based methods analyze and change the pixel intensities of an image through its histogram: the frequency distribution of the pixel values, i.e. how often each intensity occurs. A histogram is a bar plot with the **intensity values** on the x axis and their **occurrences** (counts or probabilities) on the y axis. Example: an image of 9 pixels with 5 black, 2 grey and 2 white pixels has three bars of heights 5, 2 and 2.

**HOG (Histogram of Oriented Gradients)** is a **feature descriptor** for object detection: it counts the **gradient orientations** in local parts of an image (a detection window or region of interest) and builds histograms from them, which capture the shape and appearance of local structures. The course uses it to detect pedestrians with a **sliding window**: a fixed-size rectangle that "slides" across the image.

**SVM (Support Vector Machine)**: a supervised machine-learning algorithm for classification. The HOG features of each window go to an SVM trained on positive (people) and negative (no people) samples, which classifies them (in a face detector, the HOG features of a face would be classified as "face" or "not face"); the HOG + SVM pair is popular because it recognizes objects in varied conditions and orientations. `cv2.HOGDescriptor_getDefaultPeopleDetector()` returns the coefficients of OpenCV's pre-trained people classifier, and `setSVMDetector()` makes the descriptor use it. OpenCV reference: [HOGDescriptor](https://docs.opencv.org/4.x/d5/d33/structcv_1_1HOGDescriptor.html).

**Non-maximum suppression (NMS)**: a post-processing step that removes overlapping boxes and keeps the most relevant one per object.

## `human_tracking.py`
```python
import rclpy
from rclpy.node import Node
from cv_bridge import CvBridge
from sensor_msgs.msg import Image
import cv2
import numpy as np
from imutils.object_detection import non_max_suppression
from geometry_msgs.msg import Twist


class HumanTrackerNode(Node):

    def __init__(self) -> None:
        super().__init__('human_tracker')
        self.subscription = self.create_subscription(Image, '/deepmind_robot1/deepmind_robot1_camera/image_raw', self.image_callback, 10)
        self.human_publisher = self.create_publisher(Image, '/detected_human', 10)
        self.cmd_vel_publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.bridge = CvBridge()
        # Initialize the HOG descriptor/person detector
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

    def image_callback(self, msg: Image) -> None:
        """ Process image received from camera to detect humans and track them by adjusting angular velocity of robot"""
        # Convert the ROS2 image message to an OpenCV image
        cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        # Detect humans
        (rects, _) = self.hog.detectMultiScale(cv_image, winStride=(8, 8), padding=(8, 8), scale=1.05)

        # Convert rects to the format expected by imutils' non_max_suppression
        rects = np.array([[x, y, x + w, y + h] for (x, y, w, h) in rects])

        # Apply non-maxima suppression from imutils
        pick = non_max_suppression(rects, probs=None, overlapThresh=0.65)
        self.get_logger().info(f'Detected {len(pick)} humans')

        # Draw the final bounding boxes
        for (xA, yA, xB, yB) in pick:
            cv2.rectangle(cv_image, (xA, yA), (xB, yB), (0, 255, 0), 2)

        # Convert the OpenCV image back to a ROS2 message and publish it
        image_msg = self.bridge.cv2_to_imgmsg(cv_image, encoding="bgr8")
        self.human_publisher.publish(image_msg)

        if len(pick) > 0:
            (xA, yA, xB, yB) = pick[0]
            # Calculate the position of the human's based on bounding box position
            human_center_x = (xA + xB) / 2
            # Calculate the center of the image
            image_center_x = cv_image.shape[1] / 2
            # Calculate the offset of the human from the center of the image
            offset_x = human_center_x - image_center_x
            # Determine the angular velocity needed to align the robot with detected human
            gain = 0.001
            angular_velocity = -offset_x * gain
            self.get_logger().info(f'Computed angular velocity: {angular_velocity}')

            # Create a Twist message and populate it
            twist_msg = Twist()
            twist_msg.angular.z = angular_velocity
            # Publish the Twist message to adjust the robot's angular velocity
            self.cmd_vel_publisher.publish(twist_msg)


def main(args=None) -> None:
    rclpy.init(args=args)
    human_tracker_node = HumanTrackerNode()
    rclpy.spin(human_tracker_node)
    # Explicitly destroy the node
    human_tracker_node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```
(The course's type hint was `msg: None`, PERC-V05. Its explanation words two comments differently: "Calculate the position of the human's center", "re-center the human".)
- Publishers: the image with the detected people on `/detected_human`, and motion commands on `/cmd_vel`.
- `detectMultiScale` parameters: `winStride` = step of the sliding window in x and y; `padding` = extra pixels added around each window (like a slightly wider lens, so nothing just outside the window is missed); `scale` = how much the image shrinks at each pass, so people of different sizes are found (1.05 = 5 % smaller each time). It returns rectangles `(x, y, w, h)`.
- The boxes become `[x1, y1, x2, y2]` for imutils' `non_max_suppression`; `overlapThresh` controls how much overlap is allowed (imutils' default is 0.3, the course uses 0.65), so each person is counted once (`pick`). Final boxes are drawn in green.
- With at least one person, the first box's horizontal center is compared with the image center; the offset times `gain` gives the angular speed that keeps the robot facing the person.

## Launch and test
Place the robot so that it does **not** face the person squarely, show `/detected_human` in RViz ([[perception-rviz-sensors]]), then:
```bash
cd ~/ros2_ws/
colcon build;source install/setup.bash
ros2 run hri human_tracking
```
A green box surrounds the person, and the robot turns to keep facing them.

## Pitfalls
- The robot keeps turning after the person leaves the image: the node publishes `angular.z` only while someone is detected, never a stop; publish a zero `Twist` when `pick` is empty (PERC-V28).
- `pick[0]` is just the first box, not the closest person: choose by box size if several people are visible.
- Detection slow on full 640 × 480 frames: a smaller image means fewer windows to classify; resize first, or use a YOLO model ([[perception-yolo-person-follower]]).
