---
id: cpp-srv-client
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "rclcpp service client: create_client, wait_for_service, async_send_request + spin_until_future_complete"
domain: cpp
area: communication
distro: humble
tested: false
audience: dev
summary: "create_client<Trigger>, wait_for_service(1s) loop with rclcpp::ok(), async_send_request, spin_until_future_complete from main, FutureReturnCode::SUCCESS, future.get()."
tags: [create_client, rclcpp::Client, wait_for_service, async_send_request, spin_until_future_complete, FutureReturnCode, future, chrono_literals, mars_rover_status_s_client.cpp, text_recog_s_client.cpp]
see: ["[[cpp-srv-server]]", "[[cpp-srv-sync-async]]", "[[core-srv-client-async]]", "[[core-exec-spin]]", "[[cpp-srv-custom]]"]
requires: [ros2-core]
version_notes:
  - "all: the C++ service client API is asynchronous only (async_send_request); a blocking wait is built on its future — https://docs.ros.org/en/humble/How-To-Guides/Sync-Vs-Async.html (CPP-V30)"
---
# rclcpp service client

**TL;DR** `create_client<SrvT>(name)`, wait with `wait_for_service(1s)` (leave if `!rclcpp::ok()`), send with `async_send_request(request)` and, from `main()` (not from a callback), wait with `rclcpp::spin_until_future_complete(node, future) == rclcpp::FutureReturnCode::SUCCESS` before `future.get()`.

## `src/mars_rover_status_s_client.cpp`
```cpp
#include <rclcpp/rclcpp.hpp>
#include <std_srvs/srv/trigger.hpp>
#include <chrono>
#include <memory>

using namespace std::chrono_literals;

class RobotStatusClient : public rclcpp::Node
{
public:
    RobotStatusClient() : Node("robot_status_client")
    {
        // Create the Service Client object
        // This defines the name ('/get_robot_status') and type (Trigger) of the Service Server to connect to.
        std::string name_service = "/get_robot_status";
        client_ = this->create_client<std_srvs::srv::Trigger>(name_service);

        // Wait for the service to be available (checks every second)
        while (!client_->wait_for_service(1s)) {
            if (!rclcpp::ok()) {
                RCLCPP_ERROR(this->get_logger(), "Interrupted while waiting for the service. Exiting.");
                return;
            }
            RCLCPP_INFO(this->get_logger(), "Service %s not available, waiting again...", name_service.c_str());
        }
    }

    void send_request(){
        // Create an empty Trigger request
        auto request = std::make_shared<std_srvs::srv::Trigger::Request>();

        // Send the request asynchronously
        auto result_future = client_->async_send_request(request);

        // Wait for the result
        if (rclcpp::spin_until_future_complete(this->get_node_base_interface(), result_future) ==
            rclcpp::FutureReturnCode::SUCCESS)
        {
            auto response = result_future.get();
            // Log the service response
            RCLCPP_INFO(this->get_logger(), "Success: %s", response->success ? "true" : "false");
            RCLCPP_INFO(this->get_logger(), "Status Report: %s", response->message.c_str());
        }
        else
        {
            RCLCPP_ERROR(this->get_logger(), "Failed to call service");
        }
    }

private:
    rclcpp::Client<std_srvs::srv::Trigger>::SharedPtr client_;
};

int main(int argc, char** argv){
    // Initialize the ROS communication
    rclcpp::init(argc, argv);

    // Declare the node constructor
    auto client = std::make_shared<RobotStatusClient>();

    // Run the send_request() method
    client->send_request();

    // Shutdown the ROS communication
    rclcpp::shutdown();
    return 0;
}
```
- `create_client<std_srvs::srv::Trigger>("/get_robot_status")`: name and type of the server to call.
- `wait_for_service(1s)` returns false after each second without the server; `1s` comes from `std::chrono_literals`.
- `std::make_shared<std_srvs::srv::Trigger::Request>()`: an empty request for `Trigger`.
- `async_send_request()` returns at once with a **future**; the response is not there yet. `spin_until_future_complete()` processes ROS events until it is, then `result_future.get()` gives the response (`response->success`, `response->message`).
- The program sends one request and exits: no `rclcpp::spin`.

CMake: `add_executable(mars_rover_status_s_client_executable src/mars_rover_status_s_client.cpp)` + `ament_target_dependencies(mars_rover_status_s_client_executable rclcpp std_srvs)` + `install(TARGETS …)`. Run the server first; the client prints `Success: true` and `Status Report: Battery Level: 52.95%, Temperature: 48.87°C, Camera: Faulty, ...`.

## Exercise 4.2: client of `/text_recognition_service`
`text_recog_s_client.cpp` (node `text_recognition_client`, executable `text_recog_s_client_executable`) is the same program with `name_service = "/text_recognition_service"` and one log line:
```cpp
RCLCPP_INFO(this->get_logger(), "Success: %s, Detected text: %s",
           response->success ? "true" : "false", response->message.c_str());
```
Output near the FOOD box: `[INFO] [1725957959.220329240] [text_recognition_client]: Success: true, Detected text: FOOD`.

## Pitfalls
- `spin_until_future_complete(node, …)` inside a callback of a node that is already spinning → throws or deadlocks; from a callback, use the callback form of `async_send_request` or another thread ([[cpp-srv-sync-async]], [[core-srv-client-async]]).
- After the "Interrupted" `return` in the constructor, `main()` still calls `send_request()`: check `rclcpp::ok()` before sending.
- The future returned by `async_send_request` must be kept until the response is read.
