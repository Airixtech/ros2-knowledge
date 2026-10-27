---
id: perception-yolo-person-follower
type: reference
owner: equipo-ros2
updated: 2026-10-27
review_by: 2027-04-25
source: manual
confidentiality: internal
title: "Follow a person from YOLO detections: center error to angular velocity, stop by box width, stop when lost"
domain: perception
area: yolo
distro: humble
tested: false
audience: dev
summary: "Follow the first YOLO 'person': angular = -0.001*error_x at 0.1 m/s; stop when box_width > 270 or lost."
tags: [person follower, human following, YOLO, Yolov8Inference, InferenceResult, class_name person, error_x, box_width, Twist, cmd_vel, image width, yolo_person_follower.py, advanced_perception, launch_yolo_person_follower]
see: ["[[perception-yolo-object-detection]]", "[[perception-hog-human-tracking]]", "[[perception-custom-msgs]]", "[[core-logging]]"]
requires: [ros2-core]
version_notes:
  - "humble: get_logger().warn() is a deprecated alias of warning(); lyrical removed it (AttributeError) — https://github.com/ros2/rclpy/blob/lyrical/rclpy/rclpy/impl/rcutils_logger.py (PERC-V47)"
---
# Follow a person from YOLO detections

**TL;DR** Read the detections of [[perception-yolo-object-detection]] on `/Yolov8_Inference`, take the first `person`, turn with `angular.z = -0.001 * (x - image_width / 2)` while driving at 0.1 m/s, stop when the box is wider than 270 px (close enough), and publish a zero `Twist` once when the person is lost.

## `yolo_person_follower.py`
Goal: detect a person with YOLOv8 and drive to them autonomously (here from a starting point in the museum to the person sitting on a bench).
```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from geometry_msgs.msg import Twist
from custom_msgs.msg import InferenceResult, Yolov8Inference


class PersonFollower(Node):

    def __init__(self) -> None:
        super().__init__('person_follower')
        self.subscription_inference = self.create_subscription(Yolov8Inference, '/Yolov8_Inference', self.inference_callback, 10)
        self.subscription_image = self.create_subscription(Image, '/deepmind_robot1/deepmind_robot1_camera/image_raw', self.image_callback, 10)
        self.cmd_vel_publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.bridge = CvBridge()
        self.image_width = None
        self.person_detected = False

    def image_callback(self, data: Image) -> None:
        """ Updates the image width from the incoming camera image """
        self.image_width = data.width

    def inference_callback(self, msg: Yolov8Inference) -> None:
        """ Processes each inference result, checks for 'person' class, and moves the robot accordingly """
        person_detected = False
        if self.image_width is None:
            self.get_logger().warning("Image width not set yet...")  # PERC-V47: warn() in the course
            return

        for inference_result in msg.yolov8_inference:
            if inference_result.class_name == 'person':
                person_detected = True
                self.get_logger().info(f"Person detected: {inference_result}")
                # Calculate error_x as the difference between x and the center of the image
                error_x = inference_result.x - (self.image_width / 2)
                self.get_logger().info(f"error_x = {error_x}")
                self.move_towards_person(inference_result, error_x)
                break  # Assuming we only follow the first detected person

        if not person_detected and self.person_detected:
            self.get_logger().info("Person lost, stopping...")
            self.stop_moving()

        self.person_detected = person_detected

    def move_towards_person(self, inference_result: InferenceResult, error_x: float) -> None:
        """ Calculates and publishes velocities to move towards the detected person """
        gain = 0.001
        linear_velocity = 0.1
        max_box_width = 270
        angular_velocity = -error_x * gain
        self.get_logger().info(f'Moving towards person with error_x: {error_x}, angular velocity: {angular_velocity}, linear velocity: {linear_velocity}, box_width = {inference_result.box_width}')

        if inference_result.box_width > max_box_width:
            linear_velocity = 0.0
            angular_velocity = 0.0
            self.get_logger().info("Arrived at destination...")

        self.publish_velocities(linear_velocity, angular_velocity)

    def publish_velocities(self, linear_velocity: float, angular_velocity: float) -> None:
        """ Publishes linear and angular velocities to the cmd_vel topic """
        twist_msg = Twist()
        twist_msg.linear.x = linear_velocity
        twist_msg.angular.z = angular_velocity
        self.cmd_vel_publisher.publish(twist_msg)

    def stop_moving(self) -> None:
        """ Publishes zero velocities to stop the robot """
        twist_msg = Twist()
        self.cmd_vel_publisher.publish(twist_msg)


def main(args=None) -> None:
    rclpy.init(args=args)
    person_follower = PersonFollower()
    rclpy.spin(person_follower)
    person_follower.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```
- Subscriptions: `/Yolov8_Inference` (published by the detection node) and the camera image, used only for its `width`; publisher on `/cmd_vel`.
- `inference_callback()` resets `person_detected` at each call so it reflects the latest data, and returns while the image width is unknown (a safeguard: no motion without context). It loops over the detections; `class_name == 'person'` selects people only; `error_x` (detection center − image center) says how far off-center the person is; `break` follows only the **first** person of each message.
- When a person seen before is gone, the node stops once instead of wandering or getting into unsafe situations.
- `move_towards_person()`: `gain` 0.001 scales the error into an angular speed; `linear_velocity` 0.1 m/s while a person is visible; `max_box_width` 270 px: a wider box means the person is close, so both speeds become 0 ("Arrived at destination..."). The minus sign turns toward the person (left of center → turn left).
- `publish_velocities()` sends the command; `stop_moving()` sends an all-zero `Twist`.

## Launch and test
Head back to its initial position (`move_head.py 0.0 0.0 1`), RViz with `/inference_result` ([[perception-rviz-sensors]]), drive near the start position with teleop, then the detection node and the follower:
```bash
cd ~/ros2_ws/
colcon build;source install/setup.bash
ros2 run advanced_perception yolo_object_detection
```
```bash
cd ~/ros2_ws/
colcon build;source install/setup.bash
ros2 run advanced_perception yolo_person_follower
```
The robot finds the person on the bench and drives to them. Typical log while approaching:
```text
[yolo_person_follower]: Moving towards person with error_x: 9.5, angular velocity: -0.0095, linear velocity: 0.1, box_width = 93
[INFO] [yolo_person_follower]: Arrived at destination...
```
The course's opening demo starts both nodes with one launch file of its solution package: `ros2 launch advanced_perception launch_yolo_person_follower.launch.py` (not shown in the course).

## Pitfalls
- `AttributeError: 'RcutilsLogger' object has no attribute 'warn'` on Lyrical → use `warning()` (PERC-V47, [[core-logging]]).
- If the detection node stops, no message arrives and the "lost" branch never runs: the robot keeps its last command. Add a timeout timer.
- A stop decided by box width depends on the camera's resolution and field of view: retune `max_box_width` for another camera, or use depth.
