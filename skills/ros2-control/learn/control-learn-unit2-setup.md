---
id: control-learn-unit2-setup
type: reference
owner: equipo-ros2
updated: 2026-10-24
review_by: 2027-04-22
source: manual
confidentiality: internal
title: "Unit 2 exercises 2.2–2.5: bringup package, controller YAML, xacro tags, launch file"
domain: control
area: learn
distro: jazzy
tested: false
audience: students
summary: "Unit 2 exercises 2.2.1–2.5.1: spawn rrbot without control, my_robot_bringup, one-joint controller_configuration.yaml, ros2_control tags in rrbot.xacro, my_robot.launch.py."
tags: [unit 2, rrbot_unit2, rrbot.xacro, spawn_rrbot_no_control.launch.py, my_robot_bringup, controller_configuration.yaml, my_robot.launch.py, exercise 2.2.1, exercise 2.3.1, exercise 2.4.1, exercise 2.5.1]
see: ["[[control-learn-start-here]]", "[[control-bringup-sim-launch]]", "[[control-controller-config]]", "[[control-urdf-tag]]", "[[control-learn-unit2-test]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: the course's pkg create output lists joint_state_publisher, which the command does not ask for (CONTROL-V11)"
---
# Unit 2 exercises 2.2–2.5: bringup package, controller YAML, xacro tags, launch file

**TL;DR** The robot model in Gazebo has no ros2_control yet. Five steps add it: a package, a configuration file for the controller manager and the controllers, the robot description tags, a launch file, and the test ([[control-learn-unit2-test]]).

## Simulation and robot without control
Start the unit's simulation (course script: Gazebo Sim with an empty world), download and build the course packages if not done in unit 1 ([[control-learn-unit1-demo]]), then:
```bash
ros2 launch rrbot_sim spawn_rrbot_no_control.launch.py   # after sourcing the course's simulation workspace
```
All that is needed to start is the robot description (`urdf` or `xacro`), which Gazebo already uses.

## Exercise 2.2.1: package
`ros2 pkg create --build-type=ament_cmake my_robot_bringup --dependencies urdf xacro robot_state_publisher` in `~/ros2_ws/src` ([[control-bringup-sim-launch]]). Its output ends with `creating ./my_robot_bringup/CMakeLists.txt`; the dependency list it prints are the three given (the course's output shows `joint_state_publisher` too).

## Exercise 2.3.1: configuration file
`mkdir config` in the package and create `controller_configuration.yaml`: the file of [[control-controller-config]] with **one** joint. What differs from that two-joint file:
```yaml
forward_position_controller:
  ros__parameters:
    joints:
      - joint1
    interface_name: position
```
the same `joints: [joint1]` in the trajectory controller, and two comments: `### Controllers available` above the controller types, `# Hz, Defaults to 50` after `state_publish_rate`. `joint1` is the `<joint name="joint1" type="continuous">` of the xacro.

## Exercise 2.4.1: robot description
In the course package, `ros2_control_course/unit2/rrbot_unit2/urdf/rrbot.xacro`: add the `<ros2_control>` block (GazeboSimSystem, `joint1` only) and the `<gazebo>` plugin block before `</robot>` ([[control-urdf-tag]]); save. Then delete the old robot model from Gazebo: it was spawned without these tags.

## Exercise 2.5.1: launch file
```bash
cd ~/ros2_ws/src/my_robot_bringup
mkdir launch
cd launch
touch my_robot.launch.py
chmod +x my_robot.launch.py
```
Paste the launch file of [[control-bringup-sim-launch]], add `install(DIRECTORY launch config DESTINATION share/${PROJECT_NAME}/)` to `CMakeLists.txt`, then:
```bash
cd ~/ros2_ws
colcon build
source install/setup.bash
```
