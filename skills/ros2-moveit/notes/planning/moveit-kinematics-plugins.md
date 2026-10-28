---
id: moveit-kinematics-plugins
type: reference
owner: equipo-ros2
updated: 2026-10-28
review_by: 2027-04-26
source: manual
confidentiality: internal
title: "Kinematics plugins: kinematics.yaml, KDL (default) vs LMA, FK vs IK planning, kinematics_plugin_trajectory.cpp"
domain: moveit
area: planning
distro: humble
tested: false
audience: dev
summary: "config/kinematics.yaml kinematics_solver: kdl_kinematics_plugin/KDLKinematicsPlugin (default) or lma_kinematics_plugin/LMAKinematicsPlugin; search resolution, timeout; restart move_group."
tags: [kinematics plugin, kinematics.yaml, kinematics_solver, KDLKinematicsPlugin, kdl_kinematics_plugin, LMAKinematicsPlugin, lma_kinematics_plugin, CachedKDLKinematicsPlugin, kinematics_solver_search_resolution, kinematics_solver_timeout, inverse kinematics, IK, forward kinematics, FK, kinematics_plugin_trajectory.cpp]
see: ["[[moveit-setup-assistant-model]]", "[[moveit-cpp-pose-goal]]", "[[moveit-approach-retreat]]", "[[moveit-cpp-package-setup]]", "[[moveit-learn-unit4]]"]
requires: [ros2-core, ros2-cpp]
version_notes:
  - "humble: moveit_kinematics provides kdl_kinematics_plugin/KDLKinematicsPlugin, lma_kinematics_plugin/LMAKinematicsPlugin, cached_ik_kinematics_plugin/CachedKDLKinematicsPlugin, srv_kinematics_plugin/SrvKinematicsPlugin — https://github.com/moveit/moveit2/tree/humble/moveit_kinematics (MOVEIT-V30)"
  - "humble: config files are read when move_group starts: rebuild and restart it after editing kinematics.yaml (MOVEIT-V29)"
---
# Kinematics plugins

**TL;DR** Planning to an end-effector pose needs inverse kinematics (IK), which MoveIt gets from the **kinematics plugin** of the planning group, set in `config/kinematics.yaml`. The Setup Assistant puts the default, `kdl_kinematics_plugin/KDLKinematicsPlugin`. Swap it (e.g. `lma_kinematics_plugin/LMAKinematicsPlugin`), rebuild, restart `move_group`, and compare the motions.

## Joint goals use FK, pose goals use IK
A joint-space goal needs no IK: forward kinematics (FK) gives the end-effector pose from the joints. A pose goal needs IK, and when several joint solutions reach the same pose the arm sometimes takes an unnecessarily complicated trajectory ([[moveit-approach-retreat]]).

## `config/kinematics.yaml` with LMA (exercise 4.3)
```yaml
ur_manipulator:
  #kinematics_solver: kdl_kinematics_plugin/KDLKinematicsPlugin
  kinematics_solver: lma_kinematics_plugin/LMAKinematicsPlugin
  kinematics_solver_search_resolution: 0.0050000000000000001
  kinematics_solver_timeout: 0.0050000000000000001
```
The KDL line is commented out and LMA added (a plugin based on KDL's `ChainIkSolverPos_LMA`, a Levenberg–Marquardt solver). `moveit_kinematics` also ships `cached_ik_kinematics_plugin/CachedKDLKinematicsPlugin` and `srv_kinematics_plugin/SrvKinematicsPlugin` (MOVEIT-V30); you can also write your own plugin for your robot, which can change the IK solutions a lot.

Then:
```bash
cd ~/ros2_ws
colcon build
source install/setup.bash
ros2 launch my_moveit_config move_group.launch.py
```
(restart `move_group` so it reads the file again, MOVEIT-V29).

## `src/kinematics_plugin_trajectory.cpp`: changes against `joint_space_trajectory.cpp`
Base: the executing version in [[moveit-cpp-joint-space-goal]]. The program does two things: plans to **home** with a joint goal (FK, no plugin), then to the **pregrasp** pose with a pose goal (IK, with the plugin).
1. Adds `setup_goal_pose_target()` ([[moveit-cpp-pose-goal]]).
2. `execute_trajectory_plan()`: "Going to Home Position..." with the joint target (0, −2.3562, 1.5708, −1.5708, −1.5708, 0), then "Going to Pregrasp Position..." with `setup_goal_pose_target(+0.343, +0.132, +0.264, -1.000, +0.000, +0.000, +0.000)`, both planned and executed.
3. Class `KinematicsPluginTrajectory`, node `"kinematics_plugin_trajectory"`, logs "Kinematics Plugin Trajectory".

Launch file `launch/kinematics_plugin_trajectory.launch.py` (template of [[moveit-cpp-package-setup]]), CMake block, build, and run it several times, before and after changing the plugin:
```bash
ros2 launch moveit2_scripts kinematics_plugin_trajectory.launch.py
```
Some runs solve the IK easily, others produce an unnecessarily complex trajectory. KDL and LMA give similar results for this arm: the course expects no large difference.

## Pitfalls
- The programs must load the same kinematics: the launch file passes `moveit_config.robot_description_kinematics` ([[moveit-cpp-package-setup]]).
