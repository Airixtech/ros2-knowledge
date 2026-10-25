---
id: cpp-learn-unit8-components
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "C++ unit 8: rover_components, RobotStatusService and TextRecognitionService components, exercises 8.1-8.4"
domain: cpp
area: learn
distro: humble
tested: false
audience: students
summary: "Course unit 8 (C++ only): package rover_components, status and text components, CLI loading, mission launch files, compile-time autonomous_mission executable."
tags: [course, unit 8, components, composition, rover_components, RobotStatusService, TextRecognitionService, robot_status_mission.launch.py, comprehensive_mission.launch.py, autonomous_mission, students]
see: ["[[cpp-learn-start-here]]", "[[cpp-component-write]]", "[[cpp-component-demo]]", "[[cpp-component-run]]", "[[core-composition]]"]
requires: [ros2-core]
version_notes: []
---
# C++ unit 8: components

**TL;DR** The only unit without a Python twin: components are an rclcpp feature. Mission: run the rover's services (status report, FOOD/WASTE box identification) in one process to save computing power on Mars (limited links: 256 Kbps, 4–24 min delay to Earth), loading them at run time or building them into one executable for communication blackouts.

## Exercises (pkg `rover_components`)
- **Exercise 8.1**: `ros2 pkg create rover_components --build-type ament_cmake --dependencies rclcpp rclcpp_components composition std_srvs`; `include/rover_components/robot_status_component.hpp`, `src/robot_status_component.cpp` (component `rover_components::RobotStatusService`, node `robot_status_service`, service `/get_robot_status`), `include/rover_components/visibility_control.h`; CMake builds the SHARED library `robot_status_component` → [[cpp-component-write]]. Load it into `/ComponentManager` with `ros2 component load`, test, unload → [[cpp-component-run]].
- **Exercise 8.2**: `launch/robot_status_mission.launch.py` with the container `rover_mission_control` → [[cpp-component-run]].
- **Exercise 8.3**: (a) a `TextRecognitionService` component that identifies FOOD and WASTE boxes from the camera; (b) `launch/comprehensive_mission.launch.py` with both components in one container. Use the unit 8.7 solution (Trigger service `/text_recognition_service`, library `text_recognition_component`); the 8.5 one does not compile (CPP-V12) → [[cpp-component-demo]].
- **Exercise 8.4**: `src/autonomous_mission.cpp` → executable `autonomous_mission` linking both libraries (compile-time composition) → [[cpp-component-run]].

## Mission control commands (recap)
`ros2 component types` · `ros2 component list` · `ros2 run rclcpp_components component_container` · `ros2 component load /ComponentManager <pkg_name> <component_name>` · `ros2 component unload /ComponentManager <component_id>` · `ros2 service call /get_robot_status std_srvs/srv/Trigger "{}"`.

## What to remember
- A component is built into a shared library, has no `main()`, and is registered by name.
- Run-time composition: change the running system (add a component when a box is found); compile-time composition: a fixed executable, simpler to debug, for autonomous phases.
- Components in one process share it; intra-process transport helps topics between them only when enabled.
