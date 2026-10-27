---
id: cpp-recipe-cv-bridge
type: reference
owner: equipo-ros2
updated: 2026-10-27
review_by: 2027-04-25
source: manual
confidentiality: internal
title: "cv_bridge and OpenCV in rclcpp: toCvCopy BGR8, plant detector node, HSV inRange masks, excess-green ratio, HSV trackbar tuner"
domain: cpp
area: recipes
distro: humble
tested: false
audience: dev
summary: "cv_bridge::toCvCopy(msg, BGR8), cvtColor, a String-publishing plant detector, HSV inRange green ratio, excess green 2G-R-B, trackbar HSV tuner."
tags: [cv_bridge, toCvCopy, CvImagePtr, image_encodings, BGR8, OpenCV, cvtColor, COLOR_BGR2HSV, inRange, countNonZero, excess green, createTrackbar, imshow, waitKey, plant_detector_node.cpp, green_test.cpp]
see: ["[[core-recipe-cv-bridge]]", "[[cpp-recipe-text-labels]]", "[[cpp-iface-use]]", "[[cpp-cmake-library]]", "[[cpp-exec-multi-node]]", "[[cpp-humble-to-jazzy]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: cv_bridge 4.0.0 removed cv_bridge/cv_bridge.h; use cv_bridge/cv_bridge.hpp (Humble's 3.2.1 has only the .h) — https://github.com/ros-perception/vision_opencv/blob/rolling/cv_bridge/CHANGELOG.rst (CPP-V21)"
---
# cv_bridge and OpenCV in rclcpp

**TL;DR** Convert a `sensor_msgs::msg::Image` to OpenCV with `cv_bridge::toCvCopy(msg, sensor_msgs::image_encodings::BGR8)` inside `try`/`catch (cv_bridge::Exception&)`; `cv_ptr->image` is a `cv::Mat` you own. Then any OpenCV code works: colour conversion, `cv::inRange` masks, pixel ratios. Python twin: [[core-recipe-cv-bridge]].

## Plant detector that publishes a String (unit 3.7)
```cpp
#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/image.hpp>
#include <std_msgs/msg/string.hpp>  // Include String message type
#include <cv_bridge/cv_bridge.h>
#include <opencv2/opencv.hpp>
#include "mars_rover_tasks/plant_detector.hpp"  // Include the AI class

class PlantDetectorNode : public rclcpp::Node
{
public:
    PlantDetectorNode() : Node("plant_detector_node")
    {
        // Initialize the PlantDetector (model file of the course's extra files)
        std::string path_to_model = "<path_to>/plant_detector/best_plant_detector_model.pth";
        plant_detector_ = std::make_unique<PlantDetector>(path_to_model);

        // Subscribe to the image topic
        subscription_ = this->create_subscription<sensor_msgs::msg::Image>(
            "/leo/camera/image_raw",
            10,
            std::bind(&PlantDetectorNode::image_callback, this, std::placeholders::_1));

        // Initialize the Publisher for plant detection results
        publisher_ = this->create_publisher<std_msgs::msg::String>("/plant_detector", 10);
    }

private:
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

        // Determine the result message based on the prediction
        std::string result;
        if (prediction > 0.5)
        {
            result = "Plant detected with confidence: " + std::to_string(prediction);
            RCLCPP_WARN(this->get_logger(), "%s", result.c_str());
        }
        else
        {
            result = "No plant detected. Confidence: " + std::to_string(1.0 - prediction);
            RCLCPP_INFO(this->get_logger(), "%s", result.c_str());
        }

        // Publish the result as a String message
        auto msg_out = std_msgs::msg::String();
        msg_out.data = result;
        publisher_->publish(msg_out);
    }

private:
    rclcpp::Subscription<sensor_msgs::msg::Image>::SharedPtr subscription_;
    rclcpp::Publisher<std_msgs::msg::String>::SharedPtr publisher_;
    std::unique_ptr<PlantDetector> plant_detector_;
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
- `PlantDetector` (`plant_detector.hpp`/`.cpp` and the `.pth` model) comes from the course's extra files: the course's AI model; `predict()` returns the plant confidence for an RGB image, hence `COLOR_BGR2RGB`. Library build: [[cpp-cmake-library]].
- Prediction > 0.5 → "plant", otherwise the reported confidence is `1.0 - prediction`. Other nodes can subscribe to `/plant_detector` (`ros2 topic echo /plant_detector`). One node, one subscriber, one publisher: receive, process, publish.
- With odometry and a custom message: [[cpp-iface-use]].

## Green in HSV (plant detector of unit 5.5)
`detect_plant_in_image()` of [[cpp-exec-plant-detector-demo]]: `cv::cvtColor(image, hsv, cv::COLOR_BGR2HSV)`, `cv::inRange(hsv, cv::Scalar(40, 50, 50), cv::Scalar(80, 255, 255), mask)`, `cv::countNonZero(mask)` / pixels > 0.01 → confidence 0.8, else 0.2. OpenCV's 8-bit HSV has H in 0–179 and S, V in 0–255; H 40–80 is green.

## Excess green (unit 6.7)
`2G − R − B` highlights pixels whose green channel is clearly stronger than red and blue: `cv::split` the BGR image, `convertTo(…, CV_16S)` each channel first (8-bit arithmetic would saturate at 0), `cv::threshold(…, 40, 255, cv::THRESH_BINARY)`, back to `CV_8U`, then `cv::countNonZero` / total pixels > 0.01. The code is part of `green_detector_node.cpp` in [[cpp-exec-multi-node]].

## HSV range tuner with trackbars (`green_test.cpp`, unit 6.7)
```cpp
#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/image.hpp>
#include <cv_bridge/cv_bridge.h>
#include <opencv2/opencv.hpp>
#include <memory>

using std::placeholders::_1;

class GreenDetector : public rclcpp::Node
{
public:
  GreenDetector()
  : Node("green_detector")
  {
    // Create a subscriber to the camera image topic
    subscription_ = this->create_subscription<sensor_msgs::msg::Image>(
      "/leo/camera/image_raw", 10, std::bind(&GreenDetector::image_callback, this, _1));

    // Create fullscreen window with trackbars for adjusting HSV values
    cv::namedWindow("Green Detection", cv::WINDOW_NORMAL);
    cv::setWindowProperty("Green Detection", cv::WND_PROP_FULLSCREEN, cv::WINDOW_FULLSCREEN);

    cv::createTrackbar("Lower H", "Green Detection", nullptr, 179, nullptr);
    cv::createTrackbar("Lower S", "Green Detection", nullptr, 255, nullptr);
    cv::createTrackbar("Lower V", "Green Detection", nullptr, 255, nullptr);
    cv::createTrackbar("Upper H", "Green Detection", nullptr, 179, nullptr);
    cv::createTrackbar("Upper S", "Green Detection", nullptr, 255, nullptr);
    cv::createTrackbar("Upper V", "Green Detection", nullptr, 255, nullptr);

    // Set initial values
    cv::setTrackbarPos("Upper H", "Green Detection", 179);
    cv::setTrackbarPos("Upper S", "Green Detection", 255);
    cv::setTrackbarPos("Upper V", "Green Detection", 255);
  }

  ~GreenDetector()
  {
    cv::destroyAllWindows();
  }

private:
  void image_callback(const sensor_msgs::msg::Image::SharedPtr msg){
    try {
      // Convert the ROS image message to an OpenCV image
      cv_bridge::CvImagePtr cv_ptr = cv_bridge::toCvCopy(msg, sensor_msgs::image_encodings::BGR8);
      cv::Mat cv_image = cv_ptr->image;

      // Get current positions of all trackbars
      lower_h_ = cv::getTrackbarPos("Lower H", "Green Detection");
      lower_s_ = cv::getTrackbarPos("Lower S", "Green Detection");
      lower_v_ = cv::getTrackbarPos("Lower V", "Green Detection");
      upper_h_ = cv::getTrackbarPos("Upper H", "Green Detection");
      upper_s_ = cv::getTrackbarPos("Upper S", "Green Detection");
      upper_v_ = cv::getTrackbarPos("Upper V", "Green Detection");

      // Set the lower and upper bounds for HSV
      cv::Scalar lower_green(lower_h_, lower_s_, lower_v_);
      cv::Scalar upper_green(upper_h_, upper_s_, upper_v_);

      // Convert the image to HSV color space
      cv::Mat hsv_image;
      cv::cvtColor(cv_image, hsv_image, cv::COLOR_BGR2HSV);

      // Create a mask to threshold the image
      cv::Mat mask;
      cv::inRange(hsv_image, lower_green, upper_green, mask);

      // Optionally visualize the green detection on the original image
      cv::Mat green_detected;
      cv::bitwise_and(cv_image, cv_image, green_detected, mask);

      // Display the green-detected image in fullscreen
      cv::imshow("Green Detection", green_detected);

      // Press 'q' to exit the loop
      if ((cv::waitKey(1) & 0xFF) == 'q') {
        rclcpp::shutdown();
      }
    } catch (cv_bridge::Exception& e) {
      RCLCPP_ERROR(this->get_logger(), "cv_bridge exception: %s", e.what());
    }
  }

  rclcpp::Subscription<sensor_msgs::msg::Image>::SharedPtr subscription_;
  int lower_h_ = 0, lower_s_ = 0, lower_v_ = 0;
  int upper_h_ = 179, upper_s_ = 255, upper_v_ = 255;
};

int main(int argc, char * argv[]){
  rclcpp::init(argc, argv);

  auto green_detector = std::make_shared<GreenDetector>();

  try {
    rclcpp::spin(green_detector);
  } catch (const std::exception & e) {
    RCLCPP_ERROR(green_detector->get_logger(), "Exception: %s", e.what());
  }

  rclcpp::shutdown();
  return 0;
}
```
With the lower bounds H = 34, S = 84, V = 0 mainly the green areas remain; those values are what `GreenDetectorNode` uses ([[cpp-exec-multi-node]]). CMake: `add_executable(green_test src/green_test.cpp)` with `rclcpp std_msgs cv_bridge OpenCV` in `ament_target_dependencies` (plus `sensor_msgs`, used by the code). The first launch can fail with a GDK `BadAccess` (MIT-SHM) X error in the course's graphical environment: start it again.

## Pitfalls
- A missing `try`/`catch` around `toCvCopy` → an unexpected encoding throws and the node dies.
- `cv::waitKey()` is needed for `imshow` windows to refresh; never loop on it inside a ROS callback, it blocks that executor thread ([[cpp-exec-multi-node]]).
- `#include <cv_bridge/cv_bridge.h>` exists only up to cv_bridge 3.x (Humble); Jazzy+ needs `cv_bridge/cv_bridge.hpp` (CPP-V21).
- Python versions of more pipelines (blob and line following, Haar faces, HOG people, YOLO): the ros2-perception skill.
