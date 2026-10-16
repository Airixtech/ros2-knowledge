---
id: bt-humble-to-jazzy
type: reference
owner: equipo-ros2
updated: 2026-10-15
review_by: 2027-04-13
source: manual
confidentiality: internal
title: "BehaviorTree.CPP v3 (Humble) to v4 (Jazzy, Lyrical)"
domain: bt
area: migration
distro: humble
tested: false
audience: dev
summary: "Port BehaviorTree.CPP v3 code and XML to v4: packages, BTCPP_format, renamed nodes and classes, tick methods, SubTree remapping, Groot2."
tags: [migration, BehaviorTree.CPP v4, behaviortree_cpp, BTCPP_format, SequenceWithMemory, ThreadedAction, NodeConfig, tickWhileRunning, convert_v3_to_v4.py, Groot2]
see: ["[[bt-cpp-factory]]", "[[bt-cpp-port-remapping]]", "[[bt-cpp-groot-logging]]", "[[bt-ros2-shared-node]]"]
requires: [ros2-core]
version_notes:
  - "all: v3 released for Humble (3.8.7) and Jazzy (3.8.8), v4 (4.10.0) for Humble to Lyrical; Kilted and Lyrical have no v3 — https://github.com/ros/rosdistro/blob/master/jazzy/distribution.yaml (BT-V20)"
  - "v4: tickOnce/tickExactlyOnce/tickWhileRunning — https://github.com/BehaviorTree/BehaviorTree.CPP/blob/master/include/behaviortree_cpp/bt_factory.h (BT-V21)"
  - "v4: SequenceStar → SequenceWithMemory — https://github.com/BehaviorTree/BehaviorTree.CPP/blob/master/convert_v3_to_v4.py (BT-V22)"
  - "v4: AsyncActionNode → ThreadedAction — https://github.com/BehaviorTree/BehaviorTree.CPP/blob/master/include/behaviortree_cpp/action_node.h (BT-V23)"
  - "v4: NodeConfiguration → NodeConfig — https://github.com/BehaviorTree/BehaviorTree.CPP/blob/master/include/behaviortree_cpp/tree_node.h (BT-V24)"
  - "v4: <root BTCPP_format=\"4\"> — https://github.com/BehaviorTree/BehaviorTree.CPP/blob/master/src/xml_parsing.cpp (BT-V25)"
  - "v4: SubTree remapping with {} and _autoremap — https://github.com/BehaviorTree/BehaviorTree.CPP/blob/master/convert_v3_to_v4.py (BT-V26)"
  - "v4: built-in node list changes — https://github.com/BehaviorTree/BehaviorTree.CPP/blob/master/src/bt_factory.cpp (BT-V27)"
  - "v4: FileLogger2 (.btlog), Groot2Publisher — https://github.com/BehaviorTree/BehaviorTree.CPP/tree/master/include/behaviortree_cpp/loggers (BT-V28)"
  - "v4: registerNodeType<T>(ID, args...), applyVisitor — https://github.com/BehaviorTree/BehaviorTree.CPP/blob/master/include/behaviortree_cpp/bt_factory.h (BT-V29)"
---
# BehaviorTree.CPP v3 (Humble) to v4 (Jazzy, Lyrical)

**TL;DR** The library version, not the ROS distro, decides the API: Humble and Jazzy release both `behaviortree_cpp_v3` (3.8) and `behaviortree_cpp` (4.10); Kilted and Lyrical only v4. Nav2 links v3 in Humble and v4 from Jazzy. Porting means: new package and include paths, `BTCPP_format="4"` in the XML, a few renamed nodes and classes, new tick methods, braces in SubTree remapping, and Groot2 instead of Groot 1. The official script `convert_v3_to_v4.py` converts the XML.

## Availability
| | Humble | Jazzy | Kilted | Lyrical |
|---|---|---|---|---|
| `behaviortree_cpp_v3` (v3.8) | 3.8.7 | 3.8.8 | — | — |
| `behaviortree_cpp` (v4) | 4.10.0 | 4.10.0 | 4.10.0 | 4.10.0 |
| BT.CPP used by Nav2 | v3 | v4 | v4 | v4 |

## C++ changes
| v3.8 | v4 |
|---|---|
| package `behaviortree_cpp_v3`, `#include "behaviortree_cpp_v3/bt_factory.h"` | package `behaviortree_cpp`, `#include "behaviortree_cpp/bt_factory.h"` |
| `tree.tickRoot()` (+ `tickRootWhileRunning()`) | `tree.tickOnce()`, `tree.tickExactlyOnce()`, `tree.tickWhileRunning()` |
| `AsyncActionNode` | `ThreadedAction` (alias `AsyncActionNode` kept); `StatefulActionNode` in both |
| `NodeConfiguration` | `NodeConfig` (alias kept) |
| `getInput<T>()` → `Optional<T>` | `Expected<T>` (same use: `if(!res) … res.error()`) |
| `registerBuilder` + loop over `tree.nodes` to call `init()` | `registerNodeType<T>("ID", args…)` (extra constructor arguments); `tree.applyVisitor(…)` |
| `FileLogger` → `.fbl` (Groot 1); `PublisherZMQ` (live) | `FileLogger2` → `.btlog` (Groot2); `Groot2Publisher` (live) |

## XML changes
| v3.8 | v4 |
|---|---|
| `<root main_tree_to_execute="MainTree">` | `<root BTCPP_format="4" main_tree_to_execute="MainTree">` (without it: a warning) |
| `<SequenceStar>` | `<SequenceWithMemory>` (`SequenceStar` still accepted) |
| `<SubTree ID="X" target="move_goal"/>` | `<SubTree ID="X" target="{move_goal}"/>` |
| `<SubTree … __shared_blackboard="true"/>`, `<SubTreePlus … __autoremap="1"/>` | `<SubTree … _autoremap="1"/>` (`SubTreePlus` removed) |
| `BlackboardCheckInt/Double/String/Bool` | removed: use `Precondition` or `Script`/`ScriptCondition` |
| Parallel ports `success_threshold`, `failure_threshold` | `success_count` (default −1 = all), `failure_count` |

New v4 built-ins include `Script`, `ScriptCondition`, `Precondition`, `RunOnce`, `Sleep`, `UnsetBlackboard`, `ParallelAll`, `TryCatch` and `LoopInt`/`LoopBool`/`LoopDouble`/`LoopString`. The attributes `_successIf`, `_failureIf`, `_skipIf`, `_while`, `_onSuccess`, `_onFailure`, `_onHalted` and `_post` are reserved for scripts in v4: a v3 node with a port of that name must be renamed before converting.

## Converting XML files
```bash
python3 convert_v3_to_v4.py -i old_tree.xml -o new_tree.xml
```
The script ([convert_v3_to_v4.py](https://github.com/BehaviorTree/BehaviorTree.CPP/blob/master/convert_v3_to_v4.py)) adds `BTCPP_format="4"`, renames `SequenceStar`, adds braces to SubTree remapping and converts `SubTreePlus` and `__shared_blackboard` to `_autoremap`, warning where behavior may change. Without an output file it prints to stdout.

## Checklist
1. Change `package.xml` / CMake dependencies and every include path to `behaviortree_cpp`.
2. Run the XML through the converter; review its warnings and every SubTree.
3. Replace `tickRoot()` loops with `tickWhileRunning()` or `tickOnce()` + `sleep()`.
4. Replace `BlackboardCheck*` nodes and `SubTreePlus`.
5. Switch logs and the editor to `FileLogger2` / Groot2.
6. ROS 2 nodes: keep the shared-node pattern or move to BehaviorTree.ROS2 (needs ≥ 4.6) ([[bt-ros2-shared-node]]).

## Pitfalls
- Do not mix v3 and v4 nodes in one tree; build each executable against one library version.
- Groot 1 is not expected to work with v4 trees; Groot2 is the editor for v4 ([[bt-cpp-groot-logging]]).
