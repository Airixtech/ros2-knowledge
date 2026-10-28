---
id: moveit-config-joint-limits
type: reference
owner: equipo-ros2
updated: 2026-10-28
review_by: 2027-04-26
source: manual
confidentiality: internal
title: "joint_limits.yaml of a MoveIt config: scaling factors, integer vs double values, position limits per joint"
domain: moveit
area: config
distro: humble
tested: false
audience: dev
summary: "config/joint_limits.yaml: default_velocity_scaling_factor 0.1, max_velocity 100 vs 100.0 (expected [double] got [integer]), min_position/max_position to limit IK."
tags: [joint_limits.yaml, robot_description_planning, default_velocity_scaling_factor, default_acceleration_scaling_factor, has_velocity_limits, max_velocity, has_acceleration_limits, max_acceleration, has_position_limits, min_position, max_position, expected double got integer, ParameterTypeException, UR3e, Robotiq 85]
see: ["[[moveit-setup-assistant-controllers]]", "[[moveit-kinematics-plugins]]", "[[moveit-cpp-move-group-interface]]", "[[core-param-yaml-cli]]"]
requires: [ros2-core]
version_notes:
  - "humble: the Setup Assistant writes double values through yaml-cpp, which prints 100.0 as 100 and 0.0 as 0 — https://github.com/moveit/moveit2/blob/humble/moveit_setup_assistant/moveit_setup_framework/src/srdf_config.cpp (MOVEIT-V11)"
  - "humble: move_group reads robot_description_planning.joint_limits.<joint>.max_velocity as a double; an integer raises 'expected [double] got [integer]', logged as 'When getting the parameter …', and the rest of that joint's limits is skipped; same on jazzy and main — https://github.com/moveit/moveit2/blob/humble/moveit_ros/planning/robot_model_loader/src/robot_model_loader.cpp (MOVEIT-V11)"
  - "humble: min_position/max_position are read directly and set the position limit; has_position_limits is not read; continuous joints refuse position limits — https://github.com/moveit/moveit2/blob/humble/moveit_ros/planning/robot_model_loader/src/robot_model_loader.cpp (MOVEIT-V11)"
---
# joint_limits.yaml: scaling, integer vs double, position limits

**TL;DR** `config/joint_limits.yaml` overrides or adds to the joint limits of the URDF. Two edits make the course package work well: write every number as a double (`100.0`, `0.0`), and add position limits to the arm joints so IK and planning stay inside ±π instead of wandering through ±2π.

## Why `100` breaks and `100.0` works
The Setup Assistant writes `max_velocity: 100` and `max_acceleration: 0` for joints whose URDF limits are whole numbers (yaml-cpp prints the double 100.0 as `100`). YAML reads them as integers, `move_group` keeps the parameter type, and MoveIt reads `robot_description_planning.joint_limits.<joint>.max_velocity` as a double: rclcpp throws `expected [double] got [integer]`, MoveIt logs `When getting the parameter …` and skips the remaining limits of that joint (MOVEIT-V11). So change `100` → `100.0`. `max_acceleration: 0` → `0.0` is the same habit; it is only read when `has_acceleration_limits` is `true`.

## Final file (course robot)
```yaml
# joint_limits.yaml allows the dynamics properties specified in the URDF to be overwritten or augmented as needed

# For beginners, we downscale velocity and acceleration limits.
# You can always specify higher scaling factors (<= 1.0) in your motion requests.  # Increase the values below to 1.0 to always move at maximum speed.
default_velocity_scaling_factor: 0.1
default_acceleration_scaling_factor: 0.1

# Specific joint properties can be changed with the keys [max_position, min_position, max_velocity, max_acceleration]
# Joint limits can be turned off with [has_velocity_limits, has_acceleration_limits]
joint_limits:
  elbow_joint:
    has_velocity_limits: true
    max_velocity: 3.1415926535897931
    has_acceleration_limits: false
    max_acceleration: 0.0
    has_position_limits: true
    min_position: -3.1415926535897931
    max_position: 3.1415926535897931
  robotiq_85_left_finger_tip_joint:
    has_velocity_limits: true
    max_velocity: 100.0
    has_acceleration_limits: false
    max_acceleration: 0.0
  robotiq_85_left_inner_knuckle_joint:
    has_velocity_limits: true
    max_velocity: 100.0
    has_acceleration_limits: false
    max_acceleration: 0.0
  robotiq_85_left_knuckle_joint:
    has_velocity_limits: true
    max_velocity: 0.5
    has_acceleration_limits: false
    max_acceleration: 0.0
  robotiq_85_right_finger_tip_joint:
    has_velocity_limits: true
    max_velocity: 100.0
    has_acceleration_limits: false
    max_acceleration: 0.0
  robotiq_85_right_inner_knuckle_joint:
    has_velocity_limits: true
    max_velocity: 100.0
    has_acceleration_limits: false
    max_acceleration: 0.0
  robotiq_85_right_knuckle_joint:
    has_velocity_limits: true
    max_velocity: 100.0
    has_acceleration_limits: false
    max_acceleration: 0.0
  shoulder_lift_joint:
    has_velocity_limits: true
    max_velocity: 3.1415926535897931
    has_acceleration_limits: false
    max_acceleration: 0.0
    has_position_limits: true
    min_position: -3.1415926535897931
    max_position: 3.1415926535897931
  shoulder_pan_joint:
    has_velocity_limits: true
    max_velocity: 3.1415926535897931
    has_acceleration_limits: false
    max_acceleration: 0.0
    has_position_limits: true
    min_position: -3.1415926535897931
    max_position: 3.1415926535897931
  wrist_1_joint:
    has_velocity_limits: true
    max_velocity: 6.2831853071795862
    has_acceleration_limits: false
    max_acceleration: 0.0
    has_position_limits: true
    min_position: -3.1415926535897931
    max_position: 3.1415926535897931
  wrist_2_joint:
    has_velocity_limits: true
    max_velocity: 6.2831853071795862
    has_acceleration_limits: false
    max_acceleration: 0.0
    has_position_limits: true
    min_position: -3.1415926535897931
    max_position: 3.1415926535897931
  wrist_3_joint:
    has_velocity_limits: true
    max_velocity: 6.2831853071795862
    has_acceleration_limits: false
    max_acceleration: 0.0
    has_position_limits: true
    min_position: -3.1415926535897931
    max_position: 3.1415926535897931
```
The generated file differs only in: `max_velocity: 100` and `max_acceleration: 0` (integers), and no `has_position_limits` / `min_position` / `max_position` lines. Rebuild after editing (`colcon build`, then source).

## What the keys do
- `default_velocity_scaling_factor` / `default_acceleration_scaling_factor` (0.1): every motion request runs at 10 % of the limits unless it asks for more (≤ 1.0); a `MoveGroupInterface` program uses 0.1 too when it does not get these parameters ([[moveit-cpp-move-group-interface]]).
- `min_position` / `max_position`: tighter than the URDF (UR joints allow ±2π); they keep IK solutions and plans away from unnecessarily long joint motions, the course's reason for adding them. MoveIt reads them directly (they set the position limit; `has_position_limits` itself is not read); continuous joints refuse position limits (MOVEIT-V11).

## Pitfalls
- A whole number anywhere a double is expected (`max_velocity`, `min_position`) → `expected [double] got [integer]` in the `move_group` log and the joint keeps its URDF limits.
- Position limits narrower than the poses you use (the named `home`, the IK target) make planning fail for those goals.
