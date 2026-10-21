---
id: gazebo-sensors-camera
type: reference
owner: equipo-ros2
updated: 2026-10-21
review_by: 2027-04-19
source: manual
confidentiality: internal
title: "Camera sensor: image and camera_info topics, FOV, clip, distortion, bridge"
domain: gazebo
area: sensors
distro: jazzy
tested: false
audience: dev
summary: "Gazebo camera sensor: FOV, image size, clip, distortion; image on <topic>, camera_info on its parent topic; Image/CameraInfo bridge."
tags: [camera, camera_info, camera_info_topic, horizontal_fov, image, clip, distortion, gz.msgs.Image, sensor_msgs/Image, CameraInfo]
see: ["[[gazebo-sensors-lidar]]", "[[gazebo-sensors-depth-wideangle]]", "[[gazebo-ros-gz-bridge]]", "[[core-perception-basics]]"]
requires: [ros2-core, ros2-urdf]
version_notes:
  - "jazzy/harmonic: the image is published on <topic>, camera_info on the parent of <topic> + /camera_info (robot1/camera1 → /robot1/camera_info) — https://github.com/gazebosim/gz-sensors/blob/gz-sensors8/src/CameraSensor.cc (GZ-V05)"
  - "humble/fortress: Fortress uses the same topic rule — https://github.com/gazebosim/gz-sensors/blob/ign-sensors6/src/CameraSensor.cc (GZ-V05)"
---
# Camera sensor: image and camera_info topics, FOV, clip, distortion, bridge

**TL;DR** A camera hangs from a link (often an empty one on a fixed joint), needs the Sensors system ([[gazebo-sensors-lidar]]) and publishes on Gazebo topics: the image on `<topic>`, the calibration on the parent of that topic + `/camera_info`. Bridge both before a ROS node can read them.

## Camera
```xml
<!-- Each sensor must be attached to a link. -->
<joint name="camera_joint" type="fixed">
  <parent link="base_link"/>
  <child link="camera_link"/>
  <origin xyz="0.0 0.0 0.2" rpy="0 0 0"/>
</joint>
<link name="camera_link"/>

<!-- RGB camera mounted on link `camera_link` -->
<gazebo reference="camera_link">
  <sensor name="camera" type="camera">
    <pose relative_to="camera_link">0 0 0 0 0 0</pose>
    <gz_frame_id>camera_link</gz_frame_id>
    <always_on>1</always_on>
    <update_rate>30</update_rate>
    <!-- image on robot1/camera1, camera_info on /robot1/camera_info -->
    <topic>robot1/camera1</topic>
    <camera>
      <horizontal_fov>1.3962634</horizontal_fov>
      <image><width>480</width><height>360</height><format>R8G8B8</format></image>
      <clip><near>0.01</near><far>20</far></clip>
      <!-- Brown distortion model -->
      <distortion>
        <k1>0.0</k1><k2>0.0</k2><k3>0.0</k3>
        <p1>0.0</p1><p2>0.0</p2>
        <center>0.5 0.5</center>
      </distortion>
    </camera>
  </sensor>
</gazebo>
```
- The course's comment says "subtopics /image and /camera_info will be created": the image is on `<topic>` itself, `camera_info` on its parent + `/camera_info` (set `<camera_info_topic>` to choose another).
- Bridge `/robot1/camera1` as `sensor_msgs/msg/Image` ↔ `gz.msgs.Image` and `/robot1/camera_info` as `CameraInfo`. Optical frame conventions: [[core-perception-basics]].

## Pitfalls
- Camera image in RViz2 is empty → QoS mismatch, the Sensors system is missing, or the topic name is wrong (no `/image` suffix).
- `camera_info` not where expected → it follows the image topic's parent; set `<camera_info_topic>` to pin it.
