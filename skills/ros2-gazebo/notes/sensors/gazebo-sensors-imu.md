---
id: gazebo-sensors-imu
type: reference
owner: equipo-ros2
updated: 2026-10-21
review_by: 2027-04-19
source: manual
confidentiality: internal
title: "IMU sensor with Gaussian noise and the Imu system; NavSat GPS"
domain: gazebo
area: sensors
distro: jazzy
tested: false
audience: dev
summary: "Gazebo IMU: Imu system, update rate, Gaussian noise on angular velocity and acceleration, Imu bridge; NavSat GPS needs spherical coordinates."
tags: [imu, gz-sim-imu-system, noise, gaussian, stddev, angular_velocity, linear_acceleration, sensor_msgs/Imu, gz.msgs.IMU, navsat, gz-sim-navsat-system, NavSatFix, spherical_coordinates]
see: ["[[gazebo-sensors-camera]]", "[[gazebo-sensors-lidar]]", "[[gazebo-ros-gz-bridge]]", "[[urdf-xacro-macros]]", "[[core-perception-basics]]"]
requires: [ros2-core, ros2-urdf]
version_notes:
  - "jazzy/harmonic: IMU needs the Imu system, GPS the NavSat system; bridge sensor_msgs/msg/Imu ↔ gz.msgs.IMU, sensor_msgs/msg/NavSatFix ↔ gz.msgs.NavSat — https://github.com/gazebosim/ros_gz/blob/jazzy/ros_gz_bridge/README.md (GZ-V41, GZ-V56)"
  - "jazzy/harmonic: NavSat warns 'Spherical coordinates not set.' and publishes nothing without <spherical_coordinates> — https://github.com/gazebosim/gz-sim/blob/gz-sim8/src/systems/navsat/NavSat.cc (GZ-V41)"
  - "humble/fortress: the NavSat gz::sim alias needs Fortress ≥ 6.18.0 [verify installed version] — https://github.com/gazebosim/gz-sim/pull/3369 (GZ-V12)"
---
# IMU sensor with Gaussian noise and the Imu system; NavSat GPS

**TL;DR** An IMU is a `<sensor type="imu">` on a link plus the **Imu** system, which computes its data; it publishes angular velocity and linear acceleration on a Gazebo topic. A GPS is a `navsat` sensor plus the **NavSat** system. Neither reaches ROS until it is bridged.

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
- No GPS fix → the world has no `<spherical_coordinates>`.
