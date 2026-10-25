---
id: cpp-component-run
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "Run components: component_container, ros2 component load/list/unload, ComposableNodeContainer, compile-time composition"
domain: cpp
area: components
distro: humble
tested: false
audience: dev
summary: "Run-time composition (component_container + ros2 component CLI, ComposableNodeContainer launch) vs compile-time composition (one executable adding component nodes to an executor)."
tags: [composition, component_container, ros2 component types, ros2 component load, ros2 component list, ros2 component unload, ComposableNodeContainer, ComposableNode, extra_arguments, use_intra_process_comms, SingleThreadedExecutor, autonomous_mission.cpp]
see: ["[[cpp-component-write]]", "[[cpp-component-demo]]", "[[core-composition]]", "[[cpp-exec-multi-node]]", "[[cpp-learn-unit8-components]]"]
requires: [ros2-core]
version_notes:
  - "course: 'Inter-Process Communication: components can communicate efficiently within the same process' — inside one process it is intra-process communication, enabled per node (extra argument use_intra_process_comms → NodeOptions), and it covers publishers/subscriptions only, so it changes nothing for the course's two service components — https://github.com/ros2/rclcpp/blob/humble/rclcpp_components/src/component_manager.cpp (CPP-V17)"
  - "all: ros2 component types prints each package name followed by its components, indented — https://docs.ros.org/en/humble/Tutorials/Intermediate/Composition.html (CPP-V35)"
---
# Run components

**TL;DR** **Run-time composition**: start a container (`ros2 run rclcpp_components component_container`) and load or unload components by name with `ros2 component load/unload`, or describe the container and its components in a launch file (`ComposableNodeContainer`). **Compile-time composition**: an own executable creates the component classes and adds them to one executor. Both put several nodes in one process; run-time is flexible (change the system while it runs), compile-time is fixed when you build it (simpler to debug, nothing to load).

## Run-time composition from the CLI
```bash
cd ~/ros2_ws && colcon build && source ~/ros2_ws/install/setup.bash
ros2 component types                       # rover_components then, indented, rover_components::RobotStatusService
ros2 run rclcpp_components component_container          # terminal 1: the container
ros2 component list                                      # /ComponentManager
ros2 component load /ComponentManager rover_components rover_components::RobotStatusService
#   Loaded component 1 into '/ComponentManager' container node as '/robot_status_service'
ros2 component list                                      # /ComponentManager  /  1  /robot_status_service
ros2 service call /get_robot_status std_srvs/srv/Trigger "{}"
#   response: std_srvs.srv.Trigger_Response(success=True, message='Battery Level: 87.32%, Temperature: 45.67°C, ...')
ros2 component unload /ComponentManager 1
#   Unloaded component 1 from '/ComponentManager' container node
```
- `ros2 component load /ComponentManager <pkg_name> <component_name>`; every loaded component gets its own id (1, 2, …), used by `ros2 component unload /ComponentManager <component_id>`.
- The course shows `ros2 component types` printing only the class name; it prints the package line first (CPP-V35).

## Run-time composition from a launch file
```python
import launch
from launch_ros.actions import ComposableNodeContainer
from launch_ros.descriptions import ComposableNode


def generate_launch_description():
    """Generate launch description for Mars rover status monitoring mission."""
    container = ComposableNodeContainer(
            name='rover_mission_control',
            namespace='',
            package='rclcpp_components',
            executable='component_container',
            composable_node_descriptions=[
                ComposableNode(
                    package='rover_components',
                    plugin='rover_components::RobotStatusService',
                    name='robot_status_service'),
            ],
            output='screen',
    )

    return launch.LaunchDescription([container])
```
`launch/robot_status_mission.launch.py` starts a container named `rover_mission_control` and loads the component into it; install the launch folder (`install(DIRECTORY launch DESTINATION share/${PROJECT_NAME})`) and stop any container started by hand first. `ros2 component list` → `/rover_mission_control` / `1  /robot_status_service`. Ctrl+C on the launch stops the container and its components; no unload needed.

Both components in one container (`launch/comprehensive_mission.launch.py`, unit 8.7 version; the 8.5 version names the container `mars_rover_mission_control`):
```python
import launch
from launch_ros.actions import ComposableNodeContainer
from launch_ros.descriptions import ComposableNode


def generate_launch_description():
    """Generate launch description for comprehensive Mars rover mission.

    Deploys both robot status monitoring and text recognition systems
    for coordinated supply box identification and health monitoring operations.
    """

    container = ComposableNodeContainer(
            name='rover_mission_control',
            namespace='',
            package='rclcpp_components',
            executable='component_container',
            composable_node_descriptions=[
                # Robot status monitoring service
                ComposableNode(
                    package='rover_components',
                    plugin='rover_components::RobotStatusService',
                    name='robot_status_service',
                    extra_arguments=[{'use_intra_process_comms': True}]),

                # Text recognition service for supply box identification
                ComposableNode(
                    package='rover_components',
                    plugin='rover_components::TextRecognitionService',
                    name='text_recognition_service',
                    extra_arguments=[{'use_intra_process_comms': True}]),
            ],
            output='screen',
    )

    return launch.LaunchDescription([container])
```
`ros2 component types | grep rover_components` lists both classes; `ros2 component list` → `1  /robot_status_service`, `2  /text_recognition_service`. `extra_arguments=[{'use_intra_process_comms': True}]` makes the container set `NodeOptions::use_intra_process_comms(true)`; it helps topics between components of the same container, not services, and these two components only offer services (CPP-V17).

## Compile-time composition (`src/autonomous_mission.cpp`)
```cpp
#include <memory>
#include "rover_components/robot_status_component.hpp"
#include "rover_components/text_recognition_component.hpp"
#include "rclcpp/rclcpp.hpp"

int main(int argc, char *argv[]) {
  // Force flush of the stdout buffer.
  setvbuf(stdout, NULL, _IONBF, BUFSIZ);

  rclcpp::init(argc, argv);

  rclcpp::executors::SingleThreadedExecutor exec;
  rclcpp::NodeOptions options;

  // Deploy critical rover systems for autonomous operation during communication blackouts.
  // Robot status monitoring and text recognition components work together for
  // independent supply box identification and health monitoring.
  auto robot_status = std::make_shared<rover_components::RobotStatusService>(options);
  exec.add_node(robot_status);
  auto text_recognition = std::make_shared<rover_components::TextRecognitionService>(options);
  exec.add_node(text_recognition);

  // Mission executor will continue autonomous operations until manual intervention
  // or mission completion. Critical for Mars missions when Earth communication
  // is unavailable. Can only be interrupted by Ctrl-C or mission abort signal.
  exec.spin();

  rclcpp::shutdown();

  return 0;
}
```
```cmake
add_executable(autonomous_mission
  src/autonomous_mission.cpp)
target_link_libraries(autonomous_mission
  robot_status_component
  text_recognition_component)
ament_target_dependencies(autonomous_mission
  "rclcpp")

install(TARGETS
  autonomous_mission
  DESTINATION lib/${PROJECT_NAME})
```
`ros2 run rover_components autonomous_mission` offers `/get_robot_status` and `/text_recognition_service` from one process; `ros2 component list` shows nothing, because no container loaded them. `setvbuf(stdout, NULL, _IONBF, BUFSIZ)` turns off stdout buffering so prints appear at once. The same pattern without components: [[cpp-exec-multi-node]].

## Pitfalls
- `ros2 component types` does not list your class → `rclcpp_components_register_nodes` missing or the workspace not sourced ([[cpp-component-write]]).
- The plugin name in `ComposableNode(plugin=…)` and `ros2 component load` is the fully qualified class name, the package is the one that registered it.
- A container started by hand plus the launch file's container → two containers; stop the first.
