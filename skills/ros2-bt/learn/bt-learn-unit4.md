---
id: bt-learn-unit4
type: reference
owner: equipo-ros2
updated: 2026-10-15
review_by: 2027-04-13
source: manual
confidentiality: internal
title: "Unit 4 exercises: node creation, ports, async, constructor args, ROS 2 simulation"
domain: bt
area: learn
distro: humble
tested: false
audience: students
summary: "Unit 4 exercises bt_u4_ex1–ex4 and the ROS 2 simulation test_unit4: escape a trap with a ReactiveSequence of Rotating and ReadingLaser."
tags: [course, unit 4, bt_u4_ex1, bt_u4_ex2, bt_u4_ex3, bt_u4_ex4, test_unit4, ReactiveSequence, escape trap, students]
see: ["[[bt-cpp-registration]]", "[[bt-cpp-async-action]]", "[[bt-cpp-constructor-args]]", "[[bt-reactive-async]]"]
requires: [ros2-core]
version_notes: []
---
# Unit 4 exercises: node creation, ports, async, constructor args, ROS 2 simulation

**TL;DR** Four C++ exercises about the library itself (`./bt_u4_ex1` … `./bt_u4_ex4`), then a ROS 2 simulation: the robot is trapped among walls, rotates while the laser looks for a free way, and drives out when you open one. You write the whole XML from the Groot figure.

## Exercises without ROS
| Exercise | What it shows | Note |
|---|---|---|
| 1 `bt_u4_ex1` | registration: class, simple condition, simple action | [[bt-cpp-registration]] |
| 2 `bt_u4_ex2` | custom node with an output port (CPU usage) | [[bt-cpp-sync-action-ports]] |
| 3 `bt_u4_ex3` | asynchronous node in a ReactiveSequence | [[bt-cpp-async-action]] |
| 4 `bt_u4_ex4` | constructor arguments: builder and `init()` | [[bt-cpp-constructor-args]] |
```bash
source ~/ros2_ws/install/setup.bash
cd ~/ros2_ws/src/bt_course_files/BehaviorTree.CPP/build/course_bt
./bt_u4_ex3
```

## ROS 2 simulation (`test_unit4.cpp`)
The robot is trapped among the walls. It rotates and explores for an obstacle-free way; the laser detects it automatically, then the robot stops rotating and moves forward. To free it: pause the simulation, move or delete a wall, and play again. Analyze the C++ code to see how signals pass between the BT nodes, and write in the `.cpp` the tree of the Groot figure.

Tree of the solution, generated from the course XML. Legend: `[→]` Sequence · `[R→]` ReactiveSequence · leaves are actions · `key="value"` port.
```text
BehaviorTree
└── [→] Sequence
    ├── SetBlackboard  output_key="Interface" value="360"
    ├── [R→] ReactiveSequence
    │   ├── Rotating  input="{Interface}"
    │   └── ReadingLaser name="scanner"
    └── MoveRobot name="move_robot"
```
```bash
ros2 launch my_package launch_world_unit4.launch.py
```
```bash
cd ~/ros2_ws/build/behaviortree_ros2
./test_unit4
```
**Solution:**
```cpp
static const char *xml_text = R"(
 <root >
     <BehaviorTree>
        <Sequence>
            <SetBlackboard   output_key="Interface" value="360" />
            <ReactiveSequence>
                <Rotating     input="{Interface}" />
                <ReadingLaser name="scanner"/>
            </ReactiveSequence>
            <MoveRobot name="move_robot"/>
        </Sequence>
     </BehaviorTree>
 </root>
 )";
```
Each tick the ReactiveSequence rotates the robot a bit and checks the laser; while the laser fails, the tree fails and is ticked again; when the way is free, `MoveRobot` runs ([[bt-reactive-async]]).

## Pitfalls
- In the course programs that are shown (`test_unit2.cpp`, the project), `Rotating` and `ReadingLaser` are synchronous nodes that sleep inside `tick()`: the robot reacts because the whole tree is ticked again and again ([[bt-ros2-node-pattern]]). `test_unit4.cpp` itself is not shown.
