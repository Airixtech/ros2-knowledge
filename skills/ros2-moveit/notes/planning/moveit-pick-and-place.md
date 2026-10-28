---
id: moveit-pick-and-place
type: reference
owner: equipo-ros2
updated: 2026-10-28
review_by: 2027-04-26
source: manual
confidentiality: internal
title: "Pick and place with MoveIt: home, pregrasp, open, Cartesian approach, close, retreat, place, home"
domain: moveit
area: planning
distro: humble
tested: false
audience: dev
summary: "pick_and_place_trajectory.cpp: arm and gripper MoveGroupInterfaces, joint, pose and Cartesian goals, gripper close 0.5, place by turning shoulder_pan to 1.5708."
tags: [pick and place, pick_and_place_trajectory.cpp, MoveGroupInterface, gripper, pregrasp, approach, retreat, place, computeCartesianPath, setJointValueTarget, setPoseTarget, setNamedTarget, getCurrentPose, shoulder_pan_joint, grasp_box, UR3e, Robotiq 85]
see: ["[[moveit-approach-retreat]]", "[[moveit-cpp-cartesian-path]]", "[[moveit-cpp-gripper]]", "[[moveit-scene-grasp-boxes]]", "[[moveit-learn-unit4]]", "[[moveit-learn-unit5]]"]
requires: [ros2-core, ros2-cpp]
version_notes:
  - "humble: execute() results checked and only complete Cartesian paths executed (course: unchecked, any fraction >= 0.0) (MOVEIT-V04, MOVEIT-V05)"
  - "humble: gripper joint written by index 2 [verify] (MOVEIT-V25)"
  - "jazzy: computeCartesianPath(waypoints, eef_step, jump_threshold, trajectory) is deprecated: drop jump_threshold_ (MOVEIT-V16); .hpp headers (MOVEIT-V14)"
---
# Pick and place with MoveIt

**TL;DR** The most complete program of the course (exercise 4.4) uses everything of units 3 and 4: two `MoveGroupInterface`s (arm and gripper), a joint goal for home, a pose goal above the box, Cartesian paths straight down and up, gripper joint and named targets, and a joint goal that turns only the shoulder to place the box. Spawn the box first ([[moveit-scene-grasp-boxes]]).

## Sequence
1. **Home**: joint values (0, −2.3562, 1.5708, −1.5708, −1.5708, 0).
2. **Pick (pregrasp) pose**: `setup_goal_pose_target(+0.343, +0.132, +0.264, -1.000, +0.000, +0.000, +0.000)`, above the box at (0.34, 0.13).
3. **Open** the gripper (`setNamedTarget("open")`).
4. **Approach**: Cartesian path 6 cm down (`setup_waypoints_target(+0.000, +0.000, -0.060)`).
5. **Close** the gripper (joint value 0.500).
6. **Retreat**: Cartesian path 6 cm up.
7. **Place**: read the current joint values and change only `shoulder_pan_joint` to 1.5708 (a quarter turn).
8. **Open** the gripper to release the box, wait 1 s.
9. **Home** again (optional but recommended).

## `src/pick_and_place_trajectory.cpp`
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
static const std::string PLANNING_GROUP_GRIPPER = "gripper";

class PickAndPlaceTrajectory {
public:
  PickAndPlaceTrajectory(rclcpp::Node::SharedPtr base_node_): base_node_(base_node_) {
    RCLCPP_INFO(LOGGER, "Initializing Class: Pick And Place Trajectory...");
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
    move_group_gripper_ = std::make_shared<MoveGroupInterface>(move_group_node_, PLANNING_GROUP_GRIPPER);
    // get initial state of robot and gripper
    joint_model_group_robot_ = move_group_robot_->getCurrentState()->getJointModelGroup(PLANNING_GROUP_ROBOT);
    joint_model_group_gripper_ = move_group_gripper_->getCurrentState()->getJointModelGroup(PLANNING_GROUP_GRIPPER);
    // print out basic system information
    RCLCPP_INFO(LOGGER, "Planning Frame: %s", move_group_robot_->getPlanningFrame().c_str());
    RCLCPP_INFO(LOGGER, "End Effector Link: %s", move_group_robot_->getEndEffectorLink().c_str());
    RCLCPP_INFO(LOGGER, "Available Planning Groups:");
    std::vector<std::string> group_names = move_group_robot_->getJointModelGroupNames();
    // more efficient method than std::copy() method used in the docs
    for (long unsigned int i = 0; i < group_names.size(); i++) {
      RCLCPP_INFO(LOGGER, "Group %ld: %s", i, group_names[i].c_str());
    }
    // get current state of robot and gripper
    current_state_robot_ = move_group_robot_->getCurrentState(10);
    current_state_robot_->copyJointGroupPositions(joint_model_group_robot_, joint_group_positions_robot_);
    current_state_gripper_ = move_group_gripper_->getCurrentState(10);
    current_state_gripper_->copyJointGroupPositions(joint_model_group_gripper_, joint_group_positions_gripper_);
    // set start state of robot and gripper to current state
    move_group_robot_->setStartStateToCurrentState();
    move_group_gripper_->setStartStateToCurrentState();
    // indicate initialization
    RCLCPP_INFO(LOGGER, "Class Initialized: Pick And Place Trajectory");
  }

  ~PickAndPlaceTrajectory() {
    // indicate termination
    RCLCPP_INFO(LOGGER, "Class Terminated: Pick And Place Trajectory");
  }

  void execute_trajectory_plan() {
    RCLCPP_INFO(LOGGER, "Planning and Executing Pick And Place Trajectory...");
    RCLCPP_INFO(LOGGER, "Going to Home Position...");
    // setup the joint value target
    RCLCPP_INFO(LOGGER, "Preparing Joint Value Trajectory...");
    setup_joint_value_target(+0.0000, -2.3562, +1.5708, -1.5708, -1.5708, +0.0000);
    // plan and execute the trajectory
    RCLCPP_INFO(LOGGER, "Planning Joint Value Trajectory...");
    plan_trajectory_kinematics();
    RCLCPP_INFO(LOGGER, "Executing Joint Value Trajectory...");
    execute_trajectory_kinematics();
    RCLCPP_INFO(LOGGER, "Going to Pregrasp Position...");
    // setup the goal pose target
    RCLCPP_INFO(LOGGER, "Preparing Goal Pose Trajectory...");
    setup_goal_pose_target(+0.343, +0.132, +0.264, -1.000, +0.000, +0.000, +0.000);
    // plan and execute the trajectory
    RCLCPP_INFO(LOGGER, "Planning Goal Pose Trajectory...");
    plan_trajectory_kinematics();
    RCLCPP_INFO(LOGGER, "Executing Goal Pose Trajectory...");
    execute_trajectory_kinematics();
    // open the gripper
    RCLCPP_INFO(LOGGER, "Opening Gripper...");
    // setup the gripper target by pose name
    RCLCPP_INFO(LOGGER, "Preparing Gripper Value...");
    setup_named_pose_gripper("open");
    // plan and execute the trajectory
    RCLCPP_INFO(LOGGER, "Planning Gripper Action...");
    plan_trajectory_gripper();
    RCLCPP_INFO(LOGGER, "Executing Gripper Action...");
    execute_trajectory_gripper();
    RCLCPP_INFO(LOGGER, "Gripper Opened");
    RCLCPP_INFO(LOGGER, "Approaching...");
    // setup the cartesian target
    RCLCPP_INFO(LOGGER, "Preparing Cartesian Trajectory...");
    setup_waypoints_target(+0.000, +0.000, -0.060);
    // plan and execute the trajectory
    RCLCPP_INFO(LOGGER, "Planning Cartesian Trajectory...");
    plan_trajectory_cartesian();
    RCLCPP_INFO(LOGGER, "Executing Cartesian Trajectory...");
    execute_trajectory_cartesian();
    // close the gripper
    RCLCPP_INFO(LOGGER, "Closing Gripper...");
    // setup the gripper joint value
    RCLCPP_INFO(LOGGER, "Preparing Gripper Value...");
    setup_joint_value_gripper(+0.500);
    // plan and execute the trajectory
    RCLCPP_INFO(LOGGER, "Planning Gripper Action...");
    plan_trajectory_gripper();
    RCLCPP_INFO(LOGGER, "Executing Gripper Action...");
    execute_trajectory_gripper();
    RCLCPP_INFO(LOGGER, "Gripper Closed");
    RCLCPP_INFO(LOGGER, "Retreating...");
    // setup the cartesian target
    RCLCPP_INFO(LOGGER, "Preparing Cartesian Trajectory...");
    setup_waypoints_target(+0.000, +0.000, +0.060);
    // plan and execute the trajectory
    RCLCPP_INFO(LOGGER, "Planning Cartesian Trajectory...");
    plan_trajectory_cartesian();
    RCLCPP_INFO(LOGGER, "Executing Cartesian Trajectory...");
    execute_trajectory_cartesian();
    RCLCPP_INFO(LOGGER, "Going to Place Position...");
    // get current state of robot
    current_state_robot_ = move_group_robot_->getCurrentState(10);
    current_state_robot_->copyJointGroupPositions(joint_model_group_robot_, joint_group_positions_robot_);
    // setup the joint value target
    RCLCPP_INFO(LOGGER, "Preparing Joint Value Trajectory...");
    setup_joint_value_target(+1.5708, joint_group_positions_robot_[1], joint_group_positions_robot_[2], joint_group_positions_robot_[3], joint_group_positions_robot_[4], joint_group_positions_robot_[5]);
    // plan and execute the trajectory
    RCLCPP_INFO(LOGGER, "Planning Joint Value Trajectory...");
    plan_trajectory_kinematics();
    RCLCPP_INFO(LOGGER, "Executing Joint Value Trajectory...");
    execute_trajectory_kinematics();
    // open the gripper
    RCLCPP_INFO(LOGGER, "Opening Gripper...");
    // setup the gripper target by pose name
    RCLCPP_INFO(LOGGER, "Preparing Gripper Value...");
    setup_named_pose_gripper("open");
    // plan and execute the trajectory
    RCLCPP_INFO(LOGGER, "Planning Gripper Action...");
    plan_trajectory_gripper();
    RCLCPP_INFO(LOGGER, "Executing Gripper Action...");
    execute_trajectory_gripper();
    RCLCPP_INFO(LOGGER, "Gripper Opened");
    // wait for few seconds
    std::this_thread::sleep_for(std::chrono::milliseconds(1000));
    RCLCPP_INFO(LOGGER, "Going to Home Position...");
    // setup the joint value target
    RCLCPP_INFO(LOGGER, "Preparing Joint Value Trajectory...");
    setup_joint_value_target(+0.0000, -2.3562, +1.5708, -1.5708, -1.5708, +0.0000);
    // plan and execute the trajectory
    RCLCPP_INFO(LOGGER, "Planning Joint Value Trajectory...");
    plan_trajectory_kinematics();
    RCLCPP_INFO(LOGGER, "Executing Joint Value Trajectory...");
    execute_trajectory_kinematics();
    RCLCPP_INFO(LOGGER, "Pick And Place Trajectory Execution Complete");
  }

private:
  // using shorthand for lengthy class references
  using MoveGroupInterface = moveit::planning_interface::MoveGroupInterface;
  using JointModelGroup = moveit::core::JointModelGroup;
  using RobotStatePtr = moveit::core::RobotStatePtr;
  using Plan = MoveGroupInterface::Plan;
  using Pose = geometry_msgs::msg::Pose;
  using RobotTrajectory = moveit_msgs::msg::RobotTrajectory;

  // declare rclcpp base node class
  rclcpp::Node::SharedPtr base_node_;
  // declare move_group node
  rclcpp::Node::SharedPtr move_group_node_;
  // declare single threaded executor for move_group node
  rclcpp::executors::SingleThreadedExecutor executor_;
  // declare move_group_interface variables for robot and gripper
  std::shared_ptr<MoveGroupInterface> move_group_robot_;
  std::shared_ptr<MoveGroupInterface> move_group_gripper_;
  // declare joint_model_group for robot and gripper
  const JointModelGroup *joint_model_group_robot_;
  const JointModelGroup *joint_model_group_gripper_;
  // declare trajectory planning variables for robot and gripper
  std::vector<double> joint_group_positions_robot_;
  RobotStatePtr current_state_robot_;
  Plan kinematics_trajectory_plan_;
  Pose target_pose_robot_;
  bool plan_success_robot_ = false;
  std::vector<double> joint_group_positions_gripper_;
  RobotStatePtr current_state_gripper_;
  Plan gripper_trajectory_plan_;
  bool plan_success_gripper_ = false;
  // declare cartesian trajectory planning variables for robot
  std::vector<Pose> cartesian_waypoints_;
  RobotTrajectory cartesian_trajectory_plan_;
  const double jump_threshold_ = 0.0;
  const double end_effector_step_ = 0.01;
  double plan_fraction_robot_ = 0.0;

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

  void setup_joint_value_gripper(float angle) {
    // set the joint values for each joint of gripper
    // based on values provided
    // MOVEIT-V25: index 2 must be the driven knuckle joint of the group [verify];
    // by name: move_group_gripper_->setJointValueTarget("robotiq_85_left_knuckle_joint", angle);
    joint_group_positions_gripper_[2] = angle;
    move_group_gripper_->setJointValueTarget(joint_group_positions_gripper_);
  }

  void setup_named_pose_gripper(std::string pose_name) {
    // set the joint values for each joint of gripper
    // based on predefined pose names
    move_group_gripper_->setNamedTarget(pose_name);
  }

  void plan_trajectory_gripper() {
    // plan the gripper action
    plan_success_gripper_ = (move_group_gripper_->plan(gripper_trajectory_plan_) == moveit::core::MoveItErrorCode::SUCCESS);
  }

  void execute_trajectory_gripper() {
    // execute the planned gripper action
    if (plan_success_gripper_) {
      // MOVEIT-V04: report the execution result, not only the planning result
      if (move_group_gripper_->execute(gripper_trajectory_plan_) == moveit::core::MoveItErrorCode::SUCCESS) {
        RCLCPP_INFO(LOGGER, "Gripper Action Command Success !");
      } else {
        RCLCPP_INFO(LOGGER, "Gripper Action Command Execution Failed !");
      }
    } else {
      RCLCPP_INFO(LOGGER, "Gripper Action Command Failed !");
    }
  }
}; // class PickAndPlaceTrajectory

int main(int argc, char **argv) {
  // initialize program node
  rclcpp::init(argc, argv);
  // initialize base_node as shared pointer
  std::shared_ptr<rclcpp::Node> base_node = std::make_shared<rclcpp::Node>("pick_and_place_trajectory");
  // instantiate class
  PickAndPlaceTrajectory pick_and_place_trajectory_node(base_node);
  // execute trajectory plan
  pick_and_place_trajectory_node.execute_trajectory_plan();
  // shutdown ros2 node
  rclcpp::shutdown();
  return 0;
}
// End of Code
```
Fixes against the course's file: the execute steps check `execute()` (MOVEIT-V04) and the Cartesian steps run only a complete path and log the fraction (MOVEIT-V05). The building blocks are explained in [[moveit-cpp-move-group-interface]], [[moveit-cpp-gripper]] and [[moveit-cpp-cartesian-path]].

## Run
Launch file `launch/pick_and_place_trajectory.launch.py` and CMake entry as in [[moveit-cpp-package-setup]]; then, each in its own terminal:
```bash
ros2 launch my_moveit_config move_group.launch.py
ros2 launch my_moveit_config moveit_rviz.launch.py
ros2 launch moveit2_scripts pick_and_place_trajectory.launch.py
```

## Pitfalls
- The pregrasp pose is hard-coded for the box at (0.34, 0.13); exercise 5.5 replaces it with the pose from perception ([[moveit-learn-unit5]]).
- A failed step does not stop the sequence: the gripper may close on nothing; for real robots return the result of each step and abort.
- The approach uses Cartesian paths on purpose: a pose goal for 6 cm may swing the whole arm through another IK solution ([[moveit-approach-retreat]]).
