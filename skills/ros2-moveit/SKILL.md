---
name: ros2-moveit
description: "MoveIt 2 on ROS 2 Humble (C++): Setup Assistant, config package, MoveGroupInterface, joint/pose/Cartesian goals, gripper, kinematics plugins, pick and place, simple_grasping. Jazzy/Lyrical notes."
---
# ros2-moveit — MoveIt 2 manipulation in C++

Atomic notes for writing correct code and debugging it. **Humble is canonical**; differences for later versions are marked, never substituted. Paths are relative to this skill's folder. `[[note-id]]` means the file `<note-id>.md`; find it via the area index or a glob `**/<note-id>.md`.

## Golden rules (always apply)
1. Check the distro first. Humble: `#include <moveit/move_group_interface/move_group_interface.h>` (`.h` only). Jazzy and later: `.hpp` (`.h` still builds with an "obsolete" message) and `computeCartesianPath` without `jump_threshold`. Link `moveit_ros_planning_interface::moveit_move_group_interface` with `target_link_libraries`: it works on Humble and Lyrical has no `ament_target_dependencies` ([[moveit-humble-to-jazzy]], [[moveit-cpp-package-setup]]).
2. Simulation: start `move_group` and every MoveIt program with `use_sim_time: True` (generated launch files never set it); without it **Execute** aborts with "couldn't receive full current joint state within 1s". Real robot: `False` ([[moveit-move-group-launch-sim]]).
3. Fix the Setup Assistant output. `joint_limits.yaml`: write doubles (`100.0`, `0.0`; an integer gives "expected [double] got [integer]" and the rest of that joint's limits is skipped) and add `min_position`/`max_position` to keep IK inside ±π. `moveit_controllers.yaml`: MoveIt calls `/<name>/<action_ns>`, so names and types must match `ros2 action list` / `ros2 action info -t` ([[moveit-config-joint-limits]], [[moveit-config-controllers-yaml]]).
4. A program's node: `automatically_declare_parameters_from_overrides(true)`, the launch file passes `robot_description`, `robot_description_semantic` and `robot_description_kinematics` from `MoveItConfigsBuilder`, and a background executor spins that node (without it `getCurrentState()` and execution wait for joint states that are never processed). Missing descriptions → "Unable to construct robot model…"; no `move_group` running → the constructor waits forever ([[moveit-cpp-move-group-interface]], [[moveit-cpp-package-setup]]).
5. `plan()` and `execute()` each return a `MoveItErrorCode`: execute only a successful plan and report the execution result too. `move()` plans and executes in one blocking call. Defaults: planning time 5 s, 1 attempt, velocity/acceleration scaling 0.1 ([[moveit-cpp-move-group-interface]], [[moveit-cpp-joint-space-goal]]).
6. Targets: joint values in the group's variable order (`getVariableNames()`; start from `copyJointGroupPositions` of `getCurrentState()`); pose targets for the group's end-effector link in `getPlanningFrame()`, solved by the IK plugin of `kinematics.yaml` (KDL default, LMA alternative; restart `move_group` after a change); named targets from the SRDF. Read real values with the `rqt_joint_trajectory_controller` sliders, `tf2_echo` and `/joint_states` ([[moveit-cpp-pose-goal]], [[moveit-kinematics-plugins]], [[moveit-arm-joint-pose-tools]]).
7. Cartesian paths: `computeCartesianPath(waypoints, 0.01, 0.0, trajectory)` returns the fraction computed (−1.0 = error): execute only at 1.0. `jump_threshold` 0.0 disables the jump check: not on real hardware. Clear the waypoints before the next path. Approach and retreat with Cartesian paths; pose goals make long, unpredictable motions ([[moveit-cpp-cartesian-path]], [[moveit-approach-retreat]]).
8. Gripper: its own planning group and `MoveGroupInterface`; `setNamedTarget("open")` from the SRDF, or a joint value set by joint name (`robotiq_85_left_knuckle_joint`) rather than by index. CLI: `GripperCommand` goals to `/gripper_controller/gripper_cmd` (0.0 open, 0.8 closed); with a position interface `max_effort` is not used ([[moveit-cpp-gripper]]).
9. Pick and place: home → pose above the object → open → Cartesian approach → close → Cartesian retreat → place → open. Spawn the object first with `ros_gz_sim create -file <urdf> -name <unique name> -x … -y … -z …`, with an inertia that matches its size and mass ([[moveit-pick-and-place]], [[moveit-scene-grasp-boxes]]).
10. Object poses: `sudo apt install ros-humble-simple-grasping`. `basic_grasping_perception_node` listens on `/head_camera/depth_registered/points` (remap it to your camera) and transforms the cloud into `frame_id` (`base_link`). Call `/find_objects` with `plan_grasps: false`. Check that `objects` and `primitive_poses` are not empty, and choose the object by `primitives[0]` type and dimensions, not by position in the list ([[moveit-find-objects-action]], [[moveit-cpp-get-object-pose]], [[moveit-cpp-filter-objects]]).

## Retrieval protocol
1. Pick the area from the **Areas** table below (column "Covers").
2. Open that area's `_index.md` and choose notes by their summary.
3. Open 1–3 notes. Use their code as the template: keep the structure, adapt the names, groups, joints and poses.
4. No clear match → `grep -ril "<keyword>" notes/` (API names work best: `MoveGroupInterface`, `setJointValueTarget`, `setPoseTarget`, `setNamedTarget`, `computeCartesianPath`, `MoveItConfigsBuilder`, `action_ns`, `kinematics_solver`, `find_objects`, `GraspableObject`) and open the top hits.
5. Follow a note's `see:` links **one hop** at most. The planner overview (OMPL, Pilz, CHOMP, Servo, `moveit_py`) is ros2-core's `core-moveit2-overview`; the controllers that execute the trajectories live in ros2-control.
6. Do not open `learn/` unless the question is about the manipulation course (UR3e arm with a Robotiq 85 gripper).
7. Jazzy, Kilted, Lyrical or porting a project → open `migration/` and apply the version marks.
8. Simulation → answer with modern Gazebo (Gazebo Sim, the ros2-gazebo skill), with the distro + Gazebo pair below.
If the notes do not cover the question, read the official source for the user's distro (moveit2 and moveit2_tutorials, branch of the distro) or say that you answer from standard knowledge. Never invent APIs or flags.

## Version marks and versions
`[Humble]` Humble-only · `[≥Jazzy]` added in Jazzy (or later) · `[changed in Jazzy: …]` / `[changed in Lyrical: …]` what to use there instead · `[verify]` not confirmed by a source or a build: tell the user. Each note's `version_notes` holds the source URL and audit ID of every difference (`reports/version_audit_moveit.md`).

| Distro + Gazebo | MoveIt 2 | simple_grasping | Main differences |
|---|---|---|---|
| Humble + Fortress | 2.5.10 | 0.5.0 | canonical; `.h` headers |
| Jazzy + Harmonic | 2.12.4 | 0.5.0 | `.hpp`; `jump_threshold` overload deprecated |
| Kilted + Ionic | 2.14.3 | 0.6.0 | `ament_target_dependencies` deprecated |
| Lyrical + Jetty | 2.15.2 | 0.6.0 | `ament_target_dependencies` removed |

## Areas
<!-- INDEX:START -->
<!-- generated by tools/build_index.py — do not edit by hand -->
| Area | Notes | Open | Covers |
|---|---|---|---|
| config | 7 | `notes/config/_index.md` | MoveIt 2 configuration package: architecture (move_group, robot interface, config data), MoveIt Setup Assistant (self-collisions, virtual joint, planning groups, poses, end effector, controllers), joint_limits.yaml, moveit_controllers.yaml, move_group launch with use_sim_time, RViz2 MotionPlanning |
| planning | 11 | `notes/planning/_index.md` | Move Group C++ interface (MoveGroupInterface): joint-space, pose and named targets, plan/execute/move, gripper group, Cartesian paths (computeCartesianPath), kinematics plugins (KDL, LMA), approach/retreat, pick and place, moveit2_scripts package, objects to grasp in Gazebo |
| perception | 6 | `notes/perception/_index.md` | Object detection for grasping with simple_grasping: find_objects action (FindGraspableObjects), basic_grasping_perception node and parameters, grasping_msgs (GraspableObject, Object, SolidPrimitive), C++ action client for object poses, filtering by type and size |
| learn | 4 | `learn/_index.md` | Manipulation course for students (UR3e arm with Robotiq gripper): course map, exercises of units 2-5 and their solutions; open only for course questions |
| migration | 1 | `migration/_index.md` | The course's MoveIt code on Jazzy, Kilted and Lyrical: .hpp headers, computeCartesianPath without jump_threshold, target_link_libraries, Gazebo pairs; open for other distros |
<!-- INDEX:END -->

## Related skills
Required (install them with this skill): ros2-core (nodes, topics, actions, QoS, TF, launch, the MoveIt 2 overview), ros2-cpp (rclcpp, ament_cmake, executors, action clients), ros2-control (the controllers that execute the trajectories, `joint_trajectory_controller`, gripper action controller), ros2-urdf (the robot description the Setup Assistant loads). Named in plain text, never required: ros2-gazebo (spawning objects, simulated depth camera), ros2-perception (point clouds and PCL in Python), ros2-tf (frames, `tf2_echo`).
