---
id: gazebo-sensors-depth-wideangle
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "Point cloud from a 2-D gpu_lidar, wide-angle camera, bridging and RViz QoS"
domain: gazebo
area: sensors
distro: jazzy
tested: false
audience: dev
summary: "gpu_lidar with vertical samples publishing <topic>/points as PointCloud2; wideanglecamera lens and 2π FOV; camera_info; RViz2 QoS."
tags: [gpu_lidar, vertical, point cloud, points, PointCloudPacked, PointCloud2, wideanglecamera, lens, custom_function, horizontal_fov, camera_info, Image, rviz2, qos]
see: ["[[gazebo-sensors-lidar]]", "[[gazebo-sensors-camera]]", "[[gazebo-ros-gz-bridge]]", "[[gazebo-learn-unit6-sensors]]", "[[core-perception-basics]]"]
requires: [ros2-core, ros2-urdf]
version_notes:
  - "jazzy: a gpu_lidar publishes LaserScan on <topic> and PointCloudPacked on <topic>/points (same in Fortress) — https://github.com/gazebosim/gz-sensors/blob/gz-sensors8/src/GpuLidarSensor.cc (GZ-V38)"
  - "jazzy: camera_info goes to the parent of the image topic + /camera_info — https://github.com/gazebosim/gz-sensors/blob/gz-sensors8/src/CameraSensor.cc (GZ-V05)"
  - "jazzy: wideanglecamera and its <lens> elements — https://github.com/gazebosim/gz-sensors/blob/gz-sensors8/src/WideAngleCameraSensor.cc (GZ-V39)"
---
# Point cloud from a 2-D gpu_lidar, wide-angle camera, bridging and RViz QoS

**TL;DR** Give a `gpu_lidar` a `<vertical>` row as well and it becomes a small 3-D scanner: besides the scan on `<topic>` it publishes a point cloud on `<topic>/points`. A `wideanglecamera` renders a fisheye image through a lens model. Both are attached to links (`pointcloud_link`, `rgb_camera_link_frame`) on fixed joints to `chassis`.

## Point cloud sensor
```xml
<link name="pointcloud_link"></link>
<joint name="pointcloud_link_joint" type="fixed">
  <origin rpy="0 0 0" xyz="0.051 0.0 0"/>
  <parent link="chassis"/>
  <child link="pointcloud_link"/>
</joint>
<gazebo reference="pointcloud_link">
  <sensor type="gpu_lidar" name="pointcloud_sensor">
    <pose relative_to="pointcloud_link">0 0 0 0 0 0</pose>
    <!-- Ensure ROS frame_id is clean when bridged -->
    <gz_frame_id>pointcloud_link</gz_frame_id>
    <!-- publish at ~30 Hz and show rays in GUI -->
    <always_on>1</always_on>
    <visualize>true</visualize>
    <update_rate>30</update_rate>
    <!-- Gazebo Transport topic name (not a ROS topic yet) -->
    <topic>pointcloud</topic>
    <ray>
      <scan>
        <horizontal><samples>50</samples><resolution>1</resolution><min_angle>-1.0</min_angle><max_angle>1.0</max_angle></horizontal>
        <vertical><samples>50</samples><resolution>1</resolution><min_angle>-1.0</min_angle><max_angle>1.0</max_angle></vertical>
      </scan>
      <range><min>0.10</min><max>5.0</max><resolution>0.01</resolution></range>
    </ray>
  </sensor>
</gazebo>
```
50 × 50 beams over ±1 rad in both directions. Bridge the cloud: `"/pointcloud/points" + "@sensor_msgs/msg/PointCloud2" + "[gz.msgs.PointCloudPacked"`.

## Wide-angle camera
```xml
<link name="rgb_camera_link_frame"></link>
<joint name="rgb_camera_link_frame_joint" type="fixed">
  <origin rpy="0 0 0" xyz="0.051 0.0 0.05"/>
  <parent link="chassis"/>
  <child link="rgb_camera_link_frame"/>
</joint>
<!-- Wide-angle RGB camera on link `rgb_camera_link_frame` -->
<gazebo reference="rgb_camera_link_frame">
  <sensor name="camera" type="wideanglecamera">
    <pose relative_to="rgb_camera_link_frame">0 0 0 0 0 0</pose>
    <gz_frame_id>rgb_camera_link_frame</gz_frame_id>
    <always_on>1</always_on>
    <visualize>true</visualize>
    <update_rate>30</update_rate>
    <topic>rgb_camera</topic>
    <camera>
      <horizontal_fov>6.283</horizontal_fov>
      <image><width>320</width><height>240</height><format>R8G8B8</format></image>
      <clip><near>0.1</near><far>100</far></clip>
      <!-- Wide-angle / fisheye lens settings -->
      <lens>
        <type>custom</type>
        <custom_function><c1>1.05</c1><c2>4</c2><f>1.0</f><fun>tan</fun></custom_function>
        <scale_to_hfov>true</scale_to_hfov>
        <cutoff_angle>3.1415</cutoff_angle>
        <env_texture_size>512</env_texture_size>
      </lens>
    </camera>
  </sensor>
</gazebo>
```
- The image goes to `rgb_camera`; `camera_info` to the parent of that topic + `/camera_info`, here `/camera_info`. Bridge `"/rgb_camera" + "@sensor_msgs/msg/Image" + "[gz.msgs.Image"` and `"/camera_info" + "@sensor_msgs/msg/CameraInfo" + "[gz.msgs.CameraInfo"`.
- `horizontal_fov` 6.283 rad = a full turn; `cutoff_angle` limits the lens; `env_texture_size` is the size of the cube map rendered around the camera.

## RViz2
Add PointCloud2 (`/pointcloud/points`) and Image (`/rgb_camera`). Set each display's Reliability/Durability to what `ros2 topic info <topic> --verbose` reports, otherwise the display stays empty.

## Pitfalls
- Point cloud missing in ROS → you bridged `/pointcloud` instead of `/pointcloud/points`.
- Image dark or cut → `cutoff_angle` or `scale_to_hfov` settings; try a normal `camera` first ([[gazebo-sensors-camera]]).
- Each extra rendering sensor costs GPU: lower `update_rate` and resolution when the simulation slows down.
