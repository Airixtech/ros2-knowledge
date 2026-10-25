---
id: cpp-topic-publisher
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "rclcpp publisher: create_publisher<Twist>, timer-driven publish, stop the robot in a pre-shutdown callback"
domain: cpp
area: communication
distro: humble
tested: false
audience: dev
summary: "create_publisher<geometry_msgs::msg::Twist>(\"/cmd_vel\", 10) published from a 500 ms timer; zero Twist on Ctrl+C via context->add_pre_shutdown_callback."
tags: [create_publisher, rclcpp::Publisher, Twist, cmd_vel, create_wall_timer, publish, add_pre_shutdown_callback, context, stop robot, publish_mars_rover_move.cpp]
see: ["[[core-topic-cpp]]", "[[cpp-topic-subscriber]]", "[[core-recipe-stop-and-wait]]", "[[core-topic-cli]]", "[[cpp-node-class]]"]
requires: [ros2-core]
version_notes:
  - "all: rclcpp::Context::add_pre_shutdown_callback exists in Humble, Jazzy, Kilted and Lyrical; that the zero Twist reaches the robot before the process exits is [verify] — https://github.com/ros2/rclcpp/blob/humble/rclcpp/include/rclcpp/context.hpp (CPP-V28)"
---
# rclcpp publisher

**TL;DR** `create_publisher<MsgT>(topic, depth)` in the constructor, a timer that builds a fresh message and calls `publisher_->publish(msg)`, both stored as members. To stop a robot on Ctrl+C, register a pre-shutdown callback on the node's context that publishes a zero Twist.

## `src/publish_mars_rover_move.cpp`
```cpp
#include <rclcpp/rclcpp.hpp>  // import the ROS2 C++ libraries
#include <geometry_msgs/msg/twist.hpp>  // import the Twist interface from the geometry_msgs package

class MoveRoverNode : public rclcpp::Node
{
public:
    MoveRoverNode() : Node("move_rover_node")
    {
        // Here you have the class constructor
        // call Node constructor to initialize the Node object
        // the parameter you pass is the node name
        // create the publisher object
        // in this case, the publisher will publish on /cmd_vel Topic with a queue size of 10 messages.
        // use the Twist message for /cmd_vel Topic
        publisher_ = this->create_publisher<geometry_msgs::msg::Twist>("/cmd_vel", 10);
        // define the timer period for 0.5 seconds
        auto timer_period = std::chrono::milliseconds(500);
        // create a timer sending two parameters:
        // - the duration between 2 callbacks (0.5 seconds)
        // - the timer function (timer_callback)
        timer_ = this->create_wall_timer(timer_period, std::bind(&MoveRoverNode::timer_callback, this));
    }

private:
    void timer_callback(){
        // Here you have the callback method
        // create a Twist message
        auto msg = geometry_msgs::msg::Twist();
        // define the linear x-axis velocity of /cmd_vel Topic parameter to 0.5
        msg.linear.x = 0.5;
        // define the angular z-axis velocity of /cmd_vel Topic parameter to 0.5
        msg.angular.z = 0.5;
        // Publish the message to the Topic
        publisher_->publish(msg);
        // Display the message on the console
        RCLCPP_INFO(this->get_logger(), "Publishing: linear.x=%.2f, angular.z=%.2f", msg.linear.x, msg.angular.z);
    }

    // Publisher and timer objects
    rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr publisher_;
    rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char **argv){
    // initialize the ROS communication
    rclcpp::init(argc, argv);
    // declare the node constructor
    auto simple_publisher = std::make_shared<MoveRoverNode>();
    // pause the program execution, waits for a request to kill the node (ctrl+c)
    rclcpp::spin(simple_publisher);
    // shutdown the ROS communication
    rclcpp::shutdown();
    return 0;
}
```
- `create_publisher<>()`: message type (`geometry_msgs::msg::Twist`, so the publisher only accepts that type), topic (`/cmd_vel`) and queue depth `10` (keeps up to 10 messages; when full, older ones are replaced, and a slow subscriber may still miss some).
- 0.5 m/s forward + 0.5 rad/s turn → a circle. The fields of `Twist`: `ros2 interface show geometry_msgs/msg/Twist` (two `Vector3`, `linear` and `angular`).
- The timer republishes every 0.5 s: many robots stop by themselves when commands stop arriving (command timeout), so motion commands are sent periodically.
- `std::bind(&MoveRoverNode::timer_callback, this)` needs no placeholder: a timer callback gets no argument.
- `auto msg = geometry_msgs::msg::Twist();` is a local: each tick builds a fresh command. Members hold what must survive between callbacks (publisher, timer), locals hold data for one callback.

CMake: `add_executable(publish_mars_rover_move_executable src/publish_mars_rover_move.cpp)` + `ament_target_dependencies(publish_mars_rover_move_executable rclcpp geometry_msgs)` and add it to `install(TARGETS …)` ([[cpp-cmake-library]] shows the whole `mars_rover_tasks` file).

## Run and check
```bash
ros2 run mars_rover_tasks publish_mars_rover_move_executable
#   [INFO] [1724856856.488345492] [move_rover_node]: Publishing: linear.x=0.50, angular.z=0.50
ros2 topic echo /cmd_vel           # linear.x 0.5 / angular.z 0.5, every 0.5 s
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"
```
Ctrl+C stops the program, but the robot keeps the last command: the `--once` zero Twist stops it ([[core-topic-cli]]).

## Stop the rover on Ctrl+C
```cpp
#include <geometry_msgs/msg/twist.hpp>
#include <rclcpp/rclcpp.hpp>

class MoveRoverNode : public rclcpp::Node
{
public:
  MoveRoverNode() : Node("move_rover_node")
  {
    publisher_ =
        this->create_publisher<geometry_msgs::msg::Twist>("/cmd_vel", 10);

    auto timer_period = std::chrono::milliseconds(500);

    timer_ = this->create_wall_timer(
        timer_period,
        std::bind(&MoveRoverNode::timer_callback, this));
  }

  void stop_rover(){
    auto stop_msg = geometry_msgs::msg::Twist();

    // All Twist fields are zero by default
    publisher_->publish(stop_msg);

    RCLCPP_INFO(
        this->get_logger(),
        "Publishing stop message before shutdown");
  }

private:
  void timer_callback(){
    auto msg = geometry_msgs::msg::Twist();

    msg.linear.x = 0.5;
    msg.angular.z = 0.5;

    publisher_->publish(msg);

    RCLCPP_INFO(
        this->get_logger(),
        "Publishing: linear.x=%.2f, angular.z=%.2f",
        msg.linear.x,
        msg.angular.z);
  }

  rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr publisher_;
  rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char **argv){
  rclcpp::init(argc, argv);

  auto node = std::make_shared<MoveRoverNode>();

  auto context = node->get_node_options().context();

  context->add_pre_shutdown_callback(
      [node]() {
        node->stop_rover();
      });

  rclcpp::spin(node);

  return 0;
}
```
- `stop_rover()` is public because `main()` calls it; a default-constructed `Twist` is all zeros.
- `node->get_node_options().context()` is the context that manages the application's init and shutdown; a pre-shutdown callback runs just before that context shuts down.
- rclcpp already handles Ctrl+C (SIGINT): its signal handler starts the shutdown, which runs the callback; no own signal handler is needed. The Python way: [[core-recipe-stop-and-wait]].

## Pitfalls
- Publisher or timer as a local variable → destroyed when the constructor ends, nothing is published.
- The zero Twist is the last message before exit: that it is delivered before the process ends is `[verify]` (CPP-V28); a robot with a command timeout stops anyway.
