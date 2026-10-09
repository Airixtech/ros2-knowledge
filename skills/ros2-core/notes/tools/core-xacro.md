---
id: core-xacro
title: "Xacro properties/macros/args & URDF validation"
domain: core
area: tools
distro: humble
tested: false
audience: dev
summary: "Xacro properties, macros, args, includes and expansion; validating and visualizing URDF (check_urdf, graphviz, urdf_tutorial)."
tags: [xacro, macro, property, check_urdf, urdf_to_graphviz, rviz2]
see: ["[[core-urdf-basics]]", "[[core-robot-state-publisher]]", "[[core-multi-robot-namespacing]]"]
requires: []
version_notes: []
---
# Xacro properties/macros/args & URDF validation

**TL;DR** Xacro adds `property`, `macro`, `arg` and `include` to URDF. Expand it with the `xacro` command, at build time or in launch. Validate the result with `check_urdf` before debugging in RViz.

## Xacro (variables, macros, args)
```xml
<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro" name="my_robot">
  <xacro:arg name="ns" default=""/>
  <xacro:property name="wheel_radius" value="0.05"/>
  <xacro:macro name="wheel" params="name y">
    <link name="${name}">
      <visual><geometry><cylinder radius="${wheel_radius}" length="0.02"/></geometry></visual>
    </link>
    <joint name="joint_${name}" type="continuous">
      <parent link="base_link"/><child link="${name}"/>
      <origin xyz="0 ${y} 0" rpy="${-pi/2} 0 0"/><axis xyz="0 0 1"/>
    </joint>
  </xacro:macro>
  <link name="base_link"/>
  <xacro:wheel name="wheel_left" y="0.17"/>
  <xacro:wheel name="wheel_right" y="-0.17"/>
  <xacro:include filename="$(find my_robot_description)/urdf/sensors.xacro"/>
</robot>
```
```bash
xacro robot.urdf.xacro > robot.urdf          # expand
xacro robot.urdf.xacro ns:=robot1 > r1.urdf  # with arg (multi-robot frame prefix: $(arg ns)/base_link)
```
Multi-robot prefixes: [[core-multi-robot-namespacing]].

## Visualize & validate
```bash
rviz2       # Add RobotModel (Description Topic: /robot_description) + TF; Fixed Frame: base_link
check_urdf robot.urdf                 # pkg liburdfdom-tools
urdf_to_graphviz robot.urdf           # tree diagram (pdf); older name: urdf_to_graphiz
ros2 launch urdf_tutorial display.launch.py model:=/abs/path/robot.urdf   # pkg ros-humble-urdf-tutorial
```
RViz needs `robot_description` published ([[core-robot-state-publisher]]).

## Pitfalls
- `$(find pkg)` only resolves if `pkg` is built and sourced, and its `urdf/` dir is installed in share.
- An expression typo (`${-pi/2}` vs `-${pi/2}`) expands silently to a wrong value. Check the expanded URDF.
