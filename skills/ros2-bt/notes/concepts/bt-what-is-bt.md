---
id: bt-what-is-bt
type: reference
owner: equipo-ros2
updated: 2026-10-15
review_by: 2027-04-13
source: manual
confidentiality: internal
title: "What a behavior tree is: tick, SUCCESS/FAILURE/RUNNING, control and execution nodes"
domain: bt
area: concepts
distro: humble
tested: false
audience: dev
summary: "Behavior tree definition: root, ticks, SUCCESS/FAILURE/RUNNING, control vs execution nodes, abstraction stack, pick-ball example."
tags: [behavior tree, BT, tick, SUCCESS, FAILURE, RUNNING, control flow node, execution node, abstraction stack, pick ball]
see: ["[[bt-sequence-fallback]]", "[[bt-node-types]]", "[[bt-app-architecture]]", "[[bt-vs-fsm]]"]
requires: [ros2-core]
version_notes: []
order: 1
---
# What a behavior tree is: tick, SUCCESS/FAILURE/RUNNING, control and execution nodes

**TL;DR** A behavior tree (BT) is a directed rooted tree. Internal nodes are **control flow nodes**, leaves are **execution nodes** (Action, Condition). The root sends **ticks** at a given frequency; a node runs only when it is ticked and answers its parent with **SUCCESS** (goal met), **FAILURE** or **RUNNING** (still in progress). Read a tree top to bottom, left to right.

## Definition
- The root is the only node without a parent; every other node has exactly one parent; every control flow node has at least one child. Children are drawn below their parent.
- Classical formulation: four control flow nodes (Sequence, Fallback, Parallel, Decorator) and two execution nodes (Action, Condition): [[bt-node-types]].
- Sequence ≈ logical AND (all children must succeed), Fallback ≈ logical OR (one child succeeding is enough): [[bt-sequence-fallback]].
- BTs come from games and are used in robotics and AI; the framework used here is BehaviorTree.CPP ([behaviortree.dev](https://www.behaviortree.dev/)).

## Where BTs sit: abstraction stack
Abstraction grows from bottom to top:
```text
1. Human & robot application requirements      (highest abstraction)
2. Behavior tree: logical flow (XML)
3. Behavior tree: implementation (framework, BehaviorTree.CPP)
4. Tasks: program functions of the robot
5. Robot                                       (lowest abstraction)
```
People stay at the top: the application requirements flow down, and with their skills and the BT concepts they design level 2 (the logical connections between robot tasks, written in XML); the framework (level 3) runs it; level 4 is your C++ code. Seen from the program, the BT organizes the robot's transitions between tasks (simple components).

## Example: pick a ball
The robot must find, pick and place a ball. Picking needs two steps, each guarded by a condition: approach the ball until it is close, then grasp it until it is grasped.

Tree generated from the course XML of `bt_u2_ex1` ([[bt-cpp-first-program]]). Legend: `[→]` Sequence · `[?]` Fallback · `(Name?)` condition · other leaves are actions · `name="…"` instance name.
```text
BehaviorTree "MainTree"
└── [→] Sequence name="root_sequence"
    ├── FindBall name="ball_ok"
    ├── [→] Sequence
    │   ├── [?] Fallback
    │   │   ├── (BallClose?) name="no_ball"
    │   │   └── ApproachBall name="approach_ball"
    │   └── [?] Fallback
    │       ├── (BallGrasped?) name="no_grasp"
    │       └── GraspBall name="grasp_ball"
    └── PlaceBall name="ball_placed"
```
- Every child of a Sequence must succeed for its branch to succeed.
- A Fallback stops at the first child that succeeds: if the ball is already close, `ApproachBall` is not ticked.
- The whole tree succeeds when `PlaceBall` succeeds.
- Composing simple components lets you orchestrate the robot's behavior while it interacts with the environment; mapping the tasks into a hierarchical tree makes complex tasks easy for people to understand and model (higher-level abstraction programming).

## Pitfalls
- A node that is not ticked does nothing: there is no background execution unless the node itself is asynchronous ([[bt-reactive-async]]).
- RUNNING is a normal answer, not an error: the parent decides what to do with it ([[bt-sequence-variants]]).
- Conditions only answer SUCCESS or FAILURE, never RUNNING ([[bt-node-types]]).
