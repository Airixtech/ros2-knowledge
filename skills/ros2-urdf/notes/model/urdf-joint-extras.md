---
id: urdf-joint-extras
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "mimic, dynamics, safety_controller, calibration"
domain: urdf
area: model
distro: humble
tested: false
audience: dev
summary: "Optional joint elements: <mimic> (multiplier, offset), <dynamics> damping/friction, <safety_controller> soft limits, <calibration> rising/falling, check_urdf errors."
tags: [mimic, multiplier, offset, dynamics, damping, friction, safety_controller, soft_lower_limit, k_velocity, calibration, rising, falling, check_urdf]
see: ["[[urdf-joints]]", "[[urdf-joint-state-publisher]]", "[[urdf-learn-unit2-urdfbot]]"]
requires: [ros2-core]
version_notes:
  - "humble: a mimic joint gets no slider in joint_state_publisher and its value multiplier*parent+offset is not clamped to any limit; its own <limit> is needed only because the parser requires it — https://github.com/ros/joint_state_publisher/blob/humble/joint_state_publisher/joint_state_publisher/joint_state_publisher.py (URDF-V06)"
  - "humble: check_urdf message 'Joint [x] is of type REVOLUTE but it does not specify limits' — https://github.com/ros/urdfdom/blob/humble/urdf_parser/src/joint.cpp (URDF-V28)"
  - "humble: <calibration> reads only rising and falling (reference_position is ignored) — https://github.com/ros/urdfdom/blob/humble/urdf_parser/src/joint.cpp (URDF-V30, URDF-V50)"
---
# mimic, dynamics, safety_controller, calibration

**TL;DR** Optional children of `<joint>`. `<mimic>` couples a joint to another (one actuator, two fingers); `<dynamics>` sets joint damping and friction for simulators; `<safety_controller>` and `<calibration>` describe soft limits and reference switches. Check the file with `check_urdf`.

## mimic
```xml
<joint name="upper_arm_r_link_to_claw_b_r_link_joint" type="revolute">
  <origin xyz="0 0 -0.065" rpy="-1.57 0 1.57"/>
  <parent link="lower_arm_r_link"/>
  <child link="claw_b_r_link"/>
  <axis xyz="0 0 1"/>
  <limit effort="100" velocity="1.0" lower="0.0" upper="0.0"/>   <!-- required by the parser -->
  <mimic joint="upper_arm_r_link_to_claw_a_r_link_joint" multiplier="1.0" offset="0.0"/>
</joint>
```
- `value = multiplier · other_joint_value + offset`; `joint` is required, `multiplier` defaults to 1, `offset` to 0 (rad or m). `offset="-0.8"` shifts it, `multiplier="0.1"` makes it move ten times less.
- Put `<mimic>` in the **following** joint. joint_state_publisher_gui then shows no slider for it and computes its value from the leader. That value is **not** clamped to any limit; the follower's `<limit>` is there only because revolute/prismatic joints must have one:
```text
$ check_urdf src/urdfbot_description/urdf/urdfbot_simple.urdf
Error:   Joint [upper_arm_r_link_to_claw_b_r_link_joint] is of type REVOLUTE but it does not specify limits
Error:   joint xml is not initialized correctly
ERROR: Model Parsing the xml failed
```
`check_urdf` (package `liburdfdom-tools`) also prints the link tree when the file is valid ([[core-xacro]]).

## dynamics (simulation)
```xml
<dynamics damping="0.1" friction="0.05"/>
```
`damping` in N·s/m (prismatic) or N·m·s/rad (revolute); `friction` = static friction in N or N·m. Both default to 0.

## safety_controller
```xml
<safety_controller soft_lower_limit="-1.4" soft_upper_limit="1.4" k_position="100" k_velocity="10"/>
```
`soft_lower_limit`/`soft_upper_limit` (default 0): where a safety controller starts limiting the position, inside `lower`/`upper`. `k_position` (default 0) relates position and velocity limits; `k_velocity` (**required**) relates effort and velocity limits. joint_state_publisher narrows its sliders to the soft limits (`use_smallest_joint_limits`, default true).

## calibration
```xml
<joint name="base_link_to_head_link_joint" type="revolute">
  …
  <calibration rising="1.5" falling="-1.5"/>
</joint>
```
Reference positions for joints with relative encoders (homing). Both are positions met while the joint moves in the **positive** direction: `rising` triggers the off → on edge of the reference switch, `falling` the on → off edge. Other attributes (e.g. `reference_position`) are ignored by the parser.

## Pitfalls
- A mimic chain that loops → joint_state_publisher logs "Found an infinite recursive mimic chain".
- `<dynamics>` values change simulated behaviour only; RViz ignores them.
- Values for `safety_controller` above are an example, not defaults.
