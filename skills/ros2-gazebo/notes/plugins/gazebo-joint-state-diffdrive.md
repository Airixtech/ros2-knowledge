---
id: gazebo-joint-state-diffdrive
type: reference
owner: equipo-ros2
updated: 2026-10-21
review_by: 2027-04-19
source: manual
confidentiality: internal
title: "JointStatePublisher and DiffDrive systems: elements, odom and TF output"
domain: gazebo
area: plugins
distro: jazzy
tested: false
audience: dev
summary: "Gazebo JointStatePublisher (topic, update_rate, joint_name) and DiffDrive (wheels, separation, radius, cmd_vel, odom, tf, frames) systems; teleop after bridging."
tags: [JointStatePublisher, gz-sim-joint-state-publisher-system, DiffDrive, gz-sim-diff-drive-system, joint_states, cmd_vel, odom, tf, wheel_separation, wheel_radius, child_frame_id, teleop_twist_keyboard]
see: ["[[gazebo-ros-gz-bridge]]", "[[gazebo-sim-overview]]", "[[urdf-joint-state-publisher]]", "[[core-tf-basics]]", "[[gazebo-multi-robot]]"]
requires: [ros2-core, ros2-urdf]
version_notes:
  - "jazzy/harmonic: DiffDrive reads no publish_odom, publish_odom_tf or publish_wheel_tf (not gz-sim DiffDrive elements); it always publishes odometry and the odom→child transform; wheel TFs come from JointStatePublisher + robot_state_publisher (same in Fortress and Jetty) — https://github.com/gazebosim/gz-sim/blob/gz-sim8/src/systems/diff_drive/DiffDrive.cc (GZ-V03)"
  - "jazzy/harmonic: the joint_state_publisher ROS node does not read simulated joints (GZ-V04)"
  - "jazzy/harmonic: JointStatePublisher elements topic, update_rate, joint_name (GZ-V23)"
  - "jazzy/harmonic: JointStatePublisher works only as a model plugin, not in <world> — https://github.com/gazebosim/gz-sim/blob/gz-sim8/src/systems/joint_state_publisher/JointStatePublisher.cc (GZ-V57)"
  - "humble/fortress: same file names and gz::sim::systems names work with current Fortress — https://github.com/gazebosim/gz-sim/blob/ign-gazebo6/src/SystemLoader.cc (GZ-V12)"
---
# JointStatePublisher and DiffDrive systems: elements, odom and TF output

**TL;DR** Two Gazebo systems give a wheeled robot its ROS behaviour: **JointStatePublisher** streams the simulated joint positions (robot_state_publisher turns them into TF), **DiffDrive** drives the two wheels from velocity commands and publishes odometry plus the `odom → base_link` transform. Both talk Gazebo Transport: bridge them ([[gazebo-ros-gz-bridge]]).

## In the URDF (before `</robot>`)
```xml
<!-- Joint State Publisher Plugin -->
<gazebo>
  <plugin filename="gz-sim-joint-state-publisher-system" name="gz::sim::systems::JointStatePublisher">
    <topic>/joint_states</topic>
    <update_rate>30</update_rate>
    <!-- Publish the state of these joints -->
    <joint_name>joint_left_wheel</joint_name>
    <joint_name>joint_right_wheel</joint_name>
    <joint_name>front_yaw_joint</joint_name>
    <joint_name>back_yaw_joint</joint_name>
    <joint_name>front_roll_joint</joint_name>
    <joint_name>back_roll_joint</joint_name>
    <joint_name>front_pitch_joint</joint_name>
    <joint_name>back_pitch_joint</joint_name>
  </plugin>
</gazebo>

<!-- Differential Drive Plugin -->
<gazebo>
  <plugin filename="gz-sim-diff-drive-system" name="gz::sim::systems::DiffDrive">
    <left_joint>joint_left_wheel</left_joint>
    <right_joint>joint_right_wheel</right_joint>
    <wheel_separation>0.1</wheel_separation>
    <wheel_radius>0.035</wheel_radius>
    <topic>cmd_vel</topic>
    <odom_topic>odom</odom_topic>
    <tf_topic>tf</tf_topic>
    <frame_id>odom</frame_id>
    <child_frame_id>base_link</child_frame_id>
  </plugin>
</gazebo>
```
The course block also has `<publish_odom>`, `<publish_odom_tf>` and `<publish_wheel_tf>`: not elements of this system, so it ignores them; they are left out.

## JointStatePublisher
| Element | Meaning |
|---|---|
| `<topic>` | Gazebo topic of the `gz.msgs.Model` message (bridged to `sensor_msgs/msg/JointState`) |
| `<update_rate>` | Hz (30 here) |
| `<joint_name>` | one per joint; list also passive joints (casters) so they get TF. Without any, all joints of the model are published |

It must be a model plugin: in the `<world>` it fails ("The JointStatePublisher system should be attached to a model entity"). It does not move anything. Same role as joint_state_publisher on a desk ([[urdf-joint-state-publisher]]), but with the simulated values.

## DiffDrive
| Element | Meaning |
|---|---|
| `<left_joint>`, `<right_joint>` | wheel joints (continuous) |
| `<wheel_separation>` | distance between the wheel centres (0.1 m: wheels at y = ±0.05) |
| `<wheel_radius>` | 0.035 m |
| `<topic>` | velocity command topic (`gz.msgs.Twist`) |
| `<odom_topic>`, `<tf_topic>` | odometry (`gz.msgs.Odometry`) and transform (`gz.msgs.Pose_V`) topics |
| `<frame_id>`, `<child_frame_id>` | odometry frames; the child must be the robot's root frame (`base_link`) |
| limits | optional `<max_linear_velocity>`, `<max_linear_acceleration>`, `<min_…>`, `<odom_publish_frequency>` |

## Drive it
After bridging `/cmd_vel`, `/odom`, `/tf` and `/joint_states`:
```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```
In RViz2 set the Fixed Frame to `odom`: DiffDrive now publishes `odom → base_link`.

## Pitfalls
- Robot does not move from teleop → `/cmd_vel` not bridged (Gazebo systems are not ROS nodes).
- Odometry drifts or turns the wrong way → wrong `wheel_separation` or `wheel_radius`, or the wheel axes are not along y.
- Two `odom → base_link` publishers (DiffDrive and an EKF) → choose one ([[core-tf-basics]]).
