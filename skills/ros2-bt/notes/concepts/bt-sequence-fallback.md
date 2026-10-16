---
id: bt-sequence-fallback
type: reference
owner: equipo-ros2
updated: 2026-10-15
review_by: 2027-04-13
source: manual
confidentiality: internal
title: "Sequence and Fallback: tick flow, XML, examples"
domain: bt
area: concepts
distro: humble
tested: false
audience: dev
summary: "Sequence (AND) and Fallback (OR): which children get ticked, what each returns, XML and exercise outputs."
tags: [Sequence, Fallback, Selector, AND, OR, tick flow, RobotTask, bt_u2_ex2, bt_u2_ex3]
see: ["[[bt-sequence-variants]]", "[[bt-node-types]]", "[[bt-what-is-bt]]", "[[bt-learn-unit2]]"]
requires: [ros2-core]
version_notes:
  - "all: Fallback 'Execution 1' figure lists Task 3 twice; children are Task 1, Task 2, Task 3 and only Task 1 is ticked — https://github.com/BehaviorTree/BehaviorTree.CPP/blob/v3.8/docs/FallbackNode.md (BT-V08)"
  - "all: exercise 2 analysis says task1 succeeds and task2 fails; the output and code show task1 FAILURE stops the Sequence — course code in this note (BT-V14)"
---
# Sequence and Fallback: tick flow, XML, examples

**TL;DR** **Sequence** `[→]` ticks its children from the left until one returns FAILURE or RUNNING, and returns that; it returns SUCCESS only if all children succeed (logical AND). **Fallback** `[?]` ticks its children from the left until one returns SUCCESS or RUNNING, and returns that; it returns FAILURE only if all children fail (logical OR). In both, the children after the one that stopped them are not ticked.

## Sequence
```text
Execution 1                          Execution 2
[→] Sequence → SUCCESS               [→] Sequence → FAILURE
 ├── Task 1  ↓tick ↑SUCCESS           ├── Task 1  ↓tick ↑SUCCESS
 ├── Task 2  ↓tick ↑SUCCESS           ├── Task 2  ↓tick ↑FAILURE
 └── Task 3  ↓tick ↑SUCCESS           └── Task 3  not ticked
```
```xml
<root main_tree_to_execute = "MainTree" >
  <BehaviorTree ID="MainTree">
    <Sequence name="root_sequence">
      <RobotTask1   name="task1"/>
      <RobotTask2   name="task2"/>
      <RobotTask3   name="task3"/>
    </Sequence>
  </BehaviorTree>
</root>
```

## Fallback
```text
Execution 1                          Execution 2
[?] Fallback → SUCCESS               [?] Fallback → SUCCESS
 ├── Task 1  ↓tick ↑SUCCESS           ├── Task 1  ↓tick ↑FAILURE
 ├── Task 2  not ticked               ├── Task 2  ↓tick ↑SUCCESS
 └── Task 3  not ticked               └── Task 3  not ticked
```
(The course figure of Execution 1 lists "Task 3" twice; the second child is Task 2.)
```xml
<root main_tree_to_execute = "MainTree" >
  <BehaviorTree ID="MainTree">
    <Fallback name="root_sequence">
      <RobotTask1   name="task1"/>
      <RobotTask2   name="task2"/>
      <RobotTask3   name="task3"/>
    </Fallback>
  </BehaviorTree>
</root>
```

## The task nodes and the two runs
Each task prints its name and returns a fixed status; change the returned values and compare the outputs:
```cpp
BT::NodeStatus RobotTask1::tick()
{
  std::cout << "RobotTask1: " << this->name() << std::endl;
  return BT::NodeStatus::FAILURE;
}
BT::NodeStatus RobotTask2::tick()
{
  std::cout << "RobotTask2: " << this->name() << std::endl;
  return BT::NodeStatus::FAILURE;
}
BT::NodeStatus RobotTask3::tick()
{
  std::cout << "RobotTask3: " << this->name() << std::endl;
  return BT::NodeStatus::SUCCESS;
}
```
- Sequence (`./bt_u2_ex2`) prints only `RobotTask1: task1`: task1 returns FAILURE, so the Sequence fails at once and task2 is never ticked. (The course's analysis says task1 succeeds and task2 fails "without printing"; every `tick()` prints first, so task2 was not ticked.)
- Fallback (`./bt_u2_ex3`) prints `RobotTask1: task1` and `RobotTask2: task2`: task1 fails, task2 succeeds (its flag is SUCCESS in that program), the Fallback succeeds and task3 is not ticked.

## Pitfalls
- Order matters: put cheap checks first in a Sequence and the preferred alternative first in a Fallback.
- A RUNNING child stops both nodes too: the next tick continues from that child ([[bt-sequence-variants]]).
