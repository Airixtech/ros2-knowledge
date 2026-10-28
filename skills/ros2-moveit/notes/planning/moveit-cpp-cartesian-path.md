---
id: moveit-cpp-cartesian-path
type: reference
owner: equipo-ros2
updated: 2026-10-28
review_by: 2027-04-26
source: manual
confidentiality: internal
title: "Cartesian paths: waypoints, computeCartesianPath (eef_step, jump_threshold, fraction), clear the waypoints"
domain: moveit
area: planning
distro: humble
tested: false
audience: dev
summary: "computeCartesianPath(waypoints, eef_step 0.01, jump_threshold 0.0, trajectory) returns the achieved fraction (-1 error); execute only 1.0; clear waypoints; cartesian_trajectory.cpp."
tags: [Cartesian path, computeCartesianPath, waypoints, eef_step, end_effector_step_, jump_threshold, fraction, RobotTrajectory, moveit_msgs/RobotTrajectory, getCurrentPose, cartesian_trajectory.cpp, approach, retreat, industrial]
see: ["[[moveit-pick-and-place]]", "[[moveit-approach-retreat]]", "[[moveit-cpp-move-group-interface]]", "[[moveit-learn-unit4]]", "[[moveit-humble-to-jazzy]]"]
requires: [ros2-core, ros2-cpp]
version_notes:
  - "humble: computeCartesianPath returns the fraction of the path achieved (0.0-1.0) or -1.0 on error; the course executes any fraction >= 0.0 — https://github.com/moveit/moveit2/blob/humble/moveit_ros/planning_interface/move_group_interface/include/moveit/move_group_interface/move_group_interface.h (MOVEIT-V05)"
  - "humble: jump_threshold 0.0 skips the joint-space jump check; tutorial warning about real hardware — https://github.com/moveit/moveit2/blob/humble/moveit_core/robot_state/src/cartesian_interpolator.cpp (MOVEIT-V16)"
  - "jazzy: the overload with jump_threshold is marked deprecated (\"Drop jump_threshold\") since MoveIt 2.12.0: computeCartesianPath(waypoints, eef_step, trajectory) — https://github.com/moveit/moveit2/blob/jazzy/moveit_ros/planning_interface/move_group_interface/include/moveit/move_group_interface/move_group_interface.hpp (MOVEIT-V16)"
---
# Cartesian paths

**TL;DR** A normal plan moves the robot from A to B "in free space", with no control over the path. A **Cartesian path** makes the end effector follow a list of waypoints in straight lines, for precise, predictable motions (industrial tasks, approach and retreat). `computeCartesianPath()` interpolates them and returns **how much of the path it could compute**: execute only when that fraction is 1.0.

## The Cartesian part of the programs (exercise 4.1)
```cpp
// declare cartesian trajectory planning variables for robot
std::vector<Pose> cartesian_waypoints_;
RobotTrajectory cartesian_trajectory_plan_;
const double jump_threshold_ = 0.0;
const double end_effector_step_ = 0.01;
double plan_fraction_robot_ = 0.0;

void setup_waypoints_target(float x_delta, float y_delta, float z_delta) {
  // initially set target pose to current pose of the robot
  target_pose_robot_ = move_group_robot_->getCurrentPose().pose;
  // add the current pose to the target waypoints vector
  cartesian_waypoints_.push_back(target_pose_robot_);
  // calculate the desired pose from delta value for the axis
  target_pose_robot_.position.x += x_delta;
  target_pose_robot_.position.y += y_delta;
  target_pose_robot_.position.z += z_delta;
  // add the desired pose to the target waypoints vector
  cartesian_waypoints_.push_back(target_pose_robot_);
}

void plan_trajectory_cartesian() {
  // plan the trajectory to target using cartesian path
  plan_fraction_robot_ = move_group_robot_->computeCartesianPath(cartesian_waypoints_, end_effector_step_, jump_threshold_, cartesian_trajectory_plan_);
}

void execute_trajectory_cartesian() {
  // execute the planned trajectory to target using cartesian path
  // MOVEIT-V05: the fraction is the part of the path computed (-1.0 = error);
  // execute only a complete path (the course executes any fraction >= 0.0)
  RCLCPP_INFO(LOGGER, "Cartesian path %.2f%% achieved", plan_fraction_robot_ * 100.0);
  if (plan_fraction_robot_ >= 1.0) {
    move_group_robot_->execute(cartesian_trajectory_plan_);
    RCLCPP_INFO(LOGGER, "Robot Cartesian Trajectory Success !");
  } else {
    RCLCPP_INFO(LOGGER, "Robot Cartesian Trajectory Failed !");
  }
  // clear cartesian waypoints vector
  cartesian_waypoints_.clear();
}
```
with `using RobotTrajectory = moveit_msgs::msg::RobotTrajectory;` next to the other aliases. Called like this (approach 6 cm down, then retreat 6 cm up):
```cpp
RCLCPP_INFO(LOGGER, "Approaching...");
// setup the cartesian target
RCLCPP_INFO(LOGGER, "Preparing Cartesian Trajectory...");
setup_waypoints_target(+0.000, +0.000, -0.060);
// plan and execute the trajectory
RCLCPP_INFO(LOGGER, "Planning Cartesian Trajectory...");
plan_trajectory_cartesian();
RCLCPP_INFO(LOGGER, "Executing Cartesian Trajectory...");
execute_trajectory_cartesian();
```
- `cartesian_waypoints_`: a vector of poses. Each call adds the current end-effector pose and the pose moved by the deltas (here −6 cm in z). The official tutorial: the start pose does not need to be in the list, but adding it can help with visualization.
- `end_effector_step_ = 0.01`: interpolate at a resolution of 1 cm.
- `jump_threshold_ = 0.0`: disables the check for jumps in joint space between interpolated points. The official tutorial warns: "disabling the jump threshold while operating real hardware can cause large unpredictable motions of redundant joints and could be a safety issue" (MOVEIT-V16).
- The return value: "a value that is between 0.0 and 1.0 indicating the fraction of the path achieved … -1.0 in case of error". The course executes any fraction ≥ 0.0, so a path computed only in part is executed as if complete (MOVEIT-V05).
- Clear `cartesian_waypoints_` after each path: otherwise the next plan includes the old waypoints and the robot revisits poses it already reached.

## `src/cartesian_trajectory.cpp`: changes against `pick_and_place_trajectory.cpp`
Base: [[moveit-pick-and-place]].
1. No gripper: no `PLANNING_GROUP_GRIPPER`, no gripper interface, joint model group, state, members or functions.
2. Sequence: home → pregrasp pose (+0.343, +0.132, +0.264, −1, 0, 0, 0) → approach (−0.060 in z) → `std::this_thread::sleep_for(std::chrono::milliseconds(1500))` → retreat (+0.060) → "Cartesian Trajectory Execution Complete" (no place, no return home).
3. Class `CartesianTrajectory`, node `"cartesian_trajectory"`.

Files: `launch/cartesian_trajectory.launch.py` (template of [[moveit-cpp-package-setup]] with `cartesian_trajectory`), CMake block, `colcon build --packages-select moveit2_scripts`, then with `move_group` and RViz2 running:
```bash
ros2 launch moveit2_scripts cartesian_trajectory.launch.py
```
Expected: the robot goes to the pregrasp pose, then moves the end effector 6 cm down and 6 cm up along Z, following the waypoints.

## Pitfalls
- A fraction below 1.0 means the interpolation stopped at a point it could not reach (no IK solution, a collision or a joint-space jump): change the start pose or split the path.
- [changed in Jazzy: drop the `jump_threshold_` argument, `computeCartesianPath(cartesian_waypoints_, end_effector_step_, cartesian_trajectory_plan_)`; the Humble call compiles with a deprecation warning] (MOVEIT-V16).
