---
id: bt-learn-project
type: reference
owner: equipo-ros2
updated: 2026-10-15
review_by: 2027-04-13
source: manual
confidentiality: internal
title: "Course project: cell 1 to cell 3 with a laser-checked BT"
domain: bt
area: learn
distro: humble
tested: false
audience: students
summary: "Course project: cell 1 to cell 3 through two laser-checked doors; CMake edits, hint, solution test_project.cpp, known issues."
tags: [course, project, test_project, cells, doors, ReactiveSequence, Constraint, Direction, CMakeLists, students]
see: ["[[bt-learn-unit5]]", "[[bt-ros2-node-pattern]]", "[[bt-ros2-shared-node]]", "[[bt-learn-start-here]]"]
requires: [ros2-core]
version_notes:
  - "all: in the solution MoveRobot's odometry callback is the only writer of position_x/position_y and its node is never spun, so MoveRobot cannot succeed [verify] (BT-V35)"
  - "lyrical: ament_target_dependencies is removed (deprecated in Kilted) — see ros2-core audit (V09)"
  - "humble: tf2_geometry_msgs.h is obsolete, include tf2_geometry_msgs.hpp — https://github.com/ros2/geometry2/blob/humble/tf2_geometry_msgs/include/tf2_geometry_msgs/tf2_geometry_msgs.h (BT-V32)"
---
# Course project: cell 1 to cell 3 with a laser-checked BT

**TL;DR** Architect a BT that takes the robot automatically from cell 1 to cell 3. The laser detects the free way through each door (cell 1 → 2, cell 2 → 3); you open the doors by pausing the simulation and deleting them. In cell 2 the robot must ignore the first (open) door and wait for the way to cell 3. It is the unit 1 task with a modified tree and C++ code.

## Setup
```bash
cd ~/ros2_ws/src/bt_course_files/behaviortree_ros2/test
touch test_project.cpp
```
Uncomment in the package's `CMakeLists.txt`:
```cmake
#add_executable(test_project test/test_project.cpp)
#target_include_directories(test_project PRIVATE
# $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
# $<INSTALL_INTERFACE:include>)
#ament_target_dependencies(test_project rclcpp geometry_msgs sensor_msgs nav2_msgs tf2_ros sensor_msgs image_transport cv_bridge OpenCV
# ${THIS_PACKAGE_INCLUDE_DEPENDS}
#)
```
```cmake
install(TARGETS
  test_unit1
  test_unit2
  test_unit3
  test_unit4
  test_unit5
  # test_project
  RUNTIME DESTINATION bin
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib)
```
```bash
ros2 launch my_package launch_world_project.launch.py
```

## Hint
One possible tree (other solutions are fine). Legend: `[→]` Sequence · `[R→]` ReactiveSequence · leaves are actions · `key="value"` port.
```text
Root
└── [→] Sequence
    ├── SetBlackboard  value="360" output_key="Interface"
    ├── SetBlackboard  value="0.1" output_key="DefectFactor"
    ├── [R→] ReactiveSequence
    │   ├── Rotating  input="{Interface}"
    │   └── ReadingLaser  inputlaser="{DefectFactor}"
    └── MoveRobot name="move_robot"
```

## Solution (`solution_test_project.cpp`)
Also in the course files: `~/ros2_ws/src/bt_course_files/behaviortree_ros2/test/solution_test_project.cpp`. Its tree, generated from its XML:
```text
BehaviorTree
└── [→] Sequence
    ├── SetBlackboard  output_key="Interface" value="360"
    ├── SetBlackboard  output_key="Constraint1" value="180"
    ├── SetBlackboard  output_key="Constraint2" value="270"
    ├── SetBlackboard  output_key="Direction1" value="1"
    ├── SetBlackboard  output_key="Direction2" value="2"
    ├── [R→] ReactiveSequence
    │   ├── Rotating  input="{Interface}"
    │   └── ReadingLaser  input="{Constraint1}"
    ├── MoveRobot  input="{Direction1}"
    ├── [R→] ReactiveSequence
    │   ├── Rotating  input="{Interface}"
    │   └── ReadingLaser  input="{Constraint2}"
    └── MoveRobot  input="{Direction2}"
```
```cpp
#include <behaviortree_ros2/bt_action_node.hpp>
#include <iostream>
#include <rclcpp/executors.hpp>
#include <rclcpp/rclcpp.hpp>
#include "behaviortree_cpp_v3/basic_types.h"
#include "behaviortree_cpp_v3/tree_node.h"
#include "std_msgs/msg/string.hpp"
#include <atomic>
#include <chrono>
#include <cmath>
#include <functional>
#include <memory>
#include <string>
#include <thread>
#include "geometry_msgs/msg/twist.hpp"
#include "nav_msgs/msg/odometry.hpp"
#include "sensor_msgs/msg/laser_scan.hpp"
#include <geometry_msgs/msg/pose_stamped.hpp>
#include <tf2_geometry_msgs/tf2_geometry_msgs.h>
#include "behaviortree_cpp_v3/loggers/bt_file_logger.h"
#include <math.h>

using namespace std::chrono_literals;
using std::chrono::milliseconds;
using std::placeholders::_1;
std::atomic_bool switchActive{true};
using namespace BT;

float data1;
float data2;
float robotAngle;
float position_x;
float position_y;
//-------------------------------------------------------------------------------------
//------------------------------LASER--------------------------------------------------
//-------------------------------------------------------------------------------------
class ReadingLaser : public BT::SyncActionNode, public rclcpp::Node {
private:
  rclcpp::Subscription<sensor_msgs::msg::LaserScan>::SharedPtr subscription_;
  void topic_callback(const sensor_msgs::msg::LaserScan::SharedPtr _msg) {
    data2 = _msg->ranges[100];
    data1 = _msg->ranges[0];
  }

public:
  ReadingLaser(const std::string &name, const BT::NodeConfiguration &config)
      : BT::SyncActionNode(name, config), Node("scanner_node") {
    RCLCPP_INFO(this->get_logger(), "This is a CONSTRUCTOR");
    auto sensor_qos = rclcpp::QoS(rclcpp::SensorDataQoS());
    subscription_ = this->create_subscription<sensor_msgs::msg::LaserScan>(
        "/scan", sensor_qos,
        [&](const sensor_msgs::msg::LaserScan::SharedPtr msg) {
          topic_callback(msg);
        });
  }

  BT::NodeStatus tick() override {
    auto res = getInput<float>("input");
    if (!res) {
      throw RuntimeError("error reading port [input]:", res.error());
    }
    float angleConstraint = res.value();
    RCLCPP_INFO(this->get_logger(), "This is a tick()-------");
    RCLCPP_INFO(this->get_logger(), "NODE : LASER DATA ===>: '%f' '%f'", data1,
                data2);
    // 200 readings, from right to left, from -57 to 57 degress
    // calculate new velocity cmd
    float min = 10;
    float current;
    for (int i = 0; i < 200; i++) {
      current = data1;
      if (current < min) {
        min = current;
      }
    }
    std::this_thread::sleep_for(std::chrono::milliseconds(10));
    return (data1 > 2 && robotAngle > angleConstraint) ? NodeStatus::SUCCESS
                                                        : NodeStatus::FAILURE;
  }

  static PortsList providedPorts() {
    const char *description = "Simply print the target on console...";
    return {InputPort<float>("input", description)};
  }
};
//-------------------------------------------------------------------------------------
//--------------------------MOVE_ROBOT-------------------------------------------------
//-------------------------------------------------------------------------------------
class MoveRobot : public BT::SyncActionNode, public rclcpp::Node {
public:
  MoveRobot(const std::string &name, const BT::NodeConfiguration &config)
      : BT::SyncActionNode(name, config), Node("rotating_node") {
    auto sensor_qos = rclcpp::QoS(rclcpp::SensorDataQoS());
    subscription_ = this->create_subscription<nav_msgs::msg::Odometry>(
        "/odom", sensor_qos, [&](const nav_msgs::msg::Odometry::SharedPtr msg) {
          odometry_callback(msg);
        });
  }

  NodeStatus tick() override {
    auto res = getInput<float>("input");
    if (!res) {
      throw RuntimeError("error reading port [input]:", res.error());
    }
    float x_or_y = res.value();
    publisher_ =
        this->create_publisher<geometry_msgs::msg::Twist>("/cmd_vel", 10);
    auto message = geometry_msgs::msg::Twist();
    RCLCPP_INFO(this->get_logger(), "robot position: '%f' '%f'", position_x,
                position_y);
    if (x_or_y == 1) {
      message.linear.x = 0.5;
    }
    if (x_or_y == 2) {
      message.linear.y = 0.5;
    }
    const geometry_msgs::msg::PoseStamped::SharedPtr msg;
    publisher_->publish(message);
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
    return position_x > 3.0 || position_y > 3.0 ? NodeStatus::SUCCESS
                                                 : NodeStatus::FAILURE;
  }

  static PortsList providedPorts() {
    const char *description = "Simply print the target on console...";
    return {InputPort<float>("input", description)};
  }

private:
  void odometry_callback(const nav_msgs::msg::Odometry::SharedPtr _msg) {
    position_x = _msg->pose.pose.position.x;
    position_y = _msg->pose.pose.position.y;
  }

  void timer_callback() {
    RCLCPP_INFO(this->get_logger(), "yaw: '%f'", robotAngle);
    auto message = geometry_msgs::msg::Twist();
    const geometry_msgs::msg::PoseStamped::SharedPtr msg;
    publisher_->publish(message);
  }

  rclcpp::TimerBase::SharedPtr timer_;
  rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr subscription_;
  rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr publisher_;
};
//-------------------------------------------------------------------------------------
//---------------------ROTATING_ROBOT--------------------------------------------------
//-------------------------------------------------------------------------------------
class Rotating : public BT::SyncActionNode, public rclcpp::Node {
public:
  Rotating(const std::string &name, const BT::NodeConfiguration &config)
      : BT::SyncActionNode(name, config), Node("rotating_node") {
    auto sensor_qos = rclcpp::QoS(rclcpp::SensorDataQoS());
    subscription_ = this->create_subscription<nav_msgs::msg::Odometry>(
        "/odom", sensor_qos, [&](const nav_msgs::msg::Odometry::SharedPtr msg) {
          odometry_callback(msg);
        });
  }

  NodeStatus tick() override {
    auto res = getInput<float>("input");
    if (!res) {
      throw RuntimeError("error reading port [input]:", res.error());
    }
    float angle = res.value();
    publisher_ =
        this->create_publisher<geometry_msgs::msg::Twist>("/cmd_vel", 10);
    RCLCPP_INFO(this->get_logger(), "yaw: '%f'", robotAngle);
    RCLCPP_INFO(this->get_logger(), "ROTATE NODE: LASER ===>: '%f' '%f'", data1,
                data2);
    auto message = geometry_msgs::msg::Twist();
    message.angular.z = 0.4;
    const geometry_msgs::msg::PoseStamped::SharedPtr msg;
    publisher_->publish(message);
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
    return NodeStatus::SUCCESS;
  }

  static PortsList providedPorts() {
    const char *description = "Simply print the target on console...";
    return {InputPort<float>("input", description)};
  }

private:
  void odometry_callback(const nav_msgs::msg::Odometry::SharedPtr _msg) {
    tf2::Quaternion quat_tf;
    geometry_msgs::msg::Quaternion quat_msg = _msg->pose.pose.orientation;
    tf2::fromMsg(quat_msg, quat_tf);
    double roll{}, pitch{}, yaw{};
    tf2::Matrix3x3 m(quat_tf);
    m.getRPY(roll, pitch, yaw);
    float yaw_check = yaw * 180 / M_PI;
    if (yaw_check < 0) {
      yaw_check = 360.0 - std::abs(yaw_check);
    }
    robotAngle = yaw_check;
    RCLCPP_INFO(this->get_logger(), "position: '%f' '%f'",
                _msg->pose.pose.position.x, _msg->pose.pose.position.y);
  }

  void timer_callback() {
    RCLCPP_INFO(this->get_logger(), "yaw: '%f'", robotAngle);
    auto message = geometry_msgs::msg::Twist();
    if (robotAngle < 30.0) {
      message.angular.z = 0.3;
    }
    if (robotAngle > 30.0) {
      message.angular.z = 0.0;
    }
    const geometry_msgs::msg::PoseStamped::SharedPtr msg;
    publisher_->publish(message);
  }

  rclcpp::TimerBase::SharedPtr timer_;
  rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr subscription_;
  rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr publisher_;
};
//------------------------------------------------------------------------------------------------------------
// Simple tree, used to execute once each action.
static const char *xml_text = R"(
 <root >
     <BehaviorTree>
        <Sequence>
            <SetBlackboard   output_key="Interface" value="360" />
            <SetBlackboard   output_key="Constraint1" value="180" />
            <SetBlackboard   output_key="Constraint2" value="270" />
            <SetBlackboard   output_key="Direction1" value="1" />
            <SetBlackboard   output_key="Direction2" value="2" />
            <ReactiveSequence>
                <Rotating     input="{Interface}" />
                <ReadingLaser input="{Constraint1}"/>
            </ReactiveSequence>
            <MoveRobot input="{Direction1}"/>
            <ReactiveSequence>
                <Rotating     input="{Interface}" />
                <ReadingLaser input="{Constraint2}"/>
            </ReactiveSequence>
            <MoveRobot input="{Direction2}"/>
        </Sequence>
     </BehaviorTree>
 </root>
 )";

int main(int argc, char **argv) {
  rclcpp::init(argc, argv);
  auto nh = std::make_shared<rclcpp::Node>("sleep_client");
  BehaviorTreeFactory factory;
  factory.registerNodeType<MoveRobot>("MoveRobot");
  factory.registerNodeType<ReadingLaser>("ReadingLaser");
  factory.registerNodeType<Rotating>("Rotating");
  auto tree = factory.createTreeFromText(xml_text);
  NodeStatus status = NodeStatus::FAILURE;
  BT::NodeConfiguration con = {};
  // start laser
  auto lc_listener = std::make_shared<ReadingLaser>("lc_listener", con);
  auto lc_odom = std::make_shared<Rotating>("lc_odom", con);
  FileLogger logger_file(tree, "bt_trace_project.fbl");
  while (status == BT::NodeStatus::FAILURE) {
    rclcpp::spin_some(lc_odom);
    rclcpp::spin_some(lc_listener);
    status = tree.tickRoot();
    tree.sleep(std::chrono::milliseconds(200));
  }
  return 0;
}
```
How it works: the robot rotates until its yaw passes 180° (`Constraint1`) and the laser sees more than 2 m ahead, then drives forward (`Direction1` = x); then it rotates until 270° (`Constraint2`) and drives with `Direction2`. `Rotating`'s odometry callback maps the yaw to 0–360°.

## Known issues in the solution (read before copying)
- `position_x` and `position_y` are written only by `MoveRobot`'s odometry callback, and no `MoveRobot` node is ever spun (only `lc_listener` and `lc_odom` are): read literally, `MoveRobot` can never return SUCCESS and the loop never ends `[verify]` in the simulation.
- `Direction2` sets `linear.y`, which a differential-drive TurtleBot 3 ignores `[verify]` which robot the project world spawns.
- The `for` loop in `ReadingLaser::tick()` compares `data1` with itself 200 times: it computes nothing.
- All the problems of the course pattern apply (globals, repeated node names, publishers per tick, sleeping ticks): [[bt-ros2-node-pattern]]; a cleaner structure: [[bt-ros2-shared-node]].
- `install(TARGETS … RUNTIME DESTINATION bin)` puts the programs in `bin`, so they are run from the build folder, not with `ros2 run`.
