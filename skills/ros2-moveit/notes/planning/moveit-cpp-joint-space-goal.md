---
id: moveit-cpp-joint-space-goal
type: reference
owner: equipo-ros2
updated: 2026-10-28
review_by: 2027-04-26
source: manual
confidentiality: internal
title: "Plan and execute to a joint-space goal: joint_space_trajectory.cpp"
domain: moveit
area: planning
distro: humble
tested: false
audience: dev
summary: "joint_space_trajectory.cpp: MoveGroupInterface for ur_manipulator, setJointValueTarget with six joint values, plan(), execute() with result check."
tags: [joint_space_trajectory.cpp, joint-space goal, setJointValueTarget, MoveGroupInterface, plan, execute, MoveItErrorCode, ur_manipulator, home, joint_group_positions_robot_, moveit2_scripts, UR3e]
see: ["[[moveit-cpp-move-group-interface]]", "[[moveit-cpp-package-setup]]", "[[moveit-cpp-pose-goal]]", "[[moveit-learn-unit2-3]]"]
requires: [ros2-core, ros2-cpp]
version_notes:
  - "humble: execute() returns a MoveItErrorCode; the course logs success without checking it (fixed below) — https://github.com/moveit/moveit2/blob/humble/moveit_ros/planning_interface/move_group_interface/include/moveit/move_group_interface/move_group_interface.h (MOVEIT-V04)"
  - "course: the joint target the programs call home differs from the SRDF home (MOVEIT-V47)"
  - "jazzy: use the .hpp headers (MOVEIT-V14)"
---
# Plan and execute to a joint-space goal

**TL;DR** Set the six arm joint values with `setJointValueTarget`, `plan()`, and `execute()` the plan if planning succeeded. `joint_space_trajectory.cpp` (exercises 3.1 and 3.3) moves the UR3e to the joint values (0, −2.3562, 1.5708, −1.5708, −1.5708, 0), which the course calls home.

## `src/joint_space_trajectory.cpp` (exercise 3.3, plans and executes)
```cpp
#include <moveit/move_group_interface/move_group_interface.h>
#include <moveit/planning_scene_interface/planning_scene_interface.h>
#include <moveit_msgs/msg/display_robot_state.hpp>
#include <moveit_msgs/msg/display_trajectory.hpp>
#include <chrono>
#include <cmath>
#include <memory>
#include <thread>
#include <vector>

// program variables
static const rclcpp::Logger LOGGER = rclcpp::get_logger("move_group_node");
static const std::string PLANNING_GROUP_ROBOT = "ur_manipulator";

class JointSpaceTrajectory {
public:
  JointSpaceTrajectory(rclcpp::Node::SharedPtr base_node_) : base_node_(base_node_) {
    RCLCPP_INFO(LOGGER, "Initializing Class: Joint Space Trajectory...");
    // configure node options
    rclcpp::NodeOptions node_options;
    // auto-declare node_options parameters from overrides
    node_options.automatically_declare_parameters_from_overrides(true);
    // initialize move_group node
    move_group_node_ = rclcpp::Node::make_shared("move_group_node", node_options);
    // start move_group node in a new executor thread and spin it
    executor_.add_node(move_group_node_);
    std::thread([this]() { this->executor_.spin(); }).detach();
    // initialize move_group interfaces
    move_group_robot_ = std::make_shared<MoveGroupInterface>(move_group_node_, PLANNING_GROUP_ROBOT);
    // get initial state of robot
    joint_model_group_robot_ = move_group_robot_->getCurrentState()->getJointModelGroup(PLANNING_GROUP_ROBOT);
    // print out basic system information
    RCLCPP_INFO(LOGGER, "Planning Frame: %s", move_group_robot_->getPlanningFrame().c_str());
    RCLCPP_INFO(LOGGER, "End Effector Link: %s", move_group_robot_->getEndEffectorLink().c_str());
    RCLCPP_INFO(LOGGER, "Available Planning Groups:");
    std::vector<std::string> group_names = move_group_robot_->getJointModelGroupNames();
    // more efficient method than std::copy() method used in the docs
    for (long unsigned int i = 0; i < group_names.size(); i++) {
      RCLCPP_INFO(LOGGER, "Group %ld: %s", i, group_names[i].c_str());
    }
    // get current state of robot
    current_state_robot_ = move_group_robot_->getCurrentState(10);
    current_state_robot_->copyJointGroupPositions(joint_model_group_robot_, joint_group_positions_robot_);
    // set start state of robot to current state
    move_group_robot_->setStartStateToCurrentState();
    // indicate initialization
    RCLCPP_INFO(LOGGER, "Class Initialized: Joint Space Trajectory");
  }

  ~JointSpaceTrajectory() {
    // indicate termination
    RCLCPP_INFO(LOGGER, "Class Terminated: Joint Space Trajectory");
  }

  void execute_trajectory_plan() {
    RCLCPP_INFO(LOGGER, "Planning and Executing Joint Space Trajectory...");
    // setup the joint value target
    RCLCPP_INFO(LOGGER, "Preparing Joint Value Trajectory...");
    setup_joint_value_target(+0.0000, -2.3562, +1.5708, -1.5708, -1.5708, +0.0000);
    // plan and execute the trajectory
    RCLCPP_INFO(LOGGER, "Planning Joint Value Trajectory...");
    plan_trajectory_kinematics();
    RCLCPP_INFO(LOGGER, "Executing Joint Value Trajectory...");
    execute_trajectory_kinematics();
    RCLCPP_INFO(LOGGER, "Joint Space Trajectory Execution Complete");
  }

private:
  // using shorthand for lengthy class references
  using MoveGroupInterface = moveit::planning_interface::MoveGroupInterface;
  using JointModelGroup = moveit::core::JointModelGroup;
  using RobotStatePtr = moveit::core::RobotStatePtr;
  using Plan = MoveGroupInterface::Plan;
  using Pose = geometry_msgs::msg::Pose;

  // declare rclcpp base node class
  rclcpp::Node::SharedPtr base_node_;
  // declare move_group node
  rclcpp::Node::SharedPtr move_group_node_;
  // declare single threaded executor for move_group node
  rclcpp::executors::SingleThreadedExecutor executor_;
  // declare move_group_interface variables for robot
  std::shared_ptr<MoveGroupInterface> move_group_robot_;
  // declare joint_model_group for robot
  const JointModelGroup *joint_model_group_robot_;
  // declare trajectory planning variables for robot
  std::vector<double> joint_group_positions_robot_;
  RobotStatePtr current_state_robot_;
  Plan kinematics_trajectory_plan_;
  Pose target_pose_robot_;
  bool plan_success_robot_ = false;

  void setup_joint_value_target(float angle0, float angle1, float angle2, float angle3, float angle4, float angle5) {
    // set the joint values for each joint of robot arm
    joint_group_positions_robot_[0] = angle0; // Shoulder Pan
    joint_group_positions_robot_[1] = angle1; // Shoulder Lift
    joint_group_positions_robot_[2] = angle2; // Elbow
    joint_group_positions_robot_[3] = angle3; // Wrist 1
    joint_group_positions_robot_[4] = angle4; // Wrist 2
    joint_group_positions_robot_[5] = angle5; // Wrist 3
    move_group_robot_->setJointValueTarget(joint_group_positions_robot_);
  }

  void plan_trajectory_kinematics() {
    // plan the trajectory to target using kinematics
    plan_success_robot_ = (move_group_robot_->plan(kinematics_trajectory_plan_) == moveit::core::MoveItErrorCode::SUCCESS);
  }

  void execute_trajectory_kinematics() {
    // execute the planned trajectory to target using kinematics
    if (plan_success_robot_) {
      // MOVEIT-V04: report the execution result, not only the planning result
      if (move_group_robot_->execute(kinematics_trajectory_plan_) == moveit::core::MoveItErrorCode::SUCCESS) {
        RCLCPP_INFO(LOGGER, "Robot Kinematics Trajectory Success !");
      } else {
        RCLCPP_INFO(LOGGER, "Robot Kinematics Trajectory Execution Failed !");
      }
    } else {
      RCLCPP_INFO(LOGGER, "Robot Kinematics Trajectory Failed !");
    }
  }
}; // class JointSpaceTrajectory

int main(int argc, char **argv) {
  // initialize program node
  rclcpp::init(argc, argv);
  // initialize base_node as shared pointer
  std::shared_ptr<rclcpp::Node> base_node = std::make_shared<rclcpp::Node>("joint_space_trajectory");
  // instantiate class
  JointSpaceTrajectory joint_space_trajectory_node(base_node);
  // execute trajectory plan
  joint_space_trajectory_node.execute_trajectory_plan();
  // shutdown ros2 node
  rclcpp::shutdown();
  return 0;
}
// End of Code
```
The course calls `execute()` and logs "Robot Kinematics Trajectory Success !" without looking at its result (MOVEIT-V04).

## The plan-only version (exercise 3.1)
The same program without the execute step: no `execute_trajectory_kinematics()` (neither the function nor its call), and the logs say "Planning Joint Space Trajectory..." and "Joint Space Trajectory Planning Complete". The robot in the simulation does not move: **planning is not executing**.

## Build and run
Package, launch file and CMake entries: [[moveit-cpp-package-setup]] (executable `joint_space_trajectory`, launch `joint_space_trajectory.launch.py`). With `move_group` (and optionally RViz2) running:
```bash
ros2 launch moveit2_scripts joint_space_trajectory.launch.py
```
Change the six values of `setup_joint_value_target()` to plan other motions. The SRDF's `home` (0, −2.5, 1.5, −1.5, −1.55, 0) differs a little from this target (MOVEIT-V47); `setNamedTarget("home")` would use the SRDF one.

## Pitfalls
- The vector index follows the group's variable order (shoulder pan … wrist 3 for `ur_manipulator`, as the course's comments say); print `joint_model_group_robot_->getVariableNames()` before writing by index.
- The sequence goes on after a failed step; for real tasks return the result and stop.
