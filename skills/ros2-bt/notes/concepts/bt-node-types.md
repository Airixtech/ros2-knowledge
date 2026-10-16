---
id: bt-node-types
type: reference
owner: equipo-ros2
updated: 2026-10-15
review_by: 2027-04-13
source: manual
confidentiality: internal
title: "Node types: action, condition, decorator, parallel; status table"
domain: bt
area: concepts
distro: humble
tested: false
audience: dev
summary: "Action, Condition, Decorator, Parallel, Sequence, Fallback: symbols and when each returns SUCCESS, FAILURE or RUNNING."
tags: [action node, condition node, decorator, Inverter, Parallel, success_threshold, failure_threshold, node table, symbols]
see: ["[[bt-sequence-fallback]]", "[[bt-sequence-variants]]", "[[bt-cpp-subtrees-decorators]]", "[[bt-what-is-bt]]"]
requires: [ros2-core]
version_notes:
  - "all: an Action fails if it is impossible to complete (the course table says 'possible') — https://github.com/BehaviorTree/BehaviorTree.CPP/blob/v3.8/docs/BT_basics.md (BT-V06)"
  - "v4: Parallel ports success_count (default -1 = all) and failure_count (1); v3.8: success_threshold (required) and failure_threshold (1) — https://github.com/BehaviorTree/BehaviorTree.CPP/blob/master/include/behaviortree_cpp/controls/parallel_node.h (BT-V31)"
  - "all: a Condition shall not return RUNNING — https://github.com/BehaviorTree/BehaviorTree.CPP/blob/v3.8/docs/BT_basics.md (BT-V43)"
---
# Node types: action, condition, decorator, parallel; status table

**TL;DR** **Actions** do something and return SUCCESS (done), FAILURE (could not) or RUNNING (in progress). **Conditions** check a proposition and return SUCCESS or FAILURE, never RUNNING. A **Decorator** has one child and changes how it is ticked or what it returns (invert, retry N times, time limit).

## Leaves and decorators
- **Action**: carries out a command when ticked. Drawn as a box; the label says what is done.
- **Condition**: evaluates a proposition when ticked. Drawn as an ellipse; the label says what is checked.
- **Decorator**: control flow node with a single child; ticks it according to a rule and may change its status. Drawn as a diamond labelled with the policy, child below. Examples: *Inverter* swaps SUCCESS and FAILURE; *max-N-tries* lets the child fail N times, then returns FAILURE without ticking it; *max-T-sec* lets the child run for T seconds, then returns FAILURE without ticking it. BehaviorTree.CPP versions: [[bt-cpp-subtrees-decorators]].

## Summary table
| Node type | Symbol | Succeeds | Fails | Running |
|---|---|---|---|---|
| Fallback | `[?]` | if one child succeeds | if all children fail | if one child returns RUNNING |
| Sequence | `[→]` | if all children succeed | if one child fails | if one child returns RUNNING |
| Parallel | `[⇉]` | if ≥ M children succeed | if > N − M children fail | else |
| Action | `[ ]` | upon completion | if impossible to complete | during completion |
| Condition | `( )` | if true | if false | never |
| Decorator | `◇` | custom | custom | custom |

N = number of children, M = success threshold (classical formulation). The course table says an action fails "if possible to complete": it fails when completion is **impossible**.

## Parallel in BehaviorTree.CPP v3.8
The threshold is set with ports: `success_threshold` (required: children that must succeed) and `failure_threshold` (default 1: children that must fail). [v4: `success_count` (default −1 = all children) and `failure_count` (default 1)]

## Pitfalls
- A condition that waits for data must still answer at once (SUCCESS or FAILURE); waiting belongs in an action that returns RUNNING.
- Decorators accept exactly one child; wrap several children in a Sequence first.
