---
id: core-learn-concepts-callbacks
type: reference
owner: equipo-ros2
updated: 2026-10-09
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "Concepts: nodes, callbacks & how ROS 2 runs them"
domain: core
area: learn
distro: humble
tested: false
audience: students
summary: "Plain-language explanation of workspaces/packages/nodes, from functions to classes to callbacks, and how the executor runs callbacks."
tags: [concepts, callbacks, executor, node, students]
see: ["[[core-exec-model]]", "[[core-node-skeleton]]", "[[core-learn-concepts-async]]"]
requires: []
version_notes: []
---
# Concepts: nodes, callbacks & how ROS 2 runs them

**TL;DR** A node *reacts* to events through callbacks. By default ROS 2 runs **one callback at a time**, so a slow callback freezes all the others. The code for all this is in [[core-node-skeleton]] and [[core-exec-model]].

## Node, package, workspace
A workspace contains packages, and packages contain nodes (executables). A node is one process-level unit doing one job (driver, detector, planner). Nodes talk through topics, services, actions and parameters.

## Functions → classes → callbacks
1. Plain function script: `main()` calls `robot_message()` in sequence with `time.sleep` → one task, no state, always busy.
2. Class (`Node` subclass): keeps state (`self.time_robot_on`) between calls, and its methods split the responsibilities.
3. Callbacks: methods that run **when an event happens** (timer tick, message, service request, action goal). The program stops "doing" and starts "reacting".

## What is a callback?
A function you hand to someone else, who decides **when** to call it ("call back"). Pizza analogy: synchronous = waiting at the counter; with a callback = you leave your phone number and they call you when it is ready. Kinds: event callbacks (new laser message), success/error callbacks, iteration callbacks (`map`, `filter`).
```python
def process(data, callback):
    result = [d.upper() for d in data]
    callback(result)            # the caller decides when

process(['ros', 'python'], lambda r: print(r))
```

## How ROS 2 runs callbacks
Events put callbacks in a queue, and the executor runs them. By default there is one thread + one MutuallyExclusive group ⇒ **one callback at a time**. The order is roughly first-come-first-served when things are calm, but not guaranteed under load.
A callback's **period** (how often it is triggered) ≠ its **processing time** (how long it runs). If processing time > period, calls are skipped or delayed.
Real example: a 10 s "search plant" service blocks the camera callback, so the image never updates while the robot turns, and detection fails. The fix is a multithreaded executor + callback groups ([[core-exec-callback-groups]]).

## Multithreading vs callback groups
Threads are workers; callback groups are the rules about which callbacks may overlap. Two workers but one MutuallyExclusive group still means one at a time. A Reentrant group allows overlapping (watch out for shared variables → race conditions). Separate MutuallyExclusive groups: different callbacks overlap, but each one never overlaps itself. Exercises: [[core-learn-unit5-callbacks]], [[core-learn-unit6-multithreading]].
