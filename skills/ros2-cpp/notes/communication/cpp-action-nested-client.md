---
id: cpp-action-nested-client
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "An action server that calls Nav2 NavigateToPose: initial pose, wait for localization, futures in a worker thread"
domain: cpp
area: communication
distro: humble
tested: false
audience: dev
summary: "action_server.cpp: /go_to_pose server forwarding to Nav2 NavigateToPose; /initialpose publisher, wait for /amcl_pose, wait_for, async_get_result in the execute thread."
tags: [rclcpp_action, NavigateToPose, nav2_msgs, initialpose, amcl_pose, PoseWithCovarianceStamped, tf2::Quaternion, setRPY, tf2::toMsg, async_send_goal, async_get_result, future wait_for, count_subscribers, get_topic_names_and_types, action_server.cpp]
see: ["[[cpp-action-server]]", "[[cpp-action-custom-timeout]]", "[[core-nav2-python-client]]", "[[cpp-exec-blocking]]"]
requires: [ros2-core]
version_notes:
  - "course: the explanation waits with rclcpp::spin_until_future_complete(get_node_base_interface(), future) inside execute(); the node is already spun by main(), so that call throws std::runtime_error ('has already been added to an executor'); the file's future.wait_for() is right — https://github.com/ros2/rclcpp/blob/humble/rclcpp/src/rclcpp/executor.cpp (CPP-V10)"
  - "course: after the timeout cancel of unit 7.8 this server keeps waiting for Nav2 (it never checks is_canceling() nor cancels the Nav2 goal) and reports SUCCEEDED (CPP-V11)"
  - "lyrical: tf2/LinearMath/Quaternion.h removed; Quaternion.hpp exists since Humble (CPP-V22, V44)"
---
# An action server that calls Nav2

**TL;DR** `/go_to_pose` (`leo_description/action/GoToPose`) is a thin server around Nav2's `/navigate_to_pose`: one node is both an action **server** and an action **client**. The constructor publishes an initial pose for localization; `execute()` (in its own thread) sends the Nav2 goal and waits on its futures with `wait_for()`/`wait()`, which works because `main()`'s executor delivers the responses. Do **not** call `spin_until_future_complete` there (CPP-V10). Nav2 itself is out of scope here (see the ros2-nav2 skill).

## Package
```bash
cd ~/ros2_ws/src
ros2 pkg create my_action_server --build-type ament_cmake --dependencies rclcpp rclcpp_action leo_description geometry_msgs nav2_msgs tf2 tf2_geometry_msgs action_msgs
touch my_action_server/src/action_server.cpp
```

## `src/action_server.cpp`
```cpp
#include <chrono>
#include <functional>
#include <memory>
#include <thread>
#include "action_msgs/msg/goal_status.hpp"
#include "geometry_msgs/msg/pose_with_covariance_stamped.hpp"
#include "leo_description/action/go_to_pose.hpp"
#include "nav2_msgs/action/navigate_to_pose.hpp"
#include "rclcpp/rclcpp.hpp"
#include "rclcpp_action/rclcpp_action.hpp"
#include "tf2/LinearMath/Quaternion.hpp"   // the course includes Quaternion.h (removed in Lyrical)
#include "tf2_geometry_msgs/tf2_geometry_msgs.hpp"

class MyActionServer : public rclcpp::Node {
public:
  using GoToPose = leo_description::action::GoToPose;
  using GoalHandleGoToPose = rclcpp_action::ServerGoalHandle<GoToPose>;
  using NavigateToPose = nav2_msgs::action::NavigateToPose;
  using GoalHandleNavigateToPose =
      rclcpp_action::ClientGoalHandle<NavigateToPose>;

  MyActionServer() : Node("my_action_server") {
    using namespace std::placeholders;

    // Action server to accept goals
    this->action_server_ = rclcpp_action::create_server<GoToPose>(
        this, "go_to_pose",
        std::bind(&MyActionServer::handle_goal, this, _1, _2),
        std::bind(&MyActionServer::handle_cancel, this, _1),
        std::bind(&MyActionServer::handle_accepted, this, _1));

    // Publisher to set initial pose
    initial_pose_publisher_ =
        this->create_publisher<geometry_msgs::msg::PoseWithCovarianceStamped>(
            "/initialpose", 10);

    // Action client for navigation to pose
    nav_to_pose_client_ =
        rclcpp_action::create_client<NavigateToPose>(this, "/navigate_to_pose");

    // Wait for the localization node to be ready
    wait_for_localization();

    // Set the initial pose to (0, 0, 0)
    set_initial_pose(0.0, 0.0, 0.0);
  }

private:
  rclcpp_action::Server<GoToPose>::SharedPtr action_server_;
  rclcpp::Publisher<geometry_msgs::msg::PoseWithCovarianceStamped>::SharedPtr
      initial_pose_publisher_;
  rclcpp_action::Client<NavigateToPose>::SharedPtr nav_to_pose_client_;

  void wait_for_localization() {
    RCLCPP_INFO(this->get_logger(), "Waiting for localization to be active...");

    // Wait for subscribers to /initialpose
    while (this->count_subscribers("/initialpose") == 0) {
      RCLCPP_INFO(this->get_logger(),
                  "Waiting for subscribers to /initialpose...");
      std::this_thread::sleep_for(std::chrono::milliseconds(1000));
    }

    // Wait for /amcl_pose topic
    while (!topic_exists("/amcl_pose")) {
      RCLCPP_INFO(this->get_logger(), "Waiting for /amcl_pose topic...");
      std::this_thread::sleep_for(std::chrono::milliseconds(1000));
    }

    RCLCPP_INFO(this->get_logger(), "Localization is active.");
  }

  bool topic_exists(const std::string &topic_name) {
    auto topics = this->get_topic_names_and_types();
    for (const auto &topic : topics) {
      if (topic.first == topic_name) {
        return true;
      }
    }
    return false;
  }

  void set_initial_pose(double x, double y, double yaw) {
    auto initial_pose = geometry_msgs::msg::PoseWithCovarianceStamped();
    initial_pose.header.frame_id = "map";
    initial_pose.header.stamp = this->get_clock()->now();

    initial_pose.pose.pose.position.x = x;
    initial_pose.pose.pose.position.y = y;

    // Set the orientation as quaternion (for yaw rotation)
    tf2::Quaternion q;
    q.setRPY(0, 0, yaw);
    initial_pose.pose.pose.orientation = tf2::toMsg(q);

    // Publish the initial pose multiple times
    for (int i = 0; i < 10; ++i) {
      initial_pose_publisher_->publish(initial_pose);
      RCLCPP_INFO(this->get_logger(), "Publishing initial pose (%d/10)", i + 1);
      std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }

    RCLCPP_INFO(this->get_logger(),
                "Initial pose set to x: %.2f, y: %.2f, yaw: %.2f", x, y, yaw);
  }

  rclcpp_action::GoalResponse
  handle_goal(const rclcpp_action::GoalUUID &uuid,
              std::shared_ptr<const GoToPose::Goal> goal) {
    RCLCPP_INFO(this->get_logger(),
                "Received goal request with x: %.2f, y: %.2f, yaw: %.2f",
                goal->x, goal->y, goal->yaw);
    (void)uuid;
    return rclcpp_action::GoalResponse::ACCEPT_AND_EXECUTE;
  }

  rclcpp_action::CancelResponse
  handle_cancel(const std::shared_ptr<GoalHandleGoToPose> goal_handle) {
    RCLCPP_INFO(this->get_logger(), "Received request to cancel goal");
    (void)goal_handle;
    return rclcpp_action::CancelResponse::ACCEPT;
  }

  void handle_accepted(const std::shared_ptr<GoalHandleGoToPose> goal_handle) {
    using namespace std::placeholders;
    // This needs to return quickly to avoid blocking the executor, so spin up a
    // new thread
    std::thread{std::bind(&MyActionServer::execute, this, _1), goal_handle}
        .detach();
  }

  void execute(const std::shared_ptr<GoalHandleGoToPose> goal_handle) {
    RCLCPP_INFO(this->get_logger(), "Executing goal");

    const auto goal = goal_handle->get_goal();
    auto feedback = std::make_shared<GoToPose::Feedback>();
    auto result = std::make_shared<GoToPose::Result>();

    feedback->feedback = "Navigating to goal...";
    goal_handle->publish_feedback(feedback);

    // Send navigation goal
    bool navigation_result = send_navigation_goal(goal->x, goal->y, goal->yaw);

    if (navigation_result) {
      RCLCPP_INFO(this->get_logger(), "Goal reached successfully!");
      result->success = true;
      goal_handle->succeed(result);
    } else {
      RCLCPP_INFO(this->get_logger(), "Failed to reach goal :(");
      result->success = false;
      goal_handle->abort(result);
    }
  }

  bool send_navigation_goal(double x, double y, double yaw) {
    auto goal_msg = NavigateToPose::Goal();

    // Set goal position
    goal_msg.pose.pose.position.x = x;
    goal_msg.pose.pose.position.y = y;

    // Set goal orientation (yaw as quaternion)
    tf2::Quaternion q;
    q.setRPY(0, 0, yaw);
    goal_msg.pose.pose.orientation = tf2::toMsg(q);

    // Set the frame and timestamp
    goal_msg.pose.header.frame_id = "map";
    goal_msg.pose.header.stamp = this->get_clock()->now();

    // Wait for the NavigateToPose action server
    RCLCPP_INFO(this->get_logger(),
                "Waiting for the NavigateToPose action server...");
    if (!nav_to_pose_client_->wait_for_action_server(
            std::chrono::seconds(10))) {
      RCLCPP_ERROR(this->get_logger(),
                   "NavigateToPose action server not available");
      return false;
    }

    // Send the goal
    RCLCPP_INFO(this->get_logger(),
                "Sending navigation goal to: x=%.2f, y=%.2f, yaw=%.2f", x, y,
                yaw);
    auto send_goal_future = nav_to_pose_client_->async_send_goal(goal_msg);

    // Wait for goal to be accepted
    if (send_goal_future.wait_for(std::chrono::seconds(10)) !=
        std::future_status::ready) {
      RCLCPP_ERROR(this->get_logger(), "Failed to send goal");
      return false;
    }

    auto nav_goal_handle = send_goal_future.get();
    if (!nav_goal_handle) {
      RCLCPP_INFO(this->get_logger(), "Navigation goal rejected");
      return false;
    }

    RCLCPP_INFO(this->get_logger(), "Navigation goal accepted");

    // Wait for result
    auto get_result_future =
        nav_to_pose_client_->async_get_result(nav_goal_handle);

    get_result_future.wait();

    auto nav_result = get_result_future.get();
    if (nav_result.code == rclcpp_action::ResultCode::SUCCEEDED) {
      RCLCPP_INFO(this->get_logger(), "Navigation succeeded");
      return true;
    } else {
      RCLCPP_INFO(this->get_logger(), "Navigation failed with status: %d",
                  static_cast<int>(nav_result.code));
      return false;
    }
  }
};

int main(int argc, char **argv) {
  rclcpp::init(argc, argv);
  auto node = std::make_shared<MyActionServer>();
  rclcpp::spin(node);
  rclcpp::shutdown();
  return 0;
}
```
- `wait_for_localization()` blocks the constructor until something subscribes to `/initialpose` (`count_subscribers`) and `/amcl_pose` exists (`get_topic_names_and_types()` returns a `std::map`, so `topics.find(topic_name)` would work as well as the loop).
- `set_initial_pose(0.0, 0.0, 0.0)`: the localization starts at the map origin; the pose is published 10 times, 100 ms apart. `tf2::Quaternion::setRPY` + `tf2::toMsg` turn yaw into the quaternion Nav2 expects; the goal is in the `map` frame, stamped with the node clock.
- `wait_for_action_server(10s)`, then `async_send_goal()` returns a future of the Nav2 goal handle; `wait_for(10s)` waits for acceptance, `async_get_result()` + `wait()` for the end. The futures are filled by the executor of `main()`, which keeps running because `execute()` is on another thread.
- The course explains this step with `rclcpp::spin_until_future_complete(this->get_node_base_interface(), send_goal_future)`: in this thread that call throws, since the node is already in the executor of `main()` (CPP-V10).

## The custom version (unit 7.8)
`src/custom_action_server.cpp` is the same program with `#include "custom_interfaces/action/go_to_pose.hpp"`, `using GoToPose = custom_interfaces::action::GoToPose;`, a constructor `explicit MyActionServer(const rclcpp::NodeOptions &options = rclcpp::NodeOptions()) : Node("my_action_server", options)`, `initial_pose.header.stamp = get_clock()->now();` refreshed inside the publishing loop, `<future>` and `<string>` added to the includes, no `this->`, fewer comments, `RCLCPP_WARN` for failures, and reworded logs: `"Received goal request: " "x=%.2f, y=%.2f, yaw=%.2f"`, `"Received request to cancel goal."`, `"Executing goal."`, `"Goal reached successfully."`, `"Failed to reach goal."`, `"Waiting for NavigateToPose action server..."`, `"NavigateToPose action server is not available."`, `"Sending navigation goal: " "x=%.2f, y=%.2f, yaw=%.2f"`, `"Timed out while sending navigation goal."`, `"Navigation goal was rejected."`, `"Navigation goal accepted."`, `"Navigation succeeded."`, `"Navigation failed with result code: %d"` (the result future is named `result_future`). It still ignores cancel requests: with the timeout client of [[cpp-action-custom-timeout]] the log shows `Received request to cancel goal.` and then `Navigation succeeded.` (CPP-V11). To honour the cancel, loop on `get_result_future.wait_for(100ms)` and, when `goal_handle->is_canceling()`, call `nav_to_pose_client_->async_cancel_goal(nav_goal_handle)` and `goal_handle->canceled(result)` `[verify]`.

## CMakeLists.txt
```cmake
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclcpp_action REQUIRED)
find_package(leo_description REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(nav2_msgs REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_geometry_msgs REQUIRED)
find_package(action_msgs REQUIRED)
# New GoToPose interface
find_package(custom_interfaces REQUIRED)

add_executable(action_server src/action_server.cpp)
ament_target_dependencies(action_server
  "rclcpp"
  "rclcpp_action"
  "leo_description"
  "geometry_msgs"
  "nav2_msgs"
  "tf2"
  "tf2_geometry_msgs"
  "action_msgs")

add_executable(custom_action_server_node src/custom_action_server.cpp)
ament_target_dependencies(custom_action_server_node
  rclcpp
  rclcpp_action
  custom_interfaces
  geometry_msgs
  nav2_msgs
  tf2
  tf2_geometry_msgs
  action_msgs
)

install(TARGETS
	action_server
	custom_action_server_node
  DESTINATION lib/${PROJECT_NAME})
```
`package.xml`: `<depend>` on `rclcpp`, `rclcpp_action`, `leo_description`, `geometry_msgs`, `nav2_msgs`, `tf2`, `tf2_geometry_msgs`, `action_msgs` and `custom_interfaces`. Source the simulation workspace before building, so `leo_description` is found.

## Run
```bash
ros2 launch leo_description loc_nav.launch.py      # Nav2 + localization; "Timed out waiting for transform from base_link to map" until the initial pose arrives
ros2 run my_action_server action_server           # publishes the initial pose; Nav2 reports "Managed nodes are active"
ros2 action list                                   # /go_to_pose among the Nav2 actions (/navigate_to_pose, /follow_path, /spin, ...)
ros2 action info /go_to_pose -t                    # Action servers: 1  /my_action_server [leo_description/action/GoToPose]
ros2 action send_goal /go_to_pose leo_description/action/GoToPose "{x: -8.0, y: 6.0, yaw: 1.57}"
```
The rover drives towards (−8, 6); in the course a meteor lands next to it on the way, which motivates the timeout client of [[cpp-action-custom-timeout]].
