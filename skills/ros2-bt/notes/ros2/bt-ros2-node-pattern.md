---
id: bt-ros2-node-pattern
type: reference
owner: equipo-ros2
updated: 2026-10-15
review_by: 2027-04-13
source: manual
confidentiality: internal
title: "BT action nodes that are ROS 2 nodes: course pattern, main loop, pitfalls"
domain: bt
area: ros2
distro: humble
tested: false
audience: dev
summary: "Course test_unit2.cpp: BT nodes that also inherit rclcpp::Node, globals, spin_some + tickRoot loop; why it is fragile."
tags: [rclcpp::Node, SyncActionNode, spin_some, tickRoot loop, global variables, LaserScan, Odometry, cmd_vel, test_unit2, pitfalls]
see: ["[[bt-ros2-shared-node]]", "[[bt-concurrency]]", "[[bt-app-architecture]]", "[[bt-learn-unit2]]"]
requires: [ros2-core]
version_notes:
  - "all: course pattern works but tree nodes are never spun, data goes through globals, node names repeat, publishers are created per tick, tick() sleeps — https://github.com/ros-navigation/navigation2/blob/humble/nav2_behavior_tree/plugins/condition/is_battery_low_condition.cpp (BT-V12)"
  - "humble: tf2_geometry_msgs.h warns 'header is obsolete': include tf2_geometry_msgs.hpp — https://github.com/ros2/geometry2/blob/humble/tf2_geometry_msgs/include/tf2_geometry_msgs/tf2_geometry_msgs.h (BT-V32)"
  - "all: behaviortree_ros2/bt_action_node.hpp is the course's own package; the official BehaviorTree.ROS2 needs BT.CPP >= 4.6 [verify] — https://github.com/BehaviorTree/BehaviorTree.ROS2/blob/humble/README.md (BT-V34)"
---
# BT action nodes that are ROS 2 nodes: course pattern, main loop, pitfalls

**TL;DR** In the course every BT node class inherits both `BT::SyncActionNode` and `rclcpp::Node`. Subscriber callbacks write global variables; `main()` creates two extra instances of the subscriber classes, spins them with `rclcpp::spin_some()` and ticks the tree every 200 ms until it succeeds. It runs, but the tree's own nodes are never spun, node names repeat and `tick()` sleeps. Use it to understand the course; for new code use one shared node ([[bt-ros2-shared-node]]).

## test_unit2.cpp (course solution applied)
```cpp
//we need to include header both for BT and ROS2
//there are also includes to the standard C++ libraries
//----------------------------------------------------------------------------------
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

using namespace std::chrono_literals;
using std::chrono::milliseconds;
using std::placeholders::_1;
std::atomic_bool switchActive{true};

using namespace BT;
//------------------------------------------------------------------------------------
//IMPORTANT!!
//Auxiliary variables that hold the data from the subscriber
//and later can be delivered to the BT node
//BESIDE subscriber and BT node are defined in the same class!!!

float data1;
float data2;
float robotAngle;
//-------------------------------------------------------------------------------------
// we have 5 robot actions - 5 ROS2 nodes: Laser, Print, Move robot, Stop Robot and Rotate Robot
// the "architecture" of all included ROS nodes is the same
//-------------------------------------------------------------------------------------
//------------------------------LASER--------------------------------------------------
//-------------------------------------------------------------------------------------
// standard ROS2 node with BT: public BT::SyncActionNode
class ReadingLaser : public BT::SyncActionNode, public rclcpp::Node {
private:
  rclcpp::Subscription<sensor_msgs::msg::LaserScan>::SharedPtr subscription_;
  void topic_callback(const sensor_msgs::msg::LaserScan::SharedPtr _msg) {
    data2 = _msg->ranges[100];
    data1 = _msg->ranges[0];
  }

public:
  //Node constructor
  //See how we define the subscriber. We use lambda function which "provide mechanism"
  // to collect data and later reuse data in BT node.
  ReadingLaser(const std::string &name, const BT::NodeConfiguration &config)
      : BT::SyncActionNode(name, config), Node("scanner_node") {
    auto sensor_qos = rclcpp::QoS(rclcpp::SensorDataQoS());
    subscription_ = this->create_subscription<sensor_msgs::msg::LaserScan>(
        "/scan", sensor_qos,
        [&](const sensor_msgs::msg::LaserScan::SharedPtr msg) {
          topic_callback(msg);
        });
  }

  // As previously.
  // You must override the virtual function tick()
  BT::NodeStatus tick() override {
    RCLCPP_INFO(this->get_logger(), "This is a tick()-------");
    RCLCPP_INFO(this->get_logger(), "NODE : LASER DATA ===>: '%f' '%f'", data1,
                data2);
    std::this_thread::sleep_for(std::chrono::seconds(1));
    return data1 > 3 ? NodeStatus::SUCCESS : NodeStatus::FAILURE;
  }

  // Each Node can include port IN/OUT for "communication" between BT node
  // and BlackBoard. Dateil will be proivided later
  //Here all is empty
  static BT::PortsList providedPorts() { return {}; }
};
//-------------------------------------------------------------------------------------
//------------------------------PRINT--------------------------------------------------
//-------------------------------------------------------------------------------------
class PrintValue : public BT::SyncActionNode, public rclcpp::Node {
private:
  rclcpp::TimerBase::SharedPtr timer_;
  rclcpp::Publisher<std_msgs::msg::String>::SharedPtr publisher_;
  size_t count_;

public:
  PrintValue(const std::string &name, const BT::NodeConfiguration &config)
      : BT::SyncActionNode(name, config), Node("minimum_publisher") {}

  void timer_callback() {
    auto message = std_msgs::msg::String();
    message.data = "Hello, world! 11111" + std::to_string(count_++);
    RCLCPP_INFO(this->get_logger(), "Publishing:111111 '%s'",
                message.data.c_str());
    publisher_->publish(message);
  }

  BT::NodeStatus tick() override {
    std::string msg;
    if (getInput("message", msg)) {
      std::cout << "PrintValue: " << msg << std::endl;
      //------------------------------------------------------------
      publisher_ = this->create_publisher<std_msgs::msg::String>("topicX", 10);
      auto message = std_msgs::msg::String();
      message.data = "Hello, world 222222! " + std::to_string(count_++);
      RCLCPP_INFO(this->get_logger(), "Publishing: 22222'%s'",
                  message.data.c_str());
      publisher_->publish(message);
      return NodeStatus::SUCCESS;
    } else {
      return NodeStatus::SUCCESS;
    }
  }

  static BT::PortsList providedPorts() {
    return {BT::InputPort<std::string>("message")};
  }
};
//-------------------------------------------------------------------------------------
//--------------------------MOVE_ROBOT-------------------------------------------------
//-------------------------------------------------------------------------------------
class MoveRobot : public BT::SyncActionNode, public rclcpp::Node {
private:
  rclcpp::TimerBase::SharedPtr timer_;
  rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr publisher_;
  size_t count_;

public:
  MoveRobot(const std::string &name, const BT::NodeConfiguration &config)
      : BT::SyncActionNode(name, config), Node("moving_robot") {}

  BT::NodeStatus tick() override {
    RCLCPP_INFO(this->get_logger(), "MOVING ROBOT");
    RCLCPP_INFO(this->get_logger(), "MOVE AND LASER ===>: '%f' '%f'", data1,
                data2);
    publisher_ =
        this->create_publisher<geometry_msgs::msg::Twist>("/cmd_vel", 10);
    auto message = geometry_msgs::msg::Twist();
    message.linear.x = 0.1;
    publisher_->publish(message);
    return NodeStatus::SUCCESS;
  }

  static BT::PortsList providedPorts() { return {}; }
};
//-------------------------------------------------------------------------------------
//--------------------------STOP_ROBOT-------------------------------------------------
//-------------------------------------------------------------------------------------
class StopRobot : public BT::SyncActionNode, public rclcpp::Node {
private:
  rclcpp::TimerBase::SharedPtr timer_;
  rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr publisher_;
  size_t count_;

public:
  StopRobot(const std::string &name, const BT::NodeConfiguration &config)
      : BT::SyncActionNode(name, config), Node("stop_robot") {}

  BT::NodeStatus tick() override {
    RCLCPP_INFO(this->get_logger(), "STOPPING");
    publisher_ =
        this->create_publisher<geometry_msgs::msg::Twist>("/cmd_vel", 10);
    auto message = geometry_msgs::msg::Twist();
    message.linear.x = 0.0;
    message.angular.z = 0.0;
    const geometry_msgs::msg::PoseStamped::SharedPtr msg;
    publisher_->publish(message);
    std::this_thread::sleep_for(std::chrono::seconds(1));
    return NodeStatus::SUCCESS;
  }

  static BT::PortsList providedPorts() { return {}; }
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
    printf("Angle positions: [ %.1f]\n", angle);
    publisher_ =
        this->create_publisher<geometry_msgs::msg::Twist>("/cmd_vel", 10);
    RCLCPP_INFO(this->get_logger(), "yaw: '%f'", robotAngle);
    RCLCPP_INFO(this->get_logger(), "ROTATE NODE: LASER ===>: '%f' '%f'", data1,
                data2);
    auto message = geometry_msgs::msg::Twist();
    if (robotAngle < angle) {
      message.angular.z = 0.3;
    }
    if (robotAngle > angle) {
      message.angular.z = 0.0;
    }
    const geometry_msgs::msg::PoseStamped::SharedPtr msg;
    publisher_->publish(message);
    std::this_thread::sleep_for(std::chrono::milliseconds(1250));
    return robotAngle > angle ? NodeStatus::SUCCESS : NodeStatus::FAILURE;
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
    robotAngle = yaw * 180 / M_PI;
    RCLCPP_INFO(this->get_logger(), "position: '%f' '%f'",
                _msg->pose.pose.position.x, _msg->pose.pose.position.y);
  }

  void timer_callback() {
    RCLCPP_INFO(this->get_logger(), "yaw: '%f'", robotAngle);
    auto message = geometry_msgs::msg::Twist();
    // message.linear.x = 0.0;
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
//------------------------------------------------------------------------------------------------------------
// //definition of BT which reflects logical connection between robot actions
// Simple tree, used to execute once each action.
static const char *xml_text = R"(
 <root >
     <BehaviorTree>
        <Sequence>
            <SetBlackboard   output_key="Interface" value="45" />
            <Rotating     input="{Interface}" />
            <Fallback>
                <ReadingLaser name="scanner"/>
                <Sequence>
                    <SetBlackboard   output_key="Interface" value="90" />
                    <Rotating     input="{Interface}" />
                    <Fallback>
                        <ReadingLaser name="scanner"/>
                        <Sequence>
                            <SetBlackboard   output_key="Interface" value="135" />
                            <Rotating     input="{Interface}" />
                            <ReadingLaser name="scanner"/>
                        </Sequence>
                    </Fallback>
                </Sequence>
            </Fallback>
            <MoveRobot name="move_robot"/>
        </Sequence>
     </BehaviorTree>
 </root>
 )";
//------------------------------------------------------------------------------------------------------------
//------------------------------------------------------------------------------------------------------------

int main(int argc, char **argv) {
  rclcpp::init(argc, argv);
  auto nh = std::make_shared<rclcpp::Node>("sleep_client");

  // We use the BehaviorTreeFactory to register our custom nodes
  BehaviorTreeFactory factory;

  //Node registration process
  factory.registerNodeType<PrintValue>("PrintValue");
  factory.registerNodeType<MoveRobot>("MoveRobot");
  factory.registerNodeType<StopRobot>("StopRobot");
  factory.registerNodeType<ReadingLaser>("ReadingLaser");
  factory.registerNodeType<Rotating>("Rotating");

  // we incorporated the BT (XML format)
  auto tree = factory.createTreeFromText(xml_text);

  NodeStatus status = NodeStatus::FAILURE;
  BT::NodeConfiguration con = {};

  // start laser
  //definiion of smart pointers
  auto lc_listener = std::make_shared<ReadingLaser>("lc_listener", con);
  auto lc_odom = std::make_shared<Rotating>("lc_odom", con);

  // for logging purposes. Details later
  FileLogger logger_file(tree, "bt_trace_unit1.fbl");

  while (status == BT::NodeStatus::FAILURE) {
    rclcpp::spin_some(lc_odom);
    rclcpp::spin_some(lc_listener);
    //we check the status of node
    status = tree.tickRoot();
    tree.sleep(std::chrono::milliseconds(200));
  }

  return 0;
}
```
In the course file the line `<MoveRobot name="move_robot"/>` is the exercise: it ships as a placeholder tag and the student adds it ([[bt-learn-unit2]]).

## How the data reaches the tree
```text
lc_listener (ReadingLaser, spun) ── /scan callback ──▶ globals data1, data2 ──▶ read by every ReadingLaser / Rotating tick
lc_odom     (Rotating, spun)     ── /odom callback ──▶ global robotAngle   ──▶ read by every Rotating tick
tree's ReadingLaser ×3, Rotating ×3 (never spun): their own subscriptions never deliver anything
```

## Pitfalls
- **Dead subscriptions**: the nodes created by the factory are never spun; only `lc_listener` and `lc_odom` are, which is why the data must travel through globals.
- **Repeated node names**: every `ReadingLaser` is a ROS 2 node called `scanner_node` (4 in this program) and every `Rotating` is `rotating_node`; `ros2 node list` warns about duplicate names and their parameter services share names. The XML `name="scanner"` is only the BT instance name.
- **A publisher per tick**: `MoveRobot`, `StopRobot`, `Rotating` and `PrintValue` call `create_publisher` inside `tick()`. A freshly created publisher can lose its first messages while discovery matches it with the subscribers; create it once in the constructor.
- **Sleeping ticks**: `sleep_for(1 s)` in `ReadingLaser`, 1.25 s in `Rotating`, 1 s in `StopRobot` block the whole single-threaded tree ([[bt-concurrency]]).
- **Loop condition**: `while (status == FAILURE)` also exits on RUNNING; it only works because every node here is synchronous. The node `nh` ("sleep_client") is never used.
- `#include <tf2_geometry_msgs/tf2_geometry_msgs.h>` compiles in Humble with "This header is obsolete": use `tf2_geometry_msgs.hpp`.
- `behaviortree_ros2/bt_action_node.hpp` comes from the course's own `behaviortree_ros2` package and nothing in this file uses it; the official BehaviorTree.ROS2 needs BT.CPP ≥ 4.6 ([[bt-ros2-shared-node]]).
