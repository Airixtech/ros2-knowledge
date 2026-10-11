---
id: core-learn-unit5-callbacks
type: reference
owner: equipo-ros2
updated: 2026-10-09
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "Unit 5 exercises: callbacks, tracing, blocked detector"
domain: core
area: learn
distro: humble
tested: false
audience: students
summary: "Course Unit 5 (pkg basics_ros2_multithreading, ament_cmake + Python scripts): timers, lost callbacks, tracing, blocked plant detector, spin_once exit."
tags: [course, unit 5, callbacks, tracing, ament_cmake scripts, students]
see: ["[[core-learn-concepts-callbacks]]", "[[core-exec-model]]", "[[core-exec-spin]]", "[[core-debug-tools]]"]
requires: []
version_notes:
  - "humble: ros2_tracing needs instrumented tracetools (not in Humble binaries); check the course image with 'ros2 run tracetools status' [verify] — https://github.com/ros2/ros2_tracing/blob/humble/README.md (V80)"
---
# Unit 5 exercises: callbacks, tracing, blocked detector

**TL;DR** See with your own eyes that one thread runs one callback at a time: lost timer calls and an image that freezes while a service runs. Reference: [[core-exec-model]], [[core-exec-spin]], [[core-pkg-ament-cmake]].

## Unit 5 — Callbacks (pkg `basics_ros2_multithreading`, ament_cmake with Python `scripts/`)
Setup: `ros2 pkg create --build-type ament_cmake basics_ros2_multithreading --dependencies rclpy`, with `scripts/` + `launch/`. CMake: `install(DIRECTORY scripts launch DESTINATION share/${PROJECT_NAME})` + `install(PROGRAMS scripts/<file>.py ... DESTINATION lib/${PROJECT_NAME})` ([[core-pkg-ament-cmake]]). Source `/home/simulations/ros2_sims_ws/install/setup.bash` before building.
- `function.py`: sequential `robot_message()` + `time.sleep` → then a `RobotStatus(Node)` class with `timer_counter()` (elapsed time) + `main_task()`.
- `callback_function.py`: two timers — `timer_counter` every 0.1 s, `main_task` every 1.0 s (pops "Booting Up/Ready/ShuttingDown"). Experiment: set `sleep_timer_counter=1.0`, `sleep_time_main_task=1.5` → most timer calls are lost (one callback at a time).
- Tracing: launch with `Trace(session_name='callback_function')` (tracetools_launch); `rm -rf ~/.ros/tracing/callback_function/`; visualize with `ros2 run ros2_callback_visualiser analise_trace_calback_function.py` (course tool). On a plain Humble install, tracing needs extra setup ([[core-debug-tools]]). On the course platform, check with `ros2 run tracetools status` [verify].
- Hands-on `plant_detector.py`: a camera sub stores `last_image`; Trigger service `detect_plants` rotates (`angular.z=-0.2`) for up to 10 s, running a ResNet18 alien-plant model (`best_alien_plant_detector_model.pth`, input 150×150, sigmoid > 0.5). Problem: while the service runs, the image callback never fires → frozen image → the plant is never detected unless it was already visible.
- `callback_spinonce_function.py`: replace `spin` with `while rclpy.ok(): rclpy.spin_once(node)` + `shutdown_flag` to exit cleanly ([[core-exec-spin]]).
- Project Part II: course project (link given in the course).
