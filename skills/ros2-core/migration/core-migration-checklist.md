---
id: core-migration-checklist
type: reference
owner: equipo-ros2
updated: 2026-10-09
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "Checklist to migrate a Humble project (to Jazzy / Lyrical)"
domain: core
area: migration
distro: humble
tested: false
audience: dev
summary: "Step-by-step migration of a Humble workspace: grep for known breakages, fix build/code/launch/CLI/Nav2/control/Gazebo, then test in Docker."
tags: [migration, checklist, grep, jazzy, lyrical, docker]
see: ["[[core-humble-to-jazzy]]", "[[core-jazzy-to-lyrical]]", "[[core-testing-ci-docker]]"]
requires: []
version_notes: []
---
# Checklist to migrate a Humble project (to Jazzy / Lyrical)

**TL;DR** First fix whatever already works on Humble *and* on the target (`warning()`, `.hpp`, `ConstSharedPtr`, `extras_require`, flags-style static TF). Then fix the target-only items. Build and test in `ros:<distro>` Docker. Details per item: [[core-humble-to-jazzy]], [[core-jazzy-to-lyrical]].

## 1. Find known breakages
```bash
cd ~/ros2_ws/src
grep -rn "get_logger().warn(\|\.warn(" --include=*.py .            # -> .warning()  (removed in Lyrical)
grep -rn "tests_require\|script-dir\|install-scripts" --include=setup.* .   # -> extras_require / underscores
grep -rn "ament_target_dependencies" --include=CMakeLists.txt .   # -> target_link_libraries (removed in Lyrical)
grep -rn "tf2_ros/.*\.h\"\|LinearMath/.*\.h\"\|tf2_geometry_msgs.h" --include=*.?pp .   # -> .hpp
grep -rn "StaticSingleThreadedExecutor\|qos_event.hpp" --include=*.?pp .
grep -rn "PushRosNamespace\|LaunchConfigurationEquals" --include=*.py .
grep -rn "action_tutorials_interfaces\|partial_sequence" .          # -> example_interfaces (Kilted+)
grep -rn "ROS_LOCALHOST_ONLY\|bag record.* -x \|static_transform_publisher [0-9-]" ~/.bashrc .
grep -rn "switch_controllers.*--st\(art\|op\)\|robot_description" --include=*.py --include=*.yaml .
grep -rn "ign gazebo\|ignition.msgs\|gazebo_ros" .
```

## 2. Portable fixes (valid on Humble too)
- Python: `warning()` instead of `warn()`; `extras_require={'test': ['pytest']}`; setup.cfg keys with underscores.
- C++: `MsgT::ConstSharedPtr` callbacks; `.hpp` headers for tf2; `SingleThreadedExecutor` instead of the static one.
- CLI and scripts: static TF with `--x … --frame-id … --child-frame-id`; `ros2 control switch_controllers --activate/--deactivate`; `ros2 param dump > file`.
- Interfaces: if the code must run on Kilted+, use `example_interfaces/action/Fibonacci` (feedback `sequence`).

## 3. Target-specific fixes
- **Jazzy**: `ROS_AUTOMATIC_DISCOVERY_RANGE`/`ROS_STATIC_PEERS` instead of `ROS_LOCALHOST_ONLY`; rosbag `--exclude-regex` and `--all-topics`; apt/venv instead of `pip install` (PEP 668); Gazebo Harmonic (`gz sim`, `gz.msgs`); Nav2 BT XML → v4 (`convert_v3_to_v4.py`), plugin names `::`; ros2_control `robot_description` via the RSP topic (drop the parameter from `ros2_control_node`).
- **Lyrical**: replace `ament_target_dependencies`; base controller accepts `TwistStamped` (or set `enable_stamped_cmd_vel: false` in Nav2); `FASTDDS_DEFAULT_PROFILES_FILE`; Gazebo Jetty; check C++20 and the CMake 4 warnings.

## 4. Verify
```bash
docker run --rm -it -v ~/ros2_ws/src:/ws/src ros:jazzy bash   # or ros:lyrical
cd /ws && rosdep update && rosdep install --from-paths src --ignore-src -y -r
colcon build --event-handlers console_direct+ && colcon test && colcon test-result --verbose
```
Read every deprecation warning: on Jazzy it predicts what breaks on Lyrical. CI matrix for several distros: [[core-testing-ci-docker]].
