---
id: cpp-component-demo
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "TextRecognitionService component: Trigger service on camera images, CMake and package.xml additions"
domain: cpp
area: components
distro: humble
tested: false
audience: dev
summary: "Second component of rover_components: camera subscription + Trigger service returning FOOD/WASTE (simulated), header, source, CMake and package.xml additions."
tags: [component, TextRecognitionService, text_recognition_component, std_srvs/srv/Trigger, cv_bridge, RCLCPP_COMPONENTS_REGISTER_NODE, rover_components, text_recognition_service]
see: ["[[cpp-component-write]]", "[[cpp-component-run]]", "[[cpp-recipe-text-labels]]", "[[cpp-learn-unit8-components]]"]
requires: [ros2-core]
version_notes:
  - "course: the solution of exercise 8.3 in unit 8.5 does not compile (detect_text_with_bounding_box() and to_upper() defined but not declared, srv_ assigned while the header declares service_, cv::Mat used without an OpenCV include in the header) and uses TextRecognition while 8.6/8.7 call a Trigger service; the 8.7 solution below replaces it (CPP-V12)"
  - "course: simulate_text_recognition() says 'Simulate detection with 70% probability' but uniform_int_distribution(0, 1) == 0 is 50 %; when nothing was detected the handler picks FOOD, WASTE or nothing at random (CPP-V13)"
---
# TextRecognitionService component

**TL;DR** The second component of `rover_components` (unit 8.7 solution): it subscribes to the camera, keeps the last label found by a simplified detector, and answers `std_srvs/srv/Trigger` on `text_recognition_service` with `FOOD` or `WASTE`. The "recognition" is a simulation (random draws), not OCR (CPP-V13). Writing components: [[cpp-component-write]]; running them: [[cpp-component-run]].

## `include/rover_components/text_recognition_component.hpp`
```cpp
#ifndef COMPOSITION__TEXT_RECOGNITION_COMPONENT_HPP_
#define COMPOSITION__TEXT_RECOGNITION_COMPONENT_HPP_

#include "rover_components/visibility_control.h"
#include "rclcpp/rclcpp.hpp"
#include "std_srvs/srv/trigger.hpp"
#include "sensor_msgs/msg/image.hpp"
#include <opencv2/opencv.hpp>
#include <cv_bridge/cv_bridge.h>
#include <memory>

namespace rover_components
{

class TextRecognitionService : public rclcpp::Node
{
public:
  COMPOSITION_PUBLIC
  explicit TextRecognitionService(const rclcpp::NodeOptions & options);

private:
  void image_callback(const sensor_msgs::msg::Image::SharedPtr msg);

  void handle_text_recognition_request(
    const std::shared_ptr<std_srvs::srv::Trigger::Request> request,
    std::shared_ptr<std_srvs::srv::Trigger::Response> response);

  std::string detect_text(const cv::Mat& image);
  std::string simulate_text_recognition(const cv::Mat& roi);

  rclcpp::Service<std_srvs::srv::Trigger>::SharedPtr srv_;
  rclcpp::Subscription<sensor_msgs::msg::Image>::SharedPtr image_subscriber_;

  std::string last_detected_text_;
  float confidence_threshold_;
  float nms_threshold_;
};

}  // namespace rover_components

#endif  // COMPOSITION__TEXT_RECOGNITION_COMPONENT_HPP_
```

## `src/text_recognition_component.cpp`
```cpp
#include "rover_components/text_recognition_component.hpp"

#include <chrono>
#include <iostream>
#include <memory>
#include <utility>
#include <algorithm>
#include <cctype>
#include <random>
#include <iomanip>

#include "rclcpp/rclcpp.hpp"
#include "std_srvs/srv/trigger.hpp"
#include "sensor_msgs/msg/image.hpp"
#include <opencv2/opencv.hpp>
#include <cv_bridge/cv_bridge.h>

namespace rover_components
{

TextRecognitionService::TextRecognitionService(const rclcpp::NodeOptions & options)
: Node("text_recognition_service", options)
{
  // Initialize text detection parameters
  confidence_threshold_ = 0.5;
  nms_threshold_ = 0.4;
  last_detected_text_ = "";

  // Subscribe to camera feed for supply box identification
  image_subscriber_ = this->create_subscription<sensor_msgs::msg::Image>(
    "/leo/camera/image_raw", 1,
    std::bind(&TextRecognitionService::image_callback, this, std::placeholders::_1));

  // Create service for mission control text recognition requests
  srv_ = create_service<std_srvs::srv::Trigger>(
    "text_recognition_service",
    std::bind(&TextRecognitionService::handle_text_recognition_request, this,
              std::placeholders::_1, std::placeholders::_2));

  RCLCPP_INFO(this->get_logger(), "Text Recognition Service Component Ready for supply box identification...");
}

void TextRecognitionService::image_callback(const sensor_msgs::msg::Image::SharedPtr msg){
  // Convert ROS image to OpenCV format
  cv_bridge::CvImagePtr cv_ptr;
  try {
    cv_ptr = cv_bridge::toCvCopy(msg, sensor_msgs::image_encodings::BGR8);
  } catch (cv_bridge::Exception& e) {
    RCLCPP_ERROR(this->get_logger(), "cv_bridge exception: %s", e.what());
    return;
  }

  // Perform text detection on supply boxes
  std::string detected_text = detect_text(cv_ptr->image);

  // Store the last detected text for service requests
  if (!detected_text.empty()) {
    last_detected_text_ = detected_text;
  }

  // Log detection results for mission monitoring
  if (!last_detected_text_.empty()) {
    RCLCPP_DEBUG(this->get_logger(), "Supply box detected: %s", last_detected_text_.c_str());
  }
}

std::string TextRecognitionService::detect_text(const cv::Mat& image){
  // Simplified text detection using OpenCV methods
  cv::Mat gray, thresh;
  cv::cvtColor(image, gray, cv::COLOR_BGR2GRAY);
  cv::threshold(gray, thresh, 0, 255, cv::THRESH_BINARY | cv::THRESH_OTSU);

  // Find contours that might contain text
  std::vector<std::vector<cv::Point>> contours;
  cv::findContours(thresh, contours, cv::RETR_EXTERNAL, cv::CHAIN_APPROX_SIMPLE);

  for (const auto& contour : contours) {
    cv::Rect bounding_rect = cv::boundingRect(contour);

    // Filter by size (assuming text boxes have reasonable dimensions)
    if (bounding_rect.width > 50 && bounding_rect.height > 20 &&
        bounding_rect.width < 200 && bounding_rect.height < 100) {

      // Extract ROI for text recognition
      cv::Mat roi = image(bounding_rect);

      // Simulate text recognition on supply box labels
      std::string detected_text = simulate_text_recognition(roi);

      if (!detected_text.empty()) {
        return detected_text;
      }
    }
  }

  return ""; // No text detected
}

std::string TextRecognitionService::simulate_text_recognition(const cv::Mat& roi){
  // Simple heuristic based on color patterns to identify supply box labels
  cv::Scalar mean_color = cv::mean(roi);

  // Generate random text detection for simulation purposes
  std::random_device rd;
  std::mt19937 gen(rd());
  std::uniform_int_distribution<> dis(0, 1);

  // Simulate detection with 70% probability (it is 50 %: CPP-V13)
  if (dis(gen) == 0) {
    // Analyze color patterns to distinguish FOOD vs WASTE containers
    if (mean_color[1] > mean_color[0] && mean_color[1] > mean_color[2]) {
      return "FOOD";  // Greenish tint indicates FOOD label
    } else {
      return "WASTE"; // Other patterns indicate WASTE label
    }
  }

  return ""; // No recognizable text pattern
}

void TextRecognitionService::handle_text_recognition_request(
  const std::shared_ptr<std_srvs::srv::Trigger::Request> request,
  std::shared_ptr<std_srvs::srv::Trigger::Response> response){
  (void)request; // Suppress unused parameter warning
  // For simulation purposes, generate a detection result if none exists
  if (last_detected_text_.empty()) {
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> dis(0, 2);

    int result = dis(gen);
    if (result == 0) {
      last_detected_text_ = "FOOD";
    } else if (result == 1) {
      last_detected_text_ = "WASTE";
    } else {
      last_detected_text_ = "";
    }
  }

  // Convert detected text to uppercase for consistent comparison
  std::string detected_text = last_detected_text_;
  std::transform(detected_text.begin(), detected_text.end(), detected_text.begin(), ::toupper);

  // Respond with success = true if valid supply box label detected
  if (detected_text == "FOOD" || detected_text == "WASTE") {
    response->success = true;
  } else {
    response->success = false;
  }

  // Return detected text or status message
  response->message = detected_text.empty() ? "No supply box detected" : detected_text;

  RCLCPP_INFO(this->get_logger(), "Mission control requested text recognition. Detected: %s, Success: %s",
             response->message.c_str(), response->success ? "true" : "false");
}

}

#include "rclcpp_components/register_node_macro.hpp"
RCLCPP_COMPONENTS_REGISTER_NODE(rover_components::TextRecognitionService)
```
- Otsu thresholding + `cv::findContours` + a size filter (50–200 × 20–100 px) look for label-sized boxes; the mean colour decides FOOD (greenish) or WASTE. The real label classifier of unit 4 is [[cpp-recipe-text-labels]].
- `confidence_threshold_` and `nms_threshold_` are placeholders for an EAST text model (not loaded).
- `RCLCPP_DEBUG` lines are hidden at the default INFO level ([[cpp-logging]]).

## CMake and package.xml additions
```cmake
# Find required packages for text recognition
find_package(sensor_msgs REQUIRED)
find_package(cv_bridge REQUIRED)
find_package(OpenCV REQUIRED)

# Build text recognition component
add_library(text_recognition_component SHARED src/text_recognition_component.cpp)
target_compile_definitions(text_recognition_component PRIVATE "COMPOSITION_BUILDING_DLL")
ament_target_dependencies(text_recognition_component
  "rclcpp"
  "rclcpp_components"
  "std_srvs"
  "sensor_msgs"
  "cv_bridge"
  "OpenCV")

rclcpp_components_register_nodes(text_recognition_component "rover_components::TextRecognitionService")

install(TARGETS
  text_recognition_component
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin)
```
`package.xml`: `<depend>sensor_msgs</depend>`, `<depend>cv_bridge</depend>` and `<depend>image_transport</depend>` (the last one is unused by this code). Build with `colcon build --packages-select rover_components`; `ros2 service call /text_recognition_service std_srvs/srv/Trigger "{}"` → `success=True, message='FOOD'` (or WASTE).

## The unit 8.5 version
Unit 8.5 first shows another solution with `custom_interfaces/srv/TextRecognition` and a bounding box; it does not compile (CPP-V12) and the later units call the Trigger version above. Use this one.
