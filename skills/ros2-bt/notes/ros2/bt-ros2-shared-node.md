---
id: bt-ros2-shared-node
type: reference
owner: equipo-ros2
updated: 2026-10-15
review_by: 2027-04-13
source: manual
confidentiality: internal
title: "One ROS 2 node for the whole tree: blackboard, callback group, spin_some in tick (Nav2 pattern)"
domain: bt
area: ros2
distro: humble
tested: false
audience: dev
summary: "BT.CPP v3 with rclcpp the Nav2 way: shared node in the blackboard, callback group, spin_some in tick; BehaviorTree.ROS2 (v4)."
tags: [rclcpp, shared node, blackboard, callback group, SingleThreadedExecutor, spin_some, ConditionNode, Nav2 pattern, BehaviorTree.ROS2, RosTopicSubNode]
see: ["[[bt-ros2-node-pattern]]", "[[bt-concurrency]]", "[[bt-cpp-constructor-args]]", "[[core-exec-callback-groups]]"]
requires: [ros2-core]
version_notes:
  - "humble: Nav2 BT nodes take rclcpp::Node::SharedPtr from the blackboard key \"node\", create a callback group with its own executor and spin_some() in tick() — https://github.com/ros-navigation/navigation2/blob/humble/nav2_behavior_tree/plugins/condition/is_battery_low_condition.cpp (BT-V12)"
  - "v4: BehaviorTree.ROS2 (RosTopicSubNode, RosActionNode, RosServiceNode, RosTopicPubNode, RosNodeParams) needs BT.CPP >= 4.6; source only — https://github.com/BehaviorTree/BehaviorTree.ROS2/blob/humble/README.md (BT-V12)"
---
# One ROS 2 node for the whole tree: blackboard, callback group, spin_some in tick (Nav2 pattern)

**TL;DR** Create **one** `rclcpp::Node` in `main()` and put it in the blackboard (`"node"`) before building the tree. Each BT node takes it in its constructor, creates its publishers and subscriptions **once**, puts its subscriptions in its own callback group with its own `SingleThreadedExecutor`, and calls `spin_some()` at the start of `tick()` to process what arrived since the last tick. No globals, no repeated node names, no sleeping in `tick()`. This is how Nav2 Humble writes its BT nodes on BehaviorTree.CPP v3. [v4: use BehaviorTree.ROS2]

## Where the pattern comes from (Nav2 Humble)
- The BT server stores its node in the blackboard: `blackboard->set<rclcpp::Node::SharedPtr>("node", client_node_);` ([bt_action_server_impl.hpp](https://github.com/ros-navigation/navigation2/blob/humble/nav2_behavior_tree/include/nav2_behavior_tree/bt_action_server_impl.hpp)).
- A condition reads it in its constructor and spins its own group in `tick()` ([is_battery_low_condition.cpp](https://github.com/ros-navigation/navigation2/blob/humble/nav2_behavior_tree/plugins/condition/is_battery_low_condition.cpp)):
```cpp
  node_ = config().blackboard->get<rclcpp::Node::SharedPtr>("node");
  callback_group_ = node_->create_callback_group(
    rclcpp::CallbackGroupType::MutuallyExclusive,
    false);
  callback_group_executor_.add_callback_group(callback_group_, node_->get_node_base_interface());

  rclcpp::SubscriptionOptions sub_option;
  sub_option.callback_group = callback_group_;
  battery_sub_ = node_->create_subscription<sensor_msgs::msg::BatteryState>(
    battery_topic_,
    rclcpp::SystemDefaultsQoS(),
    std::bind(&IsBatteryLowCondition::batteryCallback, this, std::placeholders::_1),
    sub_option);
}

BT::NodeStatus IsBatteryLowCondition::tick()
{
  callback_group_executor_.spin_some();
  if (is_battery_low_) {
    return BT::NodeStatus::SUCCESS;
  }
  return BT::NodeStatus::FAILURE;
}
```
(Excerpt, Apache-2.0, © the Nav2 authors.) `false` in `create_callback_group` keeps the group out of any other executor, so only this node spins it.

## The course's laser check, rewritten this way
Same behavior as the course's `ReadingLaser` and `MoveRobot` ([[bt-ros2-node-pattern]]), written with the pattern above. Built from the APIs above, not compiled here `[verify]`.
```cpp
#include <behaviortree_cpp_v3/bt_factory.h>
#include <rclcpp/rclcpp.hpp>
#include <geometry_msgs/msg/twist.hpp>
#include <sensor_msgs/msg/laser_scan.hpp>

// Condition: is the way in front free? Reads /scan through the shared node.
class ReadingLaser : public BT::ConditionNode
{
public:
  ReadingLaser(const std::string & name, const BT::NodeConfiguration & config)
  : BT::ConditionNode(name, config)
  {
    node_ = config.blackboard->get<rclcpp::Node::SharedPtr>("node");
    callback_group_ = node_->create_callback_group(
      rclcpp::CallbackGroupType::MutuallyExclusive, false);
    callback_group_executor_.add_callback_group(callback_group_, node_->get_node_base_interface());
    rclcpp::SubscriptionOptions options;
    options.callback_group = callback_group_;
    scan_sub_ = node_->create_subscription<sensor_msgs::msg::LaserScan>(
      "/scan", rclcpp::SensorDataQoS(),
      [this](sensor_msgs::msg::LaserScan::SharedPtr msg) {
        if (!msg->ranges.empty()) {front_range_ = msg->ranges[0];}
      },
      options);
  }

  static BT::PortsList providedPorts() {return {};}

  BT::NodeStatus tick() override
  {
    callback_group_executor_.spin_some();   // scans received since the last tick
    return front_range_ > 3.0f ? BT::NodeStatus::SUCCESS : BT::NodeStatus::FAILURE;
  }

private:
  rclcpp::Node::SharedPtr node_;
  rclcpp::CallbackGroup::SharedPtr callback_group_;
  rclcpp::executors::SingleThreadedExecutor callback_group_executor_;
  rclcpp::Subscription<sensor_msgs::msg::LaserScan>::SharedPtr scan_sub_;
  float front_range_{0.0f};
};

// Action: publish one velocity command; the publisher is created once.
class MoveRobot : public BT::SyncActionNode
{
public:
  MoveRobot(const std::string & name, const BT::NodeConfiguration & config)
  : BT::SyncActionNode(name, config)
  {
    auto node = config.blackboard->get<rclcpp::Node::SharedPtr>("node");
    cmd_pub_ = node->create_publisher<geometry_msgs::msg::Twist>("/cmd_vel", 10);
  }

  static BT::PortsList providedPorts() {return {};}

  BT::NodeStatus tick() override
  {
    geometry_msgs::msg::Twist cmd;
    cmd.linear.x = 0.1;
    cmd_pub_->publish(cmd);
    return BT::NodeStatus::SUCCESS;
  }

private:
  rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr cmd_pub_;
};

static const char * xml_text = R"(
<root main_tree_to_execute="MainTree">
  <BehaviorTree ID="MainTree">
    <Sequence>
      <ReadingLaser/>
      <MoveRobot/>
    </Sequence>
  </BehaviorTree>
</root>
)";

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  auto node = std::make_shared<rclcpp::Node>("bt_executor");   // the only ROS 2 node

  BT::BehaviorTreeFactory factory;
  factory.registerNodeType<ReadingLaser>("ReadingLaser");
  factory.registerNodeType<MoveRobot>("MoveRobot");

  auto blackboard = BT::Blackboard::create();
  blackboard->set<rclcpp::Node::SharedPtr>("node", node);       // before the tree is created
  auto tree = factory.createTreeFromText(xml_text, blackboard);

  BT::NodeStatus status = BT::NodeStatus::FAILURE;
  while (rclcpp::ok() && status != BT::NodeStatus::SUCCESS) {
    status = tree.tickRoot();
    tree.sleep(std::chrono::milliseconds(200));
  }
  rclcpp::shutdown();
  return 0;
}
```
Long ROS 2 actions (navigation, manipulation) follow the same idea with an action client in a `StatefulActionNode`: send the goal in `onStart()`, `spin_some()` and check the result in `onRunning()`, cancel in `onHalted()` ([[bt-cpp-async-action]]); Nav2's `BtActionNode` (`bt_action_node.hpp`, Humble) is a complete example.

## BehaviorTree.CPP v4: BehaviorTree.ROS2
For BT.CPP 4.6 or newer (Humble or newer) the official [BehaviorTree.ROS2](https://github.com/BehaviorTree/BehaviorTree.ROS2) provides ready wrappers: `RosActionNode`, `RosServiceNode`, `RosTopicSubNode` (a condition whose `onTick(last_msg)` receives the latest message) and `RosTopicPubNode`, configured with `RosNodeParams` (the node as `nh`, a default port value, `server_timeout` 1000 ms, `wait_for_server_timeout` 500 ms). It is not released as a binary: build it from source.

## Pitfalls
- Set `"node"` in the blackboard **before** `createTreeFromText`: the constructors read it.
- Do not also add the node to another executor that spins the same callback groups; each group belongs to one executor.
- Nav2 Humble links BT.CPP v3: custom BT nodes for Nav2 Humble must use `behaviortree_cpp_v3`, not BehaviorTree.ROS2.
