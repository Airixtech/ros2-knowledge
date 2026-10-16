---
id: bt-reactive-async
type: reference
owner: equipo-ros2
updated: 2026-10-15
review_by: 2027-04-13
source: manual
confidentiality: internal
title: "RUNNING, reactive control nodes and asynchronous actions"
domain: bt
area: concepts
distro: humble
tested: false
audience: dev
summary: "Asynchronous actions return RUNNING; ReactiveFallback and ReactiveSequence re-check earlier children every tick; eat-banana and obstacle examples."
tags: [RUNNING, asynchronous action, ReactiveSequence, ReactiveFallback, halt, EatBanana, TakeDecision, bt_u2_ex4, bt_u3_ex2]
see: ["[[bt-concurrency]]", "[[bt-cpp-async-action]]", "[[bt-sequence-variants]]", "[[bt-sequence-fallback]]"]
requires: [ros2-core]
version_notes:
  - "all: reactive control nodes create no thread; the thread comes from AsyncActionNode — https://github.com/BehaviorTree/BehaviorTree.CPP/blob/v3.8/docs/asynchronous_nodes.md (BT-V04)"
  - "all: the 'BT in action' figure draws a Fallback; the XML that produced the output is a ReactiveFallback — https://github.com/BehaviorTree/BehaviorTree.CPP/blob/v3.8/docs/FallbackNode.md (BT-V09)"
---
# RUNNING, reactive control nodes and asynchronous actions

**TL;DR** A tick travels from the root down to a leaf; the leaf's callback returns SUCCESS, FAILURE or RUNNING. An action that needs time (eating, thinking, moving) is **asynchronous**: it runs on its own thread and returns RUNNING until it is done. **Reactive** control nodes (`ReactiveFallback`, `ReactiveSequence`) tick their earlier children again on every tick, so a condition can interrupt the RUNNING action. Reactive nodes create no thread: the thread belongs to the asynchronous action ([[bt-cpp-async-action]]).

## Example 1: eat something (`bt_u2_ex4`)
Tree generated from the course XML. Legend: `[R?]` ReactiveFallback · `[→]` Sequence · leaves are actions · `key="value"` port.
```text
BehaviorTree "MainTree"
└── [R?] ReactiveFallback name="root"
    ├── EatSandwich name="eat_sandwich"
    ├── EatApple name="eat_apple"
    └── [→] Sequence
        ├── OpenBanana name="open_banana"
        ├── EatBanana  goal="1;2;3"
        └── SaySomething  message="banan is gone!"
```
```xml
<root main_tree_to_execute = "MainTree" >
  <BehaviorTree ID="MainTree">
    <ReactiveFallback name="root">
      <EatSandwich name="eat_sandwich"/>
      <EatApple name="eat_apple"/>
      <Sequence>
        <OpenBanana name="open_banana"/>
        <EatBanana       goal="1;2;3"/>
        <SaySomething   message="banan is gone!" />
      </Sequence>
    </ReactiveFallback>
  </BehaviorTree>
</root>
```
```text
------------ BUILDING A NEW TREE ------------

--- 1st executeTick() ---
EatSandwich: eat_sandwich
EatApple: eat_apple
OpenBanana: open_banana
[ EatBanana: STARTED ]
--- 2nd executeTick() ---
EatSandwich: eat_sandwich
EatApple: eat_apple
[ EatBanana: FINISHED ]

--- 3rd executeTick() ---
EatSandwich: eat_sandwich
EatApple: eat_apple
Robot says: banan is gone!
```
- 1st tick: no sandwich, no apple (both FAILURE); the Sequence opens the banana (SUCCESS) and starts eating it: `EatBanana` returns RUNNING, so the Sequence, the Fallback and the root return RUNNING.
- Next ticks: the **reactive** Fallback asks again for the sandwich and the apple (that is why they print every time); the Sequence continues with its RUNNING child, so `OpenBanana` is not ticked again.
- When `EatBanana` returns SUCCESS, `SaySomething` runs and the whole tree succeeds.
- The course figure draws the root as a plain Fallback; the XML (and the repeated `EatSandwich`/`EatApple` lines) show a ReactiveFallback.

## Example 2: obstacle and decision (`bt_u3_ex2`)
```text
[R→] ReactiveSequence
 ├── (Obstacle?)
 └── TakeDecision   asynchronous: "thinking" for 5 s on its own thread
```
Course timeline (one tick per second):
| Time | Obstacle? | TakeDecision | ReactiveSequence returns |
|---|---|---|---|
| tick 1 s | SUCCESS | RUNNING (counter = 1) | RUNNING |
| tick 2 s | SUCCESS | RUNNING (counter = 2) | RUNNING |
| tick 3 s | SUCCESS | RUNNING (counter = 3, 4, 5 while the thread keeps counting) | RUNNING |
| 5 s | — | SUCCESS (thinking finished) | SUCCESS |
```text
------------ BUILDING A NEW TREE ------------
OK. Detected !

--- 1st executeTick() ---
OK. Detected !
thinking for :: 0

--- 2nd executeTick() ---
OK. Detected !

--- 3rd executeTick() ---
OK. Detected !
thinking for :: 1
thinking for :: 2
thinking for :: 3
thinking for :: 4
```
Every tick re-checks the obstacle (it prints `OK. Detected !` each time) while the thinking counter advances on its own thread; the tree learns the final SUCCESS on the tick after the thread finished. If the condition failed during the thinking, the ReactiveSequence would halt `TakeDecision` and return FAILURE.

## Pitfalls
- A plain Sequence would tick only `TakeDecision` again and miss a condition that changed ([[bt-sequence-variants]]).
- An asynchronous action must stop when halted; otherwise the reactive interruption has no effect ([[bt-cpp-async-action]]).
