---
id: perception-blob-follow
type: reference
owner: equipo-ros2
updated: 2026-10-27
review_by: 2027-04-25
source: manual
confidentiality: internal
title: "Blob follower: steer from the published blob Point, rotate while no blob, run the pair"
domain: perception
area: image
distro: humble
tested: false
audience: dev
summary: "Steer from the blob Point: angular = -0.3*x clipped to ±1, stop near the blob, rotate until the first blob."
tags: [blob tracker, blob following, geometry_msgs/Point, point_blob, Twist, cmd_vel, proportional control, angular gain, create_timer, blob_tracker.py, warning]
see: ["[[perception-blob-detect]]", "[[perception-line-follower]]", "[[core-logging]]"]
requires: [ros2-core]
version_notes:
  - "course: the explanation says the robot rotates whenever no blob is detected; no_blob_detected is never set back to True, so it rotates only before the first detection (PERC-V11)"
  - "humble: get_logger().warn() is a deprecated alias of warning(); lyrical removed it (AttributeError) — https://github.com/ros2/rclpy/blob/lyrical/rclpy/rclpy/impl/rcutils_logger.py (PERC-V47)"
---
# Blob follower

**TL;DR** Turn proportionally to the blob's horizontal offset (`angular = -0.3 * x`, clipped to ±1 rad/s), drive at 0.3 m/s until the blob is low in the image (`y ≥ 0.8`), and rotate in place until a first blob appears. It needs `blob_point_pub.py` running ([[perception-blob-detect]]).

## `blob_tracker.py`
```python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point, Twist


class BlobTracker(Node):

    def __init__(self) -> None:
        super().__init__('blob_tracker')
        self.subscription = self.create_subscription(Point, '/point_blob', self.blob_callback, 10)
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.angular_gain = 0.3
        self.no_blob_detected = True
        self.timer = self.create_timer(1.0, self.rotate_continuous)

    def blob_callback(self, msg: Point) -> None:
        # Extract blob coordinates
        blob_x = msg.x
        blob_y = msg.y

        # Define linear velocity
        linear_x = 0.3

        if blob_x != 0.0 or blob_y != 0.0:
            # Adjust angular velocity based on blob's position
            angular_vel = -self.angular_gain * blob_x

            # Clip angular velocity to [-1, 1] range
            angular_vel = max(min(angular_vel, 1.0), -1.0)

            # Adjust linear velocity based on blob's position
            if blob_y < 0.8:
                linear_vel = linear_x
            else:
                linear_vel = 0.0  # Stop the robot

            self.no_blob_detected = False
        else:
            return

        self.pub_velocities(linear_vel, angular_vel)

    def rotate_continuous(self) -> None:
        # Rotate continuously
        if self.no_blob_detected:
            twist_msg = Twist()
            twist_msg.angular.z = 0.3  # Adjust angular velocity as needed
            self.publisher.publish(twist_msg)
            self.get_logger().warning("No blobs detected yet ... Rotating continuously")  # PERC-V47: warn() in the course

    def pub_velocities(self, linear: float, angular: float) -> None:
        # Create Twist message with linear and angular velocities
        twist_msg = Twist()
        twist_msg.linear.x = linear
        twist_msg.angular.z = angular
        # Publish the Twist message
        self.publisher.publish(twist_msg)
        self.get_logger().info(f"Linear vel: {linear:.2f}, Angular vel: {angular:.2f}")


def main(args=None) -> None:
    rclpy.init(args=args)
    blob_tracker = BlobTracker()
    rclpy.spin(blob_tracker)
    blob_tracker.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```
The node subscribes to `/point_blob` and publishes on `/cmd_vel`. The blob x, y are relative to the image center (x right, y down, −1…1): a blob on the right (x > 0) gives a negative (clockwise) turn toward it. A blob near the bottom (`y ≥ 0.8`) means the robot is close: linear speed 0. `rotate_continuous()` runs every second and turns the robot at 0.3 rad/s while `no_blob_detected` is true: **only until the first blob**, because nothing sets the flag back (the course text says "whenever no blob is found", PERC-V11). After that, a lost blob means no new messages and no new command.

## Run the pair
Open RViz with the saved setup ([[perception-rviz-sensors]]), tilt the robot's head slightly down (course tool `move_head.py … 0.5 …`, [[perception-learn-start-here]]), drive near the exit door with teleop, then in two terminals:
```bash
cd ~/ros2_ws/
colcon build;source install/setup.bash
ros2 run blob_tracking blob_point_pub
```
```bash
cd ~/ros2_ws/
colcon build;source install/setup.bash
ros2 run blob_tracking blob_tracker
```
The robot detects the orange blob and drives to the exit door.

## Pitfalls
- The robot keeps going after the blob disappears → no message, no command; add a watchdog timer that publishes a zero `Twist` when no blob arrived for some time, or sets `no_blob_detected` back to `True` (PERC-V11).
- A blob exactly at the image center (0, 0) is ignored by `blob_x != 0.0 or blob_y != 0.0`.
- `get_logger().warn()` fails on Lyrical (`AttributeError`): use `warning()` (PERC-V47, [[core-logging]]).
