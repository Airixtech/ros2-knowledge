---
id: urdf-xacro-macros
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "Xacro macros with params and defaults, if/unless, include and file splitting"
domain: urdf
area: workflow
distro: humble
tested: false
audience: dev
summary: "xacro:macro with params and name:=default, calls with matching attributes, xacro:if/unless, $(arg) vs ${property}, xacro:include and sim-only files, macros plus conditions."
tags: [xacro:macro, params, default, macro call, xacro:if, xacro:unless, xacro:arg, $(arg), xacro:property, xacro:include, $(find), file splitting, use_sim]
see: ["[[urdf-xacro-workflow]]", "[[core-xacro]]", "[[urdf-inertia]]", "[[core-multi-robot-namespacing]]"]
requires: [ros2-core]
version_notes:
  - "humble: a call must use exactly the macro's parameter names; extra ones give 'Invalid parameter', missing ones 'Undefined parameters [...]' — https://github.com/ros/xacro/blob/ros2/xacro/__init__.py (URDF-V09)"
  - "humble: an arg is read with $(arg name); ${name} reads a property — https://github.com/ros/xacro/blob/ros2/xacro/substitution_args.py (URDF-V10)"
  - "humble: $(arg x) needs <xacro:arg name=\"x\" default=\"…\"/> unless every caller passes x:=… (URDF-V11)"
  - "humble: $(find pkg) needs the package built, sourced and its urdf/ installed (URDF-V43)"
---
# Xacro macros with params and defaults, if/unless, include and file splitting

**TL;DR** A macro is a named block of URDF that is pasted (with its parameters filled in) wherever it is called. Conditions keep or drop blocks when the file is expanded. Includes split a robot into files, typically the simulator tags in a file of their own.

## Macros
```xml
<!-- Wheel Macro -->
<xacro:macro name="wheel" params="wheel_name">
  <link name="${wheel_name}">
    <visual>
      <origin rpy="0 1.5707 1.5707" xyz="0 0 0"/>
      <geometry><cylinder length="${wheel_width}" radius="${wheel_radius}"/></geometry>
    </visual>
    <collision>
      <origin rpy="0 1.5707 1.5707" xyz="0 0 0"/>
      <geometry><cylinder length="${wheel_width}" radius="${wheel_radius}"/></geometry>
    </collision>
    <inertial>
      <origin rpy="0 1.5707 1.5707" xyz="0 0 0"/>
      <mass value="0.05"/>
      <inertia ixx="1.531666666666667e-05" ixy="0" ixz="0" iyy="1.531666666666667e-05" iyz="0" izz="3.0625000000000006e-05"/>
    </inertial>
  </link>
</xacro:macro>

<!-- Wheel Left -->
<xacro:wheel wheel_name="left_wheel"/>
<!-- Wheel Right -->
<xacro:wheel wheel_name="right_wheel"/>
```
- Unique `name`; no parameters → `<xacro:caster_wheel/>`. Parameters are space-separated (`params="name y mass"`), defaults `name:=value`. Properties used inside (`wheel_width`, `wheel_radius`) come from the enclosing file; inertia macros: [[urdf-inertia]].
- Call with exactly the `params` names. The course's first example (`wheel_link_name=` for `params="wheel_name"`, undefined `${wheel_length}`) stops xacro with `Invalid parameter`, `Undefined parameters [wheel_name]` and `name 'wheel_length' is not defined`; the macro above is its exercise solution.

## Conditions
```xml
<xacro:arg name="indoor_robot" default="true"/>
…
<xacro:if value="$(arg indoor_robot)">
  <gazebo><plugin filename="gz-sim-imu-system" name="gz::sim::systems::Imu"></plugin></gazebo>
</xacro:if>
<xacro:unless value="$(arg indoor_robot)">
  <gazebo><plugin filename="gz-sim-navsat-system" name="gz::sim::systems::NavSat"></plugin></gazebo>
</xacro:unless>
```
- Same pattern for parts of the robot: `<xacro:if value="$(arg include_laser)">` around the laser joint and link adds the sensor only when asked.
- `xacro:if` keeps the block when `value` is true (or 1), `xacro:unless` when it is false. Set the arg from outside: `xacro robot.xacro indoor_robot:=false`.
- `$(arg indoor_robot)` reads an **arg**; `${indoor_robot}` reads a **property**. The course writes `${indoor_robot}` right after declaring the arg: that fails unless a property of that name exists.

Macros with conditions: give the macro a parameter with a default and test it inside; pass the value from a property at the call.
```xml
<xacro:property name="indoor_robot" value="true"/>
<xacro:macro name="robot_sensors" params="indoor_robot:=true">
  <xacro:if value="${indoor_robot}">
    …
  </xacro:if>
</xacro:macro>
<xacro:robot_sensors indoor_robot="${indoor_robot}"/>
```

## Includes and file splitting
```xml
<xacro:arg name="use_sim" default="true"/>
<!-- Include Gazebo specific tags (without the if: always) -->
<xacro:if value="$(arg use_sim)">
  <xacro:include filename="$(find my_box_bot_description)/urdf/box_bot.gazebo.xacro"/>
</xacro:if>
```
- The included file is a complete xacro document (`<?xml …?>`, `<robot xmlns:xacro=…>…</robot>`) whose contents are pasted in place of the include; wrap them in a macro (`gazebo_elements`) to place them with one call. Typical split: kinematics and visuals in the main file, simulator tags and plugins in `<robot>.gazebo.xacro`.

## Pitfalls
- `$(find pkg)` fails → the package is not built and sourced, or its `urdf/` folder is not installed.
- `Undefined substitution argument` → `$(arg x)` without `<xacro:arg name="x" default="…"/>` and without `x:=…` on the command line.
- `unknown macro name: xacro:…` → typo in the call, or the macro is called before its definition (or its include): define first, then call.
