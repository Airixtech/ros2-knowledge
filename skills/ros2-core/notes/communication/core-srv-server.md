---
id: core-srv-server
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "Service server, CLI & C++ server/client"
domain: core
area: communication
distro: humble
tested: false
audience: dev
summary: "ros2 service CLI, rclpy Trigger server template, custom srv fields, rclcpp server and async client, service rules."
tags: [service, create_service, Trigger, ros2 service call, async_send_request]
see: ["[[core-srv-client-async]]", "[[core-iface-package]]", "[[core-exec-callback-groups]]", "[[core-bp-comm-choice]]"]
requires: []
version_notes: []
---
# Service server, CLI & C++ server/client

**TL;DR** Services are for on-demand requests that finish in under about 1 s. There is one server per name and any number of clients. The callback signature is `(self, request, response)` and it MUST return `response`.

## CLI
```bash
ros2 service list [-t]
ros2 service type /get_robot_status
ros2 service find std_srvs/srv/Trigger
ros2 interface show std_srvs/srv/SetBool          # request --- response
ros2 interface proto std_srvs/srv/Trigger         # request template
ros2 service call /get_robot_status std_srvs/srv/Trigger "{}"
ros2 service call /add_two_ints example_interfaces/srv/AddTwoInts "{a: 5, b: 3}"
ros2 service call /spawn turtlesim/srv/Spawn "{x: 2.0, y: 2.0, theta: 0.0, name: 'turtle2'}"
ros2 service call /reset_world std_srvs/srv/Empty {}
```
Every node also exposes `/<node>/get_parameters`, `set_parameters`, … services.

## Server (Python)
```python
import rclpy
from rclpy.node import Node
from std_srvs.srv import Trigger


class StatusServer(Node):
    def __init__(self):
        super().__init__('status_server')
        self.srv = self.create_service(Trigger, '/get_robot_status', self.on_request)

    def on_request(self, request, response):          # signature: (self, request, response)
        response.success = True
        response.message = 'battery=87%, motors=OK'
        return response                                # MUST return response


def main(args=None):
    rclpy.init(args=args)
    node = StatusServer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
```
Custom srv: `from custom_interfaces.srv import TextRecognition` → read `request.label`, then fill `response.success`, `response.start_x`, … ([[core-iface-package]]).
A server callback that needs fresh sensor data while it runs must not share a MutuallyExclusive group with that sensor's subscription ([[core-exec-callback-groups]]).

## C++ (server + async client)
Full C++ servers, clients, custom services and waiting patterns: the ros2-cpp skill.
```cpp
// server
srv_ = create_service<std_srvs::srv::Trigger>("get_robot_status",
  [](const std::shared_ptr<std_srvs::srv::Trigger::Request>,
     std::shared_ptr<std_srvs::srv::Trigger::Response> res) { res->success = true; res->message = "ok"; });
// client
auto cli = create_client<std_srvs::srv::Trigger>("get_robot_status");
cli->async_send_request(std::make_shared<std_srvs::srv::Trigger::Request>(),
  [this](rclcpp::Client<std_srvs::srv::Trigger>::SharedFuture f) {
    RCLCPP_INFO(get_logger(), "%s", f.get()->message.c_str()); });
```

## Rules
- Always `wait_for_service()` / `service_is_ready()` before calling. Client patterns: [[core-srv-client-async]].
- Keep service callbacks short. Over 1 s, or when you need progress or cancel → use an action ([[core-action-server]]). Choosing a pattern: [[core-bp-comm-choice]].
