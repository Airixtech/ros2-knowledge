---
id: core-composition
type: reference
owner: equipo-ros2
updated: 2026-10-09
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "Composition, intra-process & component containers"
domain: core
area: architecture
distro: humble
tested: false
audience: dev
summary: "Write rclcpp components, register them in CMake, load them in a container from launch; composition vs processes; zero-copy intra-process."
tags: [composition, components, intra-process, zero-copy, ComposableNodeContainer, rclcpp_components]
see: ["[[core-arch-layers]]", "[[core-perception-basics]]", "[[core-exec-spin]]", "[[core-pkg-ament-cmake]]"]
requires: []
version_notes:
  - "lyrical: ament_target_dependencies removed; use target_link_libraries(my_comp PUBLIC rclcpp::rclcpp rclcpp_components::component) — https://docs.ros.org/en/rolling/Releases/Release-Kilted-Kaiju.html (V09)"
  - "lyrical: rosidl::Buffer zero-copy publishing (new) — https://docs.ros.org/en/rolling/Releases/Release-Lyrical-Luth.html (V76)"
---
# Composition, intra-process & component containers

**TL;DR** Compose latency-critical C++ pipelines (camera → rectify → detector) into one `component_container_mt` with `use_intra_process_comms`. Keep independent or fault-prone parts as separate processes. Intra-process zero-copy is rclcpp-only.

## Composition (C++ components)
```cpp
#include "rclcpp_components/register_node_macro.hpp"
namespace my_pkg {
class MyComp : public rclcpp::Node {
public:
  explicit MyComp(const rclcpp::NodeOptions & options) : Node("my_comp", options) {}
};
}  // namespace my_pkg
RCLCPP_COMPONENTS_REGISTER_NODE(my_pkg::MyComp)
```
```cmake
add_library(my_comp SHARED src/my_comp.cpp)
ament_target_dependencies(my_comp rclcpp rclcpp_components)
rclcpp_components_register_nodes(my_comp "my_pkg::MyComp")
install(TARGETS my_comp ARCHIVE DESTINATION lib LIBRARY DESTINATION lib RUNTIME DESTINATION bin)
```
[changed in Lyrical: `ament_target_dependencies` removed → `target_link_libraries(my_comp PUBLIC rclcpp::rclcpp rclcpp_components::component)` [verify]]
```python
from launch_ros.actions import ComposableNodeContainer
from launch_ros.descriptions import ComposableNode
ComposableNodeContainer(
    name='perception_container', namespace='', package='rclcpp_components',
    executable='component_container_mt',          # or component_container / component_container_isolated
    composable_node_descriptions=[
        ComposableNode(package='my_pkg', plugin='my_pkg::MyComp', name='comp',
                       extra_arguments=[{'use_intra_process_comms': True}]),
    ])
```
CLI: `ros2 component list` · `ros2 component load /container <pkg> <ns::Class> -e use_intra_process_comms:=true`.

## Composition vs processes
| | Separate processes | Composition (one container) |
|---|---|---|
| Fault isolation | yes | no (one crash kills all) |
| Latency | DDS serialization | <10 µs zero-copy |
| Debugging | simple | multithreaded |
| Memory | higher | lower |
Compose per latency domain (perception→planning→control). Keep the UI, logger, rosbag and watchdog separate.

## Intra-process (zero-copy, rclcpp only in Humble)
Requirements: same process/container · `NodeOptions().use_intra_process_comms(true)` · publish `std::unique_ptr<Msg>` with `std::move` · KEEP_LAST + VOLATILE.
```cpp
auto node = std::make_shared<MyNode>(rclcpp::NodeOptions().use_intra_process_comms(true));
auto msg = std::make_unique<sensor_msgs::msg::Image>();
pub_->publish(std::move(msg));
```
Cross-process zero-copy needs loaned messages + shared memory (Cyclone+iceoryx or FastDDS SHM). [≥Lyrical: `rosidl::Buffer` lets you publish without copying data]
