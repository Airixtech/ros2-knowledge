---
id: bt-sequence-variants
type: reference
owner: equipo-ros2
updated: 2026-10-15
review_by: 2027-04-13
source: manual
confidentiality: internal
title: "Sequence, ReactiveSequence, SequenceStar: restart vs tick again"
domain: bt
area: concepts
distro: humble
tested: false
audience: dev
summary: "Node type hierarchy; what Sequence, ReactiveSequence and SequenceStar do after a child FAILURE or RUNNING; battery example."
tags: [Sequence, ReactiveSequence, SequenceStar, SequenceWithMemory, ReactiveFallback, restart, tick again, memory, bt_u3_ex1]
see: ["[[bt-sequence-fallback]]", "[[bt-reactive-async]]", "[[bt-cpp-blackboard]]", "[[bt-node-types]]"]
requires: [ros2-core]
version_notes:
  - "all: the course hierarchy lists Reactive Sequence twice; the third sequence type is SequenceStar — https://github.com/BehaviorTree/BehaviorTree.CPP/blob/v3.8/docs/SequenceNode.md (BT-V07)"
  - "v4: SequenceStar is SequenceWithMemory (SequenceStar kept as alias) — https://github.com/BehaviorTree/BehaviorTree.CPP/blob/master/src/bt_factory.cpp (BT-V22)"
  - "all: restart / tick again table matches BT.CPP — https://github.com/BehaviorTree/BehaviorTree.CPP/blob/v3.8/docs/SequenceNode.md (BT-V40)"
---
# Sequence, ReactiveSequence, SequenceStar: restart vs tick again

**TL;DR** The three sequences differ only in what the **next** tick does after a child returned FAILURE or RUNNING. Plain **Sequence** restarts after FAILURE and continues with the RUNNING child. **ReactiveSequence** always restarts from the first child (it re-checks the conditions every tick). **SequenceStar** (with memory) never re-ticks children that already succeeded. [v4: SequenceStar is called `SequenceWithMemory`]

## Node type hierarchy (BehaviorTree.CPP)
```text
Tree
├── Control nodes
│   ├── Sequence nodes: Sequence · ReactiveSequence · SequenceStar
│   └── Fallback nodes: Fallback · ReactiveFallback
├── Leaf nodes
│   └── Action nodes: synchronous · asynchronous
└── Decorator nodes: Inverter · ForceSuccess · ForceFailure · Repeat · Retry
```
(The course figure lists "Reactive Sequence" twice; the third type is SequenceStar, as in the table below.)

## What the next tick does
| Control node | Child returns FAILURE | Child returns RUNNING |
|---|---|---|
| Sequence | Restart | Tick again |
| ReactiveSequence | Restart | Restart |
| SequenceStar | Tick again | Tick again |

- **Restart**: the whole sequence starts again from the first child. Children A, B, C, D; A and B succeed, C fails: the next tick ticks A again.
- **Tick again**: the next tick ticks the same child; the earlier children keep their remembered status. Same case: the next tick ticks C, not A and B.
- Fallbacks, from the same docs: Fallback ticks the RUNNING child again, ReactiveFallback restarts ([FallbackNode.md](https://github.com/BehaviorTree/BehaviorTree.CPP/blob/v3.8/docs/FallbackNode.md)).

## Example: avoid an obstacle (`bt_u3_ex1`)
The robot moves straight while reading its laser. If an obstacle is closer than 2 m (condition 1) it must turn; before turning left or right (random choice) it checks that the battery has enough energy (condition 2); then it rotates 90° (action 1) and moves straight again (action 2).
```xml
<root main_tree_to_execute = "MainTree" >
  <BehaviorTree ID="MainTree">
    <Sequence name="root_sequence">
      <Obstacle   name=" Obstacle detected"/>
      <EnoughBattery   name=" Battery OK"/>
      <Rotate       name=" Rotated"/>
      <MoveStraight name=" Moved"/>
    </Sequence>
  </BehaviorTree>
</root>
```
```text
OK. Detected !
is there energy remain?:  Battery OK
rotating 90 deg :  Rotated
moving again straight :  Moved
```
- If condition 1 fails (no obstacle), the Sequence ends with FAILURE and restarts on the next tick.
- If rotating takes 5 s and returns RUNNING, the next tick goes straight to `Rotate` and checks whether it finished: the Sequence remembers that both conditions succeeded and does not check them again. Use a ReactiveSequence when the conditions must be re-checked while the action runs ([[bt-reactive-async]]).
- In a real robot a battery check is more than one SUCCESS/FAILURE call; the example keeps it simple.

## Pitfalls
- A plain Sequence does not notice that a condition became false while a later child is RUNNING: that is what ReactiveSequence is for.
- SequenceStar skips children that already succeeded until the whole sequence finishes, even if the world changed meanwhile.
