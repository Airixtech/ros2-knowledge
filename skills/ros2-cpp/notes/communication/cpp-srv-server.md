---
id: cpp-srv-server
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "rclcpp service server: create_service<Trigger>, callback(request, response), status and text-recognition servers"
domain: cpp
area: communication
distro: humble
tested: false
audience: dev
summary: "create_service<std_srvs::srv::Trigger>(name, std::bind(..., _1, _2)); callback fills response->success/message; on-demand image processing; ros2 service CLI."
tags: [create_service, rclcpp::Service, std_srvs/srv/Trigger, SetBool, request, response, std::placeholders::_2, ros2 service call, get_robot_status, text_recognition_service]
see: ["[[core-srv-server]]", "[[cpp-srv-client]]", "[[cpp-srv-custom]]", "[[cpp-recipe-cv-bridge]]", "[[core-bp-comm-choice]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: create_service(name, cb, rclcpp::QoS = ServicesQoS(), group) added and the rmw_qos_profile_t overload deprecated; kilted/lyrical: the rmw_qos_profile_t overload removed (matters only when a QoS or group argument is passed) — https://github.com/ros2/rclcpp/blob/jazzy/rclcpp/include/rclcpp/node.hpp (CPP-V23)"
---
# rclcpp service server

**TL;DR** `create_service<SrvT>(name, callback)` in the constructor, stored in a `rclcpp::Service<SrvT>::SharedPtr` member. The callback receives the request and a response to fill; when it returns, rclcpp sends the response. A service suits data that is needed only on demand (status reports, image processing when asked), not continuously.

## `src/mars_rover_status_s_server.cpp`
```cpp
#include <rclcpp/rclcpp.hpp>
#include <std_srvs/srv/trigger.hpp>
#include <random>
#include <sstream>
#include <iomanip>

class RobotStatusService : public rclcpp::Node
{
public:
    RobotStatusService() : Node("robot_status_service")
    {
        // Initialize random number generator
        rng_.seed(std::random_device{}());

        // Create a service that will handle status queries
        std::string name_service = "/get_robot_status";
        service_ = this->create_service<std_srvs::srv::Trigger>(
            name_service,
            std::bind(&RobotStatusService::get_status_callback, this,
                      std::placeholders::_1, std::placeholders::_2));

        RCLCPP_INFO(this->get_logger(), "%s Service Server Ready...", name_service.c_str());
    }

private:
    void get_status_callback(
        const std::shared_ptr<std_srvs::srv::Trigger::Request> request,
        std::shared_ptr<std_srvs::srv::Trigger::Response> response){
        (void)request; // Suppress unused parameter warning
        // Simulated data
        std::uniform_real_distribution<double> battery_dist(20.0, 100.0);
        std::uniform_real_distribution<double> temp_dist(25.0, 80.0);
        std::uniform_int_distribution<int> bool_dist(0, 1);

        double battery_level = battery_dist(rng_);
        double temperature = temp_dist(rng_);
        bool camera_status = bool_dist(rng_);
        std::vector<bool> motor_statuses;

        for (int i = 0; i < 4; ++i) {
            motor_statuses.push_back(bool_dist(rng_));
        }

        // Construct response message
        response->success = true;

        std::stringstream ss;
        ss << std::fixed << std::setprecision(2);
        ss << "Battery Level: " << battery_level << "%, "
           << "Temperature: " << temperature << "°C, "
           << "Camera: " << (camera_status ? "Operational" : "Faulty") << ", "
           << "Motor 1: " << (motor_statuses[0] ? "Operational" : "Faulty") << ", "
           << "Motor 2: " << (motor_statuses[1] ? "Operational" : "Faulty") << ", "
           << "Motor 3: " << (motor_statuses[2] ? "Operational" : "Faulty") << ", "
           << "Motor 4: " << (motor_statuses[3] ? "Operational" : "Faulty") << ", ";

        response->message = ss.str();
    }

    rclcpp::Service<std_srvs::srv::Trigger>::SharedPtr service_;
    std::mt19937 rng_;
};

int main(int argc, char** argv){
    rclcpp::init(argc, argv);
    auto node = std::make_shared<RobotStatusService>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}
```
- `create_service<std_srvs::srv::Trigger>(name_service, …)`: interface type, service name `/get_robot_status`, callback. `_1` and `_2` stand for the request and the response that rclcpp passes.
- `Trigger` has an empty request, so `(void)request;` silences the unused-parameter warning. The response has `bool success` and `string message`.
- `std::fixed << std::setprecision(2)` prints two decimals; the values are random until real data replaces them.
- CMake: `find_package(std_srvs REQUIRED)`, `add_executable(mars_rover_s_server_executable src/mars_rover_status_s_server.cpp)`, `ament_target_dependencies(mars_rover_s_server_executable rclcpp std_srvs)`, `install(TARGETS …)`.

## CLI
```bash
ros2 run mars_rover_tasks mars_rover_s_server_executable   # /get_robot_status Service Server Ready...
ros2 service list | grep /get_robot_status
ros2 service type /get_robot_status                         # std_srvs/srv/Trigger
ros2 interface show std_srvs/srv/Trigger                    # request --- response
ros2 interface show std_srvs/srv/SetBool                    # bool data --- bool success, string message
ros2 interface proto std_srvs/srv/Trigger                   # "{}": the request you type as a client
ros2 service call /get_robot_status std_srvs/srv/Trigger "{}"
#   response: std_srvs.srv.Trigger_Response(success=True, message='Battery Level: 97.49%, Temperature: 51.02°C, Camera: Operational, ...')
```
A service interface has two parts separated by `---`: REQUEST arguments, then RESPONSE arguments; an empty request is common. `ros2 service list` also shows the six parameter services of every node ([[core-srv-server]]).

## Turning a topic node into a service (exercise 4.1)
`text_recog_s_server.cpp` (node `text_recognition_service`, service `/text_recognition_service`, `Trigger`) keeps subscribing to `/leo/camera/image_raw` but only stores the last image; the detection runs in the service callback, only when a client asks. The detection functions are those of `text_recog_node.cpp`, except that `detectLabel()` returns the label ([[cpp-recipe-cv-bridge]]).
```cpp
  void image_callback(const sensor_msgs::msg::Image::SharedPtr msg) {
    cv_bridge::CvImagePtr cv_ptr;

    try {
      cv_ptr = cv_bridge::toCvCopy(msg, sensor_msgs::image_encodings::BGR8);
    } catch (const cv_bridge::Exception &e) {
      RCLCPP_ERROR(this->get_logger(), "cv_bridge exception: %s", e.what());
      return;
    }

    /*
     * Only store the latest camera image.
     *
     * No text recognition is performed here.
     */
    latest_image_ = cv_ptr->image.clone();
    image_received_ = true;
  }

  void handle_text_recognition_request(
      const std::shared_ptr<std_srvs::srv::Trigger::Request> request,
      std::shared_ptr<std_srvs::srv::Trigger::Response> response) {

    (void)request;

    /*
     * Make sure that at least one camera image
     * has been received.
     */
    if (!image_received_) {
      response->success = false;
      response->message = "No camera image received";

      RCLCPP_WARN(this->get_logger(),
                  "Service called before receiving a camera image");

      return;
    }

    /*
     * Run the detection only when the
     * service is requested.
     */
    std::string detected_label = detectLabel(latest_image_);

    if (detected_label == "FOOD" || detected_label == "WASTE") {

      response->success = true;
      response->message = detected_label;

    } else {

      response->success = false;
      response->message = "No text detected";
    }

    RCLCPP_INFO(this->get_logger(), "Service called. Result: %s",
                response->message.c_str());
  }
```
Constructor: `create_subscription<sensor_msgs::msg::Image>("/leo/camera/image_raw", 1, …)` and `create_service<std_srvs::srv::Trigger>("/text_recognition_service", std::bind(&TextRecognitionService::handle_text_recognition_request, this, std::placeholders::_1, std::placeholders::_2))`, then `RCLCPP_INFO(this->get_logger(), "Text Recognition Service Server initialized");`; members `cv::Mat latest_image_;` and `bool image_received_ = false;`. CMake: executable `text_recog_s_server_executable` with `rclcpp sensor_msgs cv_bridge OpenCV std_srvs`. `ros2 service call /text_recognition_service std_srvs/srv/Trigger "{}"` → `success=True, message='FOOD'` near the FOOD box.

## Pitfalls
- A long service callback blocks every other callback of the node on the default executor ([[cpp-exec-blocking]]).
- An early `return` from the callback still sends the response as filled so far: set `success` and `message` before returning.
- On Jazzy+, passing a QoS or a callback group: `create_service<T>(name, cb, rclcpp::ServicesQoS(), group)` (CPP-V23, [[cpp-exec-callback-groups]]).
