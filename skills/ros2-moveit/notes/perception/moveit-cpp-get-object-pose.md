---
id: moveit-cpp-get-object-pose
type: reference
owner: equipo-ros2
updated: 2026-10-28
review_by: 2027-04-26
source: manual
confidentiality: internal
title: "C++ action client for /find_objects that prints the object position: get_object_pose_action_client"
domain: moveit
area: perception
distro: humble
tested: false
audience: dev
summary: "get_object_pose_action_client: rclcpp_action client for /find_objects (plan_grasps false), result_callback prints objects[0] primitive_poses[0] position; CMakeLists."
tags: [get_object_pose_action_client, rclcpp_action, create_client, async_send_goal, SendGoalOptions, result_callback, WrappedResult, ResultCode, FindGraspableObjects, primitive_poses, spin_some, ament_cmake, grasping_msgs, object position]
see: ["[[moveit-find-objects-action]]", "[[moveit-grasping-msgs]]", "[[moveit-cpp-filter-objects]]", "[[cpp-action-client]]", "[[moveit-learn-unit5]]"]
requires: [ros2-core, ros2-cpp]
version_notes:
  - "humble: objects[0] / primitive_poses[0] read without a size check (fixed below) (MOVEIT-V08)"
  - "humble: install(DIRECTORY launch …) without a launch/ folder; std_msgs and geometry_msgs found in CMake but missing from package.xml [verify] (MOVEIT-V10)"
  - "humble: the wait loop spins without sleeping; goal_handle_future unused (MOVEIT-V44)"
  - "lyrical: ament_target_dependencies removed: target_link_libraries(get_object_pose_action_client rclcpp::rclcpp rclcpp_action::rclcpp_action ${grasping_msgs_TARGETS}) [verify] (MOVEIT-V17)"
---
# C++ client that gets the object's position

**TL;DR** Exercise 5.2: a node with an `rclcpp_action` client for `/find_objects` sends `plan_grasps = false`, and its result callback prints the `[X, Y]` (and Z) position of the first detected object, `objects[0].object.primitive_poses[0].position` ([[moveit-grasping-msgs]]). General action-client patterns: [[cpp-action-client]].

## Package
```bash
ros2 pkg create get_object_pose_action_client --dependencies grasping_msgs rclcpp rclcpp_action
```
`CMakeLists.txt`:
```cmake
cmake_minimum_required(VERSION 3.8)
project(get_object_pose_action_client)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclcpp_action REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(grasping_msgs REQUIRED)

# add executables and dependencies
add_executable(get_object_pose_action_client
  src/get_object_pose_action_client.cpp)
target_include_directories(get_object_pose_action_client
  PUBLIC include)
ament_target_dependencies(get_object_pose_action_client
  rclcpp
  rclcpp_action
  std_msgs
  geometry_msgs
  grasping_msgs)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

# install the executables
install(TARGETS
  get_object_pose_action_client
  DESTINATION lib/${PROJECT_NAME})

# install the launch files
# MOVEIT-V10: the package has no launch/ folder; keep this only after creating one [verify]
# install(DIRECTORY
#   launch
#   DESTINATION share/${PROJECT_NAME}/)

ament_package()
```
`std_msgs` and `geometry_msgs` are found here but the package was created without them: add `<depend>std_msgs</depend>` and `<depend>geometry_msgs</depend>` to `package.xml`, or drop both (the client uses neither directly, MOVEIT-V10).

## `src/get_object_pose_action_client.cpp`
```cpp
#include "grasping_msgs/action/find_graspable_objects.hpp"
#include "rclcpp/rclcpp.hpp"
#include "rclcpp_action/client.hpp"
#include "rclcpp_action/rclcpp_action.hpp"
#include <memory>
#include <string>

class GetObjectPoseActionClient : public rclcpp::Node {
public:
  explicit GetObjectPoseActionClient(const rclcpp::NodeOptions &node_options = rclcpp::NodeOptions())
      : Node("get_object_pose_action_client", node_options) {
    RCLCPP_INFO(this->get_logger(), "Initializing Node: get_object_pose_action_client...");
    // initialize action client
    this->action_client_ = rclcpp_action::create_client<FindGraspableObjects>(this->get_node_base_interface(), this->get_node_graph_interface(), this->get_node_logging_interface(), this->get_node_waitables_interface(), action_name_);
    RCLCPP_INFO(this->get_logger(), "Initialized Action Client for %s", action_name_.c_str());
    // indicate initialization
    RCLCPP_INFO(this->get_logger(), "Initialized Node: get_object_pose_action_client");
  }

  ~GetObjectPoseActionClient() {
    // indicate termination
    RCLCPP_INFO(this->get_logger(), "Terminated Node: get_object_pose_action_client");
  }

  bool is_goal_done() const {
    return this->goal_done_;
  }

  void send_goal() {
    // send goal to the action server
    // reset goal done variable to false
    this->goal_done_ = false;
    // check if action client is ready
    if (!this->action_client_) {
      RCLCPP_ERROR(this->get_logger(), "Action Client is Not Initialized");
    } else {
      // do nothing
    }
    // check if action server is ready
    if (!this->action_client_->wait_for_action_server(std::chrono::seconds(10))) {
      RCLCPP_ERROR(this->get_logger(), "Action Server Unavailable. Waiting Timed Out.");
      this->goal_done_ = true;
      return;
    } else {
      RCLCPP_INFO(this->get_logger(), "Awaiting Action Server: %s", action_name_.c_str());
    }
    RCLCPP_INFO(this->get_logger(), "Sending Action Goal...");
    // set action goal
    auto goal_msg = FindGraspableObjects::Goal();
    goal_msg.plan_grasps = false;
    // prepare action goal handler
    auto send_goal_options = rclcpp_action::Client<FindGraspableObjects>::SendGoalOptions();
    send_goal_options.goal_response_callback = std::bind(&GetObjectPoseActionClient::goal_response_callback, this, std::placeholders::_1);
    send_goal_options.result_callback = std::bind(&GetObjectPoseActionClient::result_callback, this, std::placeholders::_1);
    send_goal_options.feedback_callback = std::bind(&GetObjectPoseActionClient::feedback_callback, this, std::placeholders::_1, std::placeholders::_2);
    // send action goal to action server
    auto goal_handle_future = this->action_client_->async_send_goal(goal_msg, send_goal_options);
    RCLCPP_INFO(this->get_logger(), "Goal Sent to Action Server: %s", action_name_.c_str());
  }

private:
  // using shorthand for lengthy class references
  using FindGraspableObjects = grasping_msgs::action::FindGraspableObjects;
  using FindGraspableObjectsGoalHandle = rclcpp_action::ClientGoalHandle<FindGraspableObjects>;

  // declare action client
  rclcpp_action::Client<FindGraspableObjects>::SharedPtr action_client_;

  // declare action client variables
  const std::string action_name_ = "/find_objects";
  bool goal_done_ = false;

  void goal_response_callback(const FindGraspableObjectsGoalHandle::SharedPtr &goal_handle) {
    // function to check if action goal is accepted or rejected by server
    if (!goal_handle) {
      RCLCPP_ERROR(this->get_logger(), "Goal Rejected by Action Server: %s", action_name_.c_str());
    } else {
      RCLCPP_INFO(this->get_logger(), "Goal Accepted by Action Server: %s", action_name_.c_str());
    }
  }

  void feedback_callback(FindGraspableObjectsGoalHandle::SharedPtr, const std::shared_ptr<const FindGraspableObjects::Feedback> action_feedback) {
    // function to check for action feedback from server
    RCLCPP_INFO(this->get_logger(), "Feedback: Ignored");
  }

  void result_callback(const FindGraspableObjectsGoalHandle::WrappedResult &action_result) {
    // function to check for action completion and result from server
    RCLCPP_INFO(this->get_logger(), "Getting Result from Action Server: %s", action_name_.c_str());
    this->goal_done_ = true;
    switch (action_result.code) {
      case rclcpp_action::ResultCode::SUCCEEDED:
        break;
      case rclcpp_action::ResultCode::ABORTED:
        RCLCPP_ERROR(this->get_logger(), "Goal was Aborted");
        return;
      case rclcpp_action::ResultCode::CANCELED:
        RCLCPP_ERROR(this->get_logger(), "Goal was Canceled");
        return;
      default:
        RCLCPP_ERROR(this->get_logger(), "Unknown Result Code");
        return;
    }
    RCLCPP_INFO(this->get_logger(), "Result: Received !");
    // MOVEIT-V08: the result may hold no object, or an object without primitives
    if (action_result.result->objects.empty() ||
        action_result.result->objects[0].object.primitive_poses.empty()) {
      RCLCPP_ERROR(this->get_logger(), "No object detected");
      return;
    }
    // get the first object from detected list of objects
    RCLCPP_INFO(this->get_logger(), "# ~~~~~~~~~~~ ~~~~~~~~~~~ ~~~~~~~~~~~ #");
    RCLCPP_INFO(this->get_logger(), "Result: Object of Interest Position:");
    RCLCPP_INFO(this->get_logger(), "PosX: %+0.3f, PosY: %+0.3f, PosZ: %+0.3f", action_result.result->objects[0].object.primitive_poses[0].position.x, action_result.result->objects[0].object.primitive_poses[0].position.y, action_result.result->objects[0].object.primitive_poses[0].position.z);
    RCLCPP_INFO(this->get_logger(), "# ~~~~~~~~~~~ ~~~~~~~~~~~ ~~~~~~~~~~~ #");
  }
}; // class GetObjectPoseActionClient

int main(int argc, char *argv[]) {
  // initialize program node
  rclcpp::init(argc, argv);
  // initialize action client
  auto action_client = std::make_shared<GetObjectPoseActionClient>();
  // send a goal to action server
  action_client->send_goal();
  while (!action_client->is_goal_done()) {
    rclcpp::spin_some(action_client);
  }
  // shutdown ros2 node
  rclcpp::shutdown();
  return 0;
}
// End of Code
```
Fix against the course's file: the empty-result check (MOVEIT-V08).

## Run
With the simulation, the box (x 0.5) and `basic_grasping_perception_node` running ([[moveit-find-objects-action]]):
```bash
cd ~/ros2_ws && colcon build --packages-select get_object_pose_action_client && source install/setup.bash
ros2 run get_object_pose_action_client get_object_pose_action_client
```

## Pitfalls
- `main()` waits with `while (!action_client->is_goal_done()) rclcpp::spin_some(action_client);`, a loop that never sleeps: one CPU core is busy until the result arrives (`spin_until_future_complete` or a short sleep avoids it); `goal_handle_future` is unused and the code goes on after "Action Client is Not Initialized" (MOVEIT-V44).
- Several detected objects → this program prints only the first; select by shape and size: [[moveit-cpp-filter-objects]].
