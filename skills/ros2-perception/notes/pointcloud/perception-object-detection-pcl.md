---
id: perception-object-detection-pcl
type: reference
owner: equipo-ros2
updated: 2026-10-27
review_by: 2027-04-25
source: manual
confidentiality: internal
title: "Objects on a surface from a point cloud: two height bands, two clusterings, object markers and messages"
domain: perception
area: pointcloud
distro: humble
tested: false
audience: dev
summary: "object_detection.py: plane band 0.35-0.4 m plus object band 0.4-1.2 m, two clusterings, red CUBE markers on object_markers, DetectedObjects messages."
tags: [object detection, point cloud, objects on surface, python-pcl, EuclideanClusterExtraction, MarkerArray, object_markers, object_detected, DetectedObjects, cluster_type, object_detection.py, bench_detector, spawn_cube]
see: ["[[perception-surface-detection]]", "[[perception-pcl-plane-clusters]]", "[[perception-custom-msgs]]", "[[perception-yolo-object-detection]]"]
requires: [ros2-core]
version_notes:
  - "humble only for `import pcl` (Ubuntu 22.04 python3-pcl) (PERC-V16)"
  - "course: DetectedObjects height/width/thickness carry the x/y/z extents of the cluster (PERC-V20)"
---
# Objects on a surface from a point cloud

**TL;DR** Same node as the surface detector plus a second height band (0.4–1.2 m) above the bench: cluster the plane band for the benches and the upper band for the objects, then publish green surface cubes and red object cubes with their messages. `object_detection.py` is `surface_detection.py` ([[perception-surface-detection]]) with the changes below.

## Spawn an object and create the script
```bash
ros2 launch perception_ros2 spawn_cube.launch.py
```
(course simulation: a cube on a bench, [[perception-learn-start-here]])
```bash
cd ~/ros2_ws/src/bench_detector/bench_detector
touch object_detection.py
chmod +x *.py
cd ~/ros2_ws/
```

## `object_detection.py`: every change against `surface_detection.py`
Unchanged: `from_ros_msg()`, `quaternion_to_rotation_matrix()`, `filter_cloud()`, `pub_surface_marker()`, `pub_surface_detected()` and the body of `extract_plane()`.
1. Import: `from custom_msgs.msg import DetectedSurfaces, DetectedObjects`; class `ObjectDetection`; `main()` creates `object_detection = ObjectDetection()`.
2. `__init__`: node name and two more publishers:
```python
    def __init__(self) -> None:
        super().__init__('object_detection_node')
        self.pc_sub = self.create_subscription(PointCloud2, '/deepmind_robot1_depth_sensor/points', self.callback, 10)
        self.surface_pub = self.create_publisher(MarkerArray, 'bench_markers', 10)
        self.surface_detected_pub = self.create_publisher(DetectedSurfaces, 'surface_detected', 10)
        self.objects_pub = self.create_publisher(MarkerArray, 'object_markers', 10)
        self.object_detected_pub = self.create_publisher(DetectedObjects, 'object_detected', 10)
        self.marker_id = 0
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)
```
3. `callback()`: two filters, two clusterings, four publications (the `except` part is unchanged):
```python
    def callback(self, msg: PointCloud2) -> None:
        try:
            # Convert PointCloud2 msg to pcl point cloud
            cloud = self.from_ros_msg(msg)
            # Filtered cloud for surface detection
            filtered_cloud_plane = self.filter_cloud(cloud, max_x_dist=2.15, min_height=0.35, max_height=0.4)
            # Filtered cloud for object detection
            filtered_cloud_objects = self.filter_cloud(cloud, max_x_dist=2.15, min_height=0.4, max_height=1.2)
            # Segmentation: Plane extraction
            plane_indices, plane_coefficients, plane_cloud = self.extract_plane(filtered_cloud_plane)
            # Clustering: Identify clusters corresponding to benches surfaces
            bench_clusters, surface_centroids, surface_dimensions = self.extract_clusters(plane_cloud, "Bench Surface")
            # Clustering: Identify clusters corresponding to objects placed on top of benches
            object_clusters, object_centroids, object_dimensions = self.extract_clusters(filtered_cloud_objects, "Object")
            # Publish the detected bench surface clusters as markers
            self.pub_surface_marker(surface_centroids, surface_dimensions)
            # Publish the detected object clusters as markers
            self.pub_object_marker(object_centroids, object_dimensions)
            # Publish detected surface information
            self.pub_surface_detected(surface_centroids, surface_dimensions)
            # Publish detected object information
            self.pub_object_detected(object_centroids, object_dimensions)
        except (TransformException, ConnectivityException) as e:
            self.get_logger().error(f"Transform lookup failed: {e}")
        except Exception as e:
            self.get_logger().error(f"Error in callback: {e}")
```
4. `extract_plane()` type hint: `-> Tuple[np.ndarray, np.ndarray, pcl.PointCloud]`.
5. `extract_clusters(self, cloud, cluster_type: str)`: the same clustering, with the cluster type in the logs:
```python
    def extract_clusters(self, cloud: pcl.PointCloud, cluster_type: str) -> Tuple[List[pcl.PointCloud], List[List[float]], List[List[float]]]:
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
            self.get_logger().info(f"Processing {cluster_type} cluster {idx + 1}...")
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
            self.get_logger().info(f"{cluster_type} cluster {idx + 1} has {num_points} points.")
            self.get_logger().info(f"Centroid of {cluster_type} cluster {idx + 1}: {centroid}")
            self.get_logger().info(f"Dimensions of {cluster_type} cluster {idx + 1}: {dimensions}")

        # Check if any clusters have been extracted
        if not bench_clusters:
            self.get_logger().warning(f"No {cluster_type} clusters extracted...")

        # Return the filtered bench clusters, centroids and cluster dimensions
        return bench_clusters, cluster_centroids, cluster_dimensions
```
6. Two new methods:
```python
    def pub_object_marker(self, object_centroids: List[List[float]], object_dimensions: List[List[float]]) -> None:
        """Publishes objects on flat surfaces as markers"""
        marker_array = MarkerArray()
        offset_x = 0.05
        for idx, (centroid, dimensions) in enumerate(zip(object_centroids, object_dimensions)):
            marker = Marker()
            marker.header.frame_id = "deepmind_robot1_base_link"
            marker.id = idx
            marker.type = Marker.CUBE
            marker.action = Marker.ADD
            marker.pose.position.x = float(centroid[0]) + offset_x
            marker.pose.position.y = float(centroid[1])
            marker.pose.position.z = float(centroid[2])
            marker.pose.orientation.w = 1.0
            marker.scale.x = dimensions[0]
            marker.scale.y = dimensions[1]
            marker.scale.z = dimensions[2]
            marker.color.r = 1.0
            marker.color.g = 0.0
            marker.color.b = 0.0
            marker.color.a = 0.5
            marker_array.markers.append(marker)

        if marker_array.markers:
            self.get_logger().info(f"Published {len(marker_array.markers)} objects on flat surface markers!")
            self.objects_pub.publish(marker_array)
        else:
            self.get_logger().warning("No objects on flat surface markers to publish.")

    def pub_object_detected(self, centroids: List[List[float]], dimensions: List[List[float]]) -> None:
        """Publishes the detected surface information"""
        for idx, (centroid, dimension) in enumerate(zip(centroids, dimensions)):
            object_msg = DetectedObjects()
            object_msg.object_id = idx
            object_msg.position.x = centroid[0]
            object_msg.position.y = centroid[1]
            object_msg.position.z = centroid[2]
            object_msg.height = dimension[0]
            object_msg.width = dimension[1]
            object_msg.thickness = dimension[2]
            self.object_detected_pub.publish(object_msg)
```
`filtered_cloud_plane` feeds the surface detection, `filtered_cloud_objects` the objects on top. Object markers are red cubes the size of the cluster, shifted 5 cm along x (`offset_x`) for visualization. `DetectedObjects` carries id, position and the three extents ([[perception-custom-msgs]]), one message per object on `/object_detected` (the course text names the publisher attribute `object_detected_pub` as the topic, PERC-V05).

## Launch and test
Tilt the head (`move_head.py 0.0 0.3 1`), spawn the cube if not done, drive to the bench with the green cube, start the static transform and the node ([[perception-surface-detection]], [[perception-cloud-to-base-link]]):
```bash
cd ~/ros2_ws/
colcon build;source install/setup.bash
ros2 run bench_detector object_detection
```
Add **two** `MarkerArray` displays (`/bench_markers`, `/object_markers`): the bench top is green, the object on it red.
```bash
ros2 topic echo /surface_detected
```
```yaml
surface_id: 0
position:
  x: 1.607060194015503
  y: -0.060517508536577225
  z: 0.3951207101345062
height: 0.5066673755645752
width: 1.3335667848587036
```
```bash
ros2 topic echo /object_detected
```
```yaml
object_id: 0
position:
  x: 1.5884416103363037
  y: 0.05769560858607292
  z: 0.5241749882698059
height: 0.1984626054763794
width: 0.20536842942237854
thickness: 0.1954697072505951
```
A ~20 cm cube: the three extents are about 0.2 m.

## Pitfalls
- The object band starts right above the plane band (0.4 m): a bench at another height needs both bands moved together.
- Anything in the band counts as an object (a person's hand, a backrest); filter clusters by size, or check that the cluster's centroid lies above a detected surface.
- One `DetectedObjects` message per object and frame, ids restart at 0 every frame: ids are not tracked identities.
