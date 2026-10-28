---
id: moveit-cpp-pose-goal
type: reference
owner: equipo-ros2
updated: 2026-10-28
review_by: 2027-04-26
source: manual
confidentiality: internal
title: "Plan to an end-effector pose: setPoseTarget, goal_pose_trajectory.cpp as differences"
domain: moveit
area: planning
distro: humble
tested: false
audience: dev
summary: "setPoseTarget(geometry_msgs Pose) for the end-effector link: position plus quaternion in the planning frame; goal_pose_trajectory.cpp; IK solves the pose."
tags: [setPoseTarget, pose goal, end-effector pose, geometry_msgs/Pose, quaternion, goal_pose_trajectory.cpp, setup_goal_pose_target, inverse kinematics, getEndEffectorLink, planning frame, pregrasp]
see: ["[[moveit-cpp-joint-space-goal]]", "[[moveit-cpp-move-group-interface]]", "[[moveit-kinematics-plugins]]", "[[moveit-approach-retreat]]", "[[core-tf-basics]]"]
requires: [ros2-core, ros2-cpp]
version_notes:
  - "humble: setPoseTarget(pose, end_effector_link = \"\") targets getEndEffectorLink() (the last link of a chain group); poses are in the pose reference frame, by default the model frame (URDF root link for a fixed virtual joint) — https://github.com/moveit/moveit2/blob/humble/moveit_core/robot_model/src/robot_model.cpp (MOVEIT-V26)"
  - "humble: quaternion (x -1, y 0, z 0, w 0) = half turn about X of the planning frame (MOVEIT-V35)"
---
# Plan to an end-effector pose

**TL;DR** Sometimes it is more convenient to move the end effector to a pose than to choose joint values. Fill a `geometry_msgs::msg::Pose` (position in meters, orientation as a quaternion) and call `setPoseTarget()`; MoveIt solves IK for the group's end-effector link and plans to the solution.

## The new function (exercise 3.2)
```cpp
void setup_goal_pose_target(float pos_x, float pos_y, float pos_z, float quat_x, float quat_y, float quat_z, float quat_w) {
  // set the pose values for end effector of robot arm
  target_pose_robot_.position.x = pos_x;
  target_pose_robot_.position.y = pos_y;
  target_pose_robot_.position.z = pos_z;
  target_pose_robot_.orientation.x = quat_x;
  target_pose_robot_.orientation.y = quat_y;
  target_pose_robot_.orientation.z = quat_z;
  target_pose_robot_.orientation.w = quat_w;
  move_group_robot_->setPoseTarget(target_pose_robot_);
}
```
`target_pose_robot_` is the `Pose` member every program of the course already declares.

## `src/goal_pose_trajectory.cpp`: changes against the plan-only `joint_space_trajectory.cpp`
Base: the plan-only version of [[moveit-cpp-joint-space-goal]] (plans, does not execute).
1. `setup_goal_pose_target()` above **replaces** `setup_joint_value_target()`.
2. `execute_trajectory_plan()` calls `setup_goal_pose_target(+0.343, +0.132, +0.284, -1.000, +0.000, +0.000, +0.000);`.
3. Class `GoalPoseTrajectory`, node `"goal_pose_trajectory"`, object `goal_pose_trajectory_node`, logs "Goal Pose Trajectory" instead of "Joint Space Trajectory" / "Joint Value Trajectory".

## Build and run
```bash
cd ~/ros2_ws/src/moveit2_scripts/src
touch goal_pose_trajectory.cpp
cd ~/ros2_ws/src/moveit2_scripts
cp launch/joint_space_trajectory.launch.py launch/goal_pose_trajectory.launch.py
```
In the new launch file change the node:
```python
    moveit_cpp_node = Node(
        name="goal_pose_trajectory",
        package="moveit2_scripts",
        executable="goal_pose_trajectory",
        output="screen",
        parameters=[
            moveit_config.robot_description,
            moveit_config.robot_description_semantic,
            moveit_config.robot_description_kinematics,
            {'use_sim_time': True},
        ],
    )
```
CMake:
```cmake
add_executable(goal_pose_trajectory
  src/goal_pose_trajectory.cpp)
target_include_directories(goal_pose_trajectory
  PUBLIC include)
ament_target_dependencies(goal_pose_trajectory
  ament_cmake
  rclcpp
  rclcpp_action
  moveit_core
  moveit_ros_planning_interface
  interactive_markers
  moveit_ros_planning
  control_msgs)
install(TARGETS
  joint_space_trajectory
  goal_pose_trajectory
  DESTINATION lib/${PROJECT_NAME})
```
```bash
cd ~/ros2_ws/
colcon build
source install/setup.bash
ros2 launch moveit2_scripts goal_pose_trajectory.launch.py
```
with `move_group` and RViz2 running ([[moveit-cpp-package-setup]]). To move as well, add the execute step of [[moveit-cpp-joint-space-goal]].

## Pitfalls
- The pose is for `getEndEffectorLink()` (the tip of the `ur_manipulator` chain), not for the gripper's fingertips, and it is read in the pose reference frame, by default the model frame: the parent frame of a non-fixed virtual joint, but the URDF root link when the virtual joint is `fixed` (as `fixed_base` is). The program prints it as "Planning Frame" (MOVEIT-V26).
- The quaternion (−1, 0, 0, 0) is a half turn about X: the end-effector link's Z axis points along −Z of the frame; a non-normalized quaternion is not a valid orientation.
- The same pose can have several IK solutions: two runs may move the arm along very different paths ([[moveit-kinematics-plugins]], [[moveit-approach-retreat]]).
