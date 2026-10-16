---
id: bt-cpp-factory
type: reference
owner: equipo-ros2
updated: 2026-10-15
review_by: 2027-04-13
source: manual
confidentiality: internal
title: "BehaviorTreeFactory and built-in nodes; tick() callbacks"
domain: bt
area: btcpp
distro: humble
tested: false
audience: dev
summary: "What BehaviorTree.CPP does: executor, factory, custom vs built-in nodes, the v3.8 built-in node list, tick() as callback."
tags: [BehaviorTreeFactory, executor, built-in nodes, custom nodes, plugins, bt_factory.h, SetBlackboard, Switch, IfThenElse, tick callback]
see: ["[[bt-cpp-registration]]", "[[bt-design-stack]]", "[[bt-node-types]]", "[[bt-humble-to-jazzy]]"]
requires: [ros2-core]
version_notes:
  - "all: the tick goes down from the root to the leaves (the course says 'up') — https://github.com/BehaviorTree/BehaviorTree.CPP/blob/v3.8/docs/BT_basics.md (BT-V03)"
  - "v4: BlackboardCheck* and SubTreePlus removed; Script, ScriptCondition, Precondition, RunOnce, Sleep, UnsetBlackboard, ParallelAll, Loop* added — https://github.com/BehaviorTree/BehaviorTree.CPP/blob/master/src/bt_factory.cpp (BT-V27)"
---
# BehaviorTreeFactory and built-in nodes; tick() callbacks

**TL;DR** BehaviorTree.CPP helps you build **executors**: components that load a tree at runtime and run it, by wrapping your existing code (for example ROS 2 code) into custom nodes, usually Actions under Conditions. You write the XML and the callbacks; the framework does the rest. Each node type is registered once in the `BehaviorTreeFactory`; the factory already registers the built-in nodes in its constructor.

## Workflow
```text
Robot task
   ↓
Behavior tree (logical flow, XML)
   ↓
Executor: parses the XML into custom or built-in nodes
   ↓
BehaviorTree.CPP framework (communication, logical execution of the nodes)
   node registered in the factory:  BT node i / callback i = custom functionality i or a built-in node
   BT node i  ⇄  ROS node i / robot action i  ⇄  robot
```
- The executor allocates instances of custom or built-in nodes and assembles them into a tree after parsing its text.
- Register each node type once: in the C++ code (statically linked) or at runtime, loading plugins (self-registering dynamic libraries with custom nodes).
- At registration the factory builds a model of each custom node (its ID and ports).

## Built-in nodes (BehaviorTree.CPP 3.8, `bt_factory.cpp`)
```cpp
BehaviorTreeFactory::BehaviorTreeFactory()
{
  parser_ = std::make_shared<XMLParser>(*this);
  registerNodeType<FallbackNode>("Fallback");
  registerNodeType<SequenceNode>("Sequence");
  registerNodeType<SequenceStarNode>("SequenceStar");
  registerNodeType<ParallelNode>("Parallel");
  registerNodeType<ReactiveSequence>("ReactiveSequence");
  registerNodeType<ReactiveFallback>("ReactiveFallback");
  registerNodeType<IfThenElseNode>("IfThenElse");
  registerNodeType<WhileDoElseNode>("WhileDoElse");

  registerNodeType<InverterNode>("Inverter");
  //registerNodeType<RetryNodeTypo>("RetryUntilSuccesful"); //typo but back compatibility
  registerNodeType<RetryNode>("RetryUntilSuccessful");   // correct one
  registerNodeType<KeepRunningUntilFailureNode>("KeepRunningUntilFailure");
  registerNodeType<RepeatNode>("Repeat");
  registerNodeType<TimeoutNode<>>("Timeout");
  registerNodeType<DelayNode>("Delay");

  registerNodeType<ForceSuccessNode>("ForceSuccess");
  registerNodeType<ForceFailureNode>("ForceFailure");

  registerNodeType<AlwaysSuccessNode>("AlwaysSuccess");
  registerNodeType<AlwaysFailureNode>("AlwaysFailure");
  registerNodeType<SetBlackboard>("SetBlackboard");

  registerNodeType<SubtreeNode>("SubTree");
  registerNodeType<SubtreePlusNode>("SubTreePlus");

  registerNodeType<BlackboardPreconditionNode<int>>("BlackboardCheckInt");
  registerNodeType<BlackboardPreconditionNode<double>>("BlackboardCheckDouble");
  registerNodeType<BlackboardPreconditionNode<std::string>>("BlackboardCheckString");
  registerNodeType<BlackboardPreconditionNode<bool>>("BlackboardCheckBool");

  registerNodeType<SwitchNode<2>>("Switch2");
  registerNodeType<SwitchNode<3>>("Switch3");
  registerNodeType<SwitchNode<4>>("Switch4");
  registerNodeType<SwitchNode<5>>("Switch5");
  registerNodeType<SwitchNode<6>>("Switch6");
}
```
The 3.8 source also registers `ManualSelector` when built with ncurses.

| Kind | Built-in IDs |
|---|---|
| Control | Fallback, Sequence, SequenceStar, Parallel, ReactiveSequence, ReactiveFallback, IfThenElse, WhileDoElse, Switch2–Switch6 |
| Decorator | Inverter, RetryUntilSuccessful, KeepRunningUntilFailure, Repeat, Timeout, Delay, ForceSuccess, ForceFailure, BlackboardCheckInt/Double/String/Bool |
| Action | AlwaysSuccess, AlwaysFailure, SetBlackboard |
| Subtree | SubTree, SubTreePlus |

## tick(): every node is a callback
Any TreeNode is a way to run code: you decide what its callback does (command the robot, manage internal processes). The tick is sent **from the root down** the tree until it reaches a leaf, and the statuses come back up. A Sequence ticks its children in order:
```text
Root: tick() 1
└── [→] Sequence
    ├── tick() 2 → node callback (custom node or built-in node) ⇄ ROS node 1, ROS node 2
    ├── tick() 3 → node callback (custom node or built-in node) ⇄ ROS node 3
    └── tick() N → node callback (custom node or built-in node) ⇄ ROS node N
order: tick() 1 → tick() 2 → tick() 3 → … → tick() N
```
(The course text says the tick "travels up the tree until it reaches a leaf node": it travels down.)

## Pitfalls
- Do not register a custom node with a built-in ID: the factory already owns those names.
- `RetryUntilSuccesful` (typo) is commented out in 3.8: use `RetryUntilSuccessful`.
- v4 changes this list; check [[bt-humble-to-jazzy]] before reusing XML on Jazzy, Kilted or Lyrical.
