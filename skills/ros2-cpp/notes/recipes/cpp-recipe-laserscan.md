---
id: cpp-recipe-laserscan
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "LaserScan in C++: six sectors with index ranges, sector minimums, priority rules, obstacle-detector node"
domain: cpp
area: recipes
distro: humble
tested: false
audience: dev
summary: "C++ LaserScan sectors: std::map of index ranges, std::min_element per sector, numeric_limits infinity, bounds check, 0.8 m threshold, priority actions."
tags: [LaserScan, sectors, std::map, std::pair, std::min_element, numeric_limits, infinity, static_cast, obstacle detection, Front_Left, Right_Rear, subscriber_obstacle_detector.cpp]
see: ["[[core-recipe-laserscan]]", "[[cpp-topic-subscriber]]", "[[cpp-pub-sub-node]]", "[[cpp-learn-unit3-topics]]"]
requires: [ros2-core]
version_notes:
  - "course: std::map iterates its keys in sorted order, so the program logs Front_Left, Front_Right, Left, Left_Rear, Right, Right_Rear; the course's expected output shows Right_Rear … Left_Rear — https://en.cppreference.com/w/cpp/container/map (CPP-V49)"
---
# LaserScan sectors in C++

**TL;DR** The Mars rover laser has 200 samples over 252° (`angle_min`/`angle_max` ±2.2 rad), index 0 on the right. Split it into six sectors of about 33 indices (42°), take the minimum of each with `std::min_element` on an iterator subrange, and treat a sector as "detected" below 0.8 m. Geometry and the angle↔index formulas: [[core-recipe-laserscan]].

## Sectors (exercise 3.2)
| Sector | angular range | indices | suggested action |
|---|---|---|---|
| Right_Rear | 210° – 252° | 0–33 | Go Forward |
| Right | 168° – 210° | 34–66 | Go Forward While Turning Slightly Left |
| Front_Right | 126° – 168° | 67–100 | Turn Left |
| Front_Left | 84° – 126° | 101–133 | Turn Right |
| Left | 42° – 84° | 134–166 | Go Forward While Turning Slightly Right |
| Left_Rear | 0° – 42° | 167–199 | Go Forward |

The course's table counts the 252° from the left (Left_Rear 0°–42°) while the indices progress from right to left. Combinations are yours to rank: with both front sectors detected you might reverse while turning, to avoid getting stuck; no detection → Go Forward. For the Left and Right sectors the turning intensity can depend on the angle of the obstacle.

## Solution: `src/subscriber_obstacle_detector.cpp`
```cpp
#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/laser_scan.hpp"
#include "rclcpp/qos.hpp"
#include <algorithm>
#include <map>
#include <string>
#include <limits>

class ObstacleDetectorNode : public rclcpp::Node
{
public:
    ObstacleDetectorNode(const std::string& node_name = "obstacle_detector_node")
        : Node(node_name)
    {
        // create the subscriber object
        auto qos = rclcpp::QoS(10).reliability(rclcpp::ReliabilityPolicy::Reliable);

        subscriber_ = this->create_subscription<sensor_msgs::msg::LaserScan>(
            "/laser_scan",
            qos,
            std::bind(&ObstacleDetectorNode::laserscan_callback, this, std::placeholders::_1)
        );

        RCLCPP_INFO(this->get_logger(), "%s Ready...", this->get_name());
    }

private:
    rclcpp::Subscription<sensor_msgs::msg::LaserScan>::SharedPtr subscriber_;

    void laserscan_callback(const sensor_msgs::msg::LaserScan::SharedPtr msg){
        // Define the sectors with their index ranges
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
        for (const auto& sector : sectors) {
            min_distances[sector.first] = std::numeric_limits<float>::infinity();
        }

        // Find the minimum distance in each sector
        for (const auto& sector : sectors) {
            int start_idx = sector.second.first;
            int end_idx = sector.second.second;

            // Ensure the index range is within bounds
            if (start_idx < static_cast<int>(msg->ranges.size()) && end_idx < static_cast<int>(msg->ranges.size())) {
                auto start_it = msg->ranges.begin() + start_idx;
                auto end_it = msg->ranges.begin() + end_idx + 1;

                if (start_it < end_it) {
                    min_distances[sector.first] = *std::min_element(start_it, end_it);
                }
            }
        }

        // Log the minimum distances
        for (const auto& distance : min_distances) {
            RCLCPP_INFO(this->get_logger(), "%s: %.2f meters", distance.first.c_str(), distance.second);
        }

        // Define the threshold for obstacle detection
        float obstacle_threshold = 0.8f;  // meters
        // Determine detected obstacles
        std::map<std::string, bool> detections;
        for (const auto& distance : min_distances) {
            detections[distance.first] = distance.second < obstacle_threshold;
        }

        // Determine suggested action based on detection and ordered conditions by priority
        // Priority 1: Front detection, Priority 2: Side detections, Priority 3: Rear detections
        std::string action;

        // Priority 1
        if (detections["Front_Left"] && detections["Front_Right"]) {
            std::string arbitrary_direction = "Right";
            action = "Selected Turn Arbitrary Direction " + arbitrary_direction;
        } else if (detections["Front_Left"] && !detections["Front_Right"]) {
            action = "Turn Right to avoid obstacle on the front-left";
        } else if (detections["Front_Right"] && !detections["Front_Left"]) {
            action = "Turn Left to avoid obstacle on the front-right";
        }
        // Priority 2
        else if (detections["Left"]) {
            action = "Go Forwards turning slightly right to avoid obstacle on the left";
        } else if (detections["Right"]) {
            action = "Go Forwards turning slightly left to avoid obstacle on the right";
        }
        // Priority 3
        else if (detections["Right_Rear"]) {
            action = "Go Forwards, BUT DONT reverse Right";
        } else if (detections["Left_Rear"]) {
            action = "Go Forwards, BUT DONT reverse left";
        } else {
            action = "Go Forwards";
        }

        // Log the suggested action
        RCLCPP_INFO(this->get_logger(), "Suggested action: %s", action.c_str());
    }
};

int main(int argc, char** argv){
    rclcpp::init(argc, argv);
    auto node = std::make_shared<ObstacleDetectorNode>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}
```
Output with obstacles ahead (`Front_Right: 0.51 meters`, `Front_Left: 0.46 meters`, `Left: 0.60 meters`, `Left_Rear: 0.68 meters`, `Right: inf meters`): `Suggested action: Selected Turn Arbitrary Direction Right` (both front sectors → turn right, an arbitrary choice). The six distance lines come in **alphabetical key order** (Front_Left, Front_Right, Left, Left_Rear, Right, Right_Rear), because `std::map` sorts its keys; the course's printed order Right_Rear … Left_Rear is not what this program prints (CPP-V49). Keep a `std::vector<std::pair<std::string, std::pair<int, int>>>` if you want the sensor order.

## C++ review
- `std::map` + `std::pair` name each index range; `for (const auto& sector : sectors)` iterates without copies.
- `msg->ranges.begin() + start_idx` … `+ end_idx + 1` builds a subrange for `std::min_element` (the end iterator is one past the last element).
- `msg->ranges.size()` is `std::size_t`: `static_cast<int>()` avoids comparing signed and unsigned; the bounds check matters because the sample count depends on the sensor or simulation.
- `std::numeric_limits<float>::infinity()` starts each minimum: any finite reading is smaller.

## Pitfalls
- Hard-coded indices assume 200 samples: compute them from `angle_min`, `angle_increment` and `ranges.size()` for another laser ([[core-recipe-laserscan]]).
- `std::map` order ≠ insertion order (CPP-V49).
- A NaN in a sector makes `std::min_element` unreliable: filter with `std::isfinite` first.
