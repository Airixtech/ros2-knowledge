---
id: bt-learn-unit2
type: reference
owner: equipo-ros2
updated: 2026-10-15
review_by: 2027-04-13
source: manual
confidentiality: internal
title: "Unit 2 exercises: first BTs, Sequence, Fallback, ROS 2 simulation"
domain: bt
area: learn
distro: humble
tested: false
audience: students
summary: "Unit 2 exercises bt_u2_ex1–ex4 and the ROS 2 simulation test_unit2: turn 45/90/135 degrees with Fallbacks, add the missing MoveRobot."
tags: [course, unit 2, bt_u2_ex1, bt_u2_ex2, bt_u2_ex3, bt_u2_ex4, test_unit2, Fallback, MoveRobot, students]
see: ["[[bt-cpp-first-program]]", "[[bt-sequence-fallback]]", "[[bt-reactive-async]]", "[[bt-ros2-node-pattern]]"]
requires: [ros2-core]
version_notes: []
---
# Unit 2 exercises: first BTs, Sequence, Fallback, ROS 2 simulation

**TL;DR** Four C++ exercises without ROS (`./bt_u2_ex1` … `./bt_u2_ex4` in `~/ros2_ws/src/bt_course_files/BehaviorTree.CPP/build/course_bt`), then a ROS 2 simulation where the robot looks for a free direction at 45°, 90° and 135° and you complete the tree so it also drives away.

## Exercises without ROS
| Exercise | What it shows | Note |
|---|---|---|
| 1 `bt_u2_ex1` | first program: pick-ball tree (build with `cmake ..` + `make` first) | [[bt-cpp-first-program]] |
| 2 `bt_u2_ex2` | Sequence: the first FAILURE stops it | [[bt-sequence-fallback]] |
| 3 `bt_u2_ex3` | Fallback: the first SUCCESS stops it | [[bt-sequence-fallback]] |
| 4 `bt_u2_ex4` | RUNNING and a ReactiveFallback (eat a banana) | [[bt-reactive-async]] |
```bash
source ~/ros2_ws/install/setup.bash
cd ~/ros2_ws/src/bt_course_files/BehaviorTree.CPP/build/course_bt
./bt_u2_ex2
```
Play with the flags (FAILURE/SUCCESS) of the task nodes and compare the outputs.

## ROS 2 simulation (`test_unit2.cpp`)
The robot is stopped and must turn left. It turns 45° and checks the laser; if the way is not free it turns to 90° and checks again; if still blocked it turns to 135° and moves that way. If you remove an obstacle (for example at 90°), it goes that way. This shows the Fallback: it keeps checking options while they fail and succeeds at the first success.

Tree of the solution, generated from the course XML. Legend: `[→]` Sequence · `[?]` Fallback · leaves are actions · `key="value"` port.
```text
BehaviorTree
└── [→] Sequence
    ├── SetBlackboard  output_key="Interface" value="45"
    ├── Rotating  input="{Interface}"
    ├── [?] Fallback
    │   ├── ReadingLaser name="scanner"
    │   └── [→] Sequence
    │       ├── SetBlackboard  output_key="Interface" value="90"
    │       ├── Rotating  input="{Interface}"
    │       └── [?] Fallback
    │           ├── ReadingLaser name="scanner"
    │           └── [→] Sequence
    │               ├── SetBlackboard  output_key="Interface" value="135"
    │               ├── Rotating  input="{Interface}"
    │               └── ReadingLaser name="scanner"
    └── MoveRobot name="move_robot"
```
```bash
ros2 launch my_package launch_world_unit2.launch.py
```
```bash
cd ~/ros2_ws/build/behaviortree_ros2
./test_unit2
```
**Your task:** study how the BT framework and ROS 2 connect in `behaviortree_ros2/test/test_unit2.cpp` (full code: [[bt-ros2-node-pattern]]). As shipped, the robot does not move after it finds a free way: the XML has the placeholder `<something is meesing here/>` where a node is missing. Fix the XML, rebuild with `colcon build` and run again.

**Solution:** replace the placeholder with
```xml
<MoveRobot name="move_robot"/>
```
The full XML string of the solution:
```cpp
static const char *xml_text = R"(
 <root >
     <BehaviorTree>
        <Sequence>
            <SetBlackboard   output_key="Interface" value="45" />
            <Rotating     input="{Interface}" />
            <Fallback>
                <ReadingLaser name="scanner"/>
                <Sequence>
                    <SetBlackboard   output_key="Interface" value="90" />
                    <Rotating     input="{Interface}" />
                    <Fallback>
                        <ReadingLaser name="scanner"/>
                        <Sequence>
                            <SetBlackboard   output_key="Interface" value="135" />
                            <Rotating     input="{Interface}" />
                            <ReadingLaser name="scanner"/>
                        </Sequence>
                    </Fallback>
                </Sequence>
            </Fallback>
            <MoveRobot name="move_robot"/>
        </Sequence>
     </BehaviorTree>
 </root>
 )";
```

## Pitfalls
- The XML is a C++ string: after editing it, rebuild before running.
- The ROS 2 code of this unit works but is fragile (globals, nodes never spun, sleeping ticks): read [[bt-ros2-node-pattern]] before copying it.
