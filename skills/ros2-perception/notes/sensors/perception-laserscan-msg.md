---
id: perception-laserscan-msg
type: reference
owner: equipo-ros2
updated: 2026-10-27
review_by: 2027-04-25
source: manual
confidentiality: internal
title: "sensor_msgs/LaserScan fields and a node that stops at a distance read straight ahead"
domain: perception
area: sensors
distro: humble
tested: false
audience: dev
summary: "LaserScan fields (angle_min/max, angle_increment, range_min/max, ranges, intensities) and an rclpy node that stops 0.5 m before a wall."
tags: [sensor_msgs/LaserScan, LaserScan, ranges, angle_min, angle_increment, range_min, intensities, lidar, Twist, cmd_vel, create_timer, mona_lisa_approach.py, basics_sensor_data]
see: ["[[core-recipe-laserscan]]", "[[perception-rviz-sensors]]", "[[core-topic-pub-sub-py]]", "[[perception-python-deps]]"]
requires: [ros2-core]
version_notes:
  - "humble: field definitions and the two notes (discard values outside range_min/range_max; empty intensities when the device has none) are the message's own comments — https://github.com/ros2/common_interfaces/blob/humble/sensor_msgs/msg/LaserScan.msg (PERC-V01, PERC-V04)"
  - "course: the field is `ranges`, not `range` (PERC-V05); `len(msg.ranges) // 2` is the front only for a symmetric scan (PERC-V04)"
  - "course: the timer read `self.mona_lisa_distance` before the first scan (`None > 0.5` → TypeError, PERC-V02); a second `rclpy.shutdown()` in main raises RCLError on Humble, Jazzy and Lyrical — use rclpy.try_shutdown() — https://github.com/ros2/rcl/blob/humble/rcl/src/rcl/init.c (PERC-V03)"
---
# sensor_msgs/LaserScan and a stop-at-distance node

**TL;DR** A `LaserScan` is one planar sweep: `ranges[i]` is the distance at angle `angle_min + i * angle_increment` (radians, counterclockwise around +Z, 0 = forward along +X). Discard values outside `[range_min, range_max]`. The course node drives forward until the beam straight ahead reads 0.5 m.

## The message
`sensor_msgs/LaserScan` carries the distances a laser range finder or lidar measured in one sweep. Robots use it to build maps, localize themselves in them, avoid collisions and decide in real time. Main fields ([LaserScan.msg](https://github.com/ros2/common_interfaces/blob/humble/sensor_msgs/msg/LaserScan.msg)):

| Field | Meaning |
|---|---|
| `angle_min`, `angle_max` | first and last angle of the sweep [rad]: the angular range the sensor covers |
| `angle_increment` | angle between two consecutive measurements [rad] (angular resolution) |
| `range_min`, `range_max` | closest and farthest distance the sensor can detect [m] |
| `ranges` | the measured distances [m], one per angle of the range above (the most important field) |
| `intensities` | one intensity per range, device units; **empty** when the scanner gives none |

Values `< range_min` or `> range_max` must be discarded. Index of the beam at angle 0 (straight ahead): `round(-angle_min / angle_increment)`; it is `len(ranges) // 2` only when `angle_min == -angle_max` (geometry and sector code: [[core-recipe-laserscan]]).

## Example: approach a wall until 0.5 m (`mona_lisa_approach.py`)
Goal: the robot faces the Mona Lisa painting and approaches it until the laser reads **50 cm** straight ahead. Subscriber on the laser topic, publisher on `cmd_vel`, a log of the front distance, stop at 0.5 m. The robot is assumed to face the painting already.
```bash
cd ~/ros2_ws/src/
ros2 pkg create --build-type ament_python basics_sensor_data
cd ~/ros2_ws/
colcon build
source install/setup.bash
mkdir src/basics_sensor_data/rviz
touch src/basics_sensor_data/basics_sensor_data/mona_lisa_approach.py
chmod +x src/basics_sensor_data/basics_sensor_data/mona_lisa_approach.py
```
`ros2 run basics_sensor_data mona_lisa_approach` needs a `console_scripts` entry in `setup.py` (pattern in [[perception-python-deps]]).
```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist


class MonaLisaApproach(Node):

    def __init__(self) -> None:
        super().__init__('mona_lisa_approach')
        self.subscription = self.create_subscription(LaserScan, '/deepmind_robot1/laser_scan', self.laser_callback, 10)
        self.publisher = self.create_publisher(Twist, 'cmd_vel', 10)
        self.timer = self.create_timer(0.5, self.timer_callback)
        self.mona_lisa_distance = None

    def laser_callback(self, msg: LaserScan) -> None:
        """Callback function for laser scan data"""
        # Find index corresponding to the direction directly in front of the robot
        middle_index = len(msg.ranges) // 2
        self.mona_lisa_distance = msg.ranges[middle_index]

    def timer_callback(self) -> None:
        if self.mona_lisa_distance is None:  # PERC-V02: no scan received yet
            return
        # Check if the Mona Lisa distance is greater than 0.5
        if self.mona_lisa_distance > 0.5:
            self.move_forward()  # Move the robot forward
        else:
            self.stop_robot()  # Stop the robot
            rclpy.shutdown()

    def move_forward(self) -> None:
        """Move the robot forward"""
        print(f'MOVE FORWARD... Mona Lisa is {self.mona_lisa_distance:.2f} meters away')
        twist_msg = Twist()
        twist_msg.linear.x = 0.1
        self.publisher.publish(twist_msg)

    def stop_robot(self) -> None:
        """Stop the robot"""
        print(f'STOP... ')
        twist_msg = Twist()
        twist_msg.linear.x = 0.0
        self.publisher.publish(twist_msg)


def main(args=None) -> None:
    rclpy.init(args=args)
    mona_lisa_approach = MonaLisaApproach()
    rclpy.spin(mona_lisa_approach)
    mona_lisa_approach.destroy_node()
    rclpy.try_shutdown()  # PERC-V03: the timer already called rclpy.shutdown()


if __name__ == '__main__':
    main()
```
The subscription reads `/deepmind_robot1/laser_scan`; the publisher moves the robot through `/cmd_vel`. `middle_index` is the beam straight ahead, stored in `self.mona_lisa_distance`. The timer decides: forward at 0.1 m/s while the distance is above 0.5 m, then a zero `Twist` and the end of the program. Differences from the course: the `None` check (PERC-V02) and `try_shutdown()` (the course calls `rclpy.shutdown()` twice, PERC-V03).

Run: open RViz with the saved configuration ([[perception-rviz-sensors]]), turn the robot toward the painting with `ros2 run teleop_twist_keyboard teleop_twist_keyboard`, then:
```bash
cd ~/ros2_ws/
colcon build;source install/setup.bash
ros2 run basics_sensor_data mona_lisa_approach
```

## Pitfalls
- `TypeError: '>' not supported between instances of 'NoneType' and 'float'` → a timer fired before the first scan → return while the value is `None` (PERC-V02).
- `RCLError: failed to shutdown` at exit → `rclpy.shutdown()` called in a callback and again in `main()` → `rclpy.try_shutdown()` in `main()` (PERC-V03).
- Wrong "front" distance on a scanner whose angles are not symmetric → compute the index from `angle_min` and `angle_increment` (PERC-V04).
- `inf` (no return) is greater than 0.5, so the robot keeps going; a `nan` compares false and stops it. Filter with `math.isfinite` and the range limits ([[core-recipe-laserscan]]).
