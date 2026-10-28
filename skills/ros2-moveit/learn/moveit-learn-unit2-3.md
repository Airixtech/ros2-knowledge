---
id: moveit-learn-unit2-3
type: reference
owner: equipo-ros2
updated: 2026-10-28
review_by: 2027-04-26
source: manual
confidentiality: internal
title: "Units 2-3 exercises: MoveIt package, RViz2 planning, C++ programs, double motion solution"
domain: moveit
area: learn
distro: humble
tested: false
audience: students
order: 2
summary: "Exercises 2.1-2.3 (my_moveit_config, joint_limits, moveit_controllers, use_sim_time) and 3.1-3.6 (joint, pose, execute, double motion, gripper, approach & retreat)."
tags: [course, exercises, my_moveit_config, moveit2_scripts, double_motion_trajectory.cpp, joint_space_trajectory, goal_pose_trajectory, gripper_control, approach_retreat_trajectory, unit 2, unit 3]
see: ["[[moveit-learn-start-here]]", "[[moveit-learn-unit4]]", "[[moveit-cpp-joint-space-goal]]", "[[moveit-setup-assistant-model]]"]
requires: [ros2-core]
version_notes:
  - "course: double_motion_trajectory.cpp logs 'Trajectory 1' for both motions (MOVEIT-V36)"
---
# Units 2–3: exercises

**TL;DR** Unit 2 builds the MoveIt 2 package `my_moveit_config` for the UR3e and makes it work with the simulation; unit 3 writes C++ programs in `moveit2_scripts` that plan and execute. Each exercise links the note with the steps and code.

## Unit 2: the MoveIt 2 package
| Exercise | Task | Note |
|---|---|---|
| 2.1 | Setup Assistant: load `ur_moveit.urdf.xacro`, self-collisions, virtual joint `fixed_base`, groups `ur_manipulator` (KDL) and `gripper`, poses `home`/`open`/`close`, end effector `hand_ee`, controllers, author, generate `my_moveit_config` in `ros2_ws/src`, build | [[moveit-setup-assistant-model]], [[moveit-setup-assistant-controllers]] |
| 2.2 | Fine-tune: `joint_limits.yaml` (doubles, position limits) and `moveit_controllers.yaml` (controller names, `GripperCommand`), build | [[moveit-config-joint-limits]], [[moveit-config-controllers-yaml]] |
| 2.3 | Plan and execute in RViz2; Execute aborts until `move_group.launch.py` sets `use_sim_time`; try the gripper group with `open`/`close` | [[moveit-rviz-motion-planning]], [[moveit-move-group-launch-sim]] |

Architecture of what you built: [[moveit-architecture]].

## Unit 3: Move Group C++ interface
| Exercise | Program | Note |
|---|---|---|
| 3.1 | `joint_space_trajectory.cpp`, plan only, to the course's home joint values | [[moveit-cpp-joint-space-goal]], [[moveit-cpp-package-setup]] |
| 3.2 | `goal_pose_trajectory.cpp`, plan to an end-effector pose | [[moveit-cpp-pose-goal]] |
| 3.3 | add the execute step to the programs | [[moveit-cpp-joint-space-goal]] |
| 3.4 | `double_motion_trajectory.cpp`: plan and execute two motions in a row (below) | this note |
| 3.5 | `gripper_control.cpp`: close, wait, open | [[moveit-cpp-gripper]] |
| 3.6 | `approach_retreat_trajectory.cpp` with the box `grasp_box` | [[moveit-approach-retreat]], [[moveit-scene-grasp-boxes]] |

Between them: move the arm by hand and read poses and joint values ([[moveit-arm-joint-pose-tools]]).

### Exercise 3.4: two motions
Write `double_motion_trajectory.cpp`: plan and execute a first motion to one joint configuration, then a second one (the configurations are shown in the course's figures). The course's solution: `joint_space_trajectory.cpp` (executing version, [[moveit-cpp-joint-space-goal]]) with these changes:
1. `execute_trajectory_plan()` plans and executes twice: `setup_joint_value_target(+0.0000, -1.5708, +0.0000, +0.0000, +0.0000, -1.5708);` then `setup_joint_value_target(-1.5708, -1.5708, +1.5708, +0.0000, +0.0000, +1.5708);`, each followed by `plan_trajectory_kinematics();` and `execute_trajectory_kinematics();`, with logs "Preparing Joint Value Trajectory 1..." and "Preparing Joint Value Trajectory 2...". The second motion still logs "Planning Joint Value Trajectory 1..." and "Executing Joint Value Trajectory 1..." (course typo, MOVEIT-V36).
2. It also contains `setup_goal_pose_target()` ([[moveit-cpp-pose-goal]]), unused.
3. Class `DoubleMotionTrajectory`, node `"double_motion_trajectory"`, final log "Double Motion Trajectory Execution Complete".
