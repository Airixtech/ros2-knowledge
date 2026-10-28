---
id: moveit-learn-unit4
type: reference
owner: equipo-ros2
updated: 2026-10-28
review_by: 2027-04-26
source: manual
confidentiality: internal
title: "Unit 4 exercises: Cartesian paths, draw an X, kinematics plugin, pick and place"
domain: moveit
area: learn
distro: humble
tested: false
audience: students
order: 3
summary: "Exercises 4.1 cartesian_trajectory, 4.2 draw_x_cartesian_trajectory (an X with four Cartesian moves), 4.3 kinematics plugin, 4.4 pick_and_place_trajectory."
tags: [course, exercises, unit 4, Cartesian path, draw_x_cartesian_trajectory.cpp, setup_waypoints_target, kinematics plugin, pick and place, pick_and_place_trajectory]
see: ["[[moveit-learn-unit2-3]]", "[[moveit-learn-unit5]]", "[[moveit-cpp-cartesian-path]]", "[[moveit-pick-and-place]]"]
requires: [ros2-core]
version_notes:
  - "humble: Cartesian steps execute only a complete path in the notes' code (course: any fraction >= 0.0) (MOVEIT-V05)"
---
# Unit 4: exercises

**TL;DR** Until now the robot moved "in free space" from A to B. Unit 4 controls the path with Cartesian waypoints, changes the IK plugin, and puts everything together in a pick-and-place program.

| Exercise | Program | Note |
|---|---|---|
| 4.1 | `cartesian_trajectory.cpp`: pregrasp pose, 6 cm down and up along Z | [[moveit-cpp-cartesian-path]] |
| 4.2 | `draw_x_cartesian_trajectory.cpp`: draw an X with the end effector (below) | this note |
| 4.3 | `kinematics_plugin_trajectory.cpp`, then KDL → LMA in `kinematics.yaml` | [[moveit-kinematics-plugins]] |
| 4.4 | `pick_and_place_trajectory.cpp`: home, pick, open, approach, close, retreat, place, open, home | [[moveit-pick-and-place]], [[moveit-scene-grasp-boxes]] |

## Exercise 4.2: draw an X
Copy `cartesian_trajectory.cpp` into `draw_x_cartesian_trajectory.cpp` and change it so the end effector "draws" an X on the floor (the expected motion is shown in the course's GIF). The course's solution, against `cartesian_trajectory.cpp` ([[moveit-cpp-cartesian-path]]):
1. After the pregrasp pose it waits: `std::this_thread::sleep_for(std::chrono::milliseconds(1500));`, then logs "Doing X Cartesian Trajectory...".
2. Instead of the approach and retreat it runs four Cartesian moves in the horizontal plane (each `setup_waypoints_target()` → `plan_trajectory_cartesian()` → `execute_trajectory_cartesian()`):
```cpp
setup_waypoints_target(+0.100, -0.100, +0.000);  // first diagonal
setup_waypoints_target(+0.000, +0.100, +0.000);  // move along Y
setup_waypoints_target(-0.100, -0.100, +0.000);  // second diagonal, crosses the first
setup_waypoints_target(+0.000, +0.100, +0.000);  // back along Y to the start
```
   (comments added here: the two diagonals cross at (+0.05, −0.05) from the start, which makes the X).
3. Class `DrawXCartesianTrajectory`, node `"draw_x_cartesian_trajectory"`, logs "Draw X Cartesian Trajectory".

Launch file, CMake entry and build as in [[moveit-cpp-package-setup]].
