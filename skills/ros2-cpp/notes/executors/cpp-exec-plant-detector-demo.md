---
id: cpp-exec-plant-detector-demo
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "Plant detector demo (single-threaded): image subscriber + long detect_plants service, CMake, package.xml, launch, run"
domain: cpp
area: executors
distro: humble
tested: false
audience: dev
summary: "plant_detector.cpp: camera subscription + /detect_plants Trigger service turning the rover, timing wrappers to CSV; CMake, package.xml, launch, service calls."
tags: [plant_detector.cpp, PlantDetectorNode, detect_plants, std_srvs/srv/Trigger, cv_bridge, sensor_msgs/msg/Image, cmd_vel, basics_ros2_multithreading, plant_detector.launch.py, rqt_image_view]
see: ["[[cpp-exec-blocking]]", "[[cpp-exec-groups-demo]]", "[[cpp-callbacks-timing-demo]]", "[[cpp-recipe-cv-bridge]]", "[[cpp-cmake-library]]"]
requires: [ros2-core]
version_notes:
  - "course: <depend>opencv2</depend> in package.xml is not a rosdep key; use libopencv-dev (CPP-V03)"
  - "jazzy: cv_bridge/cv_bridge.h removed, use cv_bridge/cv_bridge.hpp (CPP-V21)"
---
# Plant detector demo (single-threaded)

**TL;DR** The base program of units 5.5–6.6: an image subscription and a service that turns the rover until the camera shows green. All later versions keep this file and change only `main()` (executor) and the group lines ([[cpp-exec-groups-demo]]). On `rclcpp::spin()` the service blocks the images ([[cpp-exec-blocking]]).

## `src/plant_detector.cpp`
```cpp
#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/image.hpp>
#include <cv_bridge/cv_bridge.h>
#include <opencv2/opencv.hpp>
#include <geometry_msgs/msg/twist.hpp>
#include <std_srvs/srv/trigger.hpp>
#include <chrono>
#include <thread>
#include <memory>
#include <string>
#include <fstream>
#include <iomanip>

class PlantDetectorNode : public rclcpp::Node {
public:
    PlantDetectorNode(const std::string& image_topic_name = "/leo/camera/image_raw")
        : Node("plant_detector_node"), image_topic_name_(image_topic_name) {

        // Define the output directory (any writable folder; the course uses a folder of its simulation workspace)
        output_dir_ = "./";

        // Open timing log files with full path
        listener_callback_log_.open(output_dir_ + "listener_callback_timings.csv");
        detect_plants_callback_log_.open(output_dir_ + "detect_plants_callback_timings.csv");

        // Write CSV headers
        listener_callback_log_ << "timestamp,duration_ms,callback_type\n";
        detect_plants_callback_log_ << "timestamp,duration_ms,callback_type\n";

        subscription_ = this->create_subscription<sensor_msgs::msg::Image>(
            image_topic_name_,
            10,
            std::bind(&PlantDetectorNode::listener_callback_wrapper, this, std::placeholders::_1));

        cmd_vel_publisher_ = this->create_publisher<geometry_msgs::msg::Twist>("/cmd_vel", 10);

        // Initialize the plant detection model (simplified for this example)
        // In a real implementation, you would load a trained model here
        model_loaded_ = true;
        RCLCPP_INFO(this->get_logger(), "Plant detection model initialized");
        RCLCPP_INFO(this->get_logger(), "Callback timing instrumentation enabled");
        RCLCPP_INFO(this->get_logger(), "CSV logs will be saved to: %s", output_dir_.c_str());
        RCLCPP_INFO(this->get_logger(), "Files: listener_callback_timings.csv, detect_plants_callback_timings.csv");

        // Create the service for plant detection
        srv_ = this->create_service<std_srvs::srv::Trigger>(
            "detect_plants",
            std::bind(&PlantDetectorNode::detect_plants_callback_wrapper, this,
                     std::placeholders::_1, std::placeholders::_2));
    }

    ~PlantDetectorNode() {
        if (listener_callback_log_.is_open()) listener_callback_log_.close();
        if (detect_plants_callback_log_.is_open()) detect_plants_callback_log_.close();

        // Generate summary
        generate_timing_summary();
    }

private:
    // Wrapper functions that add timing instrumentation
    void listener_callback_wrapper(const sensor_msgs::msg::Image::SharedPtr msg) {
        auto start_time = std::chrono::high_resolution_clock::now();
        uint64_t timestamp = static_cast<uint64_t>(
            std::chrono::duration_cast<std::chrono::microseconds>(
                start_time.time_since_epoch()).count());

        // Call the actual callback
        listener_callback(msg);

        auto end_time = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(
            end_time - start_time).count() / 1000.0; // Convert to milliseconds
        // Log timing data
        listener_callback_log_ << timestamp << "," << duration << ",listener_callback\n";
        listener_callback_log_.flush();

        // Store for analysis
        listener_callback_timings_.push_back({timestamp, duration});
    }

    void detect_plants_callback_wrapper(const std::shared_ptr<std_srvs::srv::Trigger::Request> request,
                                       std::shared_ptr<std_srvs::srv::Trigger::Response> response) {
        auto start_time = std::chrono::high_resolution_clock::now();
        uint64_t timestamp = static_cast<uint64_t>(
            std::chrono::duration_cast<std::chrono::microseconds>(
                start_time.time_since_epoch()).count());

        // Call the actual callback
        detect_plants_callback(request, response);

        auto end_time = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(
            end_time - start_time).count() / 1000.0; // Convert to milliseconds
        // Log timing data
        detect_plants_callback_log_ << timestamp << "," << duration << ",detect_plants_callback\n";
        detect_plants_callback_log_.flush();

        // Store for analysis
        detect_plants_callback_timings_.push_back({timestamp, duration});
    }

    void listener_callback(const sensor_msgs::msg::Image::SharedPtr msg) {
        RCLCPP_INFO(this->get_logger(), "Receiving video frame");
        try {
            last_image_ = cv_bridge::toCvCopy(msg, "bgr8")->image;
        } catch (cv_bridge::Exception& e) {
            RCLCPP_ERROR(this->get_logger(), "cv_bridge exception: %s", e.what());
        }
    }

    void detect_plants_callback(const std::shared_ptr<std_srvs::srv::Trigger::Request> request,
                               std::shared_ptr<std_srvs::srv::Trigger::Response> response) {
        auto start_time = this->get_clock()->now();
        auto duration_10_sec = rclcpp::Duration::from_seconds(10.0);

        bool plant_found = false;

        // Start moving the robot (changed speed to 0.2)
        publish_velocity(0.0, -0.2);
        auto delta_time = this->get_clock()->now() - start_time;

        while (delta_time < duration_10_sec && !plant_found) {
            delta_time = this->get_clock()->now() - start_time;

            if (!last_image_.empty()) {
                RCLCPP_INFO(this->get_logger(), "Processing Image for Plants...");

                // Simplified plant detection algorithm
                // In a real implementation, you would use a trained ML model
                double prediction = detect_plant_in_image(last_image_);

                if (prediction > 0.5) {
                    publish_velocity(0.0, 0.0);
                    RCLCPP_INFO(this->get_logger(), "🌱 Plant Detected! Confidence: %.2f", prediction);
                    plant_found = true;
                } else {
                    RCLCPP_INFO(this->get_logger(), "❌ No Plant Detected. Confidence: %.2f", 1 - prediction);
                }
            }

            std::this_thread::sleep_for(std::chrono::milliseconds(100));
        }

        // Stop the robot
        publish_velocity(0.0, 0.0);
        response->success = plant_found;
        response->message = "Plant detection completed";
    }

    void publish_velocity(double linear, double angular) {
        auto vel_msg = geometry_msgs::msg::Twist();
        vel_msg.linear.x = linear;
        vel_msg.angular.z = angular;
        cmd_vel_publisher_->publish(vel_msg);
    }

    void generate_timing_summary() {
        RCLCPP_INFO(this->get_logger(), "=== CALLBACK TIMING SUMMARY ===");

        if (!listener_callback_timings_.empty()) {
            double avg_listener = 0, min_listener = listener_callback_timings_[0].duration, max_listener = 0;
            for (const auto& timing : listener_callback_timings_) {
                avg_listener += timing.duration;
                min_listener = std::min(min_listener, timing.duration);
                max_listener = std::max(max_listener, timing.duration);
            }
            avg_listener /= listener_callback_timings_.size();

            RCLCPP_INFO(this->get_logger(), "listener_callback: %zu calls, avg=%.2fms, min=%.2fms, max=%.2fms",
                        listener_callback_timings_.size(), avg_listener, min_listener, max_listener);
        }

        if (!detect_plants_callback_timings_.empty()) {
            double avg_detect = 0, min_detect = detect_plants_callback_timings_[0].duration, max_detect = 0;
            for (const auto& timing : detect_plants_callback_timings_) {
                avg_detect += timing.duration;
                min_detect = std::min(min_detect, timing.duration);
                max_detect = std::max(max_detect, timing.duration);
            }
            avg_detect /= detect_plants_callback_timings_.size();

            RCLCPP_INFO(this->get_logger(), "detect_plants_callback: %zu calls, avg=%.2fms, min=%.2fms, max=%.2fms",
                        detect_plants_callback_timings_.size(), avg_detect, min_detect, max_detect);
        }

        RCLCPP_INFO(this->get_logger(), "CSV files saved to: %s", output_dir_.c_str());
        RCLCPP_INFO(this->get_logger(), "Files: listener_callback_timings.csv, detect_plants_callback_timings.csv");
    }

private:
    // Simplified plant detection function
    // In a real implementation, this would use a trained ML model
    double detect_plant_in_image(const cv::Mat& image) {
        // Simple color-based detection for demonstration
        // Look for green colors that might indicate plant life
        cv::Mat hsv;
        cv::cvtColor(image, hsv, cv::COLOR_BGR2HSV);

        // Define range for green color (simplified alien plant detection)
        cv::Scalar lower_green(40, 50, 50);
        cv::Scalar upper_green(80, 255, 255);

        cv::Mat mask;
        cv::inRange(hsv, lower_green, upper_green, mask);

        // Calculate the percentage of green pixels
        int green_pixels = cv::countNonZero(mask);
        int total_pixels = image.rows * image.cols;
        double green_ratio = static_cast<double>(green_pixels) / total_pixels;

        // Return confidence based on green pixel ratio
        // This is a simplified approach - a real system would use trained models
        return green_ratio > 0.01 ? 0.8 : 0.2;
    }

    std::string image_topic_name_;
    std::string output_dir_;
    rclcpp::Subscription<sensor_msgs::msg::Image>::SharedPtr subscription_;
    rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr cmd_vel_publisher_;
    rclcpp::Service<std_srvs::srv::Trigger>::SharedPtr srv_;
    cv::Mat last_image_;
    bool model_loaded_;

    // Timing instrumentation variables
    std::ofstream listener_callback_log_;
    std::ofstream detect_plants_callback_log_;

    struct TimingData {
        uint64_t timestamp;
        double duration;
    };

    std::vector<TimingData> listener_callback_timings_;
    std::vector<TimingData> detect_plants_callback_timings_;
};

int main(int argc, char** argv) {
    rclcpp::init(argc, argv);
    auto plant_detector_node = std::make_shared<PlantDetectorNode>();
    rclcpp::spin(plant_detector_node);
    rclcpp::shutdown();
    return 0;
}
```
`model_loaded_` is set and never read (CPP-V40); the green test is the HSV recipe of [[cpp-recipe-cv-bridge]]. The loop measures 10 s with the node clock (`get_clock()->now()`, `rclcpp::Duration::from_seconds`).

## Launch, CMake, package.xml
```python
import launch
import launch_ros.actions

def generate_launch_description():

    # Nodes
    plant_detector_node = launch_ros.actions.Node(
        package='basics_ros2_multithreading',
        executable='plant_detector',
        arguments=[],
        output='screen',
    )

    return launch.LaunchDescription([
        plant_detector_node
    ])
```
```cmake
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(std_srvs REQUIRED)
find_package(cv_bridge REQUIRED)
find_package(OpenCV REQUIRED)

# Add executable
add_executable(plant_detector src/plant_detector.cpp)

# Link dependencies
ament_target_dependencies(plant_detector
  rclcpp
  sensor_msgs
  geometry_msgs
  std_srvs
  cv_bridge
  OpenCV
)
```
Plus `plant_detector` in `install(TARGETS …)` next to `function`, `callback_function` and (later) `callback_spinonce_function`, and `install(DIRECTORY launch DESTINATION share/${PROJECT_NAME})` ([[cpp-learn-unit5-callbacks]]). `package.xml`: `<depend>` on `rclcpp`, `sensor_msgs`, `geometry_msgs`, `std_srvs`, `cv_bridge` and `libopencv-dev` (the course writes `<depend>opencv2</depend>`, not a rosdep key, CPP-V03).

## Run
```bash
cd ~/ros2_ws && colcon build --packages-select basics_ros2_multithreading && source install/setup.bash
ros2 launch basics_ros2_multithreading plant_detector.launch.py      # "Receiving video frame" continuously
ros2 run teleop_twist_keyboard teleop_twist_keyboard                   # place the rover so it cannot see the plant yet
ros2 run rqt_image_view rqt_image_view /leo/camera/image_raw           # check what the camera sees
source ~/ros2_ws/install/setup.bash && ros2 service call /detect_plants std_srvs/srv/Trigger "{}"
#   response: std_srvs.srv.Trigger_Response(success=False, message='Plant detection completed')
```
The rover turns for 10 s, prints `Processing Image for Plants...` / `❌ No Plant Detected. Confidence: 0.80` every ~100 ms and **no** `Receiving video frame` meanwhile. Turned towards the plant (`j`/`l` in teleop) the same call returns `success=True` with `🌱 Plant Detected! Confidence: 0.80` at once. Stop the launch (Ctrl+C) to write the timing summary and CSV files. The first start can fail in the course's graphical environment: start it again.
