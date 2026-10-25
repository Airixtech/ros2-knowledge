---
id: cpp-learn-unit3-topics
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "C++ unit 3: Mars rover topics, obstacle detector, rover moves, plant detector, exploration, RoverEvents"
domain: cpp
area: learn
distro: humble
tested: false
audience: students
summary: "Course unit 3 in C++ (pkg mars_rover_tasks): topic CLI on the rover, obstacle detector, publisher, plant detector, autonomous exploration, RoverEvents."
tags: [course, unit 3, mars_rover_tasks, laser_scan, cmd_vel, leo/camera/image_raw, plant_detector, mars_rover_events, autonomous_exploration_executable, students]
see: ["[[cpp-learn-start-here]]", "[[cpp-topic-subscriber]]", "[[cpp-topic-publisher]]", "[[cpp-pub-sub-node]]", "[[cpp-learn-unit3-quiz]]", "[[core-learn-unit3-topics]]"]
requires: [ros2-core]
version_notes:
  - "course: the text says the command sets linear.x = 1.0, but the command it gives publishes linear.x = 0.1 (CPP-V48)"
  - "course: the ros2 topic list output is headed by the prompt of ros2 node list (CPP-V18)"
  - "course: the link on .msg fields and constants points to the Foxy docs (EOL); Humble page — https://docs.ros.org/en/humble/Concepts/Basic/About-Interfaces.html (CPP-V15)"
---
# C++ unit 3: topics on the Mars rover

**TL;DR** Unit 3 in C++ (the Python twin: [[core-learn-unit3-topics]]). Topic CLI first, then a subscriber, a publisher, a node with both, and a custom message. Exact names below are graded.

## Topics of the simulation
`ros2 topic list` → `/clock`, `/cmd_vel`, `/joint_states`, `/laser_scan`, `/leo/camera/image_raw`, `/odom`, `/parameter_events`, `/robot_description`, `/rosout`, `/tf`, `/tf_static` (the course's output is headed by the prompt of `ros2 node list`, CPP-V18). `ros2 topic info`: `/cmd_vel` is `geometry_msgs/msg/Twist` with 0 publishers and 1 subscription (the wheel controllers), `/laser_scan` is `sensor_msgs/msg/LaserScan` and `/leo/camera/image_raw` is `sensor_msgs/msg/Image`, each with 1 publisher and 0 subscriptions. Source `/opt/ros/humble/setup.bash` for the CLI, or `~/ros2_ws/install/setup.bash` when you need your own packages. CLI reference: [[core-topic-cli]]; message fields: [[core-iface-std-types]].
- **Example 3.2** (laser): `ros2 interface show sensor_msgs/msg/LaserScan`, `ros2 topic echo /laser_scan` (`--once`, `--field ranges`), turn with teleop (`j`) and watch `inf` become distances. The scan has ~200 samples, index 100 ≈ straight ahead ([[core-recipe-laserscan]]).
- **Camera**: `ros2 interface show sensor_msgs/msg/Image`, `ros2 topic echo /leo/camera/image_raw --field data` (huge: Ctrl+C at once), `ros2 run rqt_image_view rqt_image_view /leo/camera/image_raw` to see it.
- **Example 3.3** (`/cmd_vel`): echo shows nothing until someone publishes. `ros2 interface list` (Messages, Services, Actions; `.msg` files have fields and constants, explained in the Humble page "About interfaces": the course links the Foxy one, CPP-V15), `ros2 interface show` and `ros2 interface proto geometry_msgs/msg/Twist`, then `ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.1, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 1.0}}"` (forward while turning; the text says `linear.x = 1.0`, the command sends 0.1, CPP-V48). `ros2 topic info /cmd_vel --verbose` lists the publisher (`_ros2cli_<pid>` or `teleop_twist_keyboard`) and the subscribers `four_diff_controller`, `four_diff_controller2` and the echo. The robot keeps moving after you stop `pub`: send a zero Twist with `--once`, or press `k` in teleop.

## Exercises (pkg `mars_rover_tasks`)
- **Exercise 3.1**: `ros2 pkg create --build-type ament_cmake mars_rover_tasks --dependencies rclcpp std_msgs sensor_msgs geometry_msgs` (the text also lists `nav_msgs`, which the CMakeLists adds in 3.7); a `launch` folder installed by CMake; `src/subscriber_obstacle_detector.cpp` with class `ObstacleDetectorNode` that only logs `obstacle_detector_node Ready...` and ends (`make_shared` then `rclcpp::shutdown()`, no spin); executable `subscriber_obstacle_detector_executable`; `colcon build --packages-select mars_rover_tasks`.
- **Subscriber** (3.5): minimum laser distance → [[cpp-topic-subscriber]]. **Exercise 3.2**: six sectors, 0.8 m threshold, suggested action → [[cpp-recipe-laserscan]].
- **Mission 2** (3.6): `src/publish_mars_rover_move.cpp`, node `move_rover_node`, executable `publish_mars_rover_move_executable`, 0.5 m/s + 0.5 rad/s every 0.5 s, then a stop message on Ctrl+C → [[cpp-topic-publisher]].
- **Plant detector** (3.7): `src/plant_detector_node.cpp`, node `plant_detector_node`, subscribes `/leo/camera/image_raw`, publishes `std_msgs/msg/String` on `/plant_detector`, executable `image_plant_detector_executable`; uses the course's `PlantDetector` AI class → [[cpp-recipe-cv-bridge]], [[cpp-cmake-library]].
- **Exercise 3.3**: `src/autonomous_exploration.cpp`: turn until the front is clear, turn away from side obstacles, forward otherwise. **Exercise 3.4**: stay inside a 5.0 m circle around the start using `/odom` (`returning_to_origin_`, provided `return_to_origin()`), executable `autonomous_exploration_executable` → [[cpp-pub-sub-node]].
- **Mission 4** (3.8): package `custom_interfaces` (`ros2 pkg create --build-type ament_cmake custom_interfaces --dependencies rclcpp std_msgs geometry_msgs`), `msg/RoverEvents.msg` with `info` (`std_msgs/String`) and `rover_location` (`geometry_msgs/Pose`) → [[core-iface-package]]. Steps: package → `msg/` dir → `NameOfYourMessage.msg` → fields → CMakeLists → package.xml → build → source → use.
- **Example 3.6** (3.9): the plant detector publishes `RoverEvents` on `/mars_rover_events` with the pose from `/odom` → [[cpp-iface-use]].
- Quiz: [[cpp-learn-unit3-quiz]].

Solution of exercise 3.1 (`src/subscriber_obstacle_detector.cpp`):
```cpp
#include "rclcpp/rclcpp.hpp"

class ObstacleDetectorNode : public rclcpp::Node
{
public:
    ObstacleDetectorNode(const std::string& node_name = "obstacle_detector_node")
        : Node(node_name), node_name_(node_name)
    {
        RCLCPP_INFO(this->get_logger(), "%s Ready...", node_name_.c_str());
    }

private:
    std::string node_name_;
};

int main(int argc, char** argv){
    rclcpp::init(argc, argv);
    auto node = std::make_shared<ObstacleDetectorNode>();
    rclcpp::shutdown();
    return 0;
}
```

## Checks
- `ros2 topic info <topic>` tells you the interface and therefore the package to add as dependency.
- After building `custom_interfaces`, source the workspace in every terminal that uses `RoverEvents`.
