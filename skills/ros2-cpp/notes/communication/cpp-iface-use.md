---
id: cpp-iface-use
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "Use custom interfaces from C++: generated headers, find_package, ament_target_dependencies, filling RoverEvents"
domain: cpp
area: communication
distro: humble
tested: false
audience: dev
summary: "Include custom_interfaces/msg/rover_events.hpp, fill RoverEvents (info.data, rover_location from odometry), publish on /mars_rover_events; CMake and package.xml of the user."
tags: [custom interface, RoverEvents, rover_events.hpp, custom_interfaces, rosidl, generated header, std_msgs/String, geometry_msgs/Pose, Odometry, mars_rover_events, plant_detector_node.cpp]
see: ["[[core-iface-package]]", "[[core-iface-syntax-usage]]", "[[cpp-cmake-library]]", "[[cpp-recipe-cv-bridge]]", "[[cpp-srv-custom]]"]
requires: [ros2-core]
version_notes: []
---
# Use custom interfaces from C++

**TL;DR** Build the interface package first ([[core-iface-package]]) and source the workspace. In C++, `RoverEvents.msg` of `custom_interfaces` becomes the class `custom_interfaces::msg::RoverEvents` in the header `custom_interfaces/msg/rover_events.hpp` (CamelCase file → snake_case header). The using package needs `find_package(custom_interfaces REQUIRED)`, the name in `ament_target_dependencies`, and `<depend>custom_interfaces</depend>`.

## The message (mission 4)
```
# custom_interfaces/msg/RoverEvents.msg
std_msgs/String info # Info about discovery, issue, action
geometry_msgs/Pose rover_location # Location of the mars rover when the info was generated
```
`ros2 interface show custom_interfaces/msg/RoverEvents` expands the nested types: `info` → `string data`; `rover_location` → `Point position` (x, y, z) and `Quaternion orientation` (x 0, y 0, z 0, w 1: those are the default values). Example content: `info = "Detected plant, detected as tropical_plant"` with the rover pose at that moment. Interface packages are always CMake packages, and both C++ and Python nodes can use them; prefer an existing interface (`ros2 interface list`) when one fits.

## Fill and publish it
```cpp
#include <custom_interfaces/msg/rover_events.hpp>
...
auto rover_event = custom_interfaces::msg::RoverEvents();
rover_event.info.data = "The information we want to publish";
rover_event.rover_location.position.x = ROVERS_X_ODOM_LOCATION;
rover_event.rover_location.position.y = ROVERS_Y_ODOM_LOCATION;
```
Nested fields are plain members: `info` is a `std_msgs::msg::String` (so `.data`), `rover_location` a `geometry_msgs::msg::Pose` that can be assigned whole.

## `src/plant_detector_node.cpp` with RoverEvents (example 3.6)
The node of [[cpp-recipe-cv-bridge]] now also subscribes to `/odom`, keeps the last message, and publishes a `RoverEvents` on `/mars_rover_events` only when a plant is detected:
```cpp
#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/image.hpp>
#include <nav_msgs/msg/odometry.hpp>  // Import Odometry message type
#include <custom_interfaces/msg/rover_events.hpp>  // Import RoverEvents custom message type
#include <cv_bridge/cv_bridge.h>
#include <opencv2/opencv.hpp>
#include "mars_rover_tasks/plant_detector.hpp"  // Import the AI class

class PlantDetectorNode : public rclcpp::Node
{
public:
    PlantDetectorNode() : Node("plant_detector_node")
    {
        // Initialize the PlantDetector (path to the model file of the course's extra files)
        std::string path_to_model = "<path_to>/plant_detector/best_plant_detector_model.pth";
        plant_detector_ = std::make_unique<PlantDetector>(path_to_model);

        // Subscribe to the image topic
        subscription_ = this->create_subscription<sensor_msgs::msg::Image>(
            "/leo/camera/image_raw",
            10,
            std::bind(&PlantDetectorNode::image_callback, this, std::placeholders::_1));

        // Subscribe to the odometry topic
        odom_subscription_ = this->create_subscription<nav_msgs::msg::Odometry>(
            "/odom",
            10,
            std::bind(&PlantDetectorNode::odom_callback, this, std::placeholders::_1));

        // Initialize the Publisher for rover events
        publisher_ = this->create_publisher<custom_interfaces::msg::RoverEvents>("/mars_rover_events", 10);

        // Variable to store the latest odometry message
        current_odom_ = nullptr;
    }

private:
    void odom_callback(const nav_msgs::msg::Odometry::SharedPtr msg){
        // Store the current odometry data
        current_odom_ = msg;
    }

    void image_callback(const sensor_msgs::msg::Image::SharedPtr msg){
        // Convert ROS Image message to OpenCV image
        cv_bridge::CvImagePtr cv_ptr;
        try
        {
            cv_ptr = cv_bridge::toCvCopy(msg, sensor_msgs::image_encodings::BGR8);
        }
        catch (cv_bridge::Exception& e)
        {
            RCLCPP_ERROR(this->get_logger(), "cv_bridge exception: %s", e.what());
            return;
        }

        // Convert BGR to RGB
        cv::Mat rgb_image;
        cv::cvtColor(cv_ptr->image, rgb_image, cv::COLOR_BGR2RGB);

        // Use the PlantDetector to make a prediction
        float prediction = plant_detector_->predict(rgb_image);

        // Create a RoverEvents message
        auto rover_event = custom_interfaces::msg::RoverEvents();

        // Determine the result message based on the prediction
        if (prediction > 0.5)
        {
            rover_event.info.data = "Plant detected with confidence: " + std::to_string(prediction);
            RCLCPP_WARN(this->get_logger(), "%s", rover_event.info.data.c_str());
            RCLCPP_WARN(this->get_logger(), "Publishing mars rover event...");

            // If the odometry data is available, include the rover's location
            if (current_odom_)
            {
                rover_event.rover_location = current_odom_->pose.pose;  // Copy the pose data from the odometry
            }

            // Publish the RoverEvents message
            publisher_->publish(rover_event);
        }
        else
        {
            rover_event.info.data = "No plant detected. Confidence: " + std::to_string(1.0 - prediction);
            RCLCPP_INFO(this->get_logger(), "%s", rover_event.info.data.c_str());
        }
    }

private:
    rclcpp::Subscription<sensor_msgs::msg::Image>::SharedPtr subscription_;
    rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr odom_subscription_;
    rclcpp::Publisher<custom_interfaces::msg::RoverEvents>::SharedPtr publisher_;
    std::unique_ptr<PlantDetector> plant_detector_;
    nav_msgs::msg::Odometry::SharedPtr current_odom_;
};

int main(int argc, char **argv){
    rclcpp::init(argc, argv);

    auto plant_detector_node = std::make_shared<PlantDetectorNode>();

    rclcpp::spin(plant_detector_node);

    // Shutdown explicitly
    rclcpp::shutdown();
    return 0;
}
```
- Keeping the `SharedPtr` of the last odometry message (`current_odom_ = msg`) costs no copy; `if (current_odom_)` handles "no odometry yet".
- CMake and package.xml of `mars_rover_tasks` with `custom_interfaces` added: [[cpp-cmake-library]].

## Check
```bash
cd ~/ros2_ws && colcon build --packages-select mars_rover_tasks && source install/setup.bash
ros2 run mars_rover_tasks image_plant_detector_executable
source ~/ros2_ws/install/setup.bash && ros2 topic echo /mars_rover_events   # in a new terminal: source first
```
```yaml
info:
  data: 'Plant detected with confidence: 0.694875'
rover_location:
  position:
    x: 4.13154315948486
    y: -0.939910531044006
    z: -0.0132125467061996
  orientation:
    x: 0.0
    y: 0.0
    z: 0.34993486016942676
    w: 0.9367740355273537
```

## Pitfalls
- A terminal that was not sourced after building `custom_interfaces` cannot echo the topic (unknown message type) and the build of the user package cannot find the header.
- Header name: `custom_interfaces/msg/rover_events.hpp`, not `RoverEvents.hpp`.
- The model path is absolute in the course; use the path where you copied the course's extra files.
