---
id: moveit-cpp-move-group-interface
type: reference
owner: equipo-ros2
updated: 2026-10-28
review_by: 2027-04-26
source: manual
confidentiality: internal
title: "Move Group C++ interface: node and executor thread, MoveGroupInterface, joint model group, current state, plan/execute/move"
domain: moveit
area: planning
distro: humble
tested: false
audience: dev
summary: "MoveGroupInterface in C++: automatically_declare_parameters_from_overrides, executor thread, getJointModelGroup, getCurrentState, copyJointGroupPositions, plan(), execute(), move(), defaults."
tags: [MoveGroupInterface, moveit::planning_interface::MoveGroupInterface, move_group_interface.h, JointModelGroup, RobotStatePtr, getCurrentState, copyJointGroupPositions, setStartStateToCurrentState, getPlanningFrame, getEndEffectorLink, getJointModelGroupNames, plan, execute, move, MoveItErrorCode, SingleThreadedExecutor, automatically_declare_parameters_from_overrides, joint-space goal, pose goal, inverse kinematics]
see: ["[[moveit-cpp-joint-space-goal]]", "[[moveit-cpp-pose-goal]]", "[[moveit-cpp-package-setup]]", "[[moveit-architecture]]", "[[cpp-exec-spin-some]]", "[[core-moveit2-overview]]"]
requires: [ros2-core, ros2-cpp]
version_notes:
  - "humble: moveit_py (Python API) exists for Humble (ros-humble-moveit-py); the course says MoveIt 2 has no Python API (MOVEIT-V02)"
  - "humble: move() plans and executes in one blocking call; plan() stores the plan, execute() runs it and returns a MoveItErrorCode; the course says move() executes 'a random plan' — https://github.com/moveit/moveit2/blob/humble/moveit_ros/planning_interface/move_group_interface/include/moveit/move_group_interface/move_group_interface.h (MOVEIT-V03, MOVEIT-V04)"
  - "humble: copyJointGroupPositions copies the current state's values; the joint model group holds no values; move_group_node is a second node (MOVEIT-V01)"
  - "humble: defaults planning time 5 s, 1 attempt, joint tolerance 1e-4, position 1e-4, orientation 1e-3, scaling 0.1, end effector = last link of a chain group, pose reference frame = model frame, getCurrentState(wait = 1) — https://github.com/moveit/moveit2/blob/humble/moveit_ros/planning_interface/move_group_interface/src/move_group_interface.cpp (MOVEIT-V26)"
  - "jazzy: include <moveit/move_group_interface/move_group_interface.hpp>; the .h header still works with a '.h header is obsolete' message — https://github.com/moveit/moveit2/pull/3113 (MOVEIT-V14)"
  - "humble: API reference = the Humble header (the course links the API pages of an old MoveIt release) (MOVEIT-V15)"
---
# Move Group C++ interface

**TL;DR** Real applications command MoveIt from programs, not from RViz2. `moveit::planning_interface::MoveGroupInterface` calls the `move_group` node's capabilities for one planning group. Give it its own node, spin that node in a background executor (MoveIt's state monitor needs callbacks while your code waits), set a target, `plan()`, check the result, then `execute()`. A Python API exists too (`moveit_py`, released for Humble, MOVEIT-V02); this course uses C++.

## Two kinds of goals
1. **Joint-space goal**: the desired position of every arm joint; the planner moves from the current joint positions to them. No inverse kinematics (IK), so it is the simpler one ([[moveit-cpp-joint-space-goal]]).
2. **End-effector pose goal**: position and orientation of the end-effector link in space; MoveIt solves IK first ([[moveit-cpp-pose-goal]], [[moveit-kinematics-plugins]]).

## The pieces of the course's program class
(complete program: [[moveit-cpp-joint-space-goal]]; it follows the official Humble tutorial `move_group_interface_tutorial.cpp`)
- `static const rclcpp::Logger LOGGER = rclcpp::get_logger("move_group_node");` and `PLANNING_GROUP_ROBOT = "ur_manipulator"` (the group name of the SRDF).
- `node_options.automatically_declare_parameters_from_overrides(true)`: the robot description, SRDF and kinematics that the launch file passes become declared parameters of the node ([[moveit-cpp-package-setup]]).
- `move_group_node_ = rclcpp::Node::make_shared("move_group_node", node_options)` is a **second** node (the course's base node is never spun); it is added to a `rclcpp::executors::SingleThreadedExecutor` that spins in a detached thread: `std::thread([this]() { this->executor_.spin(); }).detach();` (the tutorial: the executor is "for the current state monitor to get information about the robot's state"; executors: [[cpp-exec-spin-some]]).
- `std::make_shared<MoveGroupInterface>(move_group_node_, PLANNING_GROUP_ROBOT)`: one interface per planning group (the gripper gets its own, [[moveit-cpp-gripper]]).
- `getCurrentState()->getJointModelGroup(PLANNING_GROUP_ROBOT)` returns a `const JointModelGroup*` with the group's model (joints, bounds); "Raw pointers are frequently used to refer to the planning group for improved performance" (tutorial).
- Optional checks: `getPlanningFrame()`, `getEndEffectorLink()`, `getJointModelGroupNames()` (the course prints the names with a `for` loop instead of the tutorial's `std::copy`).
- `current_state_robot_ = move_group_robot_->getCurrentState(10)` waits up to 10 s for a complete state; `copyJointGroupPositions(joint_model_group_robot_, joint_group_positions_robot_)` copies **that state's** positions of the group's joints into the vector (MOVEIT-V01: the course says they come from the joint model group); `setStartStateToCurrentState()`.
- A target (`setJointValueTarget`, `setPoseTarget`, `setNamedTarget`), then `plan(kinematics_trajectory_plan_) == moveit::core::MoveItErrorCode::SUCCESS`.

## plan, execute, move
```cpp
move_group.execute(my_plan_arm); // in a program without class
move_group->execute(my_plan_arm); // in a program with class
```
```cpp
move_group.move(); // in a program without class
move_group->move(); // in a program with class
```
- `plan(plan)`: computes a plan to the target, executes nothing.
- `execute(plan)`: runs it and waits for completion; returns a `MoveItErrorCode` (check it, MOVEIT-V04).
- `move()`: plans **and** executes in one blocking call (Plan & Execute of RViz2). Nothing is random about it (MOVEIT-V03), but you cannot inspect or choose the plan before it runs, so prefer `plan()` + check + `execute()`.

Defaults of a new interface (Humble, MOVEIT-V26): planning time 5 s, 1 planning attempt, goal tolerances 1e-4 (joint, position) and 1e-3 rad (orientation), velocity/acceleration scaling 0.1 (or `robot_description_planning.default_*_scaling_factor`), end-effector link = last link of a chain group, pose reference frame = the model frame. API reference: the Humble header `moveit/move_group_interface/move_group_interface.h` (MOVEIT-V15).

## Pitfalls
- No spinning executor for the interface's node → `getCurrentState()` and execution wait for joint states that are never processed.
- `move_group` must run first (`ros2 launch my_moveit_config move_group.launch.py`); RViz2 is optional, for watching.
- [changed in Jazzy: include `moveit/move_group_interface/move_group_interface.hpp`; the `.h` still compiles with a "header is obsolete" message] (MOVEIT-V14).
