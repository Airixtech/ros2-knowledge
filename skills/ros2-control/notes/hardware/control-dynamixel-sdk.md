---
id: control-dynamixel-sdk
type: reference
owner: equipo-ros2
updated: 2026-10-24
review_by: 2027-04-22
source: manual
confidentiality: internal
title: "Dynamixel servos with ros2_control: Wizard, SDK, Workbench, installing them, the hardware package"
domain: control
area: hardware
distro: jazzy
tested: false
audience: dev
summary: "Dynamixel servos: Wizard 2.0, DynamixelSDK, dynamixel_workbench_toolbox; install from source or apt; dynamixel_hardware_interface package; official ROBOTIS package and name clash."
tags: [Dynamixel, ROBOTIS, DynamixelSDK, dynamixel_sdk, dynamixel-workbench, dynamixel_workbench_toolbox, Dynamixel Wizard, dynamixel_hardware_interface, dynamixel_hardware, SDK, apt]
see: ["[[control-dynamixel-header]]", "[[control-dynamixel-init]]", "[[control-hw-package-build]]", "[[control-hw-interface-concept]]", "[[control-learn-unit5-dynamixel]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: the course code is an older dynamixel_hardware (deprecated upstream); ROBOTIS releases its own package named dynamixel_hardware_interface (humble 1.5.0, jazzy 1.5.2, kilted 1.5.1, lyrical 1.5.1) — https://github.com/dynamixel-community/dynamixel_hardware/blob/jazzy/README.md (CONTROL-V30)"
  - "humble/jazzy: binaries ros-<distro>-dynamixel-sdk and ros-<distro>-dynamixel-workbench-toolbox exist — http://packages.ros.org/ros2/ubuntu/dists/noble/main/binary-amd64/Packages.gz (CONTROL-V31)"
---
# Dynamixel servos with ros2_control: Wizard, SDK, Workbench, installing them, the hardware package

**TL;DR** Dynamixel servos are smart actuators (built-in controller, networking on one bus, precise position control). A hardware interface for them wraps the manufacturer's library. Learn the SDK first: what it offers decides what your interface can do.

## The ROBOTIS software
A software development kit (SDK) is the library of the hardware maker plus its documentation, examples and often tools.
| Part | Role | Used here |
|---|---|---|
| Dynamixel Wizard 2.0 | GUI for the first setup, tuning and firmware updates of the servos | no |
| Dynamixel SDK (`dynamixel_sdk`) | low-level communication library | only as a dependency of Workbench |
| Dynamixel Workbench (`dynamixel_workbench_toolbox`) | higher-level library: ping, torque, operating modes, sync read/write, unit conversion | yes: the `DynamixelWorkbench` class |

SDK documentation: https://emanual.robotis.com/docs/en/software/dynamixel/dynamixel_sdk/overview/

## Install
From source, as the course does:
```bash
cd ~/ros2_ws/src/
git clone -b ros2 https://github.com/ROBOTIS-GIT/DynamixelSDK.git
git clone -b ros2 https://github.com/ROBOTIS-GIT/dynamixel-workbench.git
cd ~/ros2_ws
colcon build
```
Warnings such as "ISO C++ forbids variable length array" do not affect the SDK. Or from binaries (Humble and Jazzy have them): `sudo apt install ros-$ROS_DISTRO-dynamixel-sdk ros-$ROS_DISTRO-dynamixel-workbench-toolbox`.

## The hardware interface package
```bash
cd ~/ros2_ws/src
ros2 pkg create --build-type=ament_cmake dynamixel_hardware_interface --dependencies rclcpp pluginlib hardware_interface
cd ~/ros2_ws && colcon build && source install/setup.bash
```
Then add `dynamixel_workbench_toolbox` to `CMakeLists.txt` and `package.xml` ([[control-hw-package-build]]). Code: [[control-dynamixel-header]] → [[control-dynamixel-init]] → [[control-dynamixel-interfaces-activate]] → [[control-dynamixel-read-write]] → [[control-dynamixel-torque-mode]] → [[control-dynamixel-plugin-urdf-launch]].

## The package name and the official package
The code of these notes is an older version of the community package `dynamixel_hardware` (plugin `dynamixel_hardware/DynamixelHardware`), which its README now marks as deprecated in favour of ROBOTIS's own **`dynamixel_hardware_interface`**, released for Humble, Jazzy, Kilted and Lyrical (`sudo apt install ros-$ROS_DISTRO-dynamixel-hardware-interface`). The course names its own package `dynamixel_hardware_interface` too: keep the name for the exercises, but while that workspace is sourced it hides the official package of the same name. For a real robot use the ROBOTIS package; the deprecated package's migration guide maps its parameters to it (https://github.com/dynamixel-community/dynamixel_hardware/blob/jazzy/docs/migration_to_dynamixel_hardware_interface.md).

## Pitfalls
- Building the SDK from source and also installing its binaries gives two copies; use one of them.
- Read the servo's control table in the e-manual before coding: register names (`Goal_Position`, `Present_Current`…) differ between protocol versions ([[control-dynamixel-header]]).
