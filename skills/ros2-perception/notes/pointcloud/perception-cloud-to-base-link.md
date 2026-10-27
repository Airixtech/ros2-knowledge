---
id: perception-cloud-to-base-link
type: reference
owner: equipo-ros2
updated: 2026-10-27
review_by: 2027-04-25
source: manual
confidentiality: internal
title: "Turn a PointCloud2 into points in base_link: TF lookup, quaternion to matrix, numpy parse, static TF workaround"
domain: perception
area: pointcloud
distro: humble
tested: false
audience: dev
summary: "Transform a depth cloud to base_link: lookup_transform, quaternion rotation matrix, per-point parse, do_transform_cloud + read_points_numpy, the static TF workaround."
tags: [PointCloud2, tf2_ros, Buffer, TransformListener, lookup_transform, spin_thread, quaternion, rotation matrix, tf2_sensor_msgs, do_transform_cloud, read_points_numpy, StaticTransformBroadcaster, tf2_echo, from_array]
see: ["[[perception-surface-detection]]", "[[perception-pointcloud2-msg]]", "[[core-tf-listener]]", "[[core-tf-broadcaster]]", "[[perception-pcl-python]]"]
requires: [ros2-core]
version_notes:
  - "humble: Python lookup_transform(..., timeout) waits in a sleep(0.02) loop on the calling thread, and TransformListener(buffer, node, spin_thread=False) is the default; same code on jazzy and lyrical — https://github.com/ros2/geometry2/blob/humble/tf2_ros_py/tf2_ros/buffer.py , https://github.com/ros2/geometry2/blob/humble/tf2_ros_py/tf2_ros/transform_listener.py (PERC-V18) [verify: cause of the course's lost transforms]"
  - "humble: `from tf2_sensor_msgs import do_transform_cloud` (Python) and sensor_msgs_py read_points_numpy exist; same on jazzy and lyrical — https://github.com/ros2/geometry2/blob/humble/tf2_sensor_msgs/tf2_sensor_msgs/__init__.py (PERC-V17)"
  - "course: the static transform holds only for the head tilt of the measurement (move_head.py 0.0 0.3 1) (PERC-V19)"
---
# PointCloud2 to points in base_link

**TL;DR** Look up `base_link ← cloud frame`, rotate every point by the transform's quaternion and add the translation; then the heights and distances of the cloud mean something for the robot. The course does it point by point in Python; the official helpers do it in one call. Its static TF "fix" is valid for one head pose only.

## The course's conversion (`from_ros_msg()` of [[perception-surface-detection]])
```python
transform = self.tf_buffer.lookup_transform('deepmind_robot1_base_link', msg.header.frame_id, rclpy.time.Time(), timeout=rclpy.time.Duration(seconds=1.0))
translation = np.array([transform.transform.translation.x, transform.transform.translation.y, transform.transform.translation.z])
rotation_quaternion = np.array([transform.transform.rotation.x, transform.transform.rotation.y, transform.transform.rotation.z, transform.transform.rotation.w])
# Convert quaternion to rotation matrix
rotation_matrix = self.quaternion_to_rotation_matrix(rotation_quaternion)
```
- The lookup brings the cloud into the common frame `deepmind_robot1_base_link`, so later steps reason in the robot's frame. `rclpy.time.Time()` = the latest available transform; `rclpy.time.Duration` works because `rclpy.time` imports `Duration` (its home module is `rclpy.duration`).
- The node keeps a `tf2_ros.Buffer()` and a `tf2_ros.TransformListener(self.tf_buffer, self)`; listener basics: [[core-tf-listener]].
- Parsing: for each of `len(msg.data) // point_step` points, the bytes at offsets 0, 4, 8 are read with `np.frombuffer(..., dtype=np.float32)`, rotated (`np.dot(rotation_matrix, point)`) and translated: the cloud's raw binary data becomes NumPy points in `base_link`.
- `data = np.array(points, dtype=np.float32)` (one row per point, columns x, y, z), an `assert` that there are 3 fields, then `cloud = pcl.PointCloud(); cloud.from_array(data)`: the PCL cloud for filtering and segmentation.

## Official helpers (same result, one call each)
```python
from sensor_msgs_py import point_cloud2
from tf2_sensor_msgs import do_transform_cloud

transform = self.tf_buffer.lookup_transform('deepmind_robot1_base_link', msg.header.frame_id, rclpy.time.Time())
cloud_base = do_transform_cloud(msg, transform)            # PointCloud2 with x, y, z in base_link
points = point_cloud2.read_points_numpy(cloud_base, field_names=('x', 'y', 'z'), skip_nans=True)
cloud = pcl.PointCloud()
cloud.from_array(points.astype(np.float32))                # python-pcl wants a float32 (N, 3) array
```
Both exist in Humble (PERC-V17); add `tf2_sensor_msgs` and `sensor_msgs_py` to `package.xml` `[verify]` (not run).

## The course's static TF workaround
The course saw transforms "disappear" and the program fail without them; it then publishes a fixed transform from `deepmind_robot1_base_link` to `deepmind_robot1_camera_depth_optical_frame`, measured once. Tilt the head as the course does, then read the transform:
```bash
ros2 run deepmind_bot_trajectory_sender move_head.py 0.0 0.3 1
ros2 run tf2_ros tf2_echo deepmind_robot1_base_link deepmind_robot1_camera_depth_optical_frame
```
```text
At time 911.423000000
- Translation: [0.301, 0.013, 1.083]
- Rotation: in Quaternion [0.805, -0.000, 0.593, 0.000]
- Rotation: in RPY (radian) [-3.142, -1.271, -0.001]
- Rotation: in RPY (degree) [-180.000, -72.811, -0.043]
- Matrix:
  0.296 -0.001  0.955  0.301
 -0.000 -1.000 -0.001  0.013
  0.955 -0.000 -0.296  1.083
  0.000  0.000  0.000  1.000
```
`static_transform_publisher.py` (in `bench_detector`):
```bash
cd ~/ros2_ws/src/bench_detector/bench_detector
touch static_transform_publisher.py
chmod +x *.py
cd ~/ros2_ws/
```
```python
import rclpy
from geometry_msgs.msg import TransformStamped
import tf2_ros


class StaticTransformPublisher:

    def __init__(self) -> None:
        self.node = rclpy.create_node('static_transform_publisher_node')
        self.broadcaster = tf2_ros.StaticTransformBroadcaster(self.node)

    def publish_static_transform(self) -> None:
        static_transform_stamped = TransformStamped()
        static_transform_stamped.header.stamp = self.node.get_clock().now().to_msg()
        static_transform_stamped.header.frame_id = 'deepmind_robot1_base_link'
        static_transform_stamped.child_frame_id = 'deepmind_robot1_camera_depth_optical_frame'
        static_transform_stamped.transform.translation.x = 0.301
        static_transform_stamped.transform.translation.y = 0.013
        static_transform_stamped.transform.translation.z = 1.083
        static_transform_stamped.transform.rotation.x = 0.805
        static_transform_stamped.transform.rotation.y = 0.0
        static_transform_stamped.transform.rotation.z = 0.593
        static_transform_stamped.transform.rotation.w = 0.0

        # Publish the static transform
        self.broadcaster.sendTransform(static_transform_stamped)

    def spin(self) -> None:
        rclpy.spin(self.node)
        self.node.destroy_node()
        rclpy.shutdown()


def main(args=None) -> None:
    rclpy.init(args=args)
    static_transform_publisher = StaticTransformPublisher()
    static_transform_publisher.publish_static_transform()
    static_transform_publisher.spin()


if __name__ == '__main__':
    main()
```
Run it before the detection node: `ros2 run bench_detector static_transform_publisher`. Static broadcasters in Python: [[core-tf-broadcaster]] (more in the ros2-tf skill).

## Pitfalls
- The fixed transform is right only while the head keeps the tilt it was measured with (`0.0 0.3 1`): the camera moves with the head joints, so another tilt puts the points in the wrong place (PERC-V19).
- A lookup with `timeout` inside a callback waits on the executor thread, and the default `TransformListener` (`spin_thread=False`) cannot receive TF while it waits; `tf2_ros.TransformListener(self.tf_buffer, self, spin_thread=True)` gives the listener its own thread (PERC-V18). The real cause of the course's lost transforms was not shown `[verify]`.
- The point-by-point loop runs 307,200 Python iterations per message; the helpers above work on whole NumPy arrays (PERC-V17).
