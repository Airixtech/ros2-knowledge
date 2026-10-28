---
id: moveit-humble-to-jazzy
type: reference
owner: equipo-ros2
updated: 2026-10-28
review_by: 2027-04-26
source: manual
confidentiality: internal
title: "MoveIt course code from Humble to Jazzy and Lyrical"
domain: moveit
area: migration
distro: humble
tested: false
audience: dev
summary: "Porting the MoveIt course code: .hpp headers, computeCartesianPath without jump_threshold, target_link_libraries for Lyrical, Gazebo pairs, simple_grasping releases."
tags: [migration, jazzy, kilted, lyrical, move_group_interface.hpp, computeCartesianPath, jump_threshold, ament_target_dependencies, target_link_libraries, moveit_py, ros_gz_sim create, Gazebo/Red, simple_grasping, MoveIt 2.12, MoveIt 2.15]
see: ["[[moveit-cpp-move-group-interface]]", "[[moveit-cpp-cartesian-path]]", "[[moveit-cpp-package-setup]]", "[[moveit-scene-grasp-boxes]]", "[[core-humble-to-jazzy]]", "[[core-jazzy-to-lyrical]]"]
requires: [ros2-core]
version_notes:
  - "sources: reports/version_audit_moveit.md (MOVEIT-V14, V16, V17, V33, V34, V37); MoveIt releases from ros/rosdistro distribution.yaml — https://github.com/ros/rosdistro/blob/master/jazzy/distribution.yaml"
---
# MoveIt course code: Humble → Jazzy → Lyrical

**TL;DR** The course's C++ programs build on Jazzy with deprecation messages only (`.h` headers, the `computeCartesianPath` overload with `jump_threshold`). Lyrical removes `ament_target_dependencies`: link the MoveIt targets with `target_link_libraries`, which already works on Humble. The rest is the Gazebo version and package versions. `MOVEIT-Vxx` = row in the repo's `reports/version_audit_moveit.md`.

| Area | Humble | Jazzy | Kilted / Lyrical | Ref |
|---|---|---|---|---|
| MoveIt 2 release | 2.5.10 | 2.12.4 | 2.14.3 / 2.15.2 | baseline |
| C++ headers | `moveit/move_group_interface/move_group_interface.h` | `.hpp`; `.h` compiles with "`.h` header is obsolete" (MoveIt 2.12.0, #3113) | same | V14 |
| `computeCartesianPath(waypoints, eef_step, jump_threshold, trajectory)` | current | deprecated ("Drop jump_threshold", 2.12.0): `computeCartesianPath(waypoints, eef_step, trajectory)` | same | V16 |
| CMake | `ament_target_dependencies(...)` | same | K: deprecated · Lyrical: **removed** → `target_link_libraries(<exe> moveit_ros_planning_interface::moveit_move_group_interface moveit_ros_planning_interface::moveit_planning_scene_interface rclcpp::rclcpp)` (namespaced targets exist on Humble too) [verify] | V17 |
| Python API | `moveit_py` 2.5.10 | 2.12.4 | 2.14.3 / 2.15.2 | V02 |
| Setup Assistant `joint_limits.yaml` | integers (`100`, `0`) break the double limits | same writer and reader | same | V11 |
| `use_sim_time` in generated launch files | not handled | not handled | not handled | V19 |
| Simulation | Fortress, `ros_gz_sim create` | Harmonic, same flags | Ionic / Jetty, same flags | V33 |
| `<material>Gazebo/Red</material>` | gz-sim 6: no lookup [verify] | gz-sim 8: mapped with a warning | — | V34 |
| `simple_grasping` / `grasping_msgs` (apt) | 0.5.0 / 0.4.0 | 0.5.0 / 0.5.0 | 0.6.0 / 0.5.0 | V37 |
| `ros2_controllers` (gripper action controller, `rqt_joint_trajectory_controller`) | 2.54.1 | 4.43.0 | 5.18.0 / 6.10.0 | V31 |
| PCL (`libpcl-dev`) | 1.12.1 | 1.14.0 | 1.14.0 / 1.15.1 | V07 |

## Porting checklist
1. Include the `.hpp` headers (Jazzy and later).
2. Drop the `jump_threshold_` argument of `computeCartesianPath` (Jazzy and later); keep checking the returned fraction ([[moveit-cpp-cartesian-path]]).
3. Replace `ament_target_dependencies` with `target_link_libraries` and namespaced targets (required on Lyrical, fine on Humble, [[moveit-cpp-package-setup]]).
4. Spawn objects with `ros_gz_sim create` for the distro's Gazebo ([[moveit-scene-grasp-boxes]]); give simulated nodes `use_sim_time`.
5. Platform changes of the distros themselves (Ubuntu, C++20 and CMake 4 in Lyrical, removed APIs): [[core-humble-to-jazzy]], [[core-jazzy-to-lyrical]].
