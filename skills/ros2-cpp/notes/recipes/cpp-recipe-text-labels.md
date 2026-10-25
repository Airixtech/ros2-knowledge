---
id: cpp-recipe-text-labels
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "Classify FOOD and WASTE box labels in C++: margin ROI, red, bright and dark pixel ratios (text_recog_node.cpp)"
domain: cpp
area: recipes
distro: humble
tested: false
audience: dev
summary: "Simplified label classifier: 5 % margin ROI, cv::Vec3b pixel loop, red/bright/dark ratios → WASTE, FOOD or none; image subscriber text_recog_node.cpp."
tags: [cv_bridge, OpenCV, cv::Mat, cv::Rect, ROI, cv::Vec3b, pixel ratio, label detection, FOOD, WASTE, text_recog_node.cpp, text_recognition_node]
see: ["[[cpp-recipe-cv-bridge]]", "[[cpp-srv-server]]", "[[cpp-srv-custom]]", "[[cpp-learn-unit4-services]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: cv_bridge 4.x ships only cv_bridge/cv_bridge.hpp (cv_bridge.h removed); Humble's cv_bridge 3.2.1 ships only cv_bridge.h — https://github.com/ros-perception/vision_opencv/blob/rolling/cv_bridge/CHANGELOG.rst (CPP-V21)"
---
# Classify FOOD and WASTE box labels

**TL;DR** The course's "text recognition" is a colour heuristic, not OCR: in the image minus a 5 % border, more than 0.2 % reddish pixels (the warning symbol) → `WASTE`; otherwise more than 10 % bright pixels (white label) and more than 1 % dark pixels (text) → `FOOD`; else no label. Unit 4 first runs it on every image, then only inside a service ([[cpp-srv-server]], [[cpp-srv-custom]]).

## `src/text_recog_node.cpp` (example 4.1)
```cpp
#include <cv_bridge/cv_bridge.h>
#include <memory>
#include <opencv2/opencv.hpp>
#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/image_encodings.hpp>
#include <sensor_msgs/msg/image.hpp>
#include <string>

class TextRecognitionNode : public rclcpp::Node {
public:
  TextRecognitionNode() : Node("text_recognition_node") {
    image_subscriber_ = this->create_subscription<sensor_msgs::msg::Image>(
        "/leo/camera/image_raw", 1,
        std::bind(&TextRecognitionNode::image_callback, this,
                  std::placeholders::_1));

    RCLCPP_INFO(this->get_logger(), "Text Recognition Node initialized");
  }

private:
  void image_callback(const sensor_msgs::msg::Image::SharedPtr msg) {
    cv_bridge::CvImagePtr cv_ptr;

    try {
      cv_ptr = cv_bridge::toCvCopy(msg, sensor_msgs::image_encodings::BGR8);
    } catch (const cv_bridge::Exception &e) {
      RCLCPP_ERROR(this->get_logger(), "cv_bridge exception: %s", e.what());

      return;
    }

    detectLabel(cv_ptr->image);
  }

  void detectLabel(const cv::Mat &image) {
    if (image.empty()) {
      return;
    }

    /*
     * Analyze almost the whole image.
     *
     * We only remove a small border to avoid irrelevant
     * pixels near the image edges.
     *
     * This is more robust than using a fixed central ROI,
     * because the WASTE warning symbol can move up or down
     * in the image depending on how close the rover is.
     */
    int margin_x = static_cast<int>(image.cols * 0.05);
    int margin_y = static_cast<int>(image.rows * 0.05);
    cv::Rect roi_rect(margin_x, margin_y, image.cols - 2 * margin_x,
                      image.rows - 2 * margin_y);
    cv::Mat roi = image(roi_rect);
    std::string detected_label = recognizeLabel(roi);

    if (!detected_label.empty()) {
      RCLCPP_INFO(this->get_logger(), "Detected label: %s",
                  detected_label.c_str());
    }
  }

  std::string recognizeLabel(const cv::Mat &roi) {
    /*
     * Simplified label classification.
     *
     * The WASTE box contains a reddish / pink warning
     * symbol above the text.
     *
     * The FOOD box does not contain this symbol.
     *
     * We also check that something resembling a label
     * is actually visible before returning FOOD.
     */
    int red_pixels = 0;
    int bright_pixels = 0;
    int dark_pixels = 0;

    const int total_pixels = roi.rows * roi.cols;

    for (int y = 0; y < roi.rows; ++y) {
      for (int x = 0; x < roi.cols; ++x) {

        const cv::Vec3b &pixel = roi.at<cv::Vec3b>(y, x);

        int blue = pixel[0];
        int green = pixel[1];
        int red = pixel[2];

        /*
         * Detect reddish / pink pixels from
         * the WASTE warning symbol.
         */
        if (red > 120 && red > green + 15 && red > blue + 15) {
          red_pixels++;
        }

        /*
         * Detect bright pixels from the
         * white background of the label.
         */
        if (blue > 180 && green > 180 && red > 180) {
          bright_pixels++;
        }

        /*
         * Detect dark pixels from the
         * FOOD / WASTE text.
         */
        if (blue < 130 && green < 130 && red < 130) {
          dark_pixels++;
        }
      }
    }

    double red_ratio = static_cast<double>(red_pixels) / total_pixels;
    double bright_ratio = static_cast<double>(bright_pixels) / total_pixels;
    double dark_ratio = static_cast<double>(dark_pixels) / total_pixels;

    /*
     * WASTE detection.
     *
     * Only a small percentage of the image needs
     * to contain reddish pixels because the warning
     * symbol is relatively small.
     */
    if (red_ratio > 0.002) {
      return "WASTE";
    }

    /*
     * Before returning FOOD, make sure that
     * a label is actually visible.
     *
     * We expect:
     * - enough bright pixels from the white label
     * - enough dark pixels from the text
     */
    bool label_visible = bright_ratio > 0.10 && dark_ratio > 0.01;

    if (label_visible) {
      return "FOOD";
    }

    /*
     * No label detected.
     */
    return "";
  }

  rclcpp::Subscription<sensor_msgs::msg::Image>::SharedPtr image_subscriber_;
};

int main(int argc, char **argv) {
  rclcpp::init(argc, argv);
  auto node = std::make_shared<TextRecognitionNode>();
  rclcpp::spin(node);
  rclcpp::shutdown();
  return 0;
}
```
- `cv_ptr->image` is BGR (`BGR8`), so `pixel[0]` is blue and `pixel[2]` red.
- `image(roi_rect)` is a view into the same pixels (no copy).
- CMake additions: `find_package(OpenCV REQUIRED)`, `find_package(cv_bridge REQUIRED)`, `add_executable(text_recog_executable src/text_recog_node.cpp)`, `ament_target_dependencies(text_recog_executable rclcpp sensor_msgs cv_bridge OpenCV)`, `install(TARGETS text_recog_executable DESTINATION lib/${PROJECT_NAME})`.
- Run `ros2 run mars_rover_tasks text_recog_executable` → `Text Recognition Node initialized`; drive to the boxes with teleop → `Detected label: WASTE` … `Detected label: FOOD`.

The course also copies a Python `text_recog.py` (from its extra files) into the package, but this C++ node does not use it.

## Pitfalls
- A per-pixel loop over every frame is slow for big images: in the service version it runs only on request ([[cpp-srv-server]]).
- Thresholds are tuned to the simulated boxes and their lighting; another camera or scene needs new values.
- `#include <cv_bridge/cv_bridge.h>` is the Humble header; Jazzy+ ships only `cv_bridge/cv_bridge.hpp` (CPP-V21).
