---
id: perception-blob-detect
type: reference
owner: equipo-ros2
updated: 2026-10-27
review_by: 2027-04-25
source: manual
confidentiality: internal
title: "Blob detection with OpenCV: HSV mask, contours, largest contour, moments centroid, Point relative to center"
domain: perception
area: image
distro: humble
tested: false
audience: dev
summary: "Detect a colored blob: cv2.inRange mask, cv2.findContours, largest contourArea, cv2.moments centroid, publish geometry_msgs/Point relative to image center."
tags: [blob tracking, blob detection, cv2.findContours, RETR_EXTERNAL, CHAIN_APPROX_SIMPLE, cv2.contourArea, cv2.moments, centroid, cv2.boundingRect, geometry_msgs/Point, point_blob, blob_point_pub.py, blob_tracking]
see: ["[[perception-blob-follow]]", "[[perception-hsv-color-ranges]]", "[[perception-opencv-cv-bridge]]"]
requires: [ros2-core]
version_notes:
  - "opencv 4.x: `contours, hierarchy = cv.findContours(...)`; 3.2–3.4 returned three values (`im2, contours, hierarchy`) — https://github.com/opencv/opencv/blob/4.x/doc/py_tutorials/py_imgproc/py_contours/py_contours_begin/py_contours_begin.markdown , https://github.com/opencv/opencv/blob/3.4/doc/py_tutorials/py_imgproc/py_contours/py_contours_begin/py_contours_begin.markdown"
---
# Blob detection: HSV mask, contours, centroid

**TL;DR** Mask the color in HSV, find the outer contours, keep the largest one, and take its centroid from the image moments (`m10/m00`, `m01/m00`). Publish it normalized to the image center (−1…1) so a follower does not depend on the resolution.

## Blob tracking
Blob tracking detects and follows regions of interest (**blobs**) through a sequence of images or a video stream; a blob is a group of connected pixels with similar properties (color, intensity, texture). It is used in surveillance, object tracking, human-computer interaction and robotics, for example to track markers or landmarks for navigation, object manipulation and interaction.

Course goal: detect the **orange** blob next to the exit door and drive the robot there, with two scripts: `blob_point_pub.py` (detects the blob and publishes its position) and `blob_tracker.py` (guides the robot, [[perception-blob-follow]]).
```bash
cd ~/ros2_ws/src/
ros2 pkg create --build-type ament_python blob_tracking
cd ~/ros2_ws/
colcon build
source install/setup.bash
cd src/blob_tracking/blob_tracking
touch blob_point_pub.py blob_tracker.py
chmod +x *.py
cd ~/ros2_ws/
```
The first step isolates the blob: a color filter in HSV, with the orange range found with the trackbar tool ([[perception-hsv-color-ranges]]).

## `blob_point_pub.py`
```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Point
import cv2
import numpy as np
from cv_bridge import CvBridge
from typing import List, Tuple


class BlobPointPublisher(Node):

    def __init__(self) -> None:
        super().__init__('blob_point_publisher')
        self.subscription = self.create_subscription(Image, '/deepmind_robot1/deepmind_robot1_camera/image_raw', self.image_callback, 10)
        self.publisher = self.create_publisher(Point, '/point_blob', 10)
        self.cv_bridge = CvBridge()

    def image_callback(self, msg: Image) -> None:
        try:
            # Convert ROS Image message to OpenCV format
            cv_image = self.cv_bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        except Exception as e:
            self.get_logger().error("Error converting ROS Image to OpenCV format: {0}".format(e))
            return

        # Convert BGR image to HSV
        hsv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)

        # Define lower and upper bounds for orange color in HSV
        lower_orange = np.array([3, 0, 233])
        upper_orange = np.array([9, 255, 255])

        # Create a binary mask for orange color
        mask = cv2.inRange(hsv_image, lower_orange, upper_orange)

        # Draw coordinate frame
        self.draw_frame(cv_image)

        # Find contours in the mask
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Draw a red circle around the blob contour
        for contour in contours:
            self.draw_blob_contour_circle(cv_image, contour)

        # If no contours are found, return
        if not contours:
            return

        # Find the largest contour
        blob_contour = max(contours, key=cv2.contourArea)

        # Calculate centroid of the contour
        moment = cv2.moments(blob_contour)
        if moment["m00"] != 0:             # Area of the object
            blob_x = float(moment["m10"] / moment["m00"])  # x-coordinate of centroid
            blob_y = float(moment["m01"] / moment["m00"])  # y-coordinate of centroid

            # x and y coordinates of the blob are computed relative to the center of the image
            x, y = self.get_blob_relative_position(cv_image, blob_x, blob_y)

            # Publish Blob
            self.publish_blob(x, y)

            # Draw detected blobs
            self.draw_keypoints(cv_image, [(blob_x, blob_y)])

        # Display the image (optional)
        cv2.imshow("Image", cv_image)
        cv2.waitKey(1)

    def draw_frame(self,
                   image: np.ndarray,
                   dimension=0.1,      #- dimension relative to frame size
                   line=2              #- line's thickness
                   ) -> None:
        """ Draw X Y coordinate frame at the center of the image"""
        rows = image.shape[0]
        cols = image.shape[1]
        size = min([rows, cols])
        center_x = int(cols/2.0)
        center_y = int(rows/2.0)

        line_length = int(size*dimension)

        #-- X
        image = cv2.line(image, (center_x, center_y), (center_x+line_length, center_y), (0,0,255), line)
        #-- Y
        image = cv2.line(image, (center_x, center_y), (center_x, center_y+line_length), (0,255,0), line)

    def draw_blob_contour_circle(self, img: np.ndarray, contour: np.ndarray) -> None:
        """ Draw a red circle around the detected blob """
        # Get the bounding rectangle of the contour
        x, y, w, h = cv2.boundingRect(contour)
        # Calculate the center of the rectangle
        center_x = x + w // 2
        center_y = y + h // 2
        # Calculate the radius of the circle based on the contour size
        radius = max(w, h) // 2
        # Draw a red circle around the center
        cv2.circle(img, (center_x, center_y), radius, (0, 0, 255), 2)

    def get_blob_relative_position(self, image: np.ndarray, x: float, y: float) -> Tuple[float, float]:
        """ Get blob position relative to the coordinate frame placed at the center of the image"""
        # The shape attribute of a NumPy array returns a tuple representing the dimensions of the array.
        # For an image, the shape tuple consists of 3 elements: (height, width, channels).
        rows = float(image.shape[0]) # height
        cols = float(image.shape[1]) # width
        #  Coordinates of the center of the image
        center_x    = 0.5*cols
        center_y    = 0.5*rows
        # The x and y coordinates of the keypoint are computed relative to the center of the image
        x = (x - center_x)/(center_x)
        y = (y - center_y)/(center_y)
        return x,y

    def publish_blob(self, x: float, y: float) -> None:
        """ Publish the blob position to /point_blob """
        # Create a Point message
        point_msg = Point()
        point_msg.x = x
        point_msg.y = y
        # Publish the Point message
        self.publisher.publish(point_msg)

    def draw_keypoints(self, img: np.ndarray, keypoints: List[Tuple[float, float]]) -> None:
        """ Draw the detected blob keypoints in red """
        # Draw red circles at the detected blob keypoints
        for kp in keypoints:
            # Convert keypoints to integers
            kp = (int(kp[0]), int(kp[1]))
            cv2.circle(img, kp, 5, (0, 0, 255), -1)


def main(args=None) -> None:
    rclpy.init(args=args)
    blob_point_publisher = BlobPointPublisher()
    rclpy.spin(blob_point_publisher)
    blob_point_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```
The node detects orange blobs, computes their position and publishes it as a `Point` on `/point_blob` (same camera topic as in [[perception-image-msg]]). cv_bridge converts the image ([[perception-opencv-cv-bridge]]); the HSV range isolates orange; `inRange` makes the binary mask; contours give the blob boundaries, and the moments of the largest one give its centroid. The centroid is converted to the frame at the image center (x right, y down, both −1…1) before publishing, which the follower uses. The drawn frame, circles and keypoint are debug overlays. (The course's explanation names the moments variable `moments`; the file uses `moment`.)

## Pitfalls
- No contour → the node publishes **nothing**; a follower then gets no new command ([[perception-blob-follow]]).
- `max(contours, key=cv2.contourArea)` on an empty list raises `ValueError`: the `if not contours: return` before it is required.
- `cv2.findContours` returns two values in OpenCV 4.x (`contours, hierarchy`); code written for OpenCV 3.2–3.4 unpacks three and fails.
