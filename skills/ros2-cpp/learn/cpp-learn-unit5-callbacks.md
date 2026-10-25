---
id: cpp-learn-unit5-callbacks
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "C++ unit 5: package basics_ros2_multithreading, functions, callbacks, plant detector, spin_some"
domain: cpp
area: learn
distro: humble
tested: false
audience: students
summary: "Course unit 5 in C++: pkg basics_ros2_multithreading files and CMakeLists, function.cpp, callback_function.cpp, plant_detector.cpp, callback_spinonce_function.cpp."
tags: [course, unit 5, callbacks, basics_ros2_multithreading, function.cpp, callback_function.cpp, plant_detector.cpp, callback_spinonce_function.cpp, students]
see: ["[[cpp-learn-start-here]]", "[[cpp-callbacks-functions]]", "[[cpp-callbacks-timing-demo]]", "[[cpp-exec-plant-detector-demo]]", "[[cpp-exec-spin-some]]", "[[core-learn-unit5-callbacks]]"]
requires: [ros2-core]
version_notes: []
---
# C++ unit 5: callbacks

**TL;DR** Unit 5 in C++ (the Python twin: [[core-learn-unit5-callbacks]]): from functions to callbacks, timing them, a long service callback that blocks a camera callback, and `spin_some()`. Mission: detect alien plants while the rover explores. Lesson: by default a node runs one callback at a time (timers, topics, services, actions), which is why unit 6 adds multithreading.

## Package and files (unit 5.2)
```bash
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_cmake basics_ros2_multithreading --dependencies rclcpp
mkdir basics_ros2_multithreading/src
touch basics_ros2_multithreading/src/function.cpp
touch basics_ros2_multithreading/src/callback_function.cpp
touch basics_ros2_multithreading/src/callback_spinonce_function.cpp
touch basics_ros2_multithreading/src/plant_detector.cpp
mkdir basics_ros2_multithreading/launch
touch basics_ros2_multithreading/launch/callback_function.launch.py
touch basics_ros2_multithreading/launch/plant_detector.launch.py
```
(The course also clones its extra files repository again, if not done in earlier units.) Start the CMakeLists with only `function` active and the other executables commented out, so the package builds while the files are empty; uncomment each one when its file has code:
```cmake
cmake_minimum_required(VERSION 3.8)
project(basics_ros2_multithreading)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

# Create executables
add_executable(function src/function.cpp)
ament_target_dependencies(function rclcpp)

#add_executable(callback_function src/callback_function.cpp)
#ament_target_dependencies(callback_function rclcpp)

#add_executable(callback_spinonce_function src/callback_spinonce_function.cpp)
#ament_target_dependencies(callback_spinonce_function rclcpp)

#add_executable(plant_detector src/plant_detector.cpp)
#ament_target_dependencies(plant_detector rclcpp)

# Install executables
install(TARGETS
  function
  #callback_function
  #callback_spinonce_function
  #plant_detector
  DESTINATION lib/${PROJECT_NAME}
)

# Install launch files
install(DIRECTORY
  launch
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
```
The plant detector later needs more dependencies in `find_package` and `ament_target_dependencies` ([[cpp-exec-plant-detector-demo]]).

## Steps
- **5.3** `function.cpp` → `ros2 run basics_ros2_multithreading function` → [[cpp-callbacks-functions]].
- **5.4** `callback_function.cpp` + `callback_function.launch.py`: two timers, timing CSV, then `sleep_timer_counter_(1.0)` and `sleep_time_main_task_(1.5)` → [[cpp-callbacks-timing-demo]].
- **5.5** `plant_detector.cpp` + `plant_detector.launch.py`: `/detect_plants` service vs the camera callback → [[cpp-exec-plant-detector-demo]], [[cpp-exec-blocking]].
- **5.6** `callback_spinonce_function.cpp`: a `spin_some()` loop that ends itself → [[cpp-exec-spin-some]].

The course plots the CSV timing files with visualization scripts of its own environment (added to `PATH` in `~/.bashrc`); with your own files, any CSV plotting tool works (columns `timestamp,duration_ms,callback_type`).
