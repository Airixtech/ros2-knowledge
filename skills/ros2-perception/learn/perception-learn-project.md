---
id: perception-learn-project
type: reference
owner: equipo-ros2
updated: 2026-10-27
review_by: 2027-04-25
source: manual
confidentiality: internal
title: "Course project, part 1: inventory robot spec, purple line and four colored areas of interest, line and AOI nodes"
domain: perception
area: learn
distro: humble
tested: false
audience: students
order: 2
summary: "Inventory project part 1: final_project package, purple line follower, go_to_aoi node driving to a yellow/green/blue/red area; solution differences."
tags: [course project, inventory management, final_project, purple line, area of interest, AOI, aoi_choice, line_follower.py, go_to_aoi.py, range_detector, trajectory_sender.py, HSV, crop]
see: ["[[perception-learn-project-inventory]]", "[[perception-door-follower]]", "[[perception-line-follower]]", "[[perception-hsv-color-ranges]]"]
requires: [ros2-core]
version_notes:
  - "course solution go_to_aoi.py: crops with one 2D index and guards the empty centroid list (the fixes of PERC-V12 and PERC-V13 in the course's followers); it calls rclpy.shutdown() in a callback and again in main (PERC-V03)"
  - "course solution line_follower.py keeps the optimized follower's double row slice and max() on an empty list (PERC-V12, PERC-V13)"
---
# Course project, part 1: line and areas of interest

**TL;DR** The robot follows a **purple** line around a shelf and stops at one of four **areas of interest** (AOIs), marked by green, yellow, blue and red blobs, chosen on `/aoi_choice`. Part 2 counts the items on the shelf there ([[perception-learn-project-inventory]]).

## The project
Last unit: use the whole course on a real-world problem, **intelligent inventory management with ROS 2**: a robot checks by itself the stock of a shelf with food and electronic devices. Three parts:
- **Color encoding retrieval**: find the HSV values of the colors in the simulation (line following and blob tracking).
- **Line follower pipeline**: follow the purple line and stop precisely at the four AOIs.
- **Inventory checking pipeline**: detect the items on the shelf and keep an exact count.

Prerequisites: a package `final_project` with four scripts, plus two course scripts (`range_detector.py`, `trajectory_sender.py`, given by the course) copied into it; the project also uses `ObjectCount` from `custom_msgs` ([[perception-custom-msgs]]).
```bash
cd ~/ros2_ws/src/
ros2 pkg create --build-type ament_python final_project
cd ~/ros2_ws/
colcon build
source install/setup.bash
cd src/final_project/final_project/
touch line_follower.py go_to_aoi.py object_detection.py inventory_checking.py
chmod +x *.py
```

## 7.3 Color encodings
The purple line's HSV range is found with `range_detector` as in unit 3 ([[perception-hsv-color-ranges]]); then the same for the four AOI colors (green, yellow, blue, red): the key places where the robot stops to check the inventory.

## 7.4.1 `line_follower.py` (spec)
One publisher `self.pub_vel` (`Twist`) and one subscriber `self.img_sub` (the camera image); the robot follows the purple line around the shelf. Tilt the head toward the floor first: `move_head.py 0.0 0.9 1` ([[perception-learn-start-here]]).

**Course solution**: `follow_yellow_line_optimized.py` ([[perception-line-follower]]) with these changes only: class `LineFollower` (and `LineFollower()` in `main()`), the subscription stored as `self.img_sub`, and the purple range (its comments still say yellow):
```python
        # Define lower and upper bounds for yellow color in HSV
        lower_purple = np.array([120, 50, 50])
        upper_purple = np.array([160, 255, 255])

        # Create a binary mask for yellow color
        mask = cv2.inRange(hsv, lower_purple, upper_purple)
```
It keeps the course's double row slice and `max()` outside the `try` (PERC-V12, PERC-V13): apply the fixes of [[perception-line-follower]].

## 7.4.2 `go_to_aoi.py` (spec)
Navigates around the shelf and, when asked, drives to one AOI. One publisher `self.pub_vel` (`Twist`); two subscribers: `self.img_sub` (camera) and `self.aoi_choice_sub` (`String` on `/aoi_choice`: yellow, green, blue or red). Hint: look for the AOI only in a crop of the image where it should appear. Trigger:
```bash
ros2 topic pub /aoi_choice std_msgs/msg/String "data: 'yellow'"
```

**Course solution**: the structure of `follow_door.py` ([[perception-door-follower]]) with `door` renamed to `aoi` everywhere (`GoToAOI`, node `'go_to_aoi'`, `aoi_choice`, `aoi_detected`, `aoi_callback()`, `search_aoi()` with the logs `'… area of interest detected'` / `'Still searching for the … area of interest'`, `is_valid_aoi_choice()` with the four colors and the warning "Please choose between 'yellow', 'green', 'blue' or 'red' for the area of interest location color."), docstrings added, and these real changes:
1. Five color ranges, and one `if self.aoi_choice == …:` block per AOI color (`detect_contours()` on the AOI crop, then `search_aoi()`):
```python
        # Define lower and upper bounds for purple, yellow, green, blue and red colors in HSV
        purple_bounds = ([120, 50, 50], [160, 255, 255])
        yellow_bounds = ([20, 100, 50], [35, 255, 255])
        green_bounds = ([45, 100, 50], [85, 255, 255])
        blue_bounds = ([90, 150, 50], [125, 255, 255])
        red_bounds = ([170, 150, 50], [180, 255, 255])
```
2. Crops with one 2D index each; the AOI crop is the middle third of the rows and the columns from 1/8 to 1/2 of the width:
```python
    def crop_image(self, cv_image: np.ndarray, height: int, width: int) -> Tuple[np.ndarray, np.ndarray]:
        """ Crop image, we create two cropped image
            One for the line follower and one to access the AOI """
        rows_to_watch = 20

        crop_img_start_row = height * 3 // 4
        crop_img_end_row = min(height, crop_img_start_row + rows_to_watch)
        crop_img = cv_image[crop_img_start_row:crop_img_end_row, 0:width]

        crop_aoi_img_start_row = height // 3
        crop_aoi_img_end_row = min(height, height * 2 // 3)
        crop_aoi_img_start_col = width // 8
        crop_aoi_img_end_col = min(width, width // 2)
        crop_aoi_img = cv_image[crop_aoi_img_start_row:crop_aoi_img_end_row, crop_aoi_img_start_col:crop_aoi_img_end_col]

        return crop_img, crop_aoi_img
```
3. When the line ends and the AOI was seen, the robot does not stop at once: `self.go_to_aoi(hsv_detect_aoi, crop_aoi_img, width)` drives to the blob. Then the empty-list guard:
```python
        # checks if arrived at the aoi destination
        if len(centres) < 1 and self.aoi_detected:
            self.go_to_aoi(hsv_detect_aoi, crop_aoi_img, width)
            return

        # Ensure centres is not empty before attempting to find the max and min centroids
        if centres:
            most_right_centroid = max(centres, key=lambda x: x[0])
            most_left_centroid = min(centres, key=lambda x: x[0])
        else:
            self.get_logger().error("No purple contours detected. Cannot find centroids.")
            return  # Exit the callback if no centroids are found
```
4. Two new methods: steer to the largest blob of the chosen color with speeds per AOI, and stop when the blob leaves the crop:
```python
    def go_to_aoi(self, hsv_detect_aoi: np.ndarray, cv_image: np.ndarray, width: int) -> None:
        """ Ensure that the robot positions itself accurately to one of the four key locations of interest"""
        # Find the blob of interest
        blob_bounds = None
        if self.aoi_choice == 'yellow':
            blob_bounds = ([20, 100, 50], [35, 255, 255])
        elif self.aoi_choice == 'green':
            blob_bounds = ([45, 100, 50], [85, 255, 255])
        elif self.aoi_choice == 'blue':
            blob_bounds = ([90, 150, 50], [125, 255, 255])
        elif self.aoi_choice == 'red':
            blob_bounds = ([170, 150, 50], [180, 255, 255])

        if blob_bounds:
            _, contours = self.detect_contours(hsv_detect_aoi, blob_bounds[0], blob_bounds[1], cv_image)
            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                moments = cv2.moments(largest_contour)
                try:
                    cx = int(moments['m10'] / moments['m00'])
                    cy = int(moments['m01'] / moments['m00'])
                    # Draw the centroid on the image for visualization
                    cv2.circle(cv_image, (cx, cy), 5, (0, 0, 255), -1)  # Red dot at the centroid
                    self.pub_aoi_velocities(cx, width)
                    # Display the image for debugging
                    cv2.imshow("Centroid Visualization", cv_image)
                    cv2.waitKey(1)
                except ZeroDivisionError:
                    self.get_logger().error("Zero division error while calculating centroid.")
                    self.stop_robot()
            else:
                self.get_logger().info("Arrived at the area of interest. Stopping the robot and shutting down.")
                self.stop_robot()
                rclpy.shutdown()
        else:
            self.get_logger().error("Invalid aoi choice. Cannot determine blob bounds.")
            self.stop_robot()

    def pub_aoi_velocities(self, cx: int, width: int) -> None:
        """ Publish aoi velocities based on the centroid and AOI color choice """
        linear_vel = 0.2
        angular_vel = 0.06

        # Adjust velocities based on AOI color choice
        if self.aoi_choice == 'green':
            angular_vel = 0.07
        elif self.aoi_choice == 'blue':
            linear_vel = 0.25
            angular_vel = 0.05

        error_x = cx - width / 2
        twist_object = Twist()
        twist_object.linear.x = linear_vel
        angular_velocity = -error_x / 100

        # Ensure angular velocity is within a certain range
        if angular_velocity < -0.3:
            angular_velocity = -angular_vel
        elif angular_velocity > 0.3:
            angular_velocity = angular_vel

        twist_object.angular.z = angular_velocity
        self.get_logger().info(f"Navigating to {self.aoi_choice} aoi: Adjusting angular velocity ---> {twist_object.angular.z:.2f}")
        self.pub_vel.publish(twist_object)
```
5. `pub_velocities()` clamps to ±0.35 rad/s instead of ±0.3 (comment "Ensure angular velocity is within a certain range"); `detect_contours()` types its bounds as `Tuple[int, int, int]`.

Notes on the solution: `rclpy.shutdown()` inside `go_to_aoi()` plus the one at the end of `main()` raises `RCLError` (PERC-V03); `pub_aoi_velocities()` replaces large turns by a small fixed one (0.05–0.07 rad/s) instead of clamping to ±0.3.
