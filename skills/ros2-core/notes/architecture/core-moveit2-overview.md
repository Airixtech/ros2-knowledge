---
id: core-moveit2-overview
type: reference
owner: equipo-ros2
updated: 2026-10-09
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "MoveIt2 overview & MoveGroupInterface"
domain: core
area: architecture
distro: humble
tested: false
audience: dev
summary: "move_group, planners available in Humble, MoveGroupInterface snippet, URDF/SRDF requirements, Servo, perception; Iron+ additions."
tags: [MoveIt2, move_group, MoveGroupInterface, OMPL, Pilz, moveit_py, Servo]
see: ["[[core-ros2-control-overview]]", "[[core-urdf-basics]]", "[[core-arch-layers]]"]
requires: []
version_notes:
  - "humble: no parallel (multi-pipeline) planning and no STOMP planner plugin; both from Iron — https://github.com/moveit/moveit2/tree/humble/moveit_planners (V53)"
  - "humble: moveit_py binary exists (ros-humble-moveit-py, MoveIt 2.5.x); Python API tutorial only in main docs — https://github.com/ros/rosdistro/blob/master/humble/distribution.yaml (V59)"
---
# MoveIt2 overview & MoveGroupInterface

**TL;DR** `move_group` loads URDF + SRDF + kinematics + planning pipelines. In Humble, use `MoveGroupInterface` (C++), `MoveItCpp` or `moveit_py`, with OMPL, Pilz or CHOMP. Parallel planning and STOMP need Iron+. Seed note for a future `ros2-moveit` skill.

## Planning stack
- `move_group` loads URDF + SRDF + kinematics + planning pipelines. Humble pipelines: OMPL (default RRTConnect), Pilz (PTP/LIN/CIRC), CHOMP.
- [changed in Jazzy (since Iron): parallel multi-pipeline planning in MoveItCpp, and the STOMP planner plugin]
- APIs: `MoveGroupInterface` (C++), `MoveItCpp`, `moveit_py` (Python). `moveit_py` has a Humble binary (`sudo apt install ros-humble-moveit-py`), but its tutorial lives in the main (Rolling) docs.
```cpp
moveit::planning_interface::MoveGroupInterface arm(node, "manipulator");
arm.setStartStateToCurrentState();
arm.setPlanningTime(2.0);                  // OMPL >= 1 s
arm.setMaxVelocityScalingFactor(0.3);
arm.setNamedTarget("home");                // SRDF group_state
arm.move();                                // plan + execute
```

## Model requirements & runtime
- URDF/SRDF: limits are mandatory on revolute/prismatic joints (no zero effort/velocity) · realistic inertia and damping · collision meshes <500 tris or primitives · SRDF groups, complete group_states, `virtual_joint`, dense disable_collisions.
- Servo (100+ Hz Twist/JointJog → forward_position_controller) for continuous teleop. Never call `plan()` inside fast sensor callbacks.
- Perception: octomap updater + self-filter; attached objects with `touch_links`.
Controllers that execute the trajectories: [[core-ros2-control-overview]].
