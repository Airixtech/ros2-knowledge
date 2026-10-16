---
id: bt-concurrency
type: reference
owner: equipo-ros2
updated: 2026-10-15
review_by: 2027-04-13
source: manual
confidentiality: internal
title: "Concurrency in BehaviorTree.CPP: single-threaded engine, halt, RUNNING propagation"
domain: bt
area: concepts
distro: humble
tested: false
audience: dev
summary: "Concurrency vs parallelism; BehaviorTree.CPP ticks on one thread, a blocking tick() blocks the tree, long actions return RUNNING."
tags: [concurrency, parallelism, single-threaded, blocking tick, RUNNING, halt, propagation, asynchronous]
see: ["[[bt-reactive-async]]", "[[bt-cpp-async-action]]", "[[bt-ros2-shared-node]]", "[[bt-design-stack]]"]
requires: [ros2-core]
version_notes:
  - "all: the tree execution engine is single-threaded; long actions return RUNNING — https://github.com/BehaviorTree/BehaviorTree.CPP/blob/v3.8/docs/asynchronous_nodes.md (BT-V42)"
  - "all: RUNNING-propagation figure puts Place ball before Pick ball and Ball close? SUCCESS before Approach ball RUNNING — https://github.com/BehaviorTree/BehaviorTree.CPP/blob/v3.8/docs/FallbackNode.md (BT-V15)"
---
# Concurrency in BehaviorTree.CPP: single-threaded engine, halt, RUNNING propagation

**TL;DR** BehaviorTree.CPP gives **concurrency**, not parallelism: the tree engine runs on one thread and calls every `tick()` one after the other. If a `tick()` blocks, the whole tree blocks. An action that takes time must return RUNNING at once ("started"), be checked again on the next tick, and stop as soon as its `halt()` is called.

## Concurrency vs parallelism
Three tasks (1, 2, 3) to run:
```text
Concurrent execution: one CPU, instructions interleaved in time
  CPU: 1 2 1 2 3 3 3 1 2 3 1 2 2 3  → time
Parallel execution: three CPUs, each task runs at the same time
  CPU 1: 3 3 3 3 3 …                → time
  CPU 2: 2 2 2 2 2 …
  CPU 3: 1 1 1 1 1 …
```
Concurrency gives the appearance of simultaneity by switching between tasks; parallelism runs them literally at the same time on several cores to go faster.

## Rules of the engine
- The tree execution engine is single-threaded.
- All `tick()` methods run sequentially: a blocked `tick()` blocks the entire execution.
- A long action returns RUNNING (not SUCCESS or FAILURE): the activity has started; when ticked again it checks whether it is complete.
- A RUNNING action must stop immediately when its `halt()` is invoked; you implement that ([[bt-cpp-async-action]]).
- Reactive behaviors come from asynchronous execution plus "concurrency": for example, the robot keeps deciding while a condition (obstacle detected) is checked on every tick ([[bt-reactive-async]]).

## RUNNING goes up the whole tree
```text
Root                                  ↑ RUNNING
└── [→] Sequence                      ↑ RUNNING
    ├── Find ball                     ↑ SUCCESS
    ├── Pick ball (subtree)           ↑ RUNNING
    │   └── [→] Sequence              ↑ RUNNING
    │       ├── [?] Fallback          ↑ RUNNING
    │       │   ├── (Ball close?)     ↑ FAILURE
    │       │   └── Approach ball     ↑ RUNNING   ← asynchronous action
    │       └── [?] Fallback          not ticked
    │           ├── (Ball grasped?)
    │           └── Grasp ball
    └── Place ball                    not ticked
```
The course figure draws Place ball (SUCCESS) before Pick ball, and Ball close? returning SUCCESS next to the RUNNING Approach ball. With Sequence and Fallback semantics, Approach ball is ticked only after Ball close? fails, and Place ball is ticked only after Pick ball succeeds ([[bt-sequence-fallback]]).

## Pitfalls
- `std::this_thread::sleep_for()` inside a `tick()` freezes every node, not only that one (the course's ROS 2 nodes do this: [[bt-ros2-node-pattern]]).
- Waiting for a ROS 2 reply inside `tick()` (spinning until a future completes) has the same effect; poll with `spin_some()` and return RUNNING instead ([[bt-ros2-shared-node]]).
