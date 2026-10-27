---
id: perception-line-follower
type: reference
owner: equipo-ros2
updated: 2026-10-27
review_by: 2027-04-25
source: manual
confidentiality: internal
title: "Line follower: crop rows, HSV mask, centroid error to angular velocity; several lines and the rightmost centroid"
domain: perception
area: image
distro: humble
tested: false
audience: dev
summary: "Follow a floor line: crop a row band, HSV mask, moments centroid, angular = -error/100; several lines: rightmost contour centroid."
tags: [line following, line follower, crop, cv2.moments, centroid, cv2.findContours, RETR_CCOMP, CHAIN_APPROX_TC89_L1, cv2.bitwise_and, error_x, follow_yellow_line.py, follow_yellow_line_optimized.py, line_following]
see: ["[[perception-door-follower]]", "[[perception-hsv-color-ranges]]", "[[perception-blob-detect]]", "[[core-node-skeleton]]"]
requires: [ros2-core]
version_notes:
  - "course: `cv_image[a:b][1:width]` sliced the rows twice and never the columns; fixed with one 2D index `cv_image[a:b, 0:width]`, as the course's project solution go_to_aoi.py does — https://numpy.org/doc/stable/user/basics.indexing.html (PERC-V12)"
  - "course: in the optimized version `max(centres, ...)` ran before the `try`, so an empty list raised ValueError and ended the node; moved inside the try (PERC-V13)"
  - "course: Ctrl+C then rclpy.shutdown() after `except KeyboardInterrupt` can raise RCLError (the signal handler already shut the context down) — https://github.com/ros2/rclpy/blob/humble/rclpy/src/rclpy/signal_handler.cpp (PERC-V48)"
---
# Line follower

**TL;DR** Look only at a thin band of rows in the lower part of the image, mask the line color in HSV, take the centroid, and steer with `angular.z = -(cx - width/2) / 100` at a constant 0.2 m/s. When several lines are visible, compute one centroid per contour and pick one by a rule (the rightmost here).

## Line following
A robot follows a marked path (usually a contrasting line on the floor) with its sensors and corrects its position as it goes; here with the camera's `sensor_msgs/Image`. Uses: automated guided vehicles (AGVs) in factories and warehouse logistics, robotic lawn mowers, surveillance robots that patrol a perimeter.

Course goal: follow the **yellow** lines around the museum (yellow range from the trackbar tool: [[perception-hsv-color-ranges]]).
```bash
cd ~/ros2_ws/src/
ros2 pkg create --build-type ament_python line_following
cd ~/ros2_ws/
colcon build
source install/setup.bash
cd src/line_following/line_following
touch follow_yellow_line.py
chmod +x follow_yellow_line.py
cd ~/ros2_ws/
```

## `follow_yellow_line.py`
```python
import rclpy
from rclpy.node import Node
import cv2
import numpy as np
from cv_bridge import CvBridge
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist


class LineFollower(Node):

    def __init__(self) -> None:
        super().__init__('line_follower')
        self.bridge = CvBridge()
        self.subscription = self.create_subscription(Image, '/deepmind_robot1/deepmind_robot1_camera/image_raw', self.camera_callback, 10)
        self.pub_vel = self.create_publisher(Twist, 'cmd_vel', 10)

    def camera_callback(self, msg: Image) -> None:
        try:
            # Convert ROS Image message to OpenCV format
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        except Exception as e:
            self.get_logger().info(f"Error converting image: {e}")
            return

        height, width, _ = cv_image.shape
        rows_to_watch = 20
        # Crop image (one 2D index: rows, then columns, PERC-V12)
        crop_img = cv_image[height*3//4:height*3//4 + rows_to_watch, 0:width]

        # Convert BGR image to HSV
        hsv = cv2.cvtColor(crop_img, cv2.COLOR_BGR2HSV)

        # Define lower and upper bounds for yellow color in HSV
        lower_yellow = np.array([20, 100, 100])
        upper_yellow = np.array([40, 255, 255])

        # Create a binary mask for yellow color
        mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

        # Calculate centroid of the mask
        moment = cv2.moments(mask, False)
        try:
            # x and y coordinates of centroid
            cx, cy = moment['m10'] / moment['m00'], moment['m01'] / moment['m00']
        except ZeroDivisionError:
            cy, cx = height/2, width/2

        res = cv2.bitwise_and(crop_img, crop_img, mask=mask)

        # Draw circle to visualize the detected centroid
        cv2.circle(res, (int(cx), int(cy)), 10, (0, 0, 255), -1)

        # Display
        cv2.imshow("RES", res)
        cv2.waitKey(1)

        # Calculate horizontal error between the centroid and the center of the image
        error_x = cx - width / 2

        # Publish velocities
        self.pub_velocities(error_x)

    def pub_velocities(self, error: float) -> None:
        twist_object = Twist()
        twist_object.linear.x = 0.2
        twist_object.angular.z = -error / 100
        self.get_logger().info(f"Adjusting the angular velocity ---> {twist_object.angular.z:.2f}" )
        self.pub_vel.publish(twist_object)


def main(args=None) -> None:
    rclpy.init(args=args)
    line_follower = LineFollower()
    try:
        rclpy.spin(line_follower)
    except KeyboardInterrupt:
        pass
    line_follower.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```
- Crop: work on the smallest image the task needs, which makes detection much faster. The course wrote `cv_image[height*3//4:height*3//4 + rows_to_watch][1:width]`: the second `[...]` slices the rows of the 20-row band again, so the columns were never cropped (PERC-V12).
- The mask keeps only yellow; the moments of the whole mask give one centroid (red circle on the debug image `res`). No yellow → `m00` is 0, `ZeroDivisionError`, and the centroid falls back to the image center (straight ahead).
- `error_x` is the horizontal offset of the centroid from the image center; the angular speed is proportional to it.
- Limit: with one line this works; where several paths are visible the single centroid lies between them, so the robot behaves erratically until one path remains and sometimes heads to a door. One centroid per line fixes that.

## `follow_yellow_line_optimized.py` (differences)
```bash
cd src/line_following/line_following
touch follow_yellow_line_optimized.py
chmod +x follow_yellow_line_optimized.py
cd ~/ros2_ws/
```
Same file except: the class is `LineFollowerOptimized` (node name still `'line_follower'`, `main()` creates `LineFollowerOptimized()`), and the single-centroid block (from `# Calculate centroid of the mask` to the red circle) becomes one centroid per contour plus a choice, with `res` computed right after the mask:
```python
        res = cv2.bitwise_and(crop_img, crop_img, mask=mask)

        # Find contours in the mask
        contours, _ = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_TC89_L1)
        self.get_logger().info("Number of centroids==>"+str(len(contours)))
        centres = []
        # Calculate centroids for each contour
        for i in range(len(contours)):
            moments = cv2.moments(contours[i])
            try:
                # append centroid coordinates for each contour
                centres.append((int(moments['m10']/moments['m00']), int(moments['m01']/moments['m00'])))
                # draw green circle to visualize detected centroids
                cv2.circle(res, centres[-1], 10, (0, 255, 0), -1)
            except ZeroDivisionError:
                pass

        try:
            # Retrieves appropriate centroid (inside the try: empty list -> ValueError, PERC-V13)
            most_right_centroid = max(centres, key=lambda x: x[0])
            # retrieve selected centroid coordinates
            cx = most_right_centroid[0]
            cy = most_right_centroid[1]
        except:
            cy, cx = height/2, width/2

        # draw red circle to visualize selected centroid
        cv2.circle(res, (int(cx), int(cy)), 5, (0, 0, 255), -1)
```
Contours are the continuous regions of non-zero pixels of the mask; each gets a centroid in `centres` (green circles). The chosen one is the centroid with the **largest x** (the rightmost, red circle): it keeps the robot on its loop around the museum instead of turning into a door. The course placed `max()` before the `try`, so no line meant `ValueError` and the end of the node (PERC-V13). The course's project version of this file only changes the HSV range to purple ([[perception-learn-project]]).

## Test
Open RViz ([[perception-rviz-sensors]]), tilt the head slightly down (`move_head.py 0.0 0.5 1`, [[perception-learn-start-here]]), place the robot near the yellow line with teleop, then run one version (stop the other with Ctrl + C first):
```bash
cd ~/ros2_ws/
colcon build;source install/setup.bash
ros2 run line_following follow_yellow_line
```
```bash
cd ~/ros2_ws/
colcon build;source install/setup.bash
ros2 run line_following follow_yellow_line_optimized
```
The optimized version moves around the museum on the yellow lines and picks the right-hand centroid (red) at forks.

## Pitfalls
- `angular.z = -error / 100` has no limit: a centroid at the image edge commands ±3.2 rad/s; clamp it as the door follower does ([[perception-door-follower]]).
- `except:` without a type also hides real errors; catch `ValueError` / `ZeroDivisionError`.
- Ctrl + C, then `rclpy.shutdown()` after `except KeyboardInterrupt` can raise `RCLError: failed to shutdown` (rclpy already shut the context down): call it only `if rclpy.ok()` (PERC-V48, [[core-node-skeleton]]).
