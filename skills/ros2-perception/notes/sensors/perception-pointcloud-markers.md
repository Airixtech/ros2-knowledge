---
id: perception-pointcloud-markers
type: reference
owner: equipo-ros2
updated: 2026-10-27
review_by: 2027-04-25
source: manual
confidentiality: internal
title: "Sample points from a PointCloud2 with struct.unpack_from and show them as a MarkerArray of spheres"
domain: perception
area: sensors
distro: humble
tested: false
audience: dev
summary: "Read float32 x, y, z from PointCloud2 bytes with struct.unpack_from, sample 50 points, publish red sphere Markers in a MarkerArray."
tags: [PointCloud2, struct.unpack_from, float32, MarkerArray, Marker, Marker.SPHERE, visualization_marker_array, geometry_msgs/Point, point_cloud_marker.py, RViz2]
see: ["[[perception-pointcloud2-msg]]", "[[perception-rviz-sensors]]", "[[core-debug-tools]]"]
requires: [ros2-core]
version_notes:
  - "course: the sampling step was len(data) // 50 bytes, aligned to point_step only by chance (9,830,400 / 50 = 6,144 points × 32 B); fixed to a whole number of points (PERC-V07) — https://github.com/ros2/common_interfaces/blob/humble/sensor_msgs/msg/PointCloud2.msg"
---
# PointCloud2 points as RViz sphere markers

**TL;DR** Read a float32 at byte `i` with `struct.unpack_from('f', data, i)[0]`. Start every read at a multiple of `point_step`, add the field offsets (x 0, y 4, z 8 here), and publish one `Marker` per point inside a `MarkerArray`.

## Example: 50 red spheres (`point_cloud_marker.py`)
Subscribe to `/deepmind_robot1_depth_sensor/points`, publish a `MarkerArray` (several markers for RViz in one message) on `visualization_marker_array`, extract **50 points** with `extract_points()`, and turn them into **red spheres** with `create_markers()`.
```bash
cd ~/ros2_ws/
touch src/basics_sensor_data/basics_sensor_data/point_cloud_marker.py
chmod +x src/basics_sensor_data/basics_sensor_data/point_cloud_marker.py
```
```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2
from visualization_msgs.msg import Marker, MarkerArray
from geometry_msgs.msg import Point
import struct
from typing import List


class PointCloudMarker(Node):

    def __init__(self) -> None:
        super().__init__('point_cloud_marker')
        self.subscription = self.create_subscription(PointCloud2, '/deepmind_robot1_depth_sensor/points', self.point_cloud_callback, 10)
        self.marker_publisher = self.create_publisher(MarkerArray, 'visualization_marker_array', 10)

    def point_cloud_callback(self, msg: PointCloud2) -> None:
        # Extract points from the point cloud message uniformly
        points = self.extract_points(msg)
        # Create markers for the extracted points
        marker_array = self.create_markers(msg, points)
        # Publish the marker array
        self.marker_publisher.publish(marker_array)

    def extract_points(self, msg: PointCloud2) -> List[Point]:
        """Extract points uniformly from the point cloud message"""
        points = []
        num_points = 50
        # Divide the data into 50 equal parts, each a whole number of points (PERC-V07)
        step_size = (msg.width * msg.height // num_points) * msg.point_step
        for i in range(0, len(msg.data), step_size):
            if len(points) >= num_points:
                break
            index = i
            x = self.read_float32(msg.data, index)
            y = self.read_float32(msg.data, index + 4)
            z = self.read_float32(msg.data, index + 8)
            p = Point()
            p.x, p.y, p.z = x, y, z
            points.append(p)
        return points

    def create_markers(self, msg: PointCloud2, points: List[Point]) -> MarkerArray:
        """Create markers for the extracted points"""
        marker_array = MarkerArray()
        for idx, point in enumerate(points):
            marker = Marker()
            marker.header = msg.header
            marker.type = Marker.SPHERE
            marker.action = Marker.ADD
            marker.scale.x = 0.1
            marker.scale.y = 0.1
            marker.scale.z = 0.1
            marker.color.r = 1.0
            marker.color.a = 1.0
            marker.pose.position = point
            marker.id = idx
            marker_array.markers.append(marker)
        return marker_array

    def read_float32(self, data: bytes, index: int) -> float:
        """Helper function to read float32 from byte array"""
        return struct.unpack_from('f', data, index)[0]


def main(args=None) -> None:
    rclpy.init(args=args)
    point_cloud_marker = PointCloudMarker()
    rclpy.spin(point_cloud_marker)
    point_cloud_marker.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```
- The subscription receives the cloud on `/deepmind_robot1_depth_sensor/points`; the publisher sends the markers on `/visualization_marker_array`. `point_cloud_callback()` is the main function: extract, build markers, publish.
- `read_float32()` extracts a 32-bit float at an index with the `struct` module. `struct.unpack_from()` takes the format string (`'f'` = float32), the bytes object (`data`) and the start offset (`index`); it returns a tuple, hence `[0]`.
- `extract_points()` walks the `data` array in `num_points` equal parts and makes a `Point` from the x, y, z bytes of each. The course used `step_size = len(msg.data) // num_points` (comment: "Divide the data into 50 equal parts"): that byte step is a multiple of `point_step` only for some cloud sizes (PERC-V07).
- `create_markers()` gives each `Marker` the cloud's header (so RViz places it in the sensor frame), sphere type, 0.1 m scale, red opaque color, the point as position and a unique `id`, then adds it to the `MarkerArray`.

Run near a 3D object (a bench): open RViz ([[perception-rviz-sensors]]), drive there with teleop, tilt the head down (course tool, [[perception-learn-start-here]]), then:
```bash
cd ~/ros2_ws/
colcon build;source install/setup.bash
ros2 run basics_sensor_data point_cloud_marker
```
Add a `MarkerArray` display on `/visualization_marker_array`: the 50 points appear as 3D spheres.

## Pitfalls
- Reads that start between two points give garbage values: the step must be `k * point_step` (PERC-V07).
- `'f'` uses the machine's byte order; for a cloud with `is_bigendian: true` use `'>f'`, or let `sensor_msgs_py.point_cloud2` handle it ([[perception-pointcloud2-msg]]).
- Markers with the same `id` overwrite each other; give each one its own id.
