---
id: gazebo-ros2-control-urdf
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "gz_ros2_control: <ros2_control> hardware plugin, interfaces, system plugin + YAML"
domain: gazebo
area: control
distro: jazzy
tested: false
audience: dev
summary: "URDF <ros2_control> with gz_ros2_control/GazeboSimSystem, command/state interfaces position/velocity/effort, gz_ros2_control-system plugin with <parameters> YAML; Humble robot_param_node."
tags: [gz_ros2_control, ros2_control, GazeboSimSystem, GazeboSimROS2ControlPlugin, gz_ros2_control-system, command_interface, state_interface, parameters, robot_param_node, controller_manager]
see: ["[[gazebo-ros2-control-controllers]]", "[[core-ros2-control-overview]]", "[[gazebo-velocity-control]]", "[[gazebo-jtc-action-client]]", "[[gazebo-sim-overview]]"]
requires: [ros2-core, ros2-urdf]
version_notes:
  - "jazzy: GazeboSimSystem exports only the interfaces named position, velocity and effort; other names are not exported — https://github.com/ros-controls/gz_ros2_control/blob/jazzy/gz_ros2_control/src/gz_system.cpp (GZ-V50)"
  - "jazzy: the controller manager receives the description from the /robot_description topic; humble: from the parameter robot_description of node robot_state_publisher (<robot_param_node>, <robot_param>) — https://github.com/ros-controls/gz_ros2_control/blob/humble/doc/index.rst (GZ-V29)"
  - "humble: gz_ros2_control 0.7.21 uses the same names (plus ign_ros2_control aliases); lyrical drops ign_ros2_control::IgnitionSystem — https://github.com/ros/rosdistro/blob/master/humble/distribution.yaml (GZ-V28)"
  - "jazzy: the course text calls the laser collision a cylinder; its file and inertia use the box shown here (GZ-V53)"
  - "jazzy: $(find pkg) in <parameters> works because the launch file runs the .urdf through xacro (GZ-V30)"
  - "jazzy: command interface min/max are metadata; whether anything clamps to them [verify] (GZ-V31)"
---
# gz_ros2_control: <ros2_control> hardware plugin, interfaces, system plugin + YAML

**TL;DR** Two blocks in the URDF: a `<ros2_control>` tag that declares the simulated hardware (`gz_ros2_control/GazeboSimSystem`) and the joints with their command and state interfaces, and a `<gazebo>` system plugin (`gz_ros2_control-system`) that starts a controller_manager inside Gazebo with your controller YAML. Then spawn the controllers ([[gazebo-ros2-control-controllers]]).

## The two blocks (laser mount on a prismatic joint)
```xml
<!-- ros2_control config -->
<ros2_control name="GazeboSimSystem" type="system">
  <hardware>
    <!-- Gazebo Sim integration plugin -->
    <plugin>gz_ros2_control/GazeboSimSystem</plugin>
  </hardware>
  <joint name="laser_scan_link_joint">
    <command_interface name="position">
      <param name="min">-0.05</param>
      <param name="max">0.0</param>
    </command_interface>
    <state_interface name="position"/>
    <state_interface name="velocity"/>
    <state_interface name="effort"/>
  </joint>
</ros2_control>

<!-- Gazebo Sim system plugin that boots the controller manager and parses the ros2_control tags -->
<gazebo>
  <plugin filename="gz_ros2_control-system" name="gz_ros2_control::GazeboSimROS2ControlPlugin">
    <!-- One or more controller YAML files -->
    <parameters>$(find my_box_bot_description)/config/controller_position.yaml</parameters>
  </plugin>
</gazebo>
```
- One `<joint>` per controlled joint, each with the interfaces its controllers claim. GazeboSimSystem knows only `position`, `velocity` and `effort`: the interface names are not free.
- `<param name="min">`/`max` describe the command range; the joint's own `<limit>` (here −0.1…0.0) still applies to the physics.
- `$(find my_box_bot_description)` is a xacro substitution: it works because the launch file passes the file through `xacro` ([[urdf-description-package]]). Use an absolute path if you load a plain URDF without xacro.
- Several `<parameters>` elements are allowed; the plugin also reads `<controller_manager_name>`, `<hold_joints>` and `<ros>` (namespace, remappings).

## The joint it moves
`laser_scan_link_joint`: prismatic, `chassis` → `laser_scan_link` along z, `<limit lower="-0.1" upper="0.0" effort="20.0" velocity="2.0"/>` (effort and velocity found by trying) and `<dynamics damping="0.1" friction="1.0"/>` so it does not run wild. An empty `laser_scan_frame` on a fixed joint marks the sensor's center. The course text calls the laser collision a cylinder; its file (and the inertia values) use a box. Full links: [[gazebo-learn-unit5-moving]].

## Humble
With gz_ros2_control on Humble the controller manager reads the URDF from the **parameter** of the node `robot_state_publisher`. The course names that node `robot_state_publisher_node`, so add `<robot_param_node>robot_state_publisher_node</robot_param_node>` inside the `<plugin>` (or keep the default node name). Docs: the [humble branch documentation](https://github.com/ros-controls/gz_ros2_control/blob/humble/doc/index.rst). Jazzy reads the `/robot_description` topic instead.

## Pitfalls
- A controller cannot claim its interface → the interface name in the URDF is not `position`/`velocity`/`effort`, or the joint is missing from `<ros2_control>`.
- Nothing loads and the log mentions an empty parameters file → wrong path in `<parameters>`.
- Joint state broadcaster plus the JointStatePublisher system on the same joints → two `/joint_states` sources; list each joint in only one.
