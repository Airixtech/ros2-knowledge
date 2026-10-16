---
id: bt-stochastic
type: reference
owner: equipo-ros2
updated: 2026-10-15
review_by: 2027-04-13
source: manual
confidentiality: internal
title: "Stochastic BTs: success probabilities, Markov chain"
domain: bt
area: concepts
distro: humble
tested: false
audience: dev
summary: "Success probabilities of Fallback and Sequence, choosing the most probable child, worked examples, BT as a memoryless Markov chain."
tags: [stochastic BT, probability, utility, Fallback probability, Sequence probability, Markov chain, memoryless, reliability]
see: ["[[bt-planning-acting]]", "[[bt-sequence-fallback]]", "[[bt-learn-unit5]]", "[[bt-node-types]]"]
requires: [ros2-core]
version_notes:
  - "all: the course writes 0.904 · 0.905; with the stated movement probability 0.95 the product is 0.904 · 0.95 = 0.8588 (BT-V02)"
  - "all: the success-probability figure lists Search Drawer before Open Drawer; the Markov chain opens the drawer first (BT-V11)"
  - "all: Fallback P = 1 − ∏(1 − Pi), Sequence P = ∏ Pi (BT-V45)"
---
# Stochastic BTs: success probabilities, Markov chain

**TL;DR** The children of a Fallback are alternative ways to reach the same result, so their order is often arbitrary. Utility theory says: try first the option that is most useful (performance, cost, time) or, as a natural variant, most likely to succeed. Success probabilities aggregate easily: a **Fallback** succeeds unless all children fail, P = 1 − ∏ᵢ (1 − Pᵢ); a **Sequence** needs all children, P = ∏ᵢ Pᵢ. A probability is a number between 0 (impossible) and 1 (certain).

## Example: choose a way and move
The laser cannot measure reliably, so the control system estimates which way is open: way B 0.8 (8 positive tests out of 10), way A 0.4, way C 0.2. The robot tries B first. Moving succeeds with 0.95 (the battery system can fail).
```text
Fallback (ways B, A, C):  1 − (1 − 0.8)·(1 − 0.4)·(1 − 0.2) = 1 − 0.2·0.6·0.8 = 0.904
Whole tree (choose a way, then move):  0.904 · 0.95 = 0.8588
```
(The course writes the last product as 0.904 · 0.905; with the stated 0.95 the result 0.8588 is correct.) The same computation can run across a whole tree, so the robot can take the most valuable decision at each moment.

The formulas assume each action is tried **once**: a robot that drops an object halfway and picks it up again is not covered.

## Example: search table, then drawer
```text
[?] Fallback                      p = 1 − (1 − 0.1)·(1 − 0.81) = 0.829
├── Search table                  p = 0.1
└── [→] Sequence                  p = 0.9 · 0.9 = 0.81
    ├── Open drawer               p = 0.9
    └── Search drawer             p = 0.9
```
(The course figure lists Search drawer before Open drawer; the task and the Markov chain below open the drawer first. The result does not depend on the order.)

## The same tree as a Markov chain
For a deeper performance analysis, turn the BT into a **Markov chain**: states linked by transition probabilities. Its key property is being memoryless: the probability of the next step does not depend on how the current state was reached.
| From | Success → | Failure → |
|---|---|---|
| Search table | Task succeeded (p = 0.1) | Open drawer (p = 0.9) |
| Open drawer | Search drawer (p = 0.9) | Task failed (p = 0.1) |
| Search drawer | Task succeeded (p = 0.9) | Task failed (p = 0.1) |

Success = 0.1 + 0.9 · 0.9 · 0.9 = 0.829, the same as the tree. Source of the example: *Behavior Trees in Robotics and AI: An Introduction* (Colledanchise, Ögren).

## Pitfalls
- Probabilities ignore cost, execution time and possible negative side effects, which matter as much as the chance of success.
- Course simulation with a laser failure probability on the blackboard: [[bt-learn-unit5]].
