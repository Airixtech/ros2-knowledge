---
id: bt-learn-unit5
type: reference
owner: equipo-ros2
updated: 2026-10-15
review_by: 2027-04-13
source: manual
confidentiality: internal
title: "Unit 5: stochastic BT simulation (DefectFactor)"
domain: bt
area: learn
distro: humble
tested: false
audience: students
summary: "Unit 5 simulation test_unit5: a laser failure probability (DefectFactor) on the blackboard sets how often the laser is trusted."
tags: [course, unit 5, stochastic, DefectFactor, probability, test_unit5, SetBlackboard, ReadingLaser, inputlaser, students]
see: ["[[bt-stochastic]]", "[[bt-planning-acting]]", "[[bt-learn-unit4]]", "[[bt-cpp-blackboard]]"]
requires: [ros2-core]
version_notes: []
---
# Unit 5: stochastic BT simulation (DefectFactor)

**TL;DR** The second part of the unit 4 simulation: the laser has an internal failure, so it detects wrongly with some probability. The probability is a blackboard entry (`DefectFactor`, default 0.1) read by `ReadingLaser`; with 0.1 the robot accepts the laser signal as valid with probability 0.9. Concepts: [[bt-stochastic]].

## The task
- Repeat the unit 4 task and write the BT in the `.cpp` from the Groot figure.
- The laser is faulty: the probability of a wrong detection is high.
- Set the probability through the blackboard; the default is 0.1. After you remove the obstacle (as in unit 4), the robot classifies the laser signal as valuable with probability 0.9.
- Raise the failure probability (towards 1.0) and the robot is less likely to get out of the trap. Try several values (the value is set in the XML).

Tree of the solution, generated from the course XML. Legend: `[→]` Sequence · `[R→]` ReactiveSequence · leaves are actions · `key="value"` port.
```text
BehaviorTree
└── [→] Sequence
    ├── SetBlackboard  output_key="Interface" value="360"
    ├── SetBlackboard  output_key="DefectFactor" value="0.1"
    ├── [R→] ReactiveSequence
    │   ├── Rotating  input="{Interface}"
    │   └── ReadingLaser  inputlaser="{DefectFactor}"
    └── MoveRobot name="move_robot"
```
```bash
ros2 launch my_package launch_world_unit5.launch.py
```
```bash
cd ~/ros2_ws/build/behaviortree_ros2
./test_unit5
```
**Solution:**
```cpp
static const char *xml_text = R"(
 <root >
     <BehaviorTree>
        <Sequence>
            <SetBlackboard   output_key="Interface" value="360" />
            <SetBlackboard   output_key="DefectFactor" value="0.1" />
            <ReactiveSequence>
                <Rotating     input="{Interface}" />
                <ReadingLaser inputlaser="{DefectFactor}"/>
            </ReactiveSequence>
            <MoveRobot name="move_robot"/>
        </Sequence>
     </BehaviorTree>
 </root>
 )";
```

## Pitfalls
- `ReadingLaser` must declare the input port `inputlaser` in its `providedPorts()` (the course does not show `test_unit5.cpp`).
- The probability changes only after a rebuild, because the XML is a string in the `.cpp`.
