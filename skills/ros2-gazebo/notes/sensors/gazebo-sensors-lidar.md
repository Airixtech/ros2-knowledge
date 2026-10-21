---
id: gazebo-sensors-lidar
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "Sensors system and gpu_lidar: frame id, topic, scan/range, RViz LaserScan"
domain: gazebo
area: sensors
distro: jazzy
tested: false
audience: dev
summary: "Sensors system (render_engine ogre2) and 360° gpu_lidar: gz_frame_id, topic, update_rate, samples, angles, range; LaserScan bridge and RViz2."
tags: [sensors system, gz-sim-sensors-system, render_engine, ogre2, gpu_lidar, lidar, ray, gz_frame_id, laser_scan, samples, min_angle, range, LaserScan, rviz2]
see: ["[[gazebo-sensors-depth-wideangle]]", "[[gazebo-sensors-camera]]", "[[gazebo-sensors-imu]]", "[[gazebo-ros-gz-bridge]]", "[[gazebo-world-sdf]]", "[[core-perception-basics]]"]
requires: [ros2-core, ros2-urdf]
version_notes:
  - "jazzy: gz_frame_id sets header.frame_id (default: the sensor's name); humble: Fortress reads ignition_frame_id and also gz_frame_id — https://github.com/gazebosim/gz-sensors/blob/gz-sensors8/src/Sensor.cc , https://github.com/gazebosim/gz-sensors/blob/ign-sensors6/src/Sensor.cc (GZ-V36)"
  - "jazzy: gpu_lidar reads <lidar> or, if absent, <ray>; resolution multiplies samples and interpolates — https://github.com/gazebosim/sdformat/blob/sdf14/src/Sensor.cc , https://github.com/gazebosim/sdformat/blob/sdf14/sdf/1.11/lidar.sdf (GZ-V37, GZ-V55)"
  - "jazzy: Sensors loaded from the robot works; the official template loads it in the world; one per world [verify] (GZ-V35)"
  - "jazzy: the up/down motion belongs to laser_scan_link_joint (prismatic); laser_scan_frame_joint is fixed (GZ-V54)"
---
# Sensors system and gpu_lidar: frame id, topic, scan/range, RViz LaserScan

**TL;DR** Rendering sensors (lidar, cameras) need the **Sensors** system once, with a render engine. Each sensor is a `<sensor>` inside `<gazebo reference="<link>">`; it publishes on a Gazebo topic that you bridge to ROS. A `gpu_lidar` (ray casting on the GPU) with one horizontal row gives a `sensor_msgs/msg/LaserScan`.

## URDF blocks
```xml
<!-- Enable Sensors in Gazebo Sim -->
<gazebo>
  <plugin filename="gz-sim-sensors-system" name="gz::sim::systems::Sensors">
    <!-- use ogre2 if ogre v2.x is installed, otherwise use ogre -->
    <render_engine>ogre2</render_engine>
  </plugin>
</gazebo>

<!-- Laser Scanner Plugin -->
<gazebo reference="laser_scan_frame">
  <sensor type="gpu_lidar" name="gpu_lidar">
    <pose relative_to='laser_scan_frame'>0 0 0 0 0 0</pose>
    <gz_frame_id>laser_scan_frame</gz_frame_id>
    <always_on>1</always_on>
    <visualize>true</visualize>
    <update_rate>100</update_rate>
    <topic>laser_scan</topic>
    <ray>
      <scan>
        <horizontal>
          <samples>200</samples>
          <resolution>1</resolution>
          <min_angle>-3.14</min_angle>
          <max_angle>3.14</max_angle>
        </horizontal>
      </scan>
      <range>
        <min>0.1</min>
        <max>5.0</max>
        <resolution>0.01</resolution>
      </range>
    </ray>
  </sensor>
</gazebo>
```
| Element | Meaning |
|---|---|
| `reference` + `<pose relative_to>` | the link that carries the sensor and the offset from it |
| `<gz_frame_id>` | `header.frame_id` of the bridged messages; without it the frame is the sensor's name |
| `<always_on>`, `<visualize>` | run even without subscribers; draw the rays in the Gazebo GUI |
| `<update_rate>` | Hz; 100 is high, lower it to save CPU/GPU |
| `<topic>` | Gazebo Transport topic (not ROS until bridged) |
| `<samples>`, `<min_angle>`, `<max_angle>` | 200 beams over ±3.14 rad (about 360°) |
| `<resolution>` (scan) | multiplies `samples`; values other than 1 interpolate the range data, they do not add real beams |
| `<range>` | min 0.1 m, max 5.0 m, quantized to 0.01 m |

`<ray>` is the older element name; `<lidar>` is the current one and both are read.

## To ROS and RViz2
- Bridge: `"/laser_scan" + "@sensor_msgs/msg/LaserScan" + "[gz.msgs.LaserScan"` ([[gazebo-ros-gz-bridge]]).
- RViz2: Add › LaserScan, topic `/laser_scan`; match its QoS to the publisher (`ros2 topic info /laser_scan --verbose`).
- Gazebo GUI: the "Visualize Lidar" panel shows the rays; add a few boxes or cylinders around the robot to see hits.
- Change the frame for ROS in `<gz_frame_id>` rather than remapping downstream.

## Pitfalls
- No scan at all → the Sensors system is missing (in the world or the model), or the render engine is not available.
- Scan in the wrong frame or "frame does not exist" in RViz2 → `gz_frame_id` missing or not a URDF link.
- The course's tip puts the up/down constraint on `laser_scan_frame_joint`; that joint is fixed, the prismatic one is `laser_scan_link_joint` (chassis → laser_scan_link).
