---
id: perception-face-eye-detection
type: reference
owner: equipo-ros2
updated: 2026-10-27
review_by: 2027-04-25
source: manual
confidentiality: internal
title: "Face and eye detection nodes with Haar cascades: grayscale, ROI search for eyes, annotated image topics"
domain: perception
area: hri
distro: humble
tested: false
audience: dev
summary: "eye_detection.py and face_detection.py: Haar face boxes on /detected_faces/faces, eyes searched inside each face ROI on /detected_faces/eyes."
tags: [face detection, eye detection, Haar cascade, CascadeClassifier, detectMultiScale, ROI, cv2.rectangle, cv2_to_imgmsg, detected_faces, get_package_share_directory, hri, eye_detection.py, face_detection.py]
see: ["[[perception-haar-cascades]]", "[[perception-face-recognition]]", "[[perception-python-deps]]", "[[perception-rviz-sensors]]"]
requires: [ros2-core]
version_notes:
  - "course: on a missing cascade file __init__ logs and returns, the node keeps running without self.face_cascade and every image raises AttributeError (PERC-V24)"
  - "course: the exported code lost its indentation; the publish calls are rebuilt after the drawing loops (one annotated image per camera frame)"
---
# Face and eye detection with Haar cascades

**TL;DR** Convert to gray, `face_cascade.detectMultiScale(gray, 1.3, 5)`, draw blue boxes and publish the image; for eyes, run the eye cascade only inside each face (region of interest), which is faster and avoids false eyes elsewhere. Cascade background: [[perception-haar-cascades]].

## Package `hri` (human-robot interaction)
Human-robot interaction (HRI) lets robots and people work together safely and intuitively in homes, workplaces and industry; perception gives the robot people's presence and actions. This unit: face detection, face recognition ([[perception-face-recognition]]) and human tracking ([[perception-hog-human-tracking]]).
```bash
cd ~/ros2_ws/src/
ros2 pkg create --build-type ament_python hri
cd ~/ros2_ws/
colcon build
source install/setup.bash
cd src/hri/hri
touch face_detection.py face_recognition.py human_tracking.py
chmod +x *.py
cd ~/ros2_ws/
```
Later: `touch eye_detection.py` in the same folder. The cascades `haarcascade_frontalface_default.xml` and `haarcascade_eye.xml` go to `~/ros2_ws/src/hri/data/`, installed by `setup.py` `data_files` (the course's `setup.py` for `hri`: [[perception-python-deps]]; update it before running).

## `eye_detection.py` (faces + eyes)
```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import os
from ament_index_python.packages import get_package_share_directory


class EyeDetectorNode(Node):

    def __init__(self) -> None:
        super().__init__('eye_detector_node')
        self.subscription = self.create_subscription(Image, '/deepmind_robot1/deepmind_robot1_camera/image_raw', self.image_callback, 10)
        self.face_publisher = self.create_publisher(Image, '/detected_faces/faces', 10)
        self.eye_publisher = self.create_publisher(Image, '/detected_faces/eyes', 10)
        self.bridge = CvBridge()
        data_folder = os.path.join(get_package_share_directory('hri'), 'data')
        face_cascade_path = os.path.join(data_folder, 'haarcascade_frontalface_default.xml')
        eye_cascade_path = os.path.join(data_folder, 'haarcascade_eye.xml')
        if not os.path.isfile(face_cascade_path) or not os.path.isfile(eye_cascade_path):
            self.get_logger().error("Cascade xml file(s) not found")
            return
        self.face_cascade = cv2.CascadeClassifier(face_cascade_path)
        self.eye_cascade = cv2.CascadeClassifier(eye_cascade_path)

    def image_callback(self, msg: Image) -> None:
        """ Detects faces and eyes drawing blue rectangles around faces and green rectangles around eyes"""
        cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        gray_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray_image, scaleFactor=1.3, minNeighbors=5)
        for (x, y, w, h) in faces:
            # draw blue box surrounding detected face
            cv2.rectangle(cv_image, (x, y), (x + w, y + h), (255, 0, 0), 2)
        self.face_publisher.publish(self.bridge.cv2_to_imgmsg(cv_image, 'bgr8'))

        for (x, y, w, h) in faces:
            roi_gray = gray_image[y:y+h, x:x+w]
            roi_color = cv_image[y:y+h, x:x+w]
            eyes = self.eye_cascade.detectMultiScale(roi_gray)
            if len(eyes) > 0:
                self.get_logger().info("Eyes detected")
            for (ex, ey, ew, eh) in eyes:
                # draw green boxes surrounding detected eyes
                cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)
        self.eye_publisher.publish(self.bridge.cv2_to_imgmsg(cv_image, 'bgr8'))


def main(args=None) -> None:
    rclpy.init(args=args)
    face_detector_node = EyeDetectorNode()
    rclpy.spin(face_detector_node)
    face_detector_node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```
- The subscription takes the camera image; two publishers send annotated images: faces on `/detected_faces/faces`, eyes on `/detected_faces/eyes`.
- `cv2.CascadeClassifier(path)` loads each cascade from the package's share folder.
- In the callback, cv_bridge converts the message, the image goes to gray, and the face cascade returns a list of rectangles (`x`, `y` top-left corner, `w`, `h` size); each face gets a blue rectangle, 2 px thick.
- For each face, the matching regions of interest (ROI) of the gray and color images are cut out; the eye cascade runs on the gray ROI and returns rectangles **relative to the ROI**, each drawn from its top-left corner (`ex`, `ey`) to its bottom-right corner (`ex + ew`, `ey + eh`). Drawing on `roi_color` (a NumPy view of `cv_image`) puts the green boxes, `(0, 255, 0)` in BGR, into the full image.

## `face_detection.py` (faces only): differences
Class `FaceDetectorNode`, node name `'face_detector_node'`; only `self.face_publisher` (`/detected_faces/faces`) and only the face cascade (`if not os.path.isfile(face_cascade_path):` → error `"Cascade xml file not found"`); `main()` creates `face_detector_node = FaceDetectorNode()`. The callback:
```python
    def image_callback(self, msg: Image) -> None:
        """ Detects faces, drawing blue rectangles around them"""
        cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        gray_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray_image, scaleFactor=1.3, minNeighbors=5)
        if len(faces) > 0:
            self.get_logger().info("Face detected")
        for (x, y, w, h) in faces:
            # draw blue box surrounding detected face
            cv2.rectangle(cv_image, (x, y), (x + w, y + h), (255, 0, 0), 2)
        self.face_publisher.publish(self.bridge.cv2_to_imgmsg(cv_image, 'bgr8'))
```
`cv2_to_imgmsg(cv_image, 'bgr8')` converts the annotated image back to a ROS message before publishing.

## Launch and test
Head straight (`move_head.py 0.0 0.0 1`, [[perception-learn-start-here]]), RViz with an `Image` display ([[perception-rviz-sensors]]), then:
```bash
cd ~/ros2_ws/
colcon build;source install/setup.bash
ros2 run hri face_detection
```
Drive around with teleop and show `/detected_faces/faces`: blue boxes around the faces. Close the terminals, then the same with `ros2 run hri eye_detection` and `/detected_faces/eyes`: green boxes around the eyes.

## Pitfalls
- `AttributeError: 'FaceDetectorNode' object has no attribute 'face_cascade'` on every frame → the XML file is not installed (missing `data_files` or no rebuild); the early `return` in `__init__` leaves the node running without it. Raise an exception there instead (PERC-V24).
- Eye boxes in the wrong place → the eye rectangles are relative to the face ROI; draw on the ROI view (as here) or add `x`, `y`.
