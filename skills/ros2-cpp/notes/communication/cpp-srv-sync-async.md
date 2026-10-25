---
id: cpp-srv-sync-async
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "Waiting for a service response in C++: future, spin_some loop, blocking wait with a spin thread"
domain: cpp
area: communication
distro: humble
tested: false
audience: dev
summary: "Async client loop with rclcpp::spin_some and future_ready(); synchronous-style client blocking on the future while std::thread runs rclcpp::spin; deadlock causes."
tags: [async_send_request, future, spin_some, spin_until_future_complete, std::thread, synchronous call, deadlock, ClientAsync, ClientSync]
see: ["[[cpp-srv-client]]", "[[core-srv-client-async]]", "[[cpp-exec-spin-some]]", "[[cpp-exec-multithreaded]]"]
requires: [ros2-core]
version_notes:
  - "all: spin_some() collects the ready work once and returns, so a loop around it without a pause keeps one CPU core busy — https://github.com/ros2/rclcpp/blob/humble/rclcpp/include/rclcpp/executor.hpp (CPP-V29)"
  - "all: the C++ client API is async only; sync calls deadlock when the thread that waits is the one that must deliver the response — https://docs.ros.org/en/humble/How-To-Guides/Sync-Vs-Async.html (CPP-V30)"
---
# Waiting for a service response in C++

**TL;DR** `async_send_request()` never blocks: it returns a future. You either keep processing events until the future is ready (`spin_until_future_complete`, or your own `spin_some` loop), or you block on the future while **another thread** spins the node. Blocking the only thread that spins is a deadlock: the response can never be delivered. Asynchronous calls are the recommended default.

## Asynchronous: your own loop
```cpp
// Initialize ROS 2
rclcpp::init(argc, argv);
// Create the client node
auto client = std::make_shared<ClientAsync>();
// Send the Service request
client->send_request();

while (rclcpp::ok()) {
    // Process any callbacks that are ready
    rclcpp::spin_some(client);
    // Check whether the future has received a response
    if (client->future_ready()) {
        try {
            // Retrieve the Service response
            auto response = client->get_future_result();
            // Process the response
            // Display a message on the console
            RCLCPP_INFO(client->get_logger(), "Pretty message");
        } catch (const std::exception& e) {
            // Display a message on the console
            RCLCPP_INFO(client->get_logger(), "Service call failed: %s", e.what());
        }
        break;
    }
}

// Shut down ROS 2
rclcpp::shutdown();
```
`ClientAsync`, `send_request()`, `future_ready()` and `get_future_result()` are the course's sketch of a client class that stores the future. `spin_some()` runs the callbacks that are ready and returns control, so the loop can do other work and check the future; `spin()` would never return to the check. Add a short `std::this_thread::sleep_for(10ms)` per turn (as in [[cpp-exec-spin-some]]) or the loop keeps a core busy (CPP-V29).

## Synchronous style: block, but spin elsewhere
```cpp
// Initialize ROS 2
rclcpp::init(argc, argv);

// Create the client node
auto client = std::make_shared<ClientSync>();

// Spin the node in a separate thread so ROS 2 can process
// the Service response while the main thread is blocked
std::thread spin_thread([&client]() {
    rclcpp::spin(client);
});

// Send the request and block the main thread until the response arrives
auto response = client->send_request_sync();

// Process the response
RCLCPP_INFO(client->get_logger(), "Pretty message");

// Shut down ROS 2 and wait for the spinning thread to finish
rclcpp::shutdown();
spin_thread.join();
```
`send_request_sync()` (course sketch) sends with `async_send_request()` and waits on the future (`get()` or `wait_for()`); the response is delivered by the executor in `spin_thread`. rclcpp has no blocking `call()`: "sync" in C++ always means waiting on the future of an async request (CPP-V30). The main drawback: you may not know how long the server takes, and if the response needs the blocked thread, execution stops forever.

## Rules
- Never wait on a future inside a callback of a single-threaded node: the callback holds the only thread the response needs ([[core-srv-client-async]]).
- From inside callbacks, either use `async_send_request(request, callback)` (a response callback) or give the client its own callback group on a MultiThreadedExecutor ([[cpp-exec-multithreaded]]).
- `spin_until_future_complete(node, future, timeout)` bounds the wait from `main()`.
