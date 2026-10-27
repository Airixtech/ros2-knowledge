---
id: perception-surface-detection
type: reference
owner: equipo-ros2
updated: 2026-10-27
review_by: 2027-04-25
source: manual
confidentiality: internal
title: "Surface detection node: benches as plane clusters, cube markers and DetectedSurfaces messages"
domain: perception
area: pointcloud
distro: humble
tested: false
audience: dev
summary: "surface_detection.py: depth cloud to base_link, height filter, RANSAC plane, Euclidean clusters, green CUBE MarkerArray, DetectedSurfaces on surface_detected."
tags: [surface detection, bench, PointCloud2, python-pcl, RANSAC, EuclideanClusterExtraction, MarkerArray, Marker.CUBE, bench_markers, surface_detected, DetectedSurfaces, custom_msgs, surface_detection.py, bench_detector]
see: ["[[perception-cloud-to-base-link]]", "[[perception-pcl-plane-clusters]]", "[[perception-object-detection-pcl]]", "[[perception-custom-msgs]]", "[[perception-pcl-python]]"]
requires: [ros2-core]
version_notes:
  - "humble only for `import pcl` (Ubuntu 22.04 python3-pcl); no package on jazzy/lyrical (PERC-V16)"
  - "course: DetectedSurfaces.height carries the x extent of the cluster (logged as Length) and width the y extent (PERC-V20)"
  - "humble: tf2_ros re-exports TransformException and ConnectivityException from tf2 — https://github.com/ros2/geometry2/blob/humble/tf2_py/src/tf2_py.cpp (PERC-V21)"
  - "humble: Marker CUBE=1, SPHERE=2, ADD=0, DELETEALL=3 — https://github.com/ros2/common_interfaces/blob/humble/visualization_msgs/msg/Marker.msg"
---
# Surface detection node (benches)

**TL;DR** Every depth cloud: transform to `base_link`, keep the 0.35–0.4 m band within 2.15 m, fit the plane, cluster it, and publish each cluster as a translucent green cube (`/bench_markers`) and as a `DetectedSurfaces` message (`/surface_detected`). Steps explained in [[perception-pcl-plane-clusters]] and [[perception-cloud-to-base-link]].

## Package
```bash
cd ~/ros2_ws/src/
ros2 pkg create --build-type ament_python bench_detector
cd ~/ros2_ws/
colcon build
source install/setup.bash
cd src/bench_detector/bench_detector
touch surface_detection.py
chmod +x *.py
cd ~/ros2_ws/
```
The node imports `DetectedSurfaces` from a `custom_msgs` package, which the course copies into `~/ros2_ws/src` (definitions: [[perception-custom-msgs]]). `import pcl` needs python-pcl ([[perception-pcl-python]]).

## `surface_detection.py`
```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2
from visualization_msgs.msg import Marker, MarkerArray
import pcl
import numpy as np
import tf2_ros
from tf2_ros import TransformException, ConnectivityException
from custom_msgs.msg import DetectedSurfaces
from typing import List, Tuple, Union


class SurfaceDetection(Node):

    def __init__(self) -> None:
        super().__init__('surface_detection_node')
        self.pc_sub = self.create_subscription(PointCloud2, '/deepmind_robot1_depth_sensor/points', self.callback, 10)
        self.surface_pub = self.create_publisher(MarkerArray, 'bench_markers', 10)
        self.surface_detected_pub = self.create_publisher(DetectedSurfaces, 'surface_detected', 10)
        self.marker_id = 0
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

    def callback(self, msg: PointCloud2) -> None:
        try:
            # Convert PointCloud2 msg to pcl point cloud
            cloud = self.from_ros_msg(msg)
            # Filter points within a certain x-distance and height range
            filtered_cloud = self.filter_cloud(cloud, max_x_dist=2.15, min_height=0.35, max_height=0.4)
            # Segmentation: Plane extraction
            plane_indices, plane_coefficients, plane_cloud = self.extract_plane(filtered_cloud)
            # Clustering: Identify clusters corresponding to benches
            bench_clusters, surface_centroids, cluster_dimensions = self.extract_clusters(plane_cloud)
            # Publish the detected bench clusters as markers
            self.pub_surface_marker(surface_centroids, cluster_dimensions)
            # Publish detected surface information
            self.pub_surface_detected(surface_centroids, cluster_dimensions)
        except (TransformException, ConnectivityException) as e:
            self.get_logger().error(f"Transform lookup failed: {e}")
        except Exception as e:
            self.get_logger().error(f"Error in callback: {e}")

    def from_ros_msg(self, msg: PointCloud2) -> Union[pcl.PointCloud, None]:
        """Converts a ROS PointCloud2 message to a PCL point cloud"""
        try:
            transform = self.tf_buffer.lookup_transform('deepmind_robot1_base_link', msg.header.frame_id, rclpy.time.Time(), timeout=rclpy.time.Duration(seconds=1.0))
            translation = np.array([transform.transform.translation.x, transform.transform.translation.y, transform.transform.translation.z])
            rotation_quaternion = np.array([transform.transform.rotation.x, transform.transform.rotation.y, transform.transform.rotation.z, transform.transform.rotation.w])
            # Convert quaternion to rotation matrix
            rotation_matrix = self.quaternion_to_rotation_matrix(rotation_quaternion)

            # Convert PointCloud2 msg to numpy array
            point_step = msg.point_step
            num_points = len(msg.data) // point_step
            points = []
            for i in range(num_points):
                start_index = i * point_step
                x_bytes = msg.data[start_index:start_index + 4]
                y_bytes = msg.data[start_index + 4:start_index + 8]
                z_bytes = msg.data[start_index + 8:start_index + 12]
                x = np.frombuffer(x_bytes, dtype=np.float32)[0]
                y = np.frombuffer(y_bytes, dtype=np.float32)[0]
                z = np.frombuffer(z_bytes, dtype=np.float32)[0]
                point = np.array([x, y, z])
                # Apply the rotation to the point
                rotated_point = np.dot(rotation_matrix, point)
                # Apply the translation to the rotated point to get its position relative to the base_link frame
                relative_point = rotated_point + translation
                points.append(relative_point)

            data = np.array(points, dtype=np.float32)
            assert data.shape[1] == 3, "Number of fields must be 3"
            cloud = pcl.PointCloud()
            cloud.from_array(data)
            return cloud

        except (TransformException, ConnectivityException) as e:
            self.get_logger().error(f"Transform lookup failed: {e}")
        except Exception as e:
            self.get_logger().error(f"Error in from_ros_msg: {e}")
        return None

    def quaternion_to_rotation_matrix(self, q: np.ndarray) -> np.ndarray:
        """Converts a quaternion to a rotation matrix"""
        x, y, z, w = q
        rotation_matrix = np.array([
            [1 - 2*y**2 - 2*z**2, 2*x*y - 2*z*w, 2*x*z + 2*y*w],
            [2*x*y + 2*z*w, 1 - 2*x**2 - 2*z**2, 2*y*z - 2*x*w],
            [2*x*z - 2*y*w, 2*y*z + 2*x*w, 1 - 2*x**2 - 2*y**2]
        ])
        return rotation_matrix

    def filter_cloud(self, cloud: pcl.PointCloud, max_x_dist: float, min_height: float, max_height: float) -> Union[pcl.PointCloud, None]:
        """Filter cloud"""
        try:
            indices = []
            for i in range(cloud.size):
                point = cloud[i]
                if (point[0] <= max_x_dist) and (min_height <= point[2] <= max_height):
                    indices.append(i)
            filtered_cloud = cloud.extract(indices)
            return filtered_cloud
        except Exception as e:
            self.get_logger().error(f"Error in filter_cloud: {e}")
            return None

    def extract_plane(self, cloud: pcl.PointCloud) -> Tuple[List[int], List[float], pcl.PointCloud]:
        """Segmentation: Extracts a plane from the point cloud."""
        seg = cloud.make_segmenter()
        seg.set_model_type(pcl.SACMODEL_PLANE)
        seg.set_method_type(pcl.SAC_RANSAC)
        seg.set_distance_threshold(0.01)
        indices, coefficients = seg.segment()
        # Extract points belonging to the plane
        plane_cloud = cloud.extract(indices)
        self.get_logger().info(f"Number of inliers: {len(indices)}")
        self.get_logger().info(f"Plane coefficients: {coefficients}")
        return indices, coefficients, plane_cloud

    def extract_clusters(self, cloud: pcl.PointCloud) -> Tuple[List[pcl.PointCloud], List[List[float]], List[List[float]]]:
        """Extracts clusters corresponding to benches from the point cloud"""
        tree = cloud.make_kdtree()
        ec = cloud.make_EuclideanClusterExtraction()
        ec.set_ClusterTolerance(0.02)
        ec.set_MinClusterSize(100)
        ec.set_MaxClusterSize(80000)
        ec.set_SearchMethod(tree)

        # Extract clusters
        cluster_indices = ec.Extract()

        # Initialize lists to store bench clusters, centroids, and dimensions
        bench_clusters = []
        cluster_centroids = []
        cluster_dimensions = []

        # Process each cluster
        for idx, indices in enumerate(cluster_indices):
            self.get_logger().info(f"Processing cluster {idx + 1}...")
            # Extract points belonging to the cluster
            cluster = cloud.extract(indices)
            # Calculate centroid
            centroid = np.mean(cluster, axis=0)
            # Computes the min and max coordinates along each axis
            min_coords = np.min(cluster, axis=0)
            max_coords = np.max(cluster, axis=0)
            dimensions = max_coords - min_coords
            # Append clusters, centroids and dimensions to lists
            bench_clusters.append(cluster)
            cluster_centroids.append(centroid.tolist())
            cluster_dimensions.append(dimensions.tolist())
            # Log cluster information
            num_points = len(indices)
            self.get_logger().info(f"Cluster {idx + 1} has {num_points} points.")
            self.get_logger().info(f"Centroid of cluster {idx + 1}: {centroid}")
            self.get_logger().info(f"Dimensions of cluster {idx + 1} --> Length: {dimensions[0]}, Width: {dimensions[1]}")

        # Check if any clusters have been extracted
        if not bench_clusters:
            self.get_logger().warning("No bench clusters extracted...")

        # Return the filtered bench clusters, centroids and cluster dimensions
        return bench_clusters, cluster_centroids, cluster_dimensions

    def pub_surface_marker(self, surface_centroids: List[List[float]], surface_dimensions: List[List[float]]) -> None:
        """Publishes the detected bench plane as cube markers"""
        marker_array = MarkerArray()
        surface_thickness = 0.05
        for idx, (centroid, dimensions) in enumerate(zip(surface_centroids, surface_dimensions)):
            length = float(dimensions[0])
            width = float(dimensions[1])
            cube_marker = Marker()
            cube_marker.header.frame_id = "deepmind_robot1_base_link"
            cube_marker.id = idx
            cube_marker.type = Marker.CUBE
            cube_marker.action = Marker.ADD
            cube_marker.pose.position.x = centroid[0]
            cube_marker.pose.position.y = centroid[1]
            cube_marker.pose.position.z = centroid[2] - surface_thickness / 2
            cube_marker.pose.orientation.w = 1.0
            cube_marker.scale.x = length
            cube_marker.scale.y = width
            cube_marker.scale.z = surface_thickness
            cube_marker.color.r = 0.0
            cube_marker.color.g = 1.0
            cube_marker.color.b = 0.0
            cube_marker.color.a = 0.5
            marker_array.markers.append(cube_marker)

        if marker_array.markers:
            self.get_logger().info(f"Published {len(marker_array.markers)} bench plane markers")
            self.surface_pub.publish(marker_array)
        else:
            self.get_logger().warning("No bench plane markers to publish.")

    def pub_surface_detected(self, centroids: List[List[float]], dimensions: List[List[float]]) -> None:
        """Publishes the detected surface information"""
        for idx, (centroid, dimension) in enumerate(zip(centroids, dimensions)):
            surface_msg = DetectedSurfaces()
            surface_msg.surface_id = idx
            surface_msg.position.x = centroid[0]
            surface_msg.position.y = centroid[1]
            surface_msg.position.z = centroid[2]
            surface_msg.height = dimension[0]
            surface_msg.width = dimension[1]
            self.surface_detected_pub.publish(surface_msg)


def main(args=None) -> None:
    rclpy.init(args=args)
    surface_detection = SurfaceDetection()
    rclpy.spin(surface_detection)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```
- Subscription to `/deepmind_robot1_depth_sensor/points`; publishers of a `MarkerArray` on `/bench_markers` and of `DetectedSurfaces` on `/surface_detected`.
- `pub_surface_marker()`: one cube `Marker` per bench in one `MarkerArray` (several benches at once), as long and wide as the plane cluster, 5 cm thick for visibility, placed at the centroid (its top at the surface height), green with alpha 0.5.
- `pub_surface_detected()`: one `DetectedSurfaces` message per surface with id, centroid position, `height` = the cluster's x extent and `width` = its y extent (PERC-V20), for other nodes to use; the topic is `/surface_detected` (the course text says `/surface_detected_pub`, the publisher's attribute name, PERC-V05).
- Every error is caught and logged in `callback()`, so a failed transform or an empty cloud only logs and waits for the next message.

## Launch and test
Open RViz ([[perception-rviz-sensors]]), tilt the head (`move_head.py 0.0 0.3 1`) and start the static transform ([[perception-cloud-to-base-link]]), face a bench with teleop, then:
```bash
cd ~/ros2_ws/
colcon build;source install/setup.bash
ros2 run bench_detector static_transform_publisher
```
```bash
cd ~/ros2_ws/
colcon build;source install/setup.bash
ros2 run bench_detector surface_detection
```
Add a `MarkerArray` display on `/bench_markers`: the bench's flat top appears as a green marker. Its data:
```bash
ros2 topic echo /surface_detected
```
```yaml
surface_id: 0
position:
  x: 1.674404263496399
  y: -0.4665426015853882
  z: 0.39481601119041443
height: 0.4992251396179199
width: 0.5274150967597961
```

## Pitfalls
- No markers and "Transform lookup failed" → no TF between the cloud frame and `deepmind_robot1_base_link` ([[perception-cloud-to-base-link]]).
- Markers stay in RViz after a bench leaves the view: the node never deletes old ids; send `Marker.DELETEALL` first when the count drops.
- `main()` has no `try/except` and no `destroy_node()`: Ctrl + C ends with a `KeyboardInterrupt` traceback; the clean pattern is in [[core-node-skeleton]].
