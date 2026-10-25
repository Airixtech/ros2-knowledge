---
id: cpp-srv-custom
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "Custom service in C++: TextRecognition.srv request/response, server and client with the custom type"
domain: cpp
area: communication
distro: humble
tested: false
audience: dev
summary: "custom_interfaces/srv/TextRecognition (label → success + bounding box) used from rclcpp: server compares labels, client sets request->label; CMake additions."
tags: [custom service, TextRecognition.srv, custom_interfaces, text_recognition.hpp, Request, Response, bounding box, toupper, text_recognition_service_custom, int32]
see: ["[[core-iface-package]]", "[[cpp-srv-server]]", "[[cpp-srv-client]]", "[[cpp-iface-use]]", "[[cpp-recipe-cv-bridge]]"]
requires: [ros2-core]
version_notes:
  - "course: the server returns the 5 %-margin search region as the 'bounding box', not the position of the label (the code comment says so); the printed (5, 5) -> (95, 95) is that region for a 100 × 100 image (CPP-V50)"
---
# Custom service in C++

**TL;DR** Add `srv/TextRecognition.srv` to the interface package, list it in `rosidl_generate_interfaces` next to the existing files, build and source ([[core-iface-package]]). In C++ the type is `custom_interfaces::srv::TextRecognition` from `custom_interfaces/srv/text_recognition.hpp`; the callback reads `request->label` and fills `response->success`, `start_x`, `start_y`, `end_x`, `end_y`.

## The interface
```
string label  # Label to look for
---
bool success  # was label string found?
int32 start_x # X axis coordinate of Start point of Bounding Box
int32 start_y # Y axis coordinate of Start point of Bounding Box
int32 end_x   # X axis coordinate of End point of Bounding Box
int32 end_y   # Y axis coordinate of End point of Bounding Box
```
Example: request `label = FOOD` → response `success = True`, `start_x = 56`, `start_y = 66`, `end_x = 108`, `end_y = 85`. `int32` is a built-in field type like `bool` and `string`; `std_msgs/msg/Int32` is a whole message with a `data` field (and its definition says it is deprecated in favour of semantically meaningful messages). Check with `ros2 interface show custom_interfaces/srv/TextRecognition` after `source ~/ros2_ws/install/setup.bash`.

## Server: `src/text_recog_s_server_custom.cpp` (exercise 4.3)
The image subscription and the pixel counting of `recognizeLabel()` are those of [[cpp-srv-server]] / [[cpp-recipe-cv-bridge]]; what changes:
```cpp
#include <algorithm>
#include <array>
#include <cctype>
#include <memory>
#include <string>
#include <utility>
#include <cv_bridge/cv_bridge.h>
#include <opencv2/opencv.hpp>
#include <custom_interfaces/srv/text_recognition.hpp>
#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/image_encodings.hpp>
#include <sensor_msgs/msg/image.hpp>

class TextRecognitionServiceCustom : public rclcpp::Node {
public:
  TextRecognitionServiceCustom()
      : Node("text_recognition_service_custom"), image_received_(false) {
    // Subscribe to the camera image
    image_subscriber_ = this->create_subscription<sensor_msgs::msg::Image>(
        "/leo/camera/image_raw", 1,
        std::bind(&TextRecognitionServiceCustom::image_callback, this,
                  std::placeholders::_1));

    // Create the custom Service Server
    service_ = this->create_service<custom_interfaces::srv::TextRecognition>(
        "/text_recognition_service_custom",
        std::bind(
            &TextRecognitionServiceCustom::handle_text_recognition_request,
            this, std::placeholders::_1, std::placeholders::_2));

    RCLCPP_INFO(this->get_logger(),
                "Text Recognition Custom Service Server initialized");
  }

private:
  std::pair<std::string, cv::Rect> detectLabel(const cv::Mat &image) {
    if (image.empty()) {
      return {"", cv::Rect()};
    }

    // Ignore a small border around the image
    int margin_x = static_cast<int>(image.cols * 0.05);
    int margin_y = static_cast<int>(image.rows * 0.05);

    cv::Rect search_region(margin_x, margin_y, image.cols - 2 * margin_x,
                           image.rows - 2 * margin_y);

    cv::Mat roi = image(search_region);

    std::string detected_label = recognizeLabel(roi);

    if (detected_label.empty()) {
      return {"", cv::Rect()};
    }

    // Return the same region used for recognition as the bounding box
    return {detected_label, search_region};
  }

  std::string toUpper(const std::string &text) {
    std::string result = text;

    std::transform(result.begin(), result.end(), result.begin(),
                   [](unsigned char c) { return std::toupper(c); });

    return result;
  }

  void handle_text_recognition_request(
      const std::shared_ptr<custom_interfaces::srv::TextRecognition::Request>
          request,
      std::shared_ptr<custom_interfaces::srv::TextRecognition::Response>
          response) {
    // Default response
    response->success = false;
    response->start_x = 0;
    response->start_y = 0;
    response->end_x = 0;
    response->end_y = 0;

    if (!image_received_) {
      RCLCPP_WARN(this->get_logger(), "No camera image received yet");
      return;
    }

    // Run the same detection logic used in the previous version
    auto result = detectLabel(latest_image_);
    std::string detected_label = toUpper(result.first);
    std::string requested_label = toUpper(request->label);

    RCLCPP_INFO(this->get_logger(), "Requested label: %s",
                request->label.c_str());
    RCLCPP_INFO(this->get_logger(), "Detected label: %s",
                detected_label.empty() ? "NONE" : detected_label.c_str());

    // Return success only if the requested label matches
    if (!detected_label.empty() && detected_label == requested_label) {
      response->success = true;

      const cv::Rect &bbox = result.second;

      response->start_x = bbox.x;
      response->start_y = bbox.y;
      response->end_x = bbox.x + bbox.width;
      response->end_y = bbox.y + bbox.height;
    }

    RCLCPP_INFO(this->get_logger(), "Success: %s",
                response->success ? "true" : "false");
  }

  // image_callback() and recognizeLabel() as in text_recog_s_server.cpp;
  // recognizeLabel() now starts with: if (roi.empty()) { return ""; }
  rclcpp::Subscription<sensor_msgs::msg::Image>::SharedPtr image_subscriber_;
  rclcpp::Service<custom_interfaces::srv::TextRecognition>::SharedPtr service_;
  cv::Mat latest_image_;
  bool image_received_;
};
```
`std::toupper` on `unsigned char` (through the lambda) avoids undefined behaviour with negative `char` values; comparing upper-case strings makes `food` and `FOOD` match. The returned box is the search region, not the label's real position (CPP-V50).

## Client: `src/text_recog_s_client_custom.cpp`
```cpp
#include <chrono>
#include <memory>
#include <string>
#include <custom_interfaces/srv/text_recognition.hpp>
#include <rclcpp/rclcpp.hpp>

using namespace std::chrono_literals;

class TextRecognitionClientCustom : public rclcpp::Node {
public:
  TextRecognitionClientCustom() : Node("text_recognition_client_custom") {
    client_ = this->create_client<custom_interfaces::srv::TextRecognition>(
        "/text_recognition_service_custom");

    while (!client_->wait_for_service(1s)) {

      if (!rclcpp::ok()) {
        RCLCPP_ERROR(this->get_logger(),
                     "Interrupted while waiting for the Service");

        return;
      }

      RCLCPP_INFO(this->get_logger(),
                  "Service not available, waiting again...");
    }
  }

  void send_request(const std::string &label) {
    auto request =
        std::make_shared<custom_interfaces::srv::TextRecognition::Request>();

    // Set the label to search for
    request->label = label;

    RCLCPP_INFO(this->get_logger(), "Searching for label: %s", label.c_str());

    // Send the request asynchronously
    auto result_future = client_->async_send_request(request);

    // Wait for the response
    if (rclcpp::spin_until_future_complete(this->get_node_base_interface(),
                                           result_future) ==
        rclcpp::FutureReturnCode::SUCCESS) {
      auto response = result_future.get();

      if (response->success) {

        RCLCPP_INFO(this->get_logger(), "Label '%s' found!", label.c_str());
        RCLCPP_INFO(this->get_logger(), "Bounding Box: (%d, %d) -> (%d, %d)",
                    response->start_x, response->start_y, response->end_x,
                    response->end_y);

      } else {

        RCLCPP_INFO(this->get_logger(), "Label '%s' not found", label.c_str());
        RCLCPP_INFO(this->get_logger(), "Bounding Box: (%d, %d) -> (%d, %d)",
                    response->start_x, response->start_y, response->end_x,
                    response->end_y);
      }

    } else {

      RCLCPP_ERROR(this->get_logger(), "Failed to call Service");
    }
  }

private:
  rclcpp::Client<custom_interfaces::srv::TextRecognition>::SharedPtr client_;
};

int main(int argc, char **argv) {
  rclcpp::init(argc, argv);
  auto client = std::make_shared<TextRecognitionClientCustom>();
  std::string label_to_find = "FOOD";
  client->send_request(label_to_find);
  rclcpp::shutdown();
  return 0;
}
```
Near the FOOD box: `Searching for label: FOOD`, `Label 'FOOD' found!`, `Bounding Box: (5, 5) -> (95, 95)`; near the WASTE box: `Label 'FOOD' not found` and `(0, 0) -> (0, 0)`.

## CMakeLists.txt additions
```cmake
# Find the custom interfaces package
find_package(custom_interfaces REQUIRED)

# Add the custom service server executable
add_executable(text_recog_s_server_custom_executable src/text_recog_s_server_custom.cpp)

ament_target_dependencies(text_recog_s_server_custom_executable
  rclcpp
  sensor_msgs
  cv_bridge
  OpenCV
  custom_interfaces
)

# Add the custom service client executable
add_executable(text_recog_s_client_custom_executable src/text_recog_s_client_custom.cpp)

ament_target_dependencies(text_recog_s_client_custom_executable
  rclcpp
  custom_interfaces
)

# Install the executables
install(TARGETS
  text_recog_s_server_custom_executable
  text_recog_s_client_custom_executable
  DESTINATION lib/${PROJECT_NAME}
)
```
Add `<depend>custom_interfaces</depend>` to `package.xml` of `mars_rover_tasks` ([[cpp-cmake-library]]).

## Pitfalls
- The interface package's `rosidl_generate_interfaces` must keep `msg/RoverEvents.msg` when `srv/TextRecognition.srv` is added (with `DEPENDENCIES std_msgs geometry_msgs`).
- Every terminal that builds or runs these programs must have sourced the workspace after the interface was built.
