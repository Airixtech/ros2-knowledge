---
id: gazebo-learn-unit6-sensors
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "Unit 6: lidar, point cloud and wide-angle camera on box_bot (exercise 6.1.1)"
domain: gazebo
area: learn
distro: jazzy
tested: false
audience: students
summary: "Unit 6: Sensors system and 360° lidar on box_bot, LaserScan in RViz2, exercise 6.1.1 point cloud and wide-angle camera."
tags: [course, unit 6, box_bot_control_complete_sensor.urdf, box_bot_final.urdf, spawn_robot_ros2_sensor.launch.xml, spawn_robot_ros2_final.launch.xml, lidar, point cloud, wide-angle camera, exercise 6.1.1]
see: ["[[gazebo-learn-start-here]]", "[[gazebo-learn-unit5-moving]]", "[[gazebo-sensors-lidar]]", "[[gazebo-sensors-depth-wideangle]]", "[[gazebo-sensors-camera]]", "[[gazebo-sensors-imu]]", "[[gazebo-ros-gz-bridge]]"]
requires: [ros2-core, ros2-urdf]
version_notes:
  - "jazzy: the laser's up/down motion is on laser_scan_link_joint, not on the fixed laser_scan_frame_joint (GZ-V54)"
---
# Unit 6: lidar, point cloud and wide-angle camera on box_bot (exercise 6.1.1)

**TL;DR** Add sensors to the final URDF of unit 5 the same way as the plugins: a Sensors system once, then one `<sensor>` per link, and a bridge entry per topic. The lidar sits on `laser_scan_frame`, so it moves up and down with the mount but does not spin with the lidar model.

## 1. 360° lidar (6.2)
- Copy `box_bot_control_complete_velocity.urdf` to `box_bot_control_complete_sensor.urdf` and add the Sensors system and the `gpu_lidar` block before `</robot>` ([[gazebo-sensors-lidar]]).
- New files: `my_box_bot_description/launch/urdf_visualize_sensor.launch.py` (RViz launch with the new URDF) and `my_box_bot_gazebo/launch/spawn_robot_ros2_sensor.launch.xml`: the three-include chain of unit 5 with `urdf_visualize_sensor.launch.py`, `spawn_robot_description.launch.py` and `control_position_velocity.launch.py`.
- Add `/laser_scan` to the bridge ([[gazebo-ros-gz-bridge]]).
```bash
cd ~/ros2_ws && colcon build && source install/setup.bash
ros2 launch my_box_bot_gazebo start_world.launch.py            # terminal 1
ros2 launch my_box_bot_gazebo spawn_robot_ros2_sensor.launch.xml   # terminal 2
ros2 run teleop_twist_keyboard teleop_twist_keyboard            # terminal 3
```
In Gazebo enable "Visualize Lidar" and drop a few shapes near the robot; in RViz2 add LaserScan on `/laser_scan`.

## 2. Exercise 6.1.1: point cloud + wide-angle camera
- `box_bot_final.urdf` = `box_bot_control_complete_sensor.urdf` + `pointcloud_link` (fixed to `chassis` at `0.051 0 0`) with the point cloud sensor + `rgb_camera_link_frame` (fixed to `chassis` at `0.051 0 0.05`) with the wide-angle camera ([[gazebo-sensors-depth-wideangle]]).
- New files: `spawn_robot_ros2_final.launch.xml` (same chain with `urdf_visualize_final.launch.py`) and `urdf_visualize_final.launch.py`.
- Bridge: add `/pointcloud/points` (PointCloud2), `/rgb_camera` (Image) and `/camera_info` (CameraInfo): the full list is in [[gazebo-ros-gz-bridge]].
- RViz2: PointCloud2 and Image displays with the QoS shown by `ros2 topic info <topic> --verbose`.
- Extra: a world with the `box_room` model, spawning box_bot inside ([[gazebo-world-sdf]]).

## 3. Other sensors (6.4–6.5)
A plain camera ([[gazebo-sensors-camera]]) and an IMU with noise ([[gazebo-sensors-imu]]) follow the same pattern; the IMU also needs the Imu system.
