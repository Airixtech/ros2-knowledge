---
id: control-learn-unit4-template
type: reference
owner: equipo-ros2
updated: 2026-10-24
review_by: 2027-04-22
source: manual
confidentiality: internal
title: "Unit 4 exercises 4.3–4.20: template hardware interface, files, build and test in RViz2"
domain: control
area: learn
distro: jazzy
tested: false
audience: students
summary: "Unit 4 exercises 4.3.1–4.20.1: my_robot_hardware_interface files, plugin switch in rrbot_unit3, launch and YAML, colcon build --packages-select, test with forward commands."
tags: [unit 4, my_robot_hardware_interface, RRBotSystemPositionOnlyHardware, rrbot_unit3, bring_up_on_hardware.launch.py, colcon build --packages-select, exercise 4.20.1, RViz2, template]
see: ["[[control-hw-interface-concept]]", "[[control-hw-template-header]]", "[[control-hw-template-init]]", "[[control-hw-template-export]]", "[[control-hw-template-activate-rw]]", "[[control-hw-plugin-export]]", "[[control-hw-package-build]]", "[[control-bringup-hardware-launch]]", "[[control-learn-unit5-dynamixel]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: the launch file spawns joint_trajectory_controller, which the YAML names position_trajectory_controller (CONTROL-V01)"
  - "kilted/lyrical: with enforce_command_limits true by default, 1.57 rad commands may be clamped to the URDF max of 1.0 [verify] (CONTROL-V22)"
---
# Unit 4 exercises 4.3–4.20: template hardware interface, files, build and test in RViz2

**TL;DR** Build a minimal hardware interface without any hardware library, replace the Gazebo plugin of the robot with it, and drive the "robot" in RViz2. The template is the starting point to add a real device's library later (unit 5).

## Exercises and where the code is
| Exercise | File or step | Note |
|---|---|---|
| 4.3.1 | package `my_robot_hardware_interface` | [[control-hw-template-header]] |
| 4.4.1 | `include/my_robot_hardware_interface/my_robot_hardware_interface.hpp` | [[control-hw-template-header]] |
| 4.5.1 | `src/my_robot_hardware_interface.cpp` skeleton | [[control-hw-template-header]] |
| 4.6.1–4.7.1 | `on_init()`, `on_configure()` | [[control-hw-template-init]] |
| 4.8.1–4.9.1 | `export_state_interfaces()`, `export_command_interfaces()` | [[control-hw-template-export]] |
| 4.10.1–4.14.1 | `on_activate()`, `on_deactivate()`, `read()`, `write()` | [[control-hw-template-activate-rw]] |
| 4.14.1–4.15.1 | `PLUGINLIB_EXPORT_CLASS`, `my_robot_hardware_interface.xml` | [[control-hw-plugin-export]] |
| 4.16.1 | `CMakeLists.txt`, `package.xml` | [[control-hw-package-build]] |
| 4.17.1 | `ros2_control_course/unit3/rrbot_unit3/urdf/rrbot.xacro`: the `DemoHardware` block | [[control-urdf-tag]] |
| 4.18.1 | `launch/bring_up_on_hardware.launch.py` | [[control-bringup-hardware-launch]] |
| 4.19.1 | `config/controller_configuration.yaml` (the unit 2 file, trajectory controller named `position_trajectory_controller`) | [[control-controller-config]] |

The course pastes the methods into a file it sometimes calls `my_robot_hardware.cpp`: it is `my_robot_hardware_interface.cpp`.

## Exercise 4.20.1: build and test
```bash
cd ~/ros2_ws
colcon build --symlink-install --packages-select my_robot_hardware_interface rrbot_unit3
source install/setup.bash
ros2 launch my_robot_hardware_interface bring_up_on_hardware.launch.py
```
The console shows the `read()`/`write()` logs as the loop runs, and RViz2 opens with the robot upright. In a second terminal:
```bash
ros2 topic list                  # /forward_position_controller/commands
ros2 control list_controllers    # joint_state_broadcaster and forward_position_controller active
ros2 topic pub /forward_position_controller/commands std_msgs/msg/Float64MultiArray "data:
- 1.57
- 0.0" -1
ros2 topic pub /forward_position_controller/commands std_msgs/msg/Float64MultiArray "data:
- 1.57
- 1.57" -1
ros2 topic pub /forward_position_controller/commands std_msgs/msg/Float64MultiArray "data:
- 0.0
- 0.0" -1
```
The joints move slowly towards each target (`hw_slowdown_`).

## Pitfalls of the course files
- Its launch file also spawns `joint_trajectory_controller`, which the YAML does not define: that spawner fails ([[control-bringup-hardware-launch]] fixes it).
- The URDF gives the command interfaces `min`/`max` ±1 while the test sends 1.57: on Jazzy nothing clamps (default `enforce_command_limits: false`); on Kilted and Lyrical the default is `true` [verify the effect].
