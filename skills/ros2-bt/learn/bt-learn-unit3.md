---
id: bt-learn-unit3
type: reference
owner: equipo-ros2
updated: 2026-10-15
review_by: 2027-04-13
source: manual
confidentiality: internal
title: "Unit 3 exercises: sequences, async, blackboard, remapping, ROS 2 simulation"
domain: bt
area: learn
distro: humble
tested: false
audience: students
summary: "Unit 3 exercises bt_u3_ex1–ex4, the SubTree example and the ROS 2 simulation test_unit3: stop at obstacles, add ReadingLaser and MoveRobot."
tags: [course, unit 3, bt_u3_ex1, bt_u3_ex2, bt_u3_ex3, bt_u3_ex4, test_unit3, StopRobot, PrintValue, Groot, students]
see: ["[[bt-sequence-variants]]", "[[bt-cpp-blackboard]]", "[[bt-cpp-port-remapping]]", "[[bt-cpp-groot-logging]]"]
requires: [ros2-core]
version_notes: []
---
# Unit 3 exercises: sequences, async, blackboard, remapping, ROS 2 simulation

**TL;DR** Four C++ exercises (`./bt_u3_ex1` … `./bt_u3_ex4`), a SubTree example to open in Groot, and a ROS 2 simulation: the robot drives forward, stops when the laser sees an obstacle and continues when you remove it; you add the two missing nodes to the XML.

## Exercises without ROS
| Exercise | What it shows | Note |
|---|---|---|
| 1 `bt_u3_ex1` | Sequence: obstacle, battery, rotate, move | [[bt-sequence-variants]] |
| 2 `bt_u3_ex2` | ReactiveSequence with an asynchronous decision | [[bt-reactive-async]] |
| 3 `bt_u3_ex3` | SequenceStar, blackboard and ports | [[bt-cpp-blackboard]] |
| 4 `bt_u3_ex4` | SubTrees with remapped ports | [[bt-cpp-port-remapping]] |
| SubTree example | Inverter, RetryUntilSuccessful, log `bt_trace.fbl` | [[bt-cpp-subtrees-decorators]] |
```bash
source ~/ros2_ws/install/setup.bash
cd ~/ros2_ws/src/bt_course_files/BehaviorTree.CPP/build/course_bt
./bt_u3_ex1
```
Open the logs in Groot (Log Replay) to watch the states change ([[bt-cpp-groot-logging]]).

## ROS 2 simulation (`test_unit3.cpp`)
The robot moves forward; obstacles appear on the way and the laser detects them. Remove each obstacle by hand: then the robot continues. Compare the expected behavior with the current tree, find what is missing and repair the XML section of the script (hint: only the XML needs changes).

Expected tree, as the course draws it. Legend: `[→]` Sequence · `[?]` Fallback · leaves are actions · `key="value"` port.
```text
Root
└── [→] Sequence
    ├── PrintValue  message="start"
    ├── [?] Fallback
    │   ├── ReadingLaser name="scanner"
    │   └── StopRobot name="stop_robot"
    ├── ReadingLaser name="scanner"
    ├── MoveRobot name="move_robot"
    └── PrintValue  message="stop"
```
```bash
ros2 launch my_package launch_world_unit3.launch.py
```
```bash
cd ~/ros2_ws/build/behaviortree_ros2
./test_unit3
```
**Solution** (the two nodes to add, in this order, after the Fallback):
```xml
<ReadingLaser name="scanner"/><MoveRobot name="move_robot"/>
```
The course's `test_unit3.cpp` is not shown; insert the `FileLogger` line there to replay the run in Groot ([[bt-cpp-groot-logging]]).

## Pitfalls
- While the way is blocked, the first `ReadingLaser` fails, so the Fallback runs `StopRobot` (SUCCESS); the second `ReadingLaser` fails too, the Sequence fails, and the next tick starts again from `PrintValue start`. Once the way is free both laser checks succeed and `MoveRobot` runs.
- Each tree and SubTree has its own blackboard: exercise 4 only works because of the remapping in the `<SubTree>` tags.
