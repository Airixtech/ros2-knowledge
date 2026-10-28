---
id: moveit-cpp-gripper
type: reference
owner: equipo-ros2
updated: 2026-10-28
review_by: 2027-04-26
source: manual
confidentiality: internal
title: "Gripper: GripperCommand goals from the CLI and gripper_control.cpp (joint value and named target)"
domain: moveit
area: planning
distro: humble
tested: false
audience: dev
summary: "ros2 action send_goal /gripper_controller/gripper_cmd GripperCommand open 0.0 close 0.8; gripper_control.cpp: gripper group, setJointValueTarget, setNamedTarget open."
tags: [gripper, GripperCommand, control_msgs/action/GripperCommand, gripper_cmd, gripper_controller, ros2 action send_goal, max_effort, gripper_control.cpp, setNamedTarget, setJointValueTarget, open, close, Robotiq 85, robotiq_85_left_knuckle_joint, GripperActionController]
see: ["[[moveit-config-controllers-yaml]]", "[[moveit-cpp-move-group-interface]]", "[[moveit-cpp-package-setup]]", "[[moveit-pick-and-place]]", "[[core-action-cli-status]]"]
requires: [ros2-core, ros2-cpp, ros2-control]
version_notes:
  - "humble: GripperCommand goal = command.position + command.max_effort; the controller serves ~/gripper_cmd; with a position interface the position is written to the joint and max_effort is not used — https://github.com/ros-controls/ros2_controllers/blob/humble/gripper_controllers/include/gripper_controllers/hardware_interface_adapter.hpp (MOVEIT-V24)"
  - "humble: joint_group_positions_gripper_[2] assumes the third variable of the gripper group is the driven joint [verify]; setJointValueTarget(joint_name, value) sets it by name — https://github.com/moveit/moveit2/blob/humble/moveit_ros/planning_interface/move_group_interface/include/moveit/move_group_interface/move_group_interface.h (MOVEIT-V25)"
  - "humble: execute() result checked below; the course ignores it (MOVEIT-V04)"
---
# Gripper: from the CLI and from MoveIt

**TL;DR** The UR3e's Robotiq 85 gripper is driven by a `GripperCommand` action server, `/gripper_controller/gripper_cmd`. Send it goals from the command line, or plan for the `gripper` planning group with its own `MoveGroupInterface`: a joint value (close) or a named pose of the SRDF (`open`).

## From the command line
```bash
# open
ros2 action send_goal /gripper_controller/gripper_cmd control_msgs/action/GripperCommand "{command: {position: 0.0, max_effort: 0.0}}"
# close
ros2 action send_goal /gripper_controller/gripper_cmd control_msgs/action/GripperCommand "{command: {position: 0.8, max_effort: 0.0}}"
```
The goal is a `GripperCommand` with `position` and `max_effort`. A gripper action controller with a position interface writes `position` to its joint as it is (here the knuckle angle; the message's comment says "gap size (in meters)") and does not use `max_effort` (MOVEIT-V24). Action CLI: [[core-action-cli-status]].

## `src/gripper_control.cpp` (exercise 3.5): close, wait 3 s, open
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
static const std::string PLANNING_GROUP_GRIPPER = "gripper";

class GripperControl {
public:
  GripperControl(rclcpp::Node::SharedPtr base_node_) : base_node_(base_node_) {
    RCLCPP_INFO(LOGGER, "Initializing Class: Gripper Control...");
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
    move_group_gripper_ = std::make_shared<MoveGroupInterface>(move_group_node_, PLANNING_GROUP_GRIPPER);
    // get initial state of gripper
    joint_model_group_gripper_ = move_group_gripper_->getCurrentState()->getJointModelGroup(PLANNING_GROUP_GRIPPER);
    // get current state of gripper
    current_state_gripper_ = move_group_gripper_->getCurrentState(10);
    current_state_gripper_->copyJointGroupPositions(joint_model_group_gripper_, joint_group_positions_gripper_);
    // set start state of gripper to current state
    move_group_gripper_->setStartStateToCurrentState();
    // indicate initialization
    RCLCPP_INFO(LOGGER, "Class Initialized: Gripper Control");
  }

  ~GripperControl() {
    // indicate termination
    RCLCPP_INFO(LOGGER, "Class Terminated: Gripper Control");
  }

  void execute_trajectory_plan() {
    RCLCPP_INFO(LOGGER, "Planning and Executing Gripper Control...");
    // close the gripper
    RCLCPP_INFO(LOGGER, "Closing Gripper...");
    // setup the gripper joint value
    RCLCPP_INFO(LOGGER, "Preparing Gripper Value...");
    setup_joint_value_gripper(+0.780);
    // plan and execute the trajectory
    RCLCPP_INFO(LOGGER, "Planning Gripper Action...");
    plan_trajectory_gripper();
    RCLCPP_INFO(LOGGER, "Executing Gripper Action...");
    execute_trajectory_gripper();
    RCLCPP_INFO(LOGGER, "Gripper Closed");
    // wait for few seconds
    std::this_thread::sleep_for(std::chrono::milliseconds(3000));
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
    RCLCPP_INFO(LOGGER, "Gripper Control Execution Complete");
  }

private:
  // using shorthand for lengthy class references
  using MoveGroupInterface = moveit::planning_interface::MoveGroupInterface;
  using JointModelGroup = moveit::core::JointModelGroup;
  using RobotStatePtr = moveit::core::RobotStatePtr;
  using Plan = MoveGroupInterface::Plan;

  // declare rclcpp base node class
  rclcpp::Node::SharedPtr base_node_;
  // declare move_group node
  rclcpp::Node::SharedPtr move_group_node_;
  // declare single threaded executor for move_group node
  rclcpp::executors::SingleThreadedExecutor executor_;
  // declare move_group_interface variables for gripper
  std::shared_ptr<MoveGroupInterface> move_group_gripper_;
  // declare joint_model_group for gripper
  const JointModelGroup *joint_model_group_gripper_;
  // declare trajectory planning variables for gripper
  std::vector<double> joint_group_positions_gripper_;
  RobotStatePtr current_state_gripper_;
  Plan gripper_trajectory_plan_;
  bool plan_success_gripper_ = false;

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
}; // class GripperControl

int main(int argc, char **argv) {
  // initialize program node
  rclcpp::init(argc, argv);
  // initialize base_node as shared pointer
  std::shared_ptr<rclcpp::Node> base_node = std::make_shared<rclcpp::Node>("gripper_control");
  // instantiate class
  GripperControl gripper_control_node(base_node);
  // execute trajectory plan
  gripper_control_node.execute_trajectory_plan();
  // shutdown ros2 node
  rclcpp::shutdown();
  return 0;
}
// End of Code
```
- `PLANNING_GROUP_GRIPPER = "gripper"` and its own `MoveGroupInterface`, joint model group and state, as for the arm ([[moveit-cpp-move-group-interface]]).
- Close: one joint value (0.780) and `setJointValueTarget(vector)`; open: `setNamedTarget("open")`, a pose defined in the Setup Assistant (SRDF `group_state`).

## Files and run
`touch src/gripper_control.cpp`, `launch/gripper_control.launch.py` (template of [[moveit-cpp-package-setup]], `name`/`executable` = `gripper_control`), CMake block for `gripper_control`, then:
```bash
cd ~/ros2_ws
colcon build --packages-select moveit2_scripts
source install/setup.bash
ros2 launch moveit2_scripts gripper_control.launch.py
```
with `move_group` and RViz2 running: the gripper closes and opens.

## Pitfalls
- The gripper only moves from MoveIt when `moveit_controllers.yaml` declares it as `GripperCommand` with `action_ns: gripper_cmd` ([[moveit-config-controllers-yaml]]).
- Close values differ per task: 0.8 (CLI), 0.780 (this program), 0.440 and 0.500 when holding the box ([[moveit-approach-retreat]], [[moveit-pick-and-place]]).
