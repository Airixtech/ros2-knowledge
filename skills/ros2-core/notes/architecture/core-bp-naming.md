---
id: core-bp-naming
title: "Naming conventions (REP 144/105) & package rules"
domain: core
area: architecture
distro: humble
tested: false
audience: dev
summary: "Naming rules for packages, nodes, topics, services, actions, frames, types, fields and parameters; package layout and dependency rules."
tags: [naming, REP 144, REP 105, conventions, package layout]
see: ["[[core-pkg-workspace]]", "[[core-tf-basics]]", "[[core-iface-package]]", "[[core-pkg-dependencies]]"]
requires: []
version_notes: []
---
# Naming conventions (REP 144/105) & package rules

**TL;DR** Use `snake_case` for packages, nodes, topics and parameters, and `PascalCase` for message types. Prefer relative names with remaps or namespaces over hard-coded absolute "magic strings".

## Naming (REP 144 / 105)
| Element | Convention | Good | Bad |
|---|---|---|---|
| Package | `snake_case` `[a-z0-9_]`, starts with letter | `laser_filters` | `MyPkg`, `my-pkg`, `2dlidar` |
| Node | `snake_case` role noun | `path_planner` | `Node1`, `test` |
| Topic | lowercase, `/ns/descriptive` | `/robot1/camera/image_raw`, `/scan` | `/Data`, `/output1` |
| Service | verb + object | `/get_map`, `/spawn_entity` | `/map_service` |
| Action | task noun | `/navigate_to_pose` | `/do_navigation` |
| TF frame | lowercase standard | `map`, `odom`, `base_link`, `camera_optical_frame` | `BaseLink` |
| Msg type / field | `PascalCase` / `snake_case` | `PoseStamped.position` | `pose_stamped.msg`, `myField` |
| Parameter | `snake_case`, hierarchical `.` | `controller.max_velocity` | `MaxVel` |
Use relative names + remap/namespace, and avoid hard-coded absolute "magic strings" ([[core-ros-args]]).

## Package rules
- Interfaces live only in a dedicated `*_interfaces` ament_cmake pkg ([[core-iface-package]]).
- ament_python for pure-Python prototypes. ament_cmake for C++, real-time or mixed packages.
- Layout: `launch/ config/ urdf/ meshes/ rviz/ test/`. Commit only `src/`.
- Declare every dependency in package.xml: `<depend>` for ROS deps, `<exec_depend>` for pure-Python runtime ([[core-pkg-dependencies]]).

## Pitfalls
- A package name with a dash or capital letters fails `ros2 pkg create` and colcon conventions.
- Frame names with a leading `/` (ROS 1 habit) do not match `base_link` in tf2.
