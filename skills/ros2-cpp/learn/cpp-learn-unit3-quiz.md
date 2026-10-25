---
id: cpp-learn-unit3-quiz
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "C++ topics quiz: autonomous navigation challenge, specifications, hints, grading"
domain: cpp
area: learn
distro: humble
tested: false
audience: students
summary: "Topics quiz in C++: pkg topics_quiz, node topics_quiz_node, /nasa_mission Go-Home/Go-Pickup, 0.1 m tolerance, hints, grading."
tags: [course, quiz, topics_quiz, topics_quiz_node, topics_quiz.launch.py, nasa_mission, Go-Home, Go-Pickup, mars_rover_status, spin_some, students]
see: ["[[cpp-learn-unit3-topics]]", "[[cpp-pub-sub-node]]", "[[cpp-recipe-laserscan]]", "[[core-recipe-command-goals]]", "[[cpp-exec-spin-some]]"]
requires: [ros2-core]
version_notes:
  - "course: hint 4 calls rclcpp::spin_some(node) once right after creating the node to read the initial odometry; at that moment usually no message has arrived yet — spin until the odometry callback sets a flag, with a timeout [verify] (CPP-V31)"
---
# C++ topics quiz: autonomous navigation challenge

**TL;DR** Exact names are graded and a failed step stops the grading. Build a node that waits for `Go-Home` / `Go-Pickup` on `/nasa_mission`, drives to the waypoint within 0.1 m while avoiding obstacles, stops, and waits again. Pattern: [[core-recipe-command-goals]]; laser and odometry code: [[cpp-pub-sub-node]].

## Specifications
- C++ package `topics_quiz`, dependencies `rclcpp sensor_msgs geometry_msgs nav_msgs std_msgs`.
- Source `src/topics_quiz.cpp`, node name `topics_quiz_node`, launch file `launch/topics_quiz.launch.py`.
- Subscribe to `/nasa_mission` (`std_msgs/msg/String`): `Go-Home` → `{'x': 0.0, 'y': 0.0}` (home base, also the start); `Go-Pickup` → `{'x': -2.342, 'y': -2.432}` (sample site near the grey box).
- Tolerance about `0.1 meters` (x: −2.442 still counts). Arrive within 90 s, avoiding the terrain obstacles; publish motion on `/cmd_vel`.
- Logic: (1) wait indefinitely for a command; (2) navigate while avoiding obstacles; (3) under 0.1 m error stop and wait; (4) the same command while already at the target does not move the rover; (5) optional: status as `std_msgs/msg/String` on `/mars_rover_status`.
```bash
ros2 topic pub /nasa_mission std_msgs/msg/String "data: 'Go-Home'" --once
ros2 topic pub /nasa_mission std_msgs/msg/String "data: 'Go-Pickup'" --once
```
```
topics_quiz/
├── CMakeLists.txt
├── package.xml
├── src/
│   └── topics_quiz.cpp
└── launch/
    └── topics_quiz.launch.py
```
The ResetSim button of the simulation puts the rover back at the start for testing.

## Hints of the course
```cpp
void odom_callback(const nav_msgs::msg::Odometry::SharedPtr msg){
    // Update the current position and yaw from odometry
    current_position_.x = msg->pose.pose.position.x;
    current_position_.y = msg->pose.pose.position.y;

    // Extract yaw from quaternion
    tf2::Quaternion q(
        msg->pose.pose.orientation.x,
        msg->pose.pose.orientation.y,
        msg->pose.pose.orientation.z,
        msg->pose.pose.orientation.w);
    tf2::Matrix3x3 m(q);
    double roll, pitch;
    m.getRPY(roll, pitch, current_yaw_);

    // Check if the goal has been reached
    if (has_active_goal_) {
        double distance_to_goal = calculate_distance(current_position_, target_position_);
        if (distance_to_goal < goal_tolerance_) {
            stop_rover();
            mission_active_ = false;
            has_active_goal_ = false;
            RCLCPP_INFO(this->get_logger(), "Goal reached. Mars rover stopped.");
            publish_status("goal-reached");
        }
    }
}

bool is_at_position(const Position& target_position){
    double distance_to_target = calculate_distance(current_position_, target_position);
    return distance_to_target < goal_tolerance_;
}

bool has_front_obstacles(const sensor_msgs::msg::LaserScan::SharedPtr laser_msg){
    // Define front sectors for Mars rover's laser scanner (adjust indices based on your laser setup)
    int front_left_start = 101;
    int front_left_end = 133;
    int front_right_start = 67;
    int front_right_end = 100;

    double obstacle_threshold = 0.8; // meters - Martian terrain clearance
    // Check front sectors for obstacles
    // Return true if obstacles detected within threshold distance
}

void mission_callback(const std_msgs::msg::String::SharedPtr msg){
    std::string command = msg->data;

    if (command == "Go-Home") {
        if (!is_at_position(home_position_)) {
            RCLCPP_INFO(this->get_logger(), "NASA Command: Go-Home. Returning to base...");
            target_position_ = home_position_;
            mission_active_ = true;
            has_active_goal_ = true;
        }
    }
    else if (command == "Go-Pickup") {
        if (!is_at_position(pickup_position_)) {
            RCLCPP_INFO(this->get_logger(), "NASA Command: Go-Pickup. Moving to sample site...");
            target_position_ = pickup_position_;
            mission_active_ = true;
            has_active_goal_ = true;
        }
    }
}
```
Hint 4 (initial position) as given:
```cpp
int main(int argc, char * argv[]){
    rclcpp::init(argc, argv);
    auto node = std::make_shared<MarsRoverNavigationNode>();

    // Process initial odometry to detect rover's starting position
    rclcpp::spin_some(node);

    // Check if rover needs to move to a known waypoint initially
    if (!node->is_at_position(node->get_home_position()) &&
        !node->is_at_position(node->get_pickup_position())) {
        RCLCPP_INFO(node->get_logger(), "Initial position unknown. Moving to home base.");
        // Set home as initial target if not at a known location
    }

    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}
```
One `spin_some()` right after creating the node usually runs before the first odometry message has arrived (CPP-V31 `[verify]`): loop `spin_some()` with a short sleep until the odom callback has set a flag, with a time limit ([[cpp-exec-spin-some]]).

## Grading guide (in order; a failed step skips the rest)
1. Package `topics_quiz` exists. 2. It compiles with all dependencies. 3. It starts with the launch file. 4. The `/nasa_mission` subscriber exists. 5. Motion commands go to `/cmd_vel`. 6. The rover reaches the commanded waypoints. 7. It avoids the obstacles. 8. It reaches them within tolerance and time.

Topics to review: package creation with `ament_cmake`, custom node classes, CMakeLists for executables and dependencies, launch files for C++ nodes, `rclcpp::Publisher`, `rclcpp::Subscription`, shared-pointer message handling, coordinate geometry and quaternions, laser scan processing.
