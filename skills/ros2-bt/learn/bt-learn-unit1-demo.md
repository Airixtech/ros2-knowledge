---
id: bt-learn-unit1-demo
type: reference
owner: equipo-ros2
updated: 2026-10-15
review_by: 2027-04-13
source: manual
confidentiality: internal
title: "Unit 1: build the course packages and run the first BT demo"
domain: bt
area: learn
distro: humble
tested: false
audience: students
summary: "Unit 1: get the course files, colcon build behaviortree_cpp_v3 and behaviortree_ros2, launch the TurtleBot3 world, run test_unit1."
tags: [course, unit 1, colcon build, behaviortree_cpp_v3, behaviortree_ros2, test_unit1, TurtleBot3, Gazebo, ReactiveSequence, students]
see: ["[[bt-learn-start-here]]", "[[bt-learn-unit2]]", "[[bt-what-is-bt]]", "[[bt-reactive-async]]"]
requires: [ros2-core]
version_notes:
  - "humble: behaviortree_cpp_v3 is also a binary: apt install ros-humble-behaviortree-cpp-v3 — http://packages.ros.org/ros2/ubuntu/dists/jammy/main/binary-amd64/Packages.gz (BT-V33)"
---
# Unit 1: build the course packages and run the first BT demo

**TL;DR** Put the course files in `~/ros2_ws/src`, build `behaviortree_cpp_v3` and `behaviortree_ros2` with colcon (it takes several minutes), source the workspace, launch the unit 1 world and run `./test_unit1` from the build folder. The robot spins in its room until you remove the wall, then drives into the next room.

## Build
```bash
cd ~/ros2_ws/src
# clone the course files repository here (folder bt_course_files)
```
```bash
cd ~/ros2_ws
colcon build --packages-select behaviortree_cpp_v3
colcon build --packages-select behaviortree_ros2
```
```bash
source ~/ros2_ws/install/setup.bash
```
On Humble you can also install the library as a binary (`sudo apt install ros-humble-behaviortree-cpp-v3`) instead of building it.

## Demo
Shell 2, the simulation:
```bash
ros2 launch my_package launch_world_unit1.launch.py
```
(`my_package` is the course's simulation package; source its workspace first.) Shell 1, the tree:
```bash
cd ~/ros2_ws/build/behaviortree_ros2
./test_unit1
```
- The robot wants to go to the next room; with the laser it looks for the open door.
- You hold the "key": remove the wall in Gazebo (right-click on the wall → **Delete**).
- The robot spins in the first room; once the way is free it moves to the other room.

The tree of the demo, as the course draws it (read it top to bottom, left to right). Legend: `[R→]` ReactiveSequence · leaves are actions · `key="value"` port.
```text
Root
└── [R→] ReactiveSequence
    ├── SetBlackboard  value="360" output_key="Interface"
    ├── [R→] ReactiveSequence
    │   ├── Rotating  input="{Interface}"
    │   └── ReadingLaser name="scanner"
    └── MoveRobot name="move_robot"
```
- The ReactiveSequence works like a logical AND: it succeeds only if all its children succeed.
- Skip the blackboard for now ([[bt-cpp-blackboard]]). In the inner ReactiveSequence the robot rotates (SUCCESS), then scans for an obstacle-free way with the laser: SUCCESS once you remove the obstacle.
- Then the inner sequence succeeds and the robot runs the last action of the outer one, `MoveRobot`.
- The figure was drawn with Groot ([[bt-cpp-groot-logging]]).

## Pitfalls
- Run `./test_unit1` from `~/ros2_ws/build/behaviortree_ros2`: the course installs the test programs to `bin`, not to `lib/<package>`, so `ros2 run` does not find them.
- Source the workspace in every new shell before running the programs.
