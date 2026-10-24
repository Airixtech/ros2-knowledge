---
id: control-dynamixel-plugin-urdf-launch
type: reference
owner: equipo-ros2
updated: 2026-10-24
review_by: 2027-04-22
source: manual
confidentiality: internal
title: "Dynamixel <ros2_control> with usb_port, baud_rate, use_dummy, ids; launch, YAML and test in RViz2"
domain: control
area: hardware
distro: jazzy
tested: false
audience: dev
summary: "rrbot.xacro <ros2_control> for dynamixel_hardware/DynamixelHardware: usb_port, baud_rate, use_dummy, joint id params; launch, controller YAML and test with dummy mode in RViz2."
tags: [DynamixelHardware, dynamixel_hardware/DynamixelHardware, use_dummy, usb_port, baud_rate, "/dev/ttyUSB0", id, bring_up_on_hardware.launch.py, rrbot_unit4, controller_configuration.yaml, dummy mode, RViz2]
see: ["[[control-urdf-tag]]", "[[control-hw-plugin-export]]", "[[control-bringup-hardware-launch]]", "[[control-dynamixel-init]]", "[[control-dynamixel-read-write]]", "[[control-learn-unit5-dynamixel]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: the explained snippet reads controllers/controllers.yaml; the launch file and 5.22 use config/controller_configuration.yaml (CONTROL-V13)"
  - "jazzy: spawner output is 'Configured and activated' and list_controllers prints columns (the course shows an older release) (CONTROL-V08, CONTROL-V10)"
  - "jazzy: the controller manager reads /robot_description from robot_state_publisher; the parameter is ignored (CONTROL-V23)"
---
# Dynamixel <ros2_control> with usb_port, baud_rate, use_dummy, ids; launch, YAML and test in RViz2

**TL;DR** The robot description chooses the plugin: replace the hardware block with the Dynamixel one. With `use_dummy` = `true` the interface mirrors commands into states, so the whole pipeline can be tested in RViz2 without servos; set it to `false` with real servos connected.

## rrbot.xacro (before `</robot>`)
```xml
<ros2_control name="DynamixelHardware" type="system">
  <hardware>
    <plugin>dynamixel_hardware/DynamixelHardware</plugin>
    <param name="usb_port">/dev/ttyUSB0</param>
    <param name="baud_rate">1000000</param>
    <param name="use_dummy">true</param>
  </hardware>
  <joint name="joint1">
    <param name="id">11</param>
    <command_interface name="position"/>
    <command_interface name="velocity"/>
    <state_interface name="position"/>
    <state_interface name="velocity"/>
    <state_interface name="effort"/>
  </joint>
  <joint name="joint2">
    <param name="id">12</param>
    <command_interface name="position"/>
    <command_interface name="velocity"/>
    <state_interface name="position"/>
    <state_interface name="velocity"/>
    <state_interface name="effort"/>
  </joint>
</ros2_control>
```
- `<plugin>` = the `name` of `dynamixel_hardware.xml` ([[control-hw-plugin-export]]).
- `usb_port`, `baud_rate`, `use_dummy` are read in `on_init()`; each joint's `id` is the servo id on the bus ([[control-dynamixel-init]]).
- The interfaces are exactly the exported ones: position and velocity commands, position, velocity and effort states ([[control-dynamixel-interfaces-activate]]).

## Launch and YAML
`launch/bring_up_on_hardware.launch.py` of this package is the template's file ([[control-bringup-hardware-launch]]) with these lines, and only the `joint_state_broadcaster` and `forward_position_controller` spawners:
```python
    package_name = "rrbot_unit4"

    rviz_config = os.path.join(get_package_share_directory("rrbot_unit4"), "rviz", "unit4.rviz")
    controller_config = os.path.join(
        get_package_share_directory("dynamixel_hardware_interface"), "config", "controller_configuration.yaml"
    )
```
(The course's explanation of this file reads `controllers/controllers.yaml` from the robot package; the file itself uses the path above.) `config/controller_configuration.yaml` is the YAML of the template units, with `position_trajectory_controller` ([[control-controller-config]]). No Gazebo plugin is loaded: the YAML reaches `ros2_control_node` from the launch file, and RViz2 shows the joint states.

## Build and test
```bash
cd ~/ros2_ws && colcon build
source install/setup.bash
ros2 launch dynamixel_hardware_interface bring_up_on_hardware.launch.py
```
```text
[ros2_control_node-1][INFO] [controller_manager]: Loading controller 'joint_state_broadcaster'
[spawner-3] [INFO] [spawner_forward_position_controller]: Loaded forward_position_controller
[ros2_control_node-1][INFO] [controller_manager]: Configuring controller 'forward_position_controller'
[ros2_control_node-1][INFO] [forward_position_controller]: configure successful
[spawner-2] [INFO][spawner_joint_state_broadcaster]: Loaded joint_state_broadcaster
[ros2_control_node-1][INFO][controller_manager]: Configuring controller 'joint_state_broadcaster'
[spawner-3] [INFO][spawner_forward_position_controller]: Configured and started forward_position_controller
[spawner-2] [INFO][spawner_joint_state_broadcaster]: Configured and started joint_state_broadcaster
```
(Course output of an older release: Jazzy prints `Configuring controller: '…'` and `Configured and activated …`.) The robot stands upright in RViz2. In a second terminal:
```bash
ros2 topic list                  # /forward_position_controller/commands
ros2 control list_controllers    # both active
ros2 topic pub /forward_position_controller/commands std_msgs/msg/Float64MultiArray "data:
- 1.5
- 1.5" -1
```

## Pitfalls
- `use_dummy` left at `true` with real servos connected → nothing moves; `false` without servos → `on_init()` fails at `init()`/`ping()` and the plugin is not loaded.
- With real servos, `/dev/ttyUSB0` must be the adapter's port and readable by your user (on Ubuntu, serial ports belong to the `dialout` group); ids and baud rate must match the servos' settings.
