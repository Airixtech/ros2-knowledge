---
id: moveit-approach-retreat
type: reference
owner: equipo-ros2
updated: 2026-10-28
review_by: 2027-04-26
source: manual
confidentiality: internal
title: "Approach and retreat with pose targets: pregrasp pose, delta_ down and up, why IK makes long motions"
domain: moveit
area: planning
distro: humble
tested: false
audience: dev
summary: "Pregrasp pose, approach, close gripper, retreat; approach_retreat_trajectory.cpp with pose goals 4 cm down and up; why IK swings the arm."
tags: [approach, retreat, pregrasp, grasp sequence, approach_retreat_trajectory.cpp, delta_, setPoseTarget, inverse kinematics, IK, gripper, grasp_box, pick]
see: ["[[moveit-pick-and-place]]", "[[moveit-cpp-cartesian-path]]", "[[moveit-cpp-pose-goal]]", "[[moveit-scene-grasp-boxes]]", "[[moveit-kinematics-plugins]]", "[[moveit-learn-unit2-3]]"]
requires: [ros2-core, ros2-cpp]
version_notes:
  - "humble: each pose goal is solved by the group's IK plugin, which may return another arm configuration; the joint-space planner then moves there (MOVEIT-V35)"
  - "humble: execute() results unchecked in the course program (MOVEIT-V04)"
---
# Approach and retreat

**TL;DR** To pick an object you do not send the end effector straight to it (the gripper could hit it). Send it to a pose **near** the object (pregrasp), open the gripper, **approach** until the object is between the fingers, close, and **retreat** to the pregrasp pose. Exercise 3.6 does approach and retreat with pose goals; unit 4 does them with Cartesian paths, because pose goals make long, unpredictable motions.

## Exercise 3.6: the task
Spawn the box at (0.34, 0.13) ([[moveit-scene-grasp-boxes]]), then write `approach_retreat_trajectory.cpp` that:
- goes to the **home** position;
- goes to a pose near the object:
```
target_pose:
  - position:
    - x: +0.343
    - y: +0.132
    - z: +0.264
  - orientation:
    - x: -1.000
    - y: +0.000
    - z: +0.000
    - w: +0.000
```
- opens the gripper;
- approaches: moves the end effector down 4 cm with a `delta_` variable: `target_pose_robot_.position.z = target_pose_robot_.position.z - delta_;`
- closes the gripper to pick the object;
- retreats: 4 cm up, `target_pose_robot_.position.z = target_pose_robot_.position.z + delta_;`
- opens the gripper to release the object.

Plus a launch file `approach_retreat_trajectory.launch.py`, then (one terminal each):
```bash
ros2 launch my_moveit_config move_group.launch.py
ros2 launch my_moveit_config moveit_rviz.launch.py
ros2 launch moveit2_scripts approach_retreat_trajectory.launch.py
```

## The course's solution: changes against `pick_and_place_trajectory.cpp`
Base: the complete program in [[moveit-pick-and-place]].
1. Approach and retreat are **pose goals**, not Cartesian paths: `setup_goal_pose_target(+0.343, +0.132, (target_pose_robot_.position.z - delta_), -1.000, +0.000, +0.000, +0.000);` then `plan_trajectory_kinematics(); execute_trajectory_kinematics();`, and the same with `+ delta_` for the retreat.
2. Member `float delta_ = 0.040; // meters` instead of the Cartesian members (`cartesian_waypoints_`, `cartesian_trajectory_plan_`, `jump_threshold_`, `end_effector_step_`, `plan_fraction_robot_`, the `RobotTrajectory` alias) and without the three Cartesian functions.
3. The gripper closes to `setup_joint_value_gripper(+0.440)` (pick and place: 0.500).
4. No place step: after the retreat it opens the gripper, waits 1 s (`std::this_thread::sleep_for(std::chrono::milliseconds(1000))`) and goes home.
5. Class `ApproachRetreatTrajectory`, node `"approach_retreat_trajectory"`, logs "Approach Retreat Trajectory", "Goal Pose Trajectory" for the approach and retreat steps.

## Why the arm makes complex motions
The motions may look different from the course's GIFs and more complicated than needed: every new end-effector pose goal is solved by inverse kinematics, and the IK solution can be a different arm configuration, which the planner then reaches with a large joint motion (MOVEIT-V35). For a straight 4 cm motion use a Cartesian path ([[moveit-cpp-cartesian-path]]), and see the kinematics plugin options ([[moveit-kinematics-plugins]]).

## Pitfalls
- The hard-coded pregrasp pose fits only the box spawned at (0.34, 0.13); find poses for other positions with the tools of [[moveit-arm-joint-pose-tools]].
- `delta_` is subtracted from the current target, so the approach and retreat poses depend on the order of the calls.
