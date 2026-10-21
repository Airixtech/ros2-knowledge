---
id: gazebo-velocity-control
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "Velocity commands on /<controller>/commands; a visual-only rotating link"
domain: gazebo
area: control
distro: jazzy
tested: false
audience: dev
summary: "JointGroupVelocityController commands with std_msgs/Float64MultiArray on /velocity_controller/commands; continuous joint with a velocity interface; spinning lidar model link."
tags: [JointGroupVelocityController, velocity_controller, commands, Float64MultiArray, ros2 topic pub, continuous joint, velocity interface, laser_scan_model_link, rplidar]
see: ["[[gazebo-ros2-control-controllers]]", "[[gazebo-ros2-control-urdf]]", "[[gazebo-sensors-lidar]]", "[[core-topic-cli]]"]
requires: [ros2-core, ros2-urdf]
version_notes:
  - "jazzy: GazeboSimSystem knows only the interface names position, velocity, effort (GZ-V50) — https://github.com/ros-controls/gz_ros2_control/blob/jazzy/gz_ros2_control/src/gz_system.cpp"
  - "jazzy: the controller does not clamp; whether Gazebo applies the URDF velocity limit to 20 rad/s commands [verify] (GZ-V34)"
  - "jazzy: the course reuses the large box's inertia for the smaller box and the cylinder (GZ-V52)"
---
# Velocity commands on /<controller>/commands; a visual-only rotating link

**TL;DR** A `velocity_controllers/JointGroupVelocityController` takes one velocity per joint as `std_msgs/msg/Float64MultiArray` on `/<controller_name>/commands` and writes it to the joints' `velocity` command interface. The course uses it to spin the lidar mesh while the lidar sensor stays on a frame that does not rotate.

## Split the lidar into a moving mount and a spinning model
- `laser_scan_link` (prismatic mount, [[gazebo-ros2-control-urdf]]) becomes a small 0.02 m box (visual and collision).
- New `laser_scan_model_link` carries the mesh and turns on a continuous joint:
```xml
<!-- Visual Laser Model to be rotated -->
<link name="laser_scan_model_link">
  <visual>
    <origin rpy="0 0 0" xyz="0 0 0"/>
    <geometry><mesh filename="package://my_box_bot_description/meshes/sensors/rplidar.dae" scale="1.0 1.0 1.0"/></geometry>
  </visual>
  <collision>
    <origin rpy="0 0 0" xyz="0 0 0.0204"/>
    <geometry><cylinder length="0.0408" radius="0.037493"/></geometry>
  </collision>
  <inertial>
    <mass value="0.01"/>
    <origin rpy="0 0 0" xyz="0 0 0.0204"/>
    <inertia ixx="6.066578520833334e-06" ixy="0" ixz="0" iyy="6.072950163333333e-06" iyz="0" izz="9.365128684166666e-06"/>
  </inertial>
</link>
<joint name="laser_scan_model_link_joint" type="continuous">
  <origin rpy="0 0 0" xyz="0.0 0.0 0.0"/>
  <parent link="laser_scan_link"/>
  <child link="laser_scan_model_link"/>
  <axis xyz="0 0 1"/>
  <limit effort="10.0" velocity="2.0"/>
  <dynamics friction="0.01"/>
</joint>
```
- Its `<ros2_control>` joint, next to `laser_scan_link_joint`:
```xml
<joint name="laser_scan_model_link_joint">
  <command_interface name="velocity">
    <param name="min">0.0</param>
    <param name="max">2.0</param>
  </command_interface>
  <state_interface name="position"/>
  <state_interface name="velocity"/>
  <state_interface name="effort"/>
</joint>
```
The interface must be called `velocity` (not any name). The sensor is attached to `laser_scan_frame`, child of `laser_scan_link`, so it moves up and down but does not spin: a 360° lidar needs no rotating link in simulation ([[gazebo-sensors-lidar]]).

## Send velocities
```bash
ros2 topic info /velocity_controller/commands
ros2 interface proto std_msgs/msg/Float64MultiArray
ros2 topic pub /velocity_controller/commands std_msgs/msg/Float64MultiArray "{data: [20.0]}"    # spin
ros2 topic pub /velocity_controller/commands std_msgs/msg/Float64MultiArray "{data: [-20.0]}"   # other way
ros2 topic pub /velocity_controller/commands std_msgs/msg/Float64MultiArray "{data: [0.0]}"     # stop
```
One value per joint listed in the controller's `joints`, in that order. The prismatic position script keeps working at the same time ([[gazebo-jtc-action-client]]).

## Pitfalls
- Commands with the wrong number of values → "command size (…) does not match number of interfaces (…)" and the command is not applied (one value per joint).
- 20 rad/s against a URDF `velocity="2.0"` and `max 2.0`: the controller passes it on unchanged; what Gazebo does with it [verify].
- The inertia values here are those of the larger box of the first version; recompute them for the 0.02 m box and for the cylinder ([[urdf-inertia]]).
