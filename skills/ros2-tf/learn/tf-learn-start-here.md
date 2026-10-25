---
id: tf-learn-start-here
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "TF course map: units 1-4, simulations, robots and frame names, package my_tf_ros2_course_pkg"
domain: tf
area: learn
distro: jazzy
tested: false
audience: students
order: 1
summary: "TF course map: units 1–4 (frames, tools, broadcasters and listeners, robot_state_publisher), simulations, robots, my_tf_ros2_course_pkg, reading order."
tags: [course, TF course, units, my_tf_ros2_course_pkg, Cam_bot, turtle, unicycle, turtle_tf_3d_ros2, unicycle_robot_pkg, reading order, humble]
see: ["[[tf-learn-unit1-frames]]", "[[tf-learn-unit2-tools]]", "[[tf-learn-unit3-broadcast]]", "[[tf-learn-unit4-rsp]]", "[[tf-frames-tree]]", "[[tf-humble-to-jazzy]]", "[[core-pkg-ament-cmake]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: the course runs on Jazzy with Gazebo Sim (Harmonic): bridge types gz.msgs.*, Topic type hash in its outputs; on Humble read tf-humble-to-jazzy (TF-V28)"
  - "course: the package is created with tf2_ros, geometry_msgs and nav_msgs only; its scripts also need rclpy, tf_transformations and ros_gz_interfaces (TF-V05)"
---
# TF course map: units 1–4

**TL;DR** The course explains TF (the transform library) in ROS 2: what coordinate frames are, the tools to inspect them, how to broadcast and listen to transforms, and what robot_state_publisher does. Each unit has a simulation started by the course platform, and you write one package, `my_tf_ros2_course_pkg`, along the way.

## Units
| Unit | Topic | Notes |
|---|---|---|
| 1 | coordinate frames, conventions, a first static frame, TF and RobotModel in RViz2 | [[tf-learn-unit1-frames]], [[tf-frames-tree]], [[tf-rviz]] |
| 2 | TF tools: `view_frames`, `rqt_tf_tree`, `tf2_echo`, RViz2 | [[tf-learn-unit2-tools]], [[tf-view-frames]], [[tf-echo]] |
| 3 | broadcasting and listening: odometry → TF, `tf2_monitor` and timestamps, static transforms, a listener that moves a model | [[tf-learn-unit3-broadcast]], [[tf-odom-broadcaster]], [[tf-monitor-stamps]], [[tf-static-publisher]], [[tf-static-python]] |
| 4 | robot_state_publisher: spawning a robot with and without it | [[tf-learn-unit4-rsp]] |

After units 2, 3 and 4 a course project (three parts, on a robot environment given in the course) applies what the unit taught.

## What you learn
What coordinate frames are and why they are required; the role of transforms; the TF2 library and how it manages frames and transforms; the ROS 2 tools to introspect and interact with TF2; how to write a static transform broadcaster; how to broadcast dynamic transforms; what the Robot State Publisher node is and its role.

## Simulations and robots
- Unit 1: a robot with a movable head; its odometry frame is `deepmind_robot1_odom`, and `deepmind_bot_trajectory_sender` moves the head.
- Units 2–3: **Cam_bot**, a robot with six degrees of freedom (moves and rotates on all three axes) and a camera, which can follow a frame you choose; and the **turtle**, a 3D version of turtlesim that drives like any differential drive robot. Unit 3 starts the same robots without some of their transforms.
- Unit 4: an empty sand world and the **unicycle** robot (`unicycle_robot_pkg`, `urdf/unicycle.urdf`).
- Ready-made programs of the course workspace: `turtle_tf_3d_ros2` (`cam_bot_teleop.py`, `cam_bot_follower.py`), `deepmind_bot_trajectory_sender` (`move_head.py`). Source that workspace before RViz so the meshes are found.

## Your package
`~/ros2_ws/src/my_tf_ros2_course_pkg`: ament_cmake, Python scripts in `scripts/`, launch files in `launch/` (the pattern: [[core-pkg-ament-cmake]]). After each change: `cd ~/ros2_ws && colcon build && source install/setup.bash`.
```bash
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_cmake my_tf_ros2_course_pkg --dependencies tf2_ros geometry_msgs nav_msgs
mkdir my_tf_ros2_course_pkg/scripts
touch my_tf_ros2_course_pkg/scripts/cam_bot_odom_to_tf_pub.py
chmod +x my_tf_ros2_course_pkg/scripts/cam_bot_odom_to_tf_pub.py
```
Add to `package.xml` what the scripts import (the course omits them; `rosdep install` needs them):
```xml
<exec_depend>rclpy</exec_depend>
<exec_depend>tf_transformations</exec_depend>   <!-- static broadcaster, tf-static-python -->
<exec_depend>ros_gz_interfaces</exec_depend>    <!-- follower of the TF course, unit 3 -->
```
`CMakeLists.txt` at the end of the course unit (each section adds its file to `install(PROGRAMS …)`; the `launch` folder line comes with the first launch file):
```cmake
cmake_minimum_required(VERSION 3.8)
project(my_tf_ros2_course_pkg)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(nav_msgs REQUIRED)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

install(
  DIRECTORY
    launch
  DESTINATION
    share/${PROJECT_NAME}/
)

install(PROGRAMS
  scripts/cam_bot_odom_to_tf_pub.py
  scripts/cam_bot_odom_to_tf_pub_late_tf_fixed.py
  scripts/static_broadcaster_front_turtle_frame.py
  scripts/move_generic_model.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
```


## Before and after
Prerequisites: ROS 2 basics (skill ros2-core) and robot models (URDF, skill ros2-urdf). Spawning and bridging in Gazebo Sim: skill ros2-gazebo. On Humble, the commands are the same; the differences are listed in [[tf-humble-to-jazzy]].
