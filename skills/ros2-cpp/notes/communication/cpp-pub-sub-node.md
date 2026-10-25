---
id: cpp-pub-sub-node
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "One rclcpp node with subscribers and a publisher: autonomous exploration on LaserScan + odometry + cmd_vel"
domain: cpp
area: communication
distro: humble
tested: false
audience: dev
summary: "Subscriptions to /laser_scan and /odom plus a /cmd_vel publisher in one node; shared state, tf2 yaw, 5 m geofence."
tags: [subscriber, publisher, nav_msgs::msg::Odometry, tf2::Quaternion, tf2::Matrix3x3, getRPY, atan2, yaw normalization, shared state, autonomous_exploration.cpp]
see: ["[[cpp-recipe-laserscan]]", "[[cpp-topic-publisher]]", "[[core-recipe-odom-go-to-goal]]", "[[core-recipe-laserscan]]", "[[cpp-learn-unit3-topics]]"]
requires: [ros2-core]
version_notes:
  - "course: yaw_error = std::fmod(yaw_error + M_PI, 2 * M_PI) - M_PI does not normalize negative errors below -pi (fmod keeps the sign); fixed with std::atan2(std::sin(e), std::cos(e)) — https://en.cppreference.com/w/cpp/numeric/math/fmod (CPP-V02)"
  - "lyrical: tf2/LinearMath/Quaternion.h and Matrix3x3.h removed; the .hpp headers exist since Humble — https://github.com/ros2/geometry2/tree/lyrical/tf2/include/tf2/LinearMath (CPP-V22, V44)"
---
# One node with subscribers and a publisher

**TL;DR** A node can hold several subscriptions and publishers. The laser callback decides the motion and publishes it; the odometry callback only updates member variables (position, yaw, a `returning_to_origin_` flag) that the laser callback reads. With the default single-threaded executor the two callbacks never run at the same time, so plain members are safe here.

## `src/autonomous_exploration.cpp` (exercises 3.3 + 3.4)
```cpp
#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/laser_scan.hpp>
#include <geometry_msgs/msg/twist.hpp>
#include <nav_msgs/msg/odometry.hpp>
#include <map>
#include <string>
#include <limits>
#include <cmath>
#include <tf2/LinearMath/Quaternion.hpp>   // the course uses the .h headers (removed in Lyrical)
#include <tf2/LinearMath/Matrix3x3.hpp>

class AutonomousExplorationNode : public rclcpp::Node
{
public:
    AutonomousExplorationNode() : Node("autonomous_exploration_node")
    {
        // Subscriber to LaserScan
        subscriber_laser_ = this->create_subscription<sensor_msgs::msg::LaserScan>(
            "/laser_scan",
            10,
            std::bind(&AutonomousExplorationNode::laserscan_callback, this, std::placeholders::_1));

        // Subscriber to Odometry
        subscriber_odom_ = this->create_subscription<nav_msgs::msg::Odometry>(
            "/odom",
            10,
            std::bind(&AutonomousExplorationNode::odom_callback, this, std::placeholders::_1));

        // Publisher for movement commands
        publisher_ = this->create_publisher<geometry_msgs::msg::Twist>("/cmd_vel", 10);

        // Initialize state variables
        turning_ = false;
        turn_direction_ = -0.5;  // Default to turning right
        distance_from_origin_ = 0.0;
        returning_to_origin_ = false;
        current_position_x_ = 0.0;
        current_position_y_ = 0.0;
        yaw_ = 0.0;

        RCLCPP_INFO(this->get_logger(), "Autonomous Exploration Node Ready...");
    }

private:
    void laserscan_callback(const sensor_msgs::msg::LaserScan::SharedPtr msg){
        // If returning to the origin, skip normal exploration behavior
        if (returning_to_origin_)
        {
            return_to_origin();
            return;
        }

        // Define the sectors
        std::map<std::string, std::pair<int, int>> sectors = {
            {"Right_Rear", {0, 33}},
            {"Right", {34, 66}},
            {"Front_Right", {67, 100}},
            {"Front_Left", {101, 133}},
            {"Left", {134, 166}},
            {"Left_Rear", {167, 199}}
        };

        // Initialize the minimum distances for each sector
        std::map<std::string, float> min_distances;
        for (const auto& sector : sectors)
        {
            min_distances[sector.first] = std::numeric_limits<float>::infinity();
        }

        // Find the minimum distance in each sector
        for (const auto& sector : sectors)
        {
            int start_idx = sector.second.first;
            int end_idx = sector.second.second;

            // Ensure the index range is within bounds and not empty
            if (start_idx < static_cast<int>(msg->ranges.size()) && end_idx < static_cast<int>(msg->ranges.size()))
            {
                float min_val = std::numeric_limits<float>::infinity();
                for (int i = start_idx; i <= end_idx; ++i)
                {
                    if (msg->ranges[i] < min_val)
                    {
                        min_val = msg->ranges[i];
                    }
                }
                min_distances[sector.first] = min_val;
            }
        }

        // Define the threshold for obstacle detection
        float obstacle_threshold = 0.8;  // meters
        // Determine detected obstacles
        std::map<std::string, bool> detections;
        for (const auto& min_dist : min_distances)
        {
            detections[min_dist.first] = min_dist.second < obstacle_threshold;
        }

        // Determine suggested action based on detection
        auto action = geometry_msgs::msg::Twist();

        // If an obstacle is detected in either front sector, continue turning
        if (detections["Front_Left"] || detections["Front_Right"])
        {
            if (!turning_)
            {
                // Start turning if not already turning
                turning_ = true;
                turn_direction_ = -0.5;  // Turning right
            }
            action.angular.z = turn_direction_;  // Continue turning
            RCLCPP_INFO(this->get_logger(), "Obstacle ahead, turning to clear path.");
        }
        else
        {
            turning_ = false;  // Stop turning when the front is clear
            // Priority 2: Side detections
            if (detections["Left"])
            {
                action.linear.x = 0.2;  // Move forward slowly
                action.angular.z = -0.3;  // Slight right turn
                RCLCPP_INFO(this->get_logger(), "Obstacle on the left, turning slightly right.");
            }
            else if (detections["Right"])
            {
                action.linear.x = 0.2;  // Move forward slowly
                action.angular.z = 0.3;  // Slight left turn
                RCLCPP_INFO(this->get_logger(), "Obstacle on the right, turning slightly left.");
            }
            // Priority 3: Rear detections
            else if (detections["Right_Rear"])
            {
                action.linear.x = 0.3;  // Move forward
                RCLCPP_INFO(this->get_logger(), "Obstacle on the right rear, moving forward.");
            }
            else if (detections["Left_Rear"])
            {
                action.linear.x = 0.3;  // Move forward
                RCLCPP_INFO(this->get_logger(), "Obstacle on the left rear, moving forward.");
            }
            else
            {
                action.linear.x = 0.5;  // Move forward
                RCLCPP_INFO(this->get_logger(), "No obstacles, moving forward.");
            }
        }

        // Publish the action command
        publisher_->publish(action);
    }

    void odom_callback(const nav_msgs::msg::Odometry::SharedPtr msg){
        // Extract the x, y coordinates from the odometry message
        current_position_x_ = msg->pose.pose.position.x;
        current_position_y_ = msg->pose.pose.position.y;

        // Calculate the distance from the origin (0,0)
        distance_from_origin_ = std::sqrt(current_position_x_ * current_position_x_ + current_position_y_ * current_position_y_);
        RCLCPP_INFO(this->get_logger(), "Distance from origin: %.2f meters", distance_from_origin_);

        // Calculate the yaw (orientation around the z-axis)
        tf2::Quaternion q(
            msg->pose.pose.orientation.x,
            msg->pose.pose.orientation.y,
            msg->pose.pose.orientation.z,
            msg->pose.pose.orientation.w);
        tf2::Matrix3x3 m(q);
        double roll, pitch;
        m.getRPY(roll, pitch, yaw_);

        // If the distance exceeds PERIMETER_DIST meters, initiate return to origin behavior
        const double PERIMETER_DIST = 5.0;
        if (distance_from_origin_ > PERIMETER_DIST)
        {
            returning_to_origin_ = true;
        }
        else if (returning_to_origin_)
        {
            // If the rover is back within 5 meters of the origin, resume normal operation
            returning_to_origin_ = false;
            RCLCPP_INFO(this->get_logger(), "Within 5 meters of origin, resuming normal operation.");
        }
    }

    void return_to_origin(){
        auto action = geometry_msgs::msg::Twist();

        // Calculate the desired angle to the origin
        double desired_yaw = std::atan2(-current_position_y_, -current_position_x_);

        // Calculate the difference between current yaw and desired yaw
        double yaw_error = desired_yaw - yaw_;

        // Normalize the yaw error to the range [-pi, pi] (fixed, CPP-V02)
        yaw_error = std::atan2(std::sin(yaw_error), std::cos(yaw_error));

        // If the yaw error is significant, rotate towards the origin
        if (std::abs(yaw_error) > 0.1)  // 0.1 radians threshold for orientation
        {
            action.angular.z = yaw_error > 0 ? 0.5 : -0.5;
            RCLCPP_INFO(this->get_logger(), "Turning towards origin. Yaw error: %.2f", yaw_error);
        }
        else
        {
            // If oriented towards the origin, move forward
            action.linear.x = 0.5;
            RCLCPP_INFO(this->get_logger(), "Heading towards origin.");
        }

        // Publish the action command
        publisher_->publish(action);
    }

private:
    rclcpp::Subscription<sensor_msgs::msg::LaserScan>::SharedPtr subscriber_laser_;
    rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr subscriber_odom_;
    rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr publisher_;
    bool turning_;
    double turn_direction_;
    double distance_from_origin_;
    bool returning_to_origin_;
    double current_position_x_;
    double current_position_y_;
    double yaw_;
};

int main(int argc, char **argv){
    rclcpp::init(argc, argv);
    auto node = std::make_shared<AutonomousExplorationNode>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}
```

## How it works
- **Exploration (3.3)**: front obstacle → keep turning right until the front is clear (no left/right oscillation); side obstacle → forward slowly while turning away; only rear obstacles or none → forward. Sector minimums use a plain loop here instead of `std::min_element` ([[cpp-recipe-laserscan]]).
- **Geofence (3.4)**: a circle of radius 5.0 m around the start. Odometry gives position and orientation relative to the start point: `std::sqrt(x² + y²)` is the distance from (0, 0) (Pythagoras); the quaternion becomes roll, pitch, yaw through `tf2::Quaternion` → `tf2::Matrix3x3` → `getRPY()`. `ros2 topic info /odom` and `ros2 interface show nav_msgs/msg/Odometry` show the message.
- **Return**: `std::atan2(-y, -x)` is the heading that points back to the origin; turn in place (`yaw_error > 0 ? 0.5 : -0.5`, the ternary operator = a compact if/else) until the error is under 0.1 rad, then drive at 0.5 m/s. The `return;` in the laser callback gives this mode priority over exploring.
- **Shared state between callbacks** is the new idea: `returning_to_origin_`, `current_position_x_`, `current_position_y_` and `yaw_` are written by `odom_callback()` and read by `laserscan_callback()`.
- Standard library used: `std::map`, `std::string`, `std::pair`, `std::numeric_limits<float>::infinity()`, `std::sqrt()`, `std::atan2()`, `std::abs()` (and `std::fmod()` in the course's normalization).

CMake: `find_package` of `nav_msgs`, `tf2`, `tf2_geometry_msgs`, and `ament_target_dependencies(autonomous_exploration_executable rclcpp sensor_msgs geometry_msgs nav_msgs tf2 tf2_geometry_msgs)` ([[cpp-cmake-library]]).

## Pitfalls
- The course normalizes with `std::fmod(yaw_error + M_PI, 2 * M_PI) - M_PI`: for an error below −π (e.g. −1.5π) the result stays below −π and the rover turns the long way round (CPP-V02). Same math in Python: [[core-recipe-odom-go-to-goal]].
- Shared members are safe only while one thread runs the callbacks; with a MultiThreadedExecutor and parallel groups they need a mutex ([[cpp-exec-callback-groups]]).
- Until the first odometry message arrives, position and yaw are the initial zeros.
