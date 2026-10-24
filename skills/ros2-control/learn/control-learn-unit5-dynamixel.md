---
id: control-learn-unit5-dynamixel
type: reference
owner: equipo-ros2
updated: 2026-10-24
review_by: 2027-04-22
source: manual
confidentiality: internal
title: "Unit 5 exercises 5.2–5.22: Dynamixel hardware interface in dummy mode, build and test"
domain: control
area: learn
distro: jazzy
tested: false
audience: students
summary: "Unit 5 exercises 5.2.1–5.22.1: Dynamixel SDK install, dynamixel_hardware_interface files, plugin switch in rrbot_unit4, launch, YAML, test with use_dummy."
tags: [unit 5, Dynamixel, dynamixel_hardware_interface, DynamixelHardware, rrbot_unit4, use_dummy, bring_up_on_hardware.launch.py, exercise 5.22.1, RViz2]
see: ["[[control-dynamixel-sdk]]", "[[control-dynamixel-header]]", "[[control-dynamixel-init]]", "[[control-dynamixel-interfaces-activate]]", "[[control-dynamixel-read-write]]", "[[control-dynamixel-torque-mode]]", "[[control-dynamixel-plugin-urdf-launch]]", "[[control-learn-unit4-template]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: ROBOTIS releases a package named dynamixel_hardware_interface too; the course's code is the deprecated dynamixel_hardware (CONTROL-V30)"
---
# Unit 5 exercises 5.2–5.22: Dynamixel hardware interface in dummy mode, build and test

**TL;DR** The same five steps as unit 4, now wrapping the ROBOTIS Dynamixel Workbench library. Dummy mode tests the whole pipeline in RViz2 without servos.

## Exercises and where the code is
| Exercise | File or step | Note |
|---|---|---|
| 5.2.1 | clone and build DynamixelSDK and dynamixel-workbench (`ros2` branch) | [[control-dynamixel-sdk]] |
| 5.3.1 | package `dynamixel_hardware_interface` | [[control-dynamixel-sdk]] |
| 5.4.1–5.5.1 | header, `.cpp` start with the constants | [[control-dynamixel-header]] |
| 5.6.1 | `on_init()` | [[control-dynamixel-init]] |
| 5.7.1–5.10.1 | exports, `on_activate()`, `on_deactivate()` | [[control-dynamixel-interfaces-activate]] |
| 5.11.1–5.12.1 | `read()`, `write()` | [[control-dynamixel-read-write]] |
| 5.13.1–5.15.1 | `enable_torque()`, `set_control_mode()`, `reset_command()` | [[control-dynamixel-torque-mode]] |
| 5.16.1–5.17.1 | export macro, `dynamixel_hardware.xml` | [[control-hw-plugin-export]] |
| 5.18.1 | `CMakeLists.txt`, `package.xml` with `dynamixel_workbench_toolbox` | [[control-hw-package-build]] |
| 5.19.1 | `ros2_control_course/unit4/rrbot_unit4/urdf/rrbot.xacro`: the `DynamixelHardware` block with `use_dummy` true | [[control-dynamixel-plugin-urdf-launch]] |
| 5.20.1–5.21.1 | `launch/bring_up_on_hardware.launch.py`, `config/controller_configuration.yaml` | [[control-dynamixel-plugin-urdf-launch]] |

The robot package of this unit is `rrbot_unit4`: the course repository's folders `unit3` and `unit4` hold the robots of units 4 and 5.

## Exercise 5.22.1: build and test
```bash
cd ~/ros2_ws && colcon build
source install/setup.bash
ros2 launch dynamixel_hardware_interface bring_up_on_hardware.launch.py
```
Delete the robot left in Gazebo first: this unit uses RViz2 only. The robot stands upright in RViz2; then check `ros2 topic list` and `ros2 control list_controllers` and send `1.5`, `1.5` to `/forward_position_controller/commands` ([[control-dynamixel-plugin-urdf-launch]]). In dummy mode the joints jump straight to the command (the command is copied to the state).

## After the course
For real Dynamixel servos prefer the ROBOTIS package `dynamixel_hardware_interface` (binaries for Humble, Jazzy, Kilted, Lyrical); the course's package of the same name hides it while your workspace is sourced ([[control-dynamixel-sdk]]).
