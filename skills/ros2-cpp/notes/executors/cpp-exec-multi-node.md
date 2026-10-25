---
id: cpp-exec-multi-node
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "Several nodes in one executor: add_node, one node reads another's data through a shared_ptr"
domain: cpp
area: executors
distro: humble
tested: false
audience: dev
summary: "PlantDetectorNode and GreenDetectorNode in one MultiThreadedExecutor (add_node twice); the second node calls get_latest_image() on a shared_ptr to the first."
tags: [MultiThreadedExecutor, add_node, multiple nodes, one process, shared_ptr, get_latest_image, GreenDetectorNode, green_detector, intra-process, green_detector_node.cpp]
see: ["[[cpp-exec-callback-groups]]", "[[cpp-exec-multithreaded]]", "[[core-exec-spin]]", "[[cpp-recipe-cv-bridge]]", "[[cpp-component-run]]"]
requires: [ros2-core]
version_notes:
  - "course: the printed response of /detect_plants ('Plant detection completed') belongs to the earlier program; this one answers 'Plant detected successfully' or 'Plant not detected within 10 seconds' (CPP-V06)"
  - "course: get_latest_image() is called a thread-safe copy but takes no lock while listener_callback() writes last_image_ in another group; <mutex> is included and unused (CPP-V05)"
  - "all: rclcpp intra-process communication covers publishers and subscriptions and must be enabled (NodeOptions::use_intra_process_comms); calling another node's method is not ROS communication — https://github.com/ros2/rclcpp/blob/humble/rclcpp/include/rclcpp/publisher.hpp (CPP-V17, CPP-V33)"
---
# Several nodes in one executor

**TL;DR** Create both nodes in one `main()`, `add_node()` each to the same executor and `spin()` once: the nodes share the executor's threads, and each stays a normal ROS 2 node with its own name and services. Here `GreenDetectorNode` gets a `std::shared_ptr` to `PlantDetectorNode` and reads its last image directly instead of subscribing to the camera a second time. That direct call needs the lock of [[cpp-exec-callback-groups]].

## `main()` with two nodes
```cpp
auto plant_detector_node = std::make_shared<PlantDetectorNode>();
auto green_detector_node = std::make_shared<GreenDetectorNode>(plant_detector_node);

// Use MultiThreadedExecutor
rclcpp::executors::MultiThreadedExecutor executor(rclcpp::ExecutorOptions(), 2);
executor.add_node(plant_detector_node);
executor.add_node(green_detector_node);

try {
  executor.spin();
} catch (const std::exception & e) {
  RCLCPP_ERROR(rclcpp::get_logger("rclcpp"), "Exception: %s", e.what());
}

rclcpp::shutdown();
```
The benefits the course names: one pool of threads for both nodes instead of an executor per node (fewer resources, which counts on limited hardware such as space robots), one camera subscription for two users, and simpler coordination. Nodes in one process *can* use intra-process communication for topics when it is enabled (`use_intra_process_comms`), but calling a method of another node is plain C++, not ROS communication, and it couples the two classes (CPP-V17, CPP-V33). Components are the reusable way to put nodes in one process ([[cpp-component-run]]).

## `src/green_detector_node.cpp` (unit 6.7)
`PlantDetectorNode` here is a compact version of the detector: two MutuallyExclusive groups, excess-green detection (`2G − R − B` on `CV_16S` channels, so the subtraction does not saturate at 0; a plant when more than 1 % of the pixels pass the threshold 40) and a public `get_latest_image()`:
```cpp
#include <chrono>
#include <cv_bridge/cv_bridge.h>
#include <geometry_msgs/msg/twist.hpp>
#include <memory>
#include <mutex>
#include <opencv2/opencv.hpp>
#include <rclcpp/callback_group.hpp>
#include <rclcpp/executors/multi_threaded_executor.hpp>
#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/image.hpp>
#include <std_srvs/srv/trigger.hpp>
#include <thread>

using namespace std::chrono_literals;
using std::placeholders::_1;
using std::placeholders::_2;

class PlantDetectorNode : public rclcpp::Node {
public:
  PlantDetectorNode(
      const std::string &image_topic_name = "/leo/camera/image_raw")
      : Node("plant_detector_node"), image_topic_name_(image_topic_name) {
    // Create two mutually exclusive callback groups
    mutuallyexclusive_group_1_ = this->create_callback_group(
        rclcpp::CallbackGroupType::MutuallyExclusive);

    mutuallyexclusive_group_2_ = this->create_callback_group(
        rclcpp::CallbackGroupType::MutuallyExclusive);

    // Assign the camera subscription to the first callback group
    rclcpp::SubscriptionOptions sub_options;
    sub_options.callback_group = mutuallyexclusive_group_1_;

    subscription_ = this->create_subscription<sensor_msgs::msg::Image>(
        image_topic_name_, 10,
        std::bind(&PlantDetectorNode::listener_callback, this, _1),
        sub_options);

    // Create publisher for velocity commands
    cmd_vel_publisher_ =
        this->create_publisher<geometry_msgs::msg::Twist>("/cmd_vel", 10);

    // Assign the service to the second callback group
    service_ = this->create_service<std_srvs::srv::Trigger>(
        "detect_plants",
        std::bind(&PlantDetectorNode::detect_plants_callback, this, _1, _2),
        rmw_qos_profile_services_default, mutuallyexclusive_group_2_);

    RCLCPP_INFO(this->get_logger(), "1- PlantDetectorNode READY...");
  }

  cv::Mat get_latest_image() const { return last_image_.clone(); }

private:
  void listener_callback(const sensor_msgs::msg::Image::SharedPtr msg) {
    try {
      // Convert ROS image to OpenCV image
      cv_bridge::CvImagePtr cv_ptr =
          cv_bridge::toCvCopy(msg, sensor_msgs::image_encodings::BGR8);

      last_image_ = cv_ptr->image.clone();
      image_received_ = true;

    } catch (cv_bridge::Exception &e) {
      RCLCPP_ERROR(this->get_logger(), "cv_bridge exception: %s", e.what());
    }
  }

  void detect_plants_callback(
      const std::shared_ptr<std_srvs::srv::Trigger::Request> request,
      std::shared_ptr<std_srvs::srv::Trigger::Response> response) {
    (void)request;

    auto start_time = this->get_clock()->now();
    auto duration_10_sec = rclcpp::Duration::from_seconds(10.0);

    bool plant_found = false;

    // Start rotating the robot
    publish_velocity(0.0, -0.2);

    auto delta_time = this->get_clock()->now() - start_time;

    while (delta_time < duration_10_sec && !plant_found) {
      delta_time = this->get_clock()->now() - start_time;

      // Get a thread-safe copy of the latest image
      cv::Mat image = get_latest_image();

      if (!image.empty()) {
        RCLCPP_INFO(this->get_logger(), "Processing Image for Plants...");

        /*
         * SIMPLE PLANT DETECTION USING EXCESS GREEN
         *
         * Excess Green = 2G - R - B
         *
         * This highlights pixels where the green channel
         * is significantly stronger than red and blue.
         */
        std::vector<cv::Mat> channels;
        cv::split(image, channels);

        cv::Mat blue;
        cv::Mat green;
        cv::Mat red;

        channels[0].convertTo(blue, CV_16S);
        channels[1].convertTo(green, CV_16S);
        channels[2].convertTo(red, CV_16S);

        // Calculate Excess Green
        cv::Mat excess_green = 2 * green - red - blue;

        // Create a binary mask
        cv::Mat plant_mask;

        cv::threshold(excess_green, plant_mask, 40, 255, cv::THRESH_BINARY);

        plant_mask.convertTo(plant_mask, CV_8U);

        // Calculate percentage of plant-like pixels
        int plant_pixels = cv::countNonZero(plant_mask);

        int total_pixels = plant_mask.rows * plant_mask.cols;

        double plant_percentage = static_cast<double>(plant_pixels) /
                                  static_cast<double>(total_pixels);

        RCLCPP_INFO(this->get_logger(), "Plant percentage: %.3f",
                    plant_percentage);

        // Detect plant if more than 1% of image
        // contains vegetation-like pixels
        if (plant_percentage > 0.01) {
          publish_velocity(0.0, 0.0);

          RCLCPP_INFO(this->get_logger(), "Plant Detected! Percentage: %.3f",
                      plant_percentage);

          plant_found = true;

        } else {
          RCLCPP_INFO(this->get_logger(), "No Plant Detected. Percentage: %.3f",
                      plant_percentage);
        }
      }

      std::this_thread::sleep_for(100ms);
    }

    // Stop the robot
    publish_velocity(0.0, 0.0);

    response->success = plant_found;

    if (plant_found) {
      response->message = "Plant detected successfully";
    } else {
      response->message = "Plant not detected within 10 seconds";
    }
  }

  void publish_velocity(double linear, double angular) {
    auto vel_msg = geometry_msgs::msg::Twist();

    vel_msg.linear.x = linear;
    vel_msg.angular.z = angular;

    cmd_vel_publisher_->publish(vel_msg);
  }

  std::string image_topic_name_;
  rclcpp::CallbackGroup::SharedPtr mutuallyexclusive_group_1_;
  rclcpp::CallbackGroup::SharedPtr mutuallyexclusive_group_2_;
  rclcpp::Subscription<sensor_msgs::msg::Image>::SharedPtr subscription_;
  rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr cmd_vel_publisher_;
  rclcpp::Service<std_srvs::srv::Trigger>::SharedPtr service_;
  cv::Mat last_image_;
  bool image_received_ = false;
};

class GreenDetectorNode : public rclcpp::Node {
public:
  GreenDetectorNode(std::shared_ptr<PlantDetectorNode> plant_detect_node)
      : Node("green_detector_node"), plant_detect_node_(plant_detect_node) {
    // Create service for green verification
    service_ = this->create_service<std_srvs::srv::Trigger>(
        "/green_detector",
        std::bind(&GreenDetectorNode::detect_green_detector_callback, this, _1,
                  _2));

    RCLCPP_INFO(this->get_logger(), "2- GreenDetectorNode READY...");
  }

private:
  void detect_green_detector_callback(
      const std::shared_ptr<std_srvs::srv::Trigger::Request> request,
      std::shared_ptr<std_srvs::srv::Trigger::Response> response) {
    (void)request;

    cv::Mat cv_image = get_image();

    auto result = detect_green_detector(cv_image);

    response->success = result.first;
    response->message = result.second;
  }

  cv::Mat get_image() { return plant_detect_node_->get_latest_image(); }

  std::pair<bool, std::string> detect_green_detector(const cv::Mat &cv_image) {
    if (cv_image.empty()) {
      return {false, "No image available"};
    }

    // Convert image to HSV
    cv::Mat hsv_image;
    cv::cvtColor(cv_image, hsv_image, cv::COLOR_BGR2HSV);

    // Define HSV color range
    cv::Scalar lower_green(34, 84, 0);
    cv::Scalar upper_green(179, 255, 255);

    // Create mask
    cv::Mat mask;
    cv::inRange(hsv_image, lower_green, upper_green, mask);

    // Apply mask to original image
    cv::Mat green_detected;
    cv::bitwise_and(cv_image, cv_image, green_detected, mask);

    // Create resizable windows
    cv::namedWindow("Mask", cv::WINDOW_NORMAL);
    cv::namedWindow("Detected Green", cv::WINDOW_NORMAL);
    cv::resizeWindow("Mask", 500, 500);
    cv::resizeWindow("Detected Green", 500, 500);

    // Display images
    cv::imshow("Mask", mask);
    cv::imshow("Detected Green", green_detected);

    // Keep windows open until 'q' is pressed
    while (true) {
      if ((cv::waitKey(1) & 0xFF) == 'q') {
        break;
      }
    }

    cv::destroyAllWindows();

    return {true, "Green areas detected"};
  }

  std::shared_ptr<PlantDetectorNode> plant_detect_node_;
  rclcpp::Service<std_srvs::srv::Trigger>::SharedPtr service_;
};

int main(int argc, char *argv[]) {
  rclcpp::init(argc, argv);

  auto plant_detector_node = std::make_shared<PlantDetectorNode>();
  auto green_detector_node =
      std::make_shared<GreenDetectorNode>(plant_detector_node);

  // Use a MultiThreadedExecutor with 2 threads
  rclcpp::executors::MultiThreadedExecutor executor(rclcpp::ExecutorOptions(),
                                                    2);

  executor.add_node(plant_detector_node);
  executor.add_node(green_detector_node);

  try {
    executor.spin();

  } catch (const std::exception &e) {
    RCLCPP_ERROR(rclcpp::get_logger("rclcpp"), "Exception: %s", e.what());
  }

  rclcpp::shutdown();

  return 0;
}
```
- `PlantDetectorNode` owns and updates the camera image and searches while turning; `GreenDetectorNode` reuses that image for a second check (green areas shown in white in the mask window). Both stay separate nodes: `/detect_plants` and `/green_detector`.
- `sensor_msgs::image_encodings::BGR8` is available through `cv_bridge/cv_bridge.h`.
- The comment "thread-safe copy" is not true without a lock: `clone()` reads `last_image_` while `listener_callback()` may be assigning it in the other group (CPP-V05). Use the `std::mutex` version of [[cpp-exec-callback-groups]].
- HSV range 34–179 / 84–255 / 0–255 comes from the trackbar tuner `green_test.cpp` ([[cpp-recipe-cv-bridge]]).

## Build and run
```cmake
add_executable(green_detector_node src/green_detector_node.cpp)
add_executable(green_test src/green_test.cpp)

ament_target_dependencies(green_test
  rclcpp
  std_msgs
  cv_bridge
  OpenCV
)

ament_target_dependencies(green_detector_node
  rclcpp
  std_msgs
  std_srvs
  sensor_msgs
  cv_bridge
  OpenCV
)

# Install executables
install(TARGETS
  green_detector_node
  green_test
  DESTINATION lib/${PROJECT_NAME}
)
```
`green_detector_node` also uses `geometry_msgs` (found only through `sensor_msgs`, CPP-V20). Launch file `green_detector_node.launch.py` = the usual single-Node launch with `executable='green_detector_node'`. Output: `[plant_detector_node]: 1- PlantDetectorNode READY...` and `[green_detector_node]: 2- GreenDetectorNode READY...`. `ros2 service call /detect_plants std_srvs/srv/Trigger "{}"` turns until the plant is seen (`success=True`; the course prints the message of the earlier program, CPP-V06), then `ros2 service call /green_detector std_srvs/srv/Trigger "{}"` opens the mask windows.

## Pitfalls
- `/green_detector` loops on `cv::waitKey(1)` until `q` is pressed in the window: the call stays at `requester: making request` and one of the two executor threads is blocked meanwhile (CPP-V32).
- A node may be added to only one executor; a second `add_node` of the same node throws.
