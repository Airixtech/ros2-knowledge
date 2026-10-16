---
id: bt-vs-fsm
type: reference
owner: equipo-ros2
updated: 2026-10-15
review_by: 2027-04-13
source: manual
confidentiality: internal
title: "Why behavior trees: FSM limits, modularity, reactivity, readability"
domain: bt
area: concepts
distro: humble
tested: false
audience: dev
summary: "Finite state machines vs behavior trees: transition explosion, coupling; BT modularity, hierarchy, reuse, reactivity, readability, examples."
tags: [FSM, finite state machine, state transitions, modularity, reusability, reactivity, human readable, obstacle avoidance, grab and throw]
see: ["[[bt-what-is-bt]]", "[[bt-sequence-fallback]]", "[[bt-cpp-subtrees-decorators]]", "[[bt-planning-acting]]"]
requires: [ros2-core]
version_notes: []
---
# Why behavior trees: FSM limits, modularity, reactivity, readability

**TL;DR** A finite state machine (FSM) has one active state and labelled transitions between states. With N states there can be N×N transitions, adding or removing a state touches every state that connects to it, and big FSMs become unreadable for people. BTs are hierarchical and modular: any subtree is a reusable action, the order is fixed (top to bottom, left to right) and the tree reacts to changes on every tick.

## FSM example: grab and throw a ball
| State | Event | Next state |
|---|---|---|
| Approach ball | ball close | Grasp ball |
| Grasp ball | ball grasped | Move to destination |
| Move to destination | destination reached | Throw ball |
| Throw ball | ball thrown | **Success** |
| Approach ball / Grasp ball / Move to destination / Throw ball | fault | Wait for help |
| Wait for help | help OK | **Success** |
| Wait for help | help not OK | **Failure** |

An FSM is predictable and observable (you always know the current state), which is why it is still common for robot "brains", algorithms and games.

## Challenges with FSMs
- Up to N×N transitions for N states, and N grows quickly with the execution context.
- Adding or removing a state means changing the conditions of every state that transitions to or from it.
- States are tightly coupled, so they are hard to reuse.
- Large graphical or textual FSMs are too complex for a designer to understand. A computer handles them easily; people do not.

## Same behavior: FSM with 9 transitions vs one BT
```text
FSM (3 states, 9 transitions)                 BT: obstacle detection as a Fallback
Move Left     -- obstacle right --> Move Left     [?] Fallback
Move Left     -- obstacle left  --> Move Right     ├── [→] Sequence
Move Left     -- no obstacle    --> Move Straight  │   ├── (Obstacle right?)
Move Right    -- obstacle left  --> Move Right     │   └── Move left
Move Right    -- obstacle right --> Move Left      ├── [→] Sequence
Move Right    -- no obstacle    --> Move Straight  │   ├── (Obstacle left?)
Move Straight -- no obstacle    --> Move Straight  │   └── Move right
Move Straight -- obstacle right --> Move Left      └── [→] Sequence
Move Straight -- obstacle left  --> Move Right         ├── (No obstacle?)
                                                       └── Move straight
```
Obstacle detection can be a ConditionNode (a leaf returning SUCCESS or FAILURE, as here) or a DecoratorNode that ticks its child only when the internal condition holds.

## Main advantages of BTs
- **Modular**: every subtree is a module that can be designed, implemented, tested and reused one at a time (divide and conquer, from the top subtrees down to the leaves).
- **Hierarchical**: several decision-making layers, following the tree.
- **Reusable**: any subtree can be reused in several places; every leaf returns the same predefined statuses (RUNNING, SUCCESS, FAILURE), which is its whole interface.
- **Reactive**: ticks are created continuously and traverse the tree in a closed loop, so actions start and are cancelled as the statuses of the leaves change; plans computed offline and run open loop often fail in unstructured environments.
- **Human readable**: a coherent, compact structure stays understandable even for big systems, which lowers development and debugging cost.
- BTs use actions instead of states, closer to how people describe behavior and to the interfaces of service-oriented architectures.
- Developers can use and extend the "language" of BT nodes to apply common design patterns.

## Pitfalls
- A BT does not remove the need to design: badly ordered Fallbacks behave as surprisingly as a tangled FSM ([[bt-sequence-fallback]]).
