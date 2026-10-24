---
id: control-urdf-tag
type: reference
owner: equipo-ros2
updated: 2026-10-24
review_by: 2027-04-22
source: manual
confidentiality: internal
title: "<ros2_control> tag: hardware plugin and params, joints with command/state interfaces, sim vs real hardware"
domain: control
area: setup
distro: jazzy
tested: false
audience: dev
summary: "URDF <ros2_control> tag: type system, <hardware><plugin> and <param>, <joint> command_interface/state_interface, min/max, GazeboSimSystem vs own hardware plugin."
tags: ["<ros2_control>", hardware, plugin, param, joint, command_interface, state_interface, min, max, GazeboSimSystem, gz_ros2_control, xacro, hardware_parameters, enforce_command_limits]
see: ["[[control-controller-config]]", "[[control-hw-template-init]]", "[[control-hw-plugin-export]]", "[[control-bringup-sim-launch]]", "[[control-bringup-hardware-launch]]", "[[control-dynamixel-plugin-urdf-launch]]", "[[urdf-xacro-workflow]]"]
requires: [ros2-core, ros2-urdf]
version_notes:
  - "jazzy: the element is <parameters>, as in the XML (the course text says <parameter>) (CONTROL-V04)"
  - "jazzy: min/max are combined with the URDF <limit> and enforced only with controller_manager enforce_command_limits: true (default false); kilted/lyrical: default true; humble: not enforced — https://github.com/ros-controls/ros2_control/blob/jazzy/hardware_interface/src/component_parser.cpp (CONTROL-V22)"
  - "jazzy: since ros2_control 4.35.0 a node named after the lower-case <ros2_control name> is created for each component — https://github.com/ros-controls/ros2_control/blob/jazzy/hardware_interface/src/hardware_component_interface.cpp (CONTROL-V20)"
  - "jazzy/harmonic: GazeboSimSystem exports only position, velocity and effort; Humble + Fortress reads the description parameter of robot_state_publisher — ros2-gazebo skill (GZ-V50, GZ-V29)"
---
# <ros2_control> tag: hardware plugin and params, joints with command/state interfaces, sim vs real hardware

**TL;DR** The robot description says which hardware component drives which joints. One `<ros2_control>` element per component, before `</robot>`: a `<hardware>` with the plugin (and its parameters), and one `<joint>` per real joint with the command and state interfaces it offers. To go from simulation to real hardware you change only this block (and the launch file).

## Simulation (rrbot in Gazebo Sim)
```xml
<ros2_control name="GazeboSimSystem" type="system">
  <hardware>
    <!-- Gazebo Sim integration plugin -->
    <plugin>gz_ros2_control/GazeboSimSystem</plugin>
  </hardware>
  <joint name="joint1">
    <command_interface name="position">
      <param name="min">-6.28</param>
      <param name="max">6.28</param>
    </command_interface>
    <state_interface name="position"/>
    <state_interface name="velocity"/>
    <state_interface name="effort"/>
  </joint>
  <joint name="joint2">
    <command_interface name="position">
      <param name="min">-6.28</param>
      <param name="max">6.28</param>
    </command_interface>
    <state_interface name="position"/>
    <state_interface name="velocity"/>
    <state_interface name="effort"/>
  </joint>
</ros2_control>
<!-- Gazebo Sim system plugin that boots the controller manager and parses the ros2_control tags -->
<gazebo>
  <plugin filename="gz_ros2_control-system" name="gz_ros2_control::GazeboSimROS2ControlPlugin">
    <!-- Controller configuration YAML file -->
    <parameters>$(find my_robot_bringup)/config/controller_configuration.yaml</parameters>
  </plugin>
</gazebo>
```
The `<gazebo>` block is read by Gazebo Sim, not by ros2_control: in simulation the controller YAML ([[control-controller-config]]) goes only into its `<parameters>` element. `$(find …)` works because the launch file runs the file through xacro. Gazebo details (interface names GazeboSimSystem exports, Humble + Fortress): ros2-gazebo skill, `gazebo-ros2-control-urdf`.

## Real hardware (the template plugin)
```xml
<ros2_control name="DemoHardware" type="system">
  <hardware>
    <plugin>my_robot_hardware_interface/RRBotSystemPositionOnlyHardware</plugin>
    <param name="example_param_hw_start_duration_sec">0.0</param>
    <param name="example_param_hw_stop_duration_sec">3.0</param>
    <param name="example_param_hw_slowdown">10.0</param>
  </hardware>
  <joint name="joint1">
    <command_interface name="position">
      <param name="min">-1</param>
      <param name="max">1</param>
    </command_interface>
    <state_interface name="position"/>
  </joint>
  <joint name="joint2">
    <command_interface name="position">
      <param name="min">-1</param>
      <param name="max">1</param>
    </command_interface>
    <state_interface name="position"/>
  </joint>
</ros2_control>
```
Without Gazebo the `<gazebo>` block is ignored, so the controller YAML comes from the launch file ([[control-bringup-hardware-launch]]).

## Elements
- `type`: `system`, `actuator` or `sensor` ([[control-hw-interface-concept]]). `name`: the component's name [≥Jazzy 4.35: also the name, in lower case, of the node created for the component].
- `<plugin>`: the plugin name declared in the package's plugin XML ([[control-hw-plugin-export]]).
- `<param>` inside `<hardware>`: values your plugin reads in `on_init()` from `info.hardware_parameters` ([[control-hw-template-init]]); `<param>` inside `<joint>` (for example a servo `id`) lands in that joint's `parameters`.
- `<command_interface>`/`<state_interface>`: what each joint accepts and reports (position, velocity, effort…). A joint can offer several command interfaces (position and velocity); state interfaces are what `joint_state_broadcaster` publishes.
- `min`/`max` of a command interface: limits combined with the URDF `<limit>` (the most restrictive wins). [Humble: not enforced] [≥Jazzy: enforced only with `enforce_command_limits: true` in the controller manager parameters, default `false`] [changed in Kilted/Lyrical: default `true`].

## Pitfalls
- Joints and interfaces must be the ones your plugin accepts: the template returns `ERROR` from `on_init()` unless each joint has exactly one `position` command and one `position` state interface.
- Changed the xacro and relaunched, but the robot in Gazebo is still the old one → delete the old model before spawning the new one.
- The controller's `joints` must be in this block, not only in the URDF.
