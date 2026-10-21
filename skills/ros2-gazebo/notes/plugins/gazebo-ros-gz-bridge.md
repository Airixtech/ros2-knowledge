---
id: gazebo-ros-gz-bridge
type: reference
owner: equipo-ros2
updated: 2026-10-21
review_by: 2027-04-19
source: manual
confidentiality: internal
title: "ros_gz_bridge parameter_bridge syntax (@ [ ]), type pairs, /clock and sim time"
domain: gazebo
area: plugins
distro: jazzy
tested: false
audience: dev
summary: "ros_gz_bridge parameter_bridge topic@ros_type[gz_type, @ both ways, [ to ROS, ] to Gazebo; Clock, Twist, TFMessage-Pose_V, JointState-Model, LaserScan, PointCloud2, Image pairs."
tags: [ros_gz_bridge, parameter_bridge, bridge, gz.msgs, ignition.msgs, clock, use_sim_time, cmd_vel, tf, odom, joint_states, LaserScan, PointCloud2, PointCloudPacked, Image, CameraInfo]
see: ["[[core-gazebo-bridge]]", "[[gazebo-joint-state-diffdrive]]", "[[gazebo-sensors-lidar]]", "[[gazebo-multi-robot]]", "[[core-time-timers]]"]
requires: [ros2-core, ros2-urdf]
version_notes:
  - "jazzy/harmonic: direction characters and the message pairs below — https://github.com/gazebosim/ros_gz/blob/jazzy/ros_gz_bridge/README.md (GZ-V26)"
  - "humble/fortress: the bridge accepts gz.msgs.* and ignition.msgs.* type names, so the same arguments work with Fortress — https://github.com/gazebosim/ros_gz/blob/humble/ros_gz_bridge/resource/get_mappings.cpp.em (GZ-V26, V66)"
---
# ros_gz_bridge parameter_bridge syntax (@ [ ]), type pairs, /clock and sim time

**TL;DR** Every Gazebo topic a ROS node needs goes through `ros_gz_bridge`'s `parameter_bridge`. Each argument is `<topic>@<ROS type><direction><Gazebo type>`, where the direction is `@` (both ways), `[` (Gazebo → ROS) or `]` (ROS → Gazebo). Always bridge `/clock` and run the ROS nodes with `use_sim_time: true`.

## The course's bridge node (in spawn_robot_description.launch.py)
```python
gz_bridge = Node(
    package="ros_gz_bridge",
    executable="parameter_bridge",
    name="gz_bridge",
    arguments=[
        "/clock" + "@rosgraph_msgs/msg/Clock" + "[gz.msgs.Clock",
        "/cmd_vel" + "@geometry_msgs/msg/Twist" + "@gz.msgs.Twist",
        "/tf" + "@tf2_msgs/msg/TFMessage" + "[gz.msgs.Pose_V",
        "/odom" + "@nav_msgs/msg/Odometry" + "[gz.msgs.Odometry",
        "/joint_states" + "@sensor_msgs/msg/JointState" + "[gz.msgs.Model",
        "/laser_scan" + "@sensor_msgs/msg/LaserScan" + "[gz.msgs.LaserScan",
        "/pointcloud/points" + "@sensor_msgs/msg/PointCloud2" + "[gz.msgs.PointCloudPacked",
        "/rgb_camera" + "@sensor_msgs/msg/Image" + "[gz.msgs.Image",
        "/camera_info" + "@sensor_msgs/msg/CameraInfo" + "[gz.msgs.CameraInfo",
    ],
    remappings=[
        # there are no remappings for this robot description
    ],
    output="screen",
)
```
Add it to the `LaunchDescription` of the spawn file ([[gazebo-spawn-urdf]]). Unit 5 starts with the first five topics; unit 6 adds the sensor topics ([[gazebo-sensors-lidar]], [[gazebo-sensors-depth-wideangle]]).

## Type pairs used here
| ROS 2 | Gazebo | Typical direction |
|---|---|---|
| `rosgraph_msgs/msg/Clock` | `gz.msgs.Clock` | `[` |
| `geometry_msgs/msg/Twist` | `gz.msgs.Twist` | `]` or `@` |
| `tf2_msgs/msg/TFMessage` | `gz.msgs.Pose_V` | `[` |
| `nav_msgs/msg/Odometry` | `gz.msgs.Odometry` | `[` |
| `sensor_msgs/msg/JointState` | `gz.msgs.Model` | `[` |
| `sensor_msgs/msg/LaserScan` | `gz.msgs.LaserScan` | `[` |
| `sensor_msgs/msg/PointCloud2` | `gz.msgs.PointCloudPacked` | `[` |
| `sensor_msgs/msg/Image`, `CameraInfo` | `gz.msgs.Image`, `gz.msgs.CameraInfo` | `[` |

Full list: the bridge README. A YAML config file instead of arguments: [[core-gazebo-bridge]].

## Sim time
- The `/clock` bridge is what makes `use_sim_time: true` work; without it, nodes with sim time see time 0.
- `SetParameter(name="use_sim_time", value=True)` sets it for the ROS nodes started after it in the same launch file; Gazebo is not affected ([[core-time-timers]]).

## Pitfalls
- A sensor topic visible with `gz topic -l` ([Humble + Fortress] Fortress: `ign topic -l`) but not in `ros2 topic list` → not bridged, or the topic name differs (lidar point clouds end in `/points`).
- `/cmd_vel` bridged with `[` (Gazebo → ROS only) → teleop commands never reach Gazebo.
- Two robots on the same topics → namespace them ([[gazebo-multi-robot]]).
