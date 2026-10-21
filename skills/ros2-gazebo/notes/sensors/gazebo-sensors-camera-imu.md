---
id: gazebo-sensors-camera-imu
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "Camera (image + camera_info) and IMU sensors with noise; Imu/NavSat systems"
domain: gazebo
area: sensors
distro: jazzy
tested: false
audience: dev
summary: "Gazebo camera (FOV, distortion, camera_info naming) and IMU with Gaussian noise plus Imu system; NavSat GPS; bridge types."
tags: [camera, camera_info, horizontal_fov, distortion, imu, gz-sim-imu-system, noise, gaussian, angular_velocity, linear_acceleration, navsat, gz-sim-navsat-system, sensor_msgs/Imu, NavSatFix]
see: ["[[gazebo-sensors-lidar]]", "[[gazebo-sensors-depth-wideangle]]", "[[gazebo-ros-gz-bridge]]", "[[core-perception-basics]]"]
requires: [ros2-core, ros2-urdf]
version_notes:
  - "jazzy: the image is published on <topic>, camera_info on the parent of <topic> + /camera_info (robot1/camera1 → /robot1/camera_info) — https://github.com/gazebosim/gz-sensors/blob/gz-sensors8/src/CameraSensor.cc (GZ-V05)"
  - "jazzy: IMU needs the Imu system, GPS the NavSat system; bridge sensor_msgs/msg/Imu ↔ gz.msgs.IMU, sensor_msgs/msg/NavSatFix ↔ gz.msgs.NavSat — https://github.com/gazebosim/ros_gz/blob/jazzy/ros_gz_bridge/README.md (GZ-V41, GZ-V56)"
  - "humble: the NavSat gz::sim alias needs Fortress ≥ 6.18.0 [verify installed version] — https://github.com/gazebosim/gz-sim/pull/3369 (GZ-V12)"
---
# Camera (image + camera_info) and IMU sensors with noise; Imu/NavSat systems

**TL;DR** Every sensor hangs from a link (often an empty one on a fixed joint) and publishes on Gazebo topics: bridge them before a ROS node can read them. Cameras need the Sensors system ([[gazebo-sensors-lidar]]); an IMU needs the **Imu** system and a GPS the **NavSat** system.

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

## IMU
```xml
<!-- Each sensor must be attached to a link. -->
<joint name="imu_joint" type="fixed">
  <parent link="base_link"/>
  <child link="imu_link"/>
  <origin xyz="-0.10 0 0.05" rpy="0 0 0"/>
</joint>
<link name="imu_link"/>

<!-- Enable Imu plugin in Gazebo Sim -->
<gazebo>
  <plugin filename="gz-sim-imu-system" name="gz::sim::systems::Imu"></plugin>
</gazebo>
<!-- IMU mounted on link `imu_link` -->
<gazebo reference="imu_link">
  <sensor name="br_imu" type="imu">
    <pose relative_to="imu_link">0 0 0 0 0 0</pose>
    <gz_frame_id>imu_link</gz_frame_id>
    <always_on>1</always_on>
    <update_rate>100</update_rate>
    <!-- Gazebo Transport topic (not ROS yet) -->
    <topic>imu</topic>
    <imu>
      <angular_velocity>
        <x><noise type="gaussian"><mean>0.0</mean><stddev>2e-4</stddev></noise></x>
        <y><noise type="gaussian"><mean>0.0</mean><stddev>2e-4</stddev></noise></y>
        <z><noise type="gaussian"><mean>0.0</mean><stddev>2e-4</stddev></noise></z>
      </angular_velocity>
      <linear_acceleration>
        <x><noise type="gaussian"><mean>0.0</mean><stddev>1.7e-2</stddev></noise></x>
        <y><noise type="gaussian"><mean>0.0</mean><stddev>1.7e-2</stddev></noise></y>
        <z><noise type="gaussian"><mean>0.0</mean><stddev>1.7e-2</stddev></noise></z>
      </linear_acceleration>
    </imu>
  </sensor>
</gazebo>
```
Angular velocity and linear acceleration with Gaussian noise (σ 2e-4 rad/s and 1.7e-2 m/s²). Bridge `"/imu" + "@sensor_msgs/msg/Imu" + "[gz.msgs.IMU"`: the course says the IMU then "publishes to ROS topics", which is true only after this bridge.

## GPS
A `navsat` sensor needs the NavSat system (`gz-sim-navsat-system`, `gz::sim::systems::NavSat`) and a world with `<spherical_coordinates>` (without them the system warns "Spherical coordinates not set." and publishes nothing); bridge `sensor_msgs/msg/NavSatFix` ↔ `gz.msgs.NavSat`. Choosing IMU or GPS by a xacro argument: [[urdf-xacro-macros]].

## Pitfalls
- IMU topic exists in Gazebo but stays silent → the Imu system is not loaded.
- Camera image in RViz2 is empty → QoS mismatch or the Sensors system is missing.
