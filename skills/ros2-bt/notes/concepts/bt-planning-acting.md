---
id: bt-planning-acting
type: reference
owner: equipo-ros2
updated: 2026-10-15
review_by: 2027-04-13
source: manual
confidentiality: internal
title: "Planning and acting with BTs (PA-BT, backchaining)"
domain: bt
area: concepts
distro: humble
tested: false
audience: dev
summary: "Planning and Acting with Behavior Trees (PA-BT): backchaining from postconditions, expanding the tree at runtime when obstacles appear."
tags: [PA-BT, planning, acting, backchaining, postcondition, precondition, replanning, dynamic environment, tree expansion]
see: ["[[bt-stochastic]]", "[[bt-vs-fsm]]", "[[bt-sequence-fallback]]", "[[bt-learn-unit5]]"]
requires: [ros2-core]
version_notes: []
---
# Planning and acting with BTs (PA-BT, backchaining)

**TL;DR** In a static world every behavior can be modelled in advance. With other agents, a planned action may have unexpected results and make the next one infeasible. Replanning from scratch is expensive; **Planning and Acting with BTs (PA-BT)** instead uses *backchaining*: a goal condition is achieved by the actions whose postcondition it is, each guarded by its preconditions, and the tree is **expanded during execution** when a condition fails. Because BTs are reactive and modular, the parts of the plan that still hold keep running.

## Backchaining template
The postcondition C (Condition 1) can be achieved by Action 1 (preconditions 1 and 2) or by Action 2 (preconditions 3 and 4):
```text
[?] Fallback
├── (Condition 1?)              already true → nothing to do
├── [→] Sequence
│   ├── (Pre Condition 1?)
│   ├── (Pre Condition 2?)
│   └── Action 1
└── [→] Sequence
    ├── (Pre Condition 3?)
    ├── (Pre Condition 4?)
    └── Action 2
```

## Expanding the tree when obstacles appear
First iteration (in the course, `Obstacle?` succeeds when the way is free):
```text
[?] Fallback
├── (Goal?)
└── [→] Sequence
    ├── [?] Fallback
    │   ├── (Obstacle?)
    │   └── [→] Sequence
    │       ├── Avoid obstacle
    │       └── (Collision free?)   ┄┄ expanded with the subtree below when new obstacles appear
    └── Move
```
```text
Extension subtree: "BT extension if new obstacles appear"
[?] Fallback
├── (Obstacle?)
└── [→] Sequence
    ├── Avoid obstacle
    └── (Collision free?)
```
- The goal is reached when one child of the root Fallback succeeds; while the goal is not reached, the Sequence must succeed: the robot checks that the way is free, then moves.
- If the way is not free, the robot avoids the obstacle; when a new obstacle appears the move fails and the tree is extended at that point with the same pattern (the course figure connects it with a dotted line at `Collision free?`).
- The tree is updated **at execution time**: the robot stops and avoids the obstacle without replanning the whole task.

## Pitfalls
- Expanding the tree changes the structure while it runs: keep each expansion a self-contained subtree so the rest of the plan is untouched.
- The course shows the idea with examples, not the full algorithm; for the theory see *Behavior Trees in Robotics and AI: An Introduction* (Colledanchise, Ögren).
