# Version audit — ros2-bt (Phase 1)

> Date: 2026-10-14.
> Scope: every version-dependent statement of the course wiki "Behavior Trees in ROS 2" (not published):
> behavior tree concepts, BehaviorTree.CPP XML and C++ API, Groot, the course's ROS 2 integration code and its
> stochastic-BT unit. Section IDs: `Pnn.Smm` = course page and section.
> Baseline: **Humble is canonical**, with **BehaviorTree.CPP v3.8** (`behaviortree_cpp_v3`), the version the course
> uses and the one Nav2 Humble links. v4 (`behaviortree_cpp`) differences are annotated, not substituted.
> Generic ROS 2 rows are in [version_audit.md](version_audit.md) (IDs `Vnn`); this report cites them instead of repeating them.

## Method
- Primary sources: `BehaviorTree/BehaviorTree.CPP` on the `v3.8` branch (package 3.8.8: `src/bt_factory.cpp`,
  `action_node.h/.cpp`, `bt_factory.h`, `tree_node.h`, `controls/parallel_node.h`, `loggers/`, and its `docs/`:
  `BT_basics.md`, `SequenceNode.md`, `FallbackNode.md`, `xml_format.md`, `asynchronous_nodes.md`, tutorials 01–08)
  and on `master` (4.10.0: the same files, `src/xml_parsing.cpp`, and the official converter `convert_v3_to_v4.py`),
  `BehaviorTree/BehaviorTree.ROS2` (`humble` branch), `BehaviorTree/Groot` (`master`), `ros-navigation/navigation2`
  (`humble`, `jazzy`: `nav2_behavior_tree`), `ros2/geometry2` (`humble`), the rosdistro `distribution.yaml` of
  Humble, Jazzy, Kilted and Lyrical, and the packages.ros.org apt index for Jammy.
- Course arithmetic and diagrams were checked against the course's own XML, code and expected outputs: when a
  diagram disagrees with the XML that produced the output, the XML wins.
- Actions: **keep** = correct for Humble · **annotate** = correct for Humble (v3), add a v4 mark · **fix** = wrong
  for Humble itself (or a course mistake). Confidence: High (read in code/docs) · Medium (inferred) · `[verify]` (Phase 5).
- The original wiki is not edited (and not part of this repo). Fixes and marks live in the notes; each row ID
  becomes a `version_notes` entry in the affected note.

## Distro baseline (BehaviorTree.CPP)
| | Humble | Jazzy | Kilted | Lyrical |
|---|---|---|---|---|
| Release – EOL | May 2022 – **May 2027** | May 2024 – May 2029 | May 2025 – Nov 2026 | May 2026 – May 2031 |
| `behaviortree_cpp_v3` (v3.8) released | ✓ 3.8.7 | ✓ 3.8.8 | ✗ | ✗ |
| `behaviortree_cpp` (v4) released | ✓ 4.10.0 | ✓ 4.10.0 | ✓ 4.10.0 | ✓ 4.10.0 |
| BT.CPP linked by Nav2 | v3 | v4 | v4 | v4 |
| Groot | Groot 1 (v3 only, source build, maintenance mode); Groot2 for v4 | Groot2 | Groot2 | Groot2 |
| `BehaviorTree.ROS2` | source only (needs BT.CPP ≥ 4.6) | source only | source only | source only |
| Sources | [rosdistro humble][rd-h], [jammy apt][apt-j], [nav2 humble package.xml][n2-h] | [rosdistro jazzy][rd-j], [nav2 jazzy package.xml][n2-j] | [rosdistro kilted][rd-k] | [rosdistro lyrical][rd-l] |

## Real Humble errors (fix)
| ID | Section | Error in the course | Correct Humble statement |
|---|---|---|---|
| BT-V01 | P21.S05 | `AnalyzeCPU::halt()` overrides the base method with `_halt_requested.store(false)`, and `tick()` checks that same private flag | The flag never becomes `true`, so a halt never stops the loop; the base `AsyncActionNode::halt()` (sets the flag and waits for the thread) is never called. v3.8: in `tick()` check `isHaltRequested()`; if you override `halt()`, call `AsyncActionNode::halt()`; a halted async action should return `IDLE`. |
| BT-V02 | P22.S02 | "for BT: 0.904 · 0.905 = 0.8588" | The text gives 0.95 for the movement: 0.904 · 0.95 = 0.8588 (0.905 is a typo). |
| BT-V03 | P21.S02 | "A tick signal is transmitted to the tree's root and travels **up** the tree until it reaches a leaf" | The tick goes **down** from the root to the leaves; the statuses (SUCCESS, FAILURE, RUNNING) go back up. |
| BT-V04 | P21.S05 | "Running a reactive node (ReactiveSequence or ReactiveFallback) allows you to run tasks in a separate thread" | The thread comes from `AsyncActionNode`. A reactive control node ticks its earlier children (conditions) again on every tick and halts the RUNNING child when one of them fails; it creates no thread. |
| BT-V05 | P20.S08 | `source …/devel/setup.bash` + `rosrun groot Groot` | That is a ROS 1 workspace and command of the course platform. No ROS 2 distro releases a Groot package. Groot 1 is in maintenance mode, works only with BT.CPP 3.8 and its colcon build is "discouraged"; BT.CPP v4 uses Groot2 (standalone application from behaviortree.dev). |
| BT-V06 | P10.S00 | Node table: Action "Fails: If possible to complete" | An action fails if it is **impossible** to complete (succeeds upon completion, RUNNING during completion). |
| BT-V07 | P19.S04 | Node type hierarchy lists "Reactive Sequence" twice under Sequence node | The third sequence type is **SequenceStar** (the table right below lists Sequence, ReactiveSequence, SequenceStar). |
| BT-V08 | P05.S00 | Fallback "Execution 1" diagram: children "Task 1 (SUCCESS), Task 3, Task 3" | Children are Task 1, Task 2, Task 3; after Task 1 returns SUCCESS, Task 2 and Task 3 are not ticked. |
| BT-V09 | P07.S00 | "BT in action" diagram root is a **Fallback** | The XML that produced the output uses **ReactiveFallback**: that is why the 2nd and 3rd ticks tick `EatSandwich` and `EatApple` again before the RUNNING `EatBanana`. |
| BT-V10 | P20.S06 | Snippet `<Inverter></Inverter><RetryUntilSuccessful num_attempts="4"><RetryUntilSuccessful>` | Not well-formed XML: the second tag must be a closing tag, and a decorator has exactly one child: `<RetryUntilSuccessful num_attempts="4"><Measuring/></RetryUntilSuccessful>` (as in the full XML of the same section). |
| BT-V11 | P22.S03 | Success-probability tree: Sequence children "Search Drawer, Open Drawer" | The Markov chain of the same section (and the task) opens the drawer first: Sequence = Open Drawer → Search Drawer. The probability (0.9 · 0.9 = 0.81) does not depend on the order. |
| BT-V12 | P16.S00, P23.S00 | ROS 2 pattern: each BT node class is also an `rclcpp::Node`; the tree's own instances are never spun (only the separate `lc_listener`/`lc_odom` objects), so data reaches the tree through global variables; several nodes share one name (`scanner_node` for every `ReadingLaser`, `rotating_node` for `MoveRobot` and `Rotating` in the project); a publisher is created on every tick; `sleep_for` inside `tick()` | The code runs, but: the tree's subscriptions are dead code, nodes with the same name collide (`ros2 node list` warns; their parameter services share names), and a sleeping `tick()` blocks the whole single-threaded tree (the course's own rule in P20.S03). Pattern used by Nav2 Humble (BT.CPP v3): one `rclcpp::Node` stored in the blackboard under `"node"`; each BT node takes it in its constructor, creates its publishers/subscriptions once with its own callback group and `SingleThreadedExecutor`, and calls `spin_some()` in `tick()`. v4: `BehaviorTree.ROS2` (`RosTopicSubNode`, `RosActionNode`, `RosNodeParams`). |
| BT-V13 | P21.S04, P21.S05 | "The default (and recommended) way … inheritance (SyncActionNode or **AsyncActionNode**)" | v3.8's own header: `AsyncActionNode` is "quite hard to implement correctly"; `StatefulActionNode` (`onStart`/`onRunning`/`onHalted`) is "the preferred way to implement asynchronous Actions". `SyncActionNode` stays the default for actions that finish in one tick. |

## Full table
| # | Section | Statement | Humble (v3.8) | Jazzy | Lyrical | Action | Source | Confidence |
|---|---|---|---|---|---|---|---|---|
| BT-V01 | P21.S05 | `halt()` with `store(false)` | ✗ (see fix table) | ✗ same (v4 `ThreadedAction` same rule) | ✗ same | **fix** | [action_node.h v3.8][an3], [action_node.cpp v3.8][anc3] | High |
| BT-V02 | P22.S02 | 0.904 · 0.905 | ✗ 0.904 · 0.95 | — | — | **fix** | arithmetic in the section | High |
| BT-V03 | P21.S02 | tick travels up | ✗ down | — | — | **fix** | [BT_basics v3.8][basics3] | High |
| BT-V04 | P21.S05 | reactive node = separate thread | ✗ thread = AsyncActionNode | ✗ same | ✗ same | **fix** | [asynchronous_nodes v3.8][async3], [SequenceNode v3.8][seq3] | High |
| BT-V05 | P20.S08 | `rosrun groot Groot` | ✗ ROS 1; no ROS 2 Groot package | Groot2 | Groot2 | **fix** | [Groot README][groot], [rosdistro humble][rd-h] | High |
| BT-V06 | P10.S00 | Action fails "if possible to complete" | ✗ impossible | — | — | **fix** | node semantics ([BT_basics v3.8][basics3]) | Medium |
| BT-V07 | P19.S04 | hierarchy: Reactive Sequence twice | ✗ SequenceStar | — | — | **fix** | [SequenceNode v3.8][seq3] | High |
| BT-V08 | P05.S00 | Fallback diagram "Task 3, Task 3" | ✗ Task 2, Task 3 | — | — | **fix** | [FallbackNode v3.8][fb3] | High |
| BT-V09 | P07.S00 | diagram Fallback vs XML ReactiveFallback | ✗ ReactiveFallback | — | — | **fix** | course XML and output, [FallbackNode v3.8][fb3] | High |
| BT-V10 | P20.S06 | malformed `RetryUntilSuccessful` snippet | ✗ closing tag, one child | — | — | **fix** | [xml_format v3.8][xml3] | High |
| BT-V11 | P22.S03 | Search Drawer before Open Drawer | ✗ Open → Search | — | — | **fix** | Markov chain of the same section | Medium |
| BT-V12 | P16.S00, P23.S00 | BT node = `rclcpp::Node`, globals, never-spun tree nodes | ✗ works, fragile (see fix table) | v4: BehaviorTree.ROS2 | same | **fix** | course code, [IsBatteryLowCondition (nav2 humble)][n2-batt], [BehaviorTree.ROS2][btros2] | High |
| BT-V13 | P21.S04, P21.S05 | AsyncActionNode "recommended" | ✗ StatefulActionNode preferred | `ThreadedAction` (alias `AsyncActionNode`) | same | **fix** | [action_node.h v3.8][an3] | High |
| BT-V20 | P01.S02, P02.S01 | package and headers `behaviortree_cpp_v3`, `behaviortree_cpp_v3/bt_factory.h` | ✓ v3.8 (Humble also ships v4 as `behaviortree_cpp`) | both released; Nav2 uses v4 | v4 only (`behaviortree_cpp/bt_factory.h`) | annotate | [rosdistro humble][rd-h], [rosdistro lyrical][rd-l], [nav2 jazzy package.xml][n2-j] | High |
| BT-V21 | P02.S01, P16.S00 | `tree.tickRoot()` (one tick) | ✓ (+ `tickRootWhileRunning()`) | v4: `tickOnce()`, `tickExactlyOnce()`, `tickWhileRunning()` | same | annotate | [bt_factory.h v3.8][f3], [bt_factory.h v4][f4] | High |
| BT-V22 | P19.S04, P20.S05, P20.S07 | `SequenceStar` | ✓ | v4: `SequenceWithMemory` (`SequenceStar` kept as alias) | same | annotate | [bt_factory.cpp v4][fc4], [convert_v3_to_v4.py][conv] | High |
| BT-V23 | P21.S05 | `AsyncActionNode` | ✓ | v4: `ThreadedAction` (alias kept) | same | annotate | [action_node.h v4][an4] | High |
| BT-V24 | P16.S00, P21.S04 | `NodeConfiguration` | ✓ | v4: `NodeConfig` (alias kept) | same | annotate | [tree_node.h v4][tn4] | High |
| BT-V25 | P19.S05 | `<root main_tree_to_execute="MainTree">` | ✓ | v4: add `BTCPP_format="4"` (missing → warning) | same | annotate | [xml_parsing.cpp v4][xp4], [convert_v3_to_v4.py][conv] | High |
| BT-V26 | P20.S07 | SubTree remapping `target="move_goal"` | ✓ v3 (`__shared_blackboard`, `SubTreePlus`) | v4: `target="{move_goal}"`, `_autoremap`; `SubTreePlus` removed | same | annotate | [tutorial 06 v3.8][t06], [convert_v3_to_v4.py][conv] | High |
| BT-V27 | P21.S01 | built-in node list of `BehaviorTreeFactory` | ✓ same list in v3.8 (+ `ManualSelector` with ncurses) | v4 removes `BlackboardCheck*`, `SubTreePlus`; adds `Script`, `ScriptCondition`, `Precondition`, `RunOnce`, `Sleep`, `UnsetBlackboard`, `ParallelAll`, `Loop*`, … | same | annotate | [bt_factory.cpp v3.8][fc3], [bt_factory.cpp v4][fc4] | High |
| BT-V28 | P20.S08 | `FileLogger` → `.fbl`, Groot log replay | ✓ (live view: `PublisherZMQ`) | v4: `FileLogger2` → `.btlog` (Groot2); live: `Groot2Publisher` | same | annotate | [loggers v3.8][log3], [bt_file_logger_v2.h][log4] | High |
| BT-V29 | P21.S06 | `registerBuilder` + `init()` through `tree.nodes` | ✓ | v4: `registerNodeType<T>(ID, args...)`; `tree.applyVisitor()` | same | annotate | [tutorial 08 v3.8][t08], [bt_factory.h v4][f4] | High |
| BT-V30 | P16.S00, P21.S05 | `getInput<T>()` + `if(!res) throw RuntimeError(…, res.error())` | ✓ (`Optional<T>`) | v4: `Expected<T>`, same use | same | keep | [tree_node.h v3.8][tn3], [tree_node.h v4][tn4] | High |
| BT-V31 | P10.S00 | Parallel: succeeds if ≥ M succeed, fails if > N−M fail | ✓ book formulation; BT.CPP ports `success_threshold` (required), `failure_threshold` (default 1) | v4: `success_count` (default −1 = all), `failure_count` (1) | same | annotate | [parallel_node.h v3.8][par3], [parallel_node.h v4][par4] | High |
| BT-V32 | P16.S00, P23.S00 | `#include <tf2_geometry_msgs/tf2_geometry_msgs.h>` | ✓ compiles with "header is obsolete" warning: use `.hpp` | `.hpp` | `.hpp` | annotate | [tf2_geometry_msgs.h (humble)][tf2h] | High |
| BT-V33 | P01.S02 | build `behaviortree_cpp_v3` from the course sources | ✓ also `apt install ros-humble-behaviortree-cpp-v3` | `ros-jazzy-behaviortree-cpp-v3` or v4 | v4 only | annotate | [jammy apt][apt-j], [rosdistro jazzy][rd-j] | High |
| BT-V34 | P16.S00 | `#include <behaviortree_ros2/bt_action_node.hpp>` (course package `behaviortree_ros2`) | course copy for v3 (official BehaviorTree.ROS2 needs BT.CPP ≥ 4.6) `[verify]` | official BehaviorTree.ROS2 (source) | same | annotate | [BehaviorTree.ROS2 README][btros2] | Medium |
| BT-V40 | P19.S04 | Sequence / ReactiveSequence / SequenceStar: Restart vs Tick again table | ✓ | ✓ (v4 names: see BT-V22) | ✓ | keep | [SequenceNode v3.8][seq3] | High |
| BT-V41 | P19.S05 | `main_tree_to_execute` mandatory with several trees; ControlNodes 1..N children, decorators and subtrees 1, leaves 0 | ✓ | ✓ (+ BT-V25) | ✓ | keep | [xml_format v3.8][xml3], [xml_parsing.cpp v4][xp4] | High |
| BT-V42 | P20.S03 | engine single-threaded; a blocking `tick()` blocks the tree; long actions return RUNNING | ✓ | ✓ | ✓ | keep | [asynchronous_nodes v3.8][async3] | High |
| BT-V43 | P08.S00 | a Condition never returns RUNNING | ✓ | ✓ | ✓ | keep | [BT_basics v3.8][basics3] | High |
| BT-V44 | P16.S00 | `tree.sleep(ms)` between ticks | ✓ (`void sleep`) | ✓ (`bool sleep`) | ✓ | keep | [bt_factory.h v3.8][f3], [bt_factory.h v4][f4] | High |
| BT-V45 | P22.S02, P22.S03 | Fallback P = 1 − ∏(1 − Pᵢ), Sequence P = ∏ Pᵢ; 0.904, 0.829 | ✓ | — | — | keep | arithmetic (Colledanchise & Ögren) | High |

## Humble alternatives to v4 features
| v4 feature (Jazzy+, also released for Humble) | On Humble |
|---|---|
| Groot2, `FileLogger2`, `Groot2Publisher` | Install `ros-humble-behaviortree-cpp` (4.10.0) and write v4 code; with v3 keep Groot 1 (`.fbl`, `PublisherZMQ`). |
| BehaviorTree.ROS2 wrappers (`RosTopicSubNode`, `RosActionNode`) | Need v4 (≥ 4.6) + source build of `BehaviorTree.ROS2` (`humble` branch). With v3: the Nav2 Humble pattern of BT-V12. |
| Nav2 BT plugins | Nav2 Humble links v3: custom Nav2 BT nodes for Humble must be written against `behaviortree_cpp_v3`. |

## Open `[verify]` (Phase 5 or a real robot)
- BT-V34: content and BT.CPP version of the course's own `behaviortree_ros2` package (the course repository is not public in this repo).
- Phase 5: build the course examples against `ros-humble-behaviortree-cpp-v3` 3.8.7 and compare the expected outputs.

[rd-h]: https://github.com/ros/rosdistro/blob/master/humble/distribution.yaml
[rd-j]: https://github.com/ros/rosdistro/blob/master/jazzy/distribution.yaml
[rd-k]: https://github.com/ros/rosdistro/blob/master/kilted/distribution.yaml
[rd-l]: https://github.com/ros/rosdistro/blob/master/lyrical/distribution.yaml
[apt-j]: http://packages.ros.org/ros2/ubuntu/dists/jammy/main/binary-amd64/Packages.gz
[n2-h]: https://github.com/ros-navigation/navigation2/blob/humble/nav2_behavior_tree/package.xml
[n2-j]: https://github.com/ros-navigation/navigation2/blob/jazzy/nav2_behavior_tree/package.xml
[n2-batt]: https://github.com/ros-navigation/navigation2/blob/humble/nav2_behavior_tree/plugins/condition/is_battery_low_condition.cpp
[btros2]: https://github.com/BehaviorTree/BehaviorTree.ROS2/blob/humble/README.md
[groot]: https://github.com/BehaviorTree/Groot/blob/master/README.md
[tf2h]: https://github.com/ros2/geometry2/blob/humble/tf2_geometry_msgs/include/tf2_geometry_msgs/tf2_geometry_msgs.h
[an3]: https://github.com/BehaviorTree/BehaviorTree.CPP/blob/v3.8/include/behaviortree_cpp_v3/action_node.h
[anc3]: https://github.com/BehaviorTree/BehaviorTree.CPP/blob/v3.8/src/action_node.cpp
[an4]: https://github.com/BehaviorTree/BehaviorTree.CPP/blob/master/include/behaviortree_cpp/action_node.h
[f3]: https://github.com/BehaviorTree/BehaviorTree.CPP/blob/v3.8/include/behaviortree_cpp_v3/bt_factory.h
[f4]: https://github.com/BehaviorTree/BehaviorTree.CPP/blob/master/include/behaviortree_cpp/bt_factory.h
[fc3]: https://github.com/BehaviorTree/BehaviorTree.CPP/blob/v3.8/src/bt_factory.cpp
[fc4]: https://github.com/BehaviorTree/BehaviorTree.CPP/blob/master/src/bt_factory.cpp
[tn3]: https://github.com/BehaviorTree/BehaviorTree.CPP/blob/v3.8/include/behaviortree_cpp_v3/tree_node.h
[tn4]: https://github.com/BehaviorTree/BehaviorTree.CPP/blob/master/include/behaviortree_cpp/tree_node.h
[xp4]: https://github.com/BehaviorTree/BehaviorTree.CPP/blob/master/src/xml_parsing.cpp
[conv]: https://github.com/BehaviorTree/BehaviorTree.CPP/blob/master/convert_v3_to_v4.py
[par3]: https://github.com/BehaviorTree/BehaviorTree.CPP/blob/v3.8/include/behaviortree_cpp_v3/controls/parallel_node.h
[par4]: https://github.com/BehaviorTree/BehaviorTree.CPP/blob/master/include/behaviortree_cpp/controls/parallel_node.h
[log3]: https://github.com/BehaviorTree/BehaviorTree.CPP/tree/v3.8/include/behaviortree_cpp_v3/loggers
[log4]: https://github.com/BehaviorTree/BehaviorTree.CPP/blob/master/include/behaviortree_cpp/loggers/bt_file_logger_v2.h
[basics3]: https://github.com/BehaviorTree/BehaviorTree.CPP/blob/v3.8/docs/BT_basics.md
[seq3]: https://github.com/BehaviorTree/BehaviorTree.CPP/blob/v3.8/docs/SequenceNode.md
[fb3]: https://github.com/BehaviorTree/BehaviorTree.CPP/blob/v3.8/docs/FallbackNode.md
[xml3]: https://github.com/BehaviorTree/BehaviorTree.CPP/blob/v3.8/docs/xml_format.md
[async3]: https://github.com/BehaviorTree/BehaviorTree.CPP/blob/v3.8/docs/asynchronous_nodes.md
[t06]: https://github.com/BehaviorTree/BehaviorTree.CPP/blob/v3.8/docs/tutorial_06_subtree_ports.md
[t08]: https://github.com/BehaviorTree/BehaviorTree.CPP/blob/v3.8/docs/tutorial_08_additional_args.md
