---
id: perception-door-follower
type: reference
owner: equipo-ros2
updated: 2026-10-27
review_by: 2027-04-25
source: manual
confidentiality: internal
title: "Line follower that turns toward a door marked by a colored blob chosen on a String topic"
domain: perception
area: image
distro: humble
tested: false
audience: dev
summary: "Follow a line, detect the chosen door's color blob in a top crop, then take the leftmost centroid; /door_choice String."
tags: [line following, door follower, std_msgs/String, door_choice, crop, HSV, contours, centroid, time.time, ros2 topic pub, follow_door.py, line_following]
see: ["[[perception-line-follower]]", "[[perception-hsv-color-ranges]]", "[[perception-learn-project]]", "[[core-topic-cli]]"]
requires: [ros2-core]
version_notes:
  - "course: both crops used `img[a:b][c:d]` (rows sliced twice, PERC-V12); fixed with one 2D index; the door crop keeps the course's rows 1-19 and all columns"
  - "course: with no yellow contour and no door, `max(centres, ...)` raised ValueError and ended the node; the guard comes from the course's project solution go_to_aoi.py (PERC-V13)"
  - "course: the 3.11 explanation names the top crop `crop_top_image`; the file uses `crop_top_img` (PERC-V05)"
---
# Door follower: line + colored door blob

**TL;DR** Follow the yellow line with the rightmost centroid; when the chosen door's color appears in a crop of the image's **top rows**, switch to the leftmost centroid (the branch toward the door) and keep that choice 60 s; stop when the line ends while the door is detected. The door color arrives as a `std_msgs/String` on `/door_choice`.

## Spec
Doors are marked by **orange** or **green** blobs. The robot follows the yellow lines through the museum and heads to the door named on `/door_choice` (`"orange"` or `"green"`, published by hand with `ros2 topic pub`), then stops in front of it. Node: a `String` subscriber on `/door_choice`, an `Image` subscriber on the camera topic, a `Twist` publisher on `/cmd_vel`.
```bash
cd src/line_following/line_following
touch follow_door.py
chmod +x follow_door.py
cd ~/ros2_ws/
```

## `follow_door.py`
```python
import rclpy
from rclpy.node import Node
import cv2
import numpy as np
from cv_bridge import CvBridge
from std_msgs.msg import String
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
import time
from typing import List, Tuple


class DoorFollower(Node):

    def __init__(self) -> None:
        super().__init__('door_follower')
        self.bridge = CvBridge()
        self.door_choice_sub = self.create_subscription(String, '/door_choice', self.door_callback, 10)
        self.img_sub = self.create_subscription(Image, '/deepmind_robot1/deepmind_robot1_camera/image_raw', self.camera_callback, 10)
        self.pub_vel = self.create_publisher(Twist, 'cmd_vel', 10)
        self.door_choice = None
        self.door_detected = False
        self.last_detection_time = None

    def door_callback(self, msg: String) -> None:
        self.door_choice = msg.data

    def camera_callback(self, msg: Image) -> None:
        try:
            # Convert ROS Image message to OpenCV format
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        except Exception as e:
            self.get_logger().info(f"Error converting image: {e}")
            return

        # Define lower and upper bounds for yellow, green and orange colors in HSV
        yellow_bounds = ([20, 100, 100], [40, 255, 255])
        orange_bounds = ([3, 0, 233], [9, 255, 255])
        green_bounds = ([34, 255, 0], [82, 255, 255])
        # Define height and width of image
        height, width, _ = cv_image.shape

        # Crop images
        crop_img, crop_top_img = self.crop_image(cv_image, height, width)
        # Convert to HSV
        hsv, hsv_detect_door = self.convert_to_hsv(crop_img, crop_top_img)

        # Detects yellow contours
        res, yellow_contours = self.detect_contours(hsv, yellow_bounds[0], yellow_bounds[1], crop_img)

        if self.door_choice == 'orange':
            # Detects orange contours
            res2, orange_contours = self.detect_contours(hsv_detect_door, orange_bounds[0], orange_bounds[1], crop_top_img)
            # Checks if orange door has been detected
            self.door_detected = self.search_door('orange', orange_contours, res2)

        if self.door_choice == 'green':
            # Detects green contours
            res2, green_contours = self.detect_contours(hsv_detect_door, green_bounds[0], green_bounds[1], crop_top_img)
            # Checks if green door has been detected
            self.door_detected = self.search_door('green', green_contours, res2)

        # Calculate centroids for each yellow contours
        centres = []
        for i in range(len(yellow_contours)):
            moments = cv2.moments(yellow_contours[i])
            try:
                # append centroid coordinates for each contour
                centres.append((int(moments['m10']/moments['m00']), int(moments['m01']/moments['m00'])))
                # draw green circle to visualize detected centroids
                cv2.circle(res, centres[-1], 10, (0, 255, 0), -1)
            except ZeroDivisionError:
                pass

        # checks if arrived at the door destination
        if len(centres) < 1 and self.door_detected:
            self.stop_robot()
            return

        # Ensure centres is not empty before attempting to find the max and min centroids (PERC-V13)
        if not centres:
            self.get_logger().error("No yellow contours detected. Cannot find centroids.")
            return

        # Retrieves appropriate centroid
        most_right_centroid = max(centres, key=lambda x: x[0])
        most_left_centroid = min(centres, key=lambda x: x[0])

        # Checks if the door choice color choice is valid
        self.is_valid_door_choice()

        # Calculate centroids coordinates
        if (self.is_valid_door_choice() and self.door_detected):
            cx, cy = self.get_centroid_coordinates(most_left_centroid, height, width)
        else:
            cx, cy = self.get_centroid_coordinates(most_right_centroid, height, width)

        # draw red circle to visualize selected centroid
        cv2.circle(res, (int(cx), int(cy)), 5, (0, 0, 255), -1)

        # Display
        cv2.imshow("RES", res)
        cv2.waitKey(1)

        # Calculate horizontal error between the centroid and the center of the image
        error_x = cx - width / 2

        # Publish velocities
        self.pub_velocities(error_x)

    def crop_image(self, cv_image: np.ndarray, height: int, width: int) -> Tuple[np.ndarray, np.ndarray]:
        """ Crop image """
        rows_to_watch = 20
        cols_to_watch = 20
        # One 2D index each: rows, then columns (PERC-V12)
        crop_img = cv_image[height*3//4:height*3//4 + rows_to_watch, 0:width]
        crop_top_img = cv_image[1:cols_to_watch, 0:width]
        return crop_img, crop_top_img

    def convert_to_hsv(self, crop_img: np.ndarray, crop_top_img: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """ Converts from BGR to HSV """
        hsv = cv2.cvtColor(crop_img, cv2.COLOR_BGR2HSV)
        hsv_detect_door = cv2.cvtColor(crop_top_img, cv2.COLOR_BGR2HSV)
        return hsv, hsv_detect_door

    def detect_contours(self, hsv: np.ndarray, lower_bound: List[int], upper_bound: List[int], image: np.ndarray) -> Tuple[np.ndarray, List[np.ndarray]]:
        """ Detects for contours based on HSV range values """
        mask = cv2.inRange(hsv, np.array(lower_bound), np.array(upper_bound))
        res = cv2.bitwise_and(image, image, mask=mask)
        contours, _ = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_TC89_L1)
        return res, contours

    def is_recently_detected(self) -> bool:
        """ Determines if door was recently detected """
        if self.last_detection_time is not None:
            current_time = time.time()
            elapsed_time = current_time - self.last_detection_time
            if elapsed_time < 60:
                return True
        return False

    def search_door(self, door_color: str, contours: List[np.ndarray], res: np.ndarray) -> bool:
        """ Searches for a specific colored door """
        if contours:
            self.get_logger().warning(f'{door_color.capitalize()} door detected')
            self.door_detected = True
            # Set timer when the contour has been detected
            self.last_detection_time = time.time()
            cv2.imshow("RES2", res)
            cv2.waitKey(1)
        else:
            if self.is_recently_detected():
                self.door_detected = True
            else:
                self.get_logger().warning(f'Still searching for the {door_color} door')
                self.door_detected = False

        return self.door_detected

    def is_valid_door_choice(self) -> bool:
        """ Checks if the door color choice is valid """
        valid_door_colors = ['orange', 'green']
        if self.door_choice in valid_door_colors:
            return True
        else:
            self.get_logger().warning("Please choose between 'orange' and 'green' for the door color.")
            return False

    def get_centroid_coordinates(self, centroid: Tuple[int, int], height: int, width: int) -> Tuple[int, int]:
        """ Retrieves centroid's x and y coorinates"""
        try:
            # retrieve selected centroid coordinates
            cx = centroid[0]
            cy = centroid[1]
        except:
            cy, cx = height/2, width/2

        return cx, cy

    def stop_robot(self) -> None:
        """ Stops the robot movement """
        twist_object = Twist()
        twist_object.linear.x = 0.0
        twist_object.angular.z = 0.0
        self.pub_vel.publish(twist_object)

    def pub_velocities(self, error: float) -> None:
        """ Publish command velocities """
        twist_object = Twist()
        twist_object.linear.x = 0.2
        angular_velocity = -error / 100

        # Ensure angular velocity is within [-0.3, 0.3]
        if angular_velocity < -0.3:
            angular_velocity = -0.3
        elif angular_velocity >= 0.3:
            angular_velocity = 0.3

        twist_object.angular.z = angular_velocity
        self.get_logger().info(f"Adjusting the angular velocity ---> {twist_object.angular.z:.2f}" )
        self.pub_vel.publish(twist_object)


def main(args=None) -> None:
    rclpy.init(args=args)
    door_follower = DoorFollower()
    try:
        rclpy.spin(door_follower)
    except KeyboardInterrupt:
        pass
    door_follower.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```
How it works:
- Color bounds for yellow, green and orange; two crops: `crop_img` (the line band, as in [[perception-line-follower]]) and `crop_top_img` (the top rows, where the door markers appear; the variable says "cols", it holds rows). Both go to HSV.
- Yellow contours keep the robot on the line. The `door_choice` conditions look only for the chosen door's color in the top crop; `search_door()` sets `door_detected` and remembers the detection time, so the choice holds 60 s after the blob leaves the crop.
- One centroid per yellow contour (green circles). No yellow line while the door is detected = **destination reached**: stop. Otherwise the rightmost centroid follows the loop around the museum, and the leftmost one turns into the branch toward the door once it was seen. `is_valid_door_choice()` warns when the topic carries another color.
- `error_x` drives the angular speed, clamped to ±0.3 rad/s.
- Changes from the course: one 2D index per crop (PERC-V12) and the empty-list guard (PERC-V13), the same guard the course's project solution uses.

## Test
Stop the previous node, tilt the head further down (`move_head.py 0.0 0.9 1`, [[perception-learn-start-here]]), then:
```bash
cd ~/ros2_ws/
colcon build;source install/setup.bash
ros2 run line_following follow_door
```
```bash
ros2 topic pub /door_choice std_msgs/String "data: 'orange'"
```
The robot first follows the yellow lane; asked for the orange door (once it is past the flower paintings), it goes there without leaving the lane. Try `green` too. `ros2 topic pub` repeats the message every second until stopped ([[core-topic-cli]]).

## Pitfalls
- Wrong door or none: the door crop sees only the top rows; tilt the head as in the course so the markers fall there.
- `get_centroid_coordinates()`'s `try/except` never triggers (a tuple always has two items); the empty case needs the explicit guard above.
- Ctrl + C, then `rclpy.shutdown()` can raise `RCLError` (PERC-V48, [[core-node-skeleton]]).
