---
id: control-learn-unit7-custom
type: reference
owner: equipo-ros2
updated: 2026-10-24
review_by: 2027-04-22
source: manual
confidentiality: internal
title: "Unit 7 exercises 7.3.1–7.20.1: rrbot_controller files in order, build, start the world, launch, check"
domain: control
area: learn
distro: jazzy
tested: false
audience: students
summary: "Unit 7 exercises: create rrbot_controller files step by step, build with my_robot_bringup and rrbot_unit2, start world, launch rrbot_with_rrbot_controller, list_controllers."
tags: [unit 7, exercise 7.3.1, exercise 7.16.1, exercise 7.20.1, rrbot_controller, custom controller, colcon build, start_world.launch.py, rrbot_with_rrbot_controller.launch.py, list_controllers, JointJog, hands-on]
see: ["[[control-custom-header]]", "[[control-custom-plugin-export]]", "[[control-custom-package-build]]", "[[control-custom-config-launch]]", "[[control-learn-unit6-controllers]]", "[[control-learn-unit8-project]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: list_controllers prints name, type and state in columns (CONTROL-V10)"
  - "jazzy: the appendix's complete .cpp has the older update(): Humble form, warnings on Jazzy, no build on Kilted/Lyrical (CONTROL-V74)"
---
# Unit 7 exercises 7.3.1–7.20.1: rrbot_controller files in order, build, start the world, launch, check

**TL;DR** The unit builds a custom controller in small steps, one file or method per exercise, then runs it on the rrbot of unit 2 in Gazebo Sim. The code with its explanations is in the `controllers` notes linked below.

## The files, in the order of the exercises
| Exercise | Do | Code |
|---|---|---|
| 7.3.1 | `cd ~/ros2_ws/src` and `ros2 pkg create … rrbot_controller` | [[control-custom-header]] |
| 7.4.1 | `touch ~/ros2_ws/src/rrbot_controller/include/rrbot_controller/rrbot_controller.hpp`, paste the header | [[control-custom-header]] |
| 7.5.1 | `touch ~/ros2_ws/src/rrbot_controller/src/rrbot_controller.cpp`, paste the skeleton | [[control-custom-init]] |
| 7.6.1–7.13.1 | inside the namespace: `on_init`, `on_configure`, the two interface configurations, `on_activate`, `on_deactivate`, `update` | [[control-custom-init]], [[control-custom-configure]], [[control-custom-interfaces]], [[control-custom-activate-update]] |
| 7.14.1 | the plugin macro at the very bottom, after the namespace | [[control-custom-plugin-export]] |
| 7.15.1 | `touch ~/ros2_ws/src/rrbot_controller/rrbot_controller.xml` | [[control-custom-plugin-export]] |
| 7.16.1 | `CMakeLists.txt` and `package.xml`, then `cd ~/ros2_ws && colcon build --packages-select rrbot_controller` | [[control-custom-package-build]] |
| 7.17.1 | `config/rrbot_controllers_custom.yaml` and its install | [[control-custom-config-launch]] |
| 7.18.1 | `<parameters>` in `~/ros2_ws/src/ros2_control_course/unit2/rrbot_unit2/urdf/rrbot.xacro` | [[control-custom-config-launch]] |
| 7.19.1 | `touch ~/ros2_ws/src/my_robot_bringup/launch/rrbot_with_rrbot_controller.launch.py` | [[control-custom-config-launch]] |

The 7.10.1 template `get_ordered_interfaces()` is not needed and does not work: leave it out ([[control-custom-interfaces]]). If the build fails, read the compiler messages one by one; the course's appendix gives the complete `.cpp`, which is these methods in this order with the older two lines of `update()` ([[control-custom-activate-update]]).

## Exercise 7.20.1: build and run
```bash
cd ~/ros2_ws
colcon build --packages-select rrbot_controller my_robot_bringup rrbot_unit2
source install/setup.bash
```
Start the empty world: source the course's simulation workspace (provided by the course platform) and run `ros2 launch rrbot_sim start_world.launch.py`. Wait until Gazebo is shown, then in a second terminal:
```bash
source ~/ros2_ws/install/setup.bash
ros2 launch my_robot_bringup rrbot_with_rrbot_controller.launch.py
```
After the 10 s pause of the launch file, check the controllers:
```bash
ros2 control list_controllers
```
`rrbot_controller` (`rrbot_controller/RRBotController`) and `joint_state_broadcaster` (`joint_state_broadcaster/JointStateBroadcaster`) are both `active`. The course stops here; to move the joints, send a `JointJog` [verify]:
```bash
ros2 topic pub /rrbot_controller/commands control_msgs/msg/JointJog "{joint_names: [joint1, joint2], displacements: [0.5, 0.5]}" -1
```
Press Ctrl+C in all terminals when done. Next: the course project, [[control-learn-unit8-project]].
