---
id: nav2-bt-control-nodes
type: reference
owner: equipo-ros2
updated: 2026-10-10
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "Nav2 BT control nodes: RecoveryNode, PipelineSequence, RateController, SequenceStar; ports and blackboard"
domain: nav2
area: behavior-trees
distro: humble
tested: false
audience: dev
summary: "How bt_navigator behaviors are built: root/BehaviorTree tags, RecoveryNode retries, PipelineSequence, RateController, SequenceStar, input/output ports, blackboard."
tags: [behavior tree, BT nodes, RecoveryNode, PipelineSequence, RateController, SequenceStar, SequenceWithMemory, number_of_retries, ports, blackboard, BehaviorTree.CPP, nav2_bt_navigator]
see: ["[[nav2-behavior-tree-xml]]", "[[nav2-bt-action-nodes]]", "[[nav2-bt-navigator]]", "[[nav2-recovery-flow]]", "[[nav2-bt-battery-abort]]"]
requires: [ros2-core]
version_notes:
  - "humble: a custom XML is optional — if default_nav_to_pose_bt_xml is not set, navigate_to_pose_w_replanning_and_recovery.xml of nav2_bt_navigator is loaded — https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/configuration_guide/core_servers/configuring_bt_navigator.md (NAV2-V45)"
  - "humble: BehaviorTree.CPP 3.8 (SequenceStar keeps its index on FAILURE); jazzy: BT.CPP 4.5, SequenceStar accepted as alias of SequenceWithMemory — https://github.com/ros-navigation/navigation2/blob/humble/nav2_behavior_tree/plugins/control/recovery_node.cpp (NAV2-V20, NAV2-V62)"
---
# Nav2 BT control nodes: RecoveryNode, PipelineSequence, RateController, SequenceStar

**TL;DR** The package **`nav2_bt_navigator`** is in charge of managing behavior trees and of controlling the movement of the robot to the goal. It is composed of several parts: the `bt_navigator` node and its configuration file, the behavior of the `bt_navigator` node (a BT XML), and the behavior server (`recoveries_server` in the course launch) with its config file. The `bt_navigator` node manages the path planner, the controller and the recovery behaviors, and the way it must manage them is defined in a **behavior tree** XML ([[nav2-bt-navigator]]). You do not have to write one: Humble loads Nav2's default tree when no XML is set (NAV2-V45). To customize it, create an XML file with the behavior nodes available.

The BehaviorTree.CPP library provides a set of generic behavior nodes; Nav2 adds its own. Do not confuse **ROS nodes** with **behavior nodes**: they are two different things.

## The tags of every behavior
```xml
<root main_tree_to_execute="MainTree">
  <BehaviorTree ID="MainTree">
    ...
  </BehaviorTree>
</root>
```
`root` identifies the main tree to execute; `BehaviorTree` identifies what follows as a behavior tree with a given name (`ID`). Inside it go the behavior nodes, in the order that builds the behavior you want. The course's `behavior.xml` (Nav2's replanning tree, [[nav2-behavior-tree-xml]]) does: replan the global path every second (1 Hz) → follow that path → if the robot is stuck: clear the local costmap, clear the global costmap, rotate to see the obstacles and rebuild the costmaps, wait 5 seconds, then go back to the main behavior.

## Control nodes
- **RecoveryNode** (Nav2) encapsulates two sub-nodes: it executes the first; if it returns SUCCESS the RecoveryNode returns SUCCESS; if it returns FAILURE it executes the second; if the second returns SUCCESS it executes the first again; if the second returns FAILURE it returns FAILURE and ends. It is usually used to launch a navigation task (first sub-node) and define its recovery action if it fails (second sub-node). With `number_of_retries="6"` it makes up to six recovery attempts; if the first sub-node still fails, it returns FAILURE.
  ```xml
  <RecoveryNode number_of_retries="6" name="NavigateRecovery">
    <PipelineSequence name="NavigateWithReplanning">...</PipelineSequence>
    <SequenceStar name="RecoveryActions">...</SequenceStar>
  </RecoveryNode>
  ```
- **PipelineSequence** (Nav2) ticks the first child until it returns SUCCESS, then the first and second children (again) until the second returns SUCCESS, then the first, second and third, and so on. It stops if any child returns FAILURE, or when the last child returns SUCCESS. Here it computes the global path every second (`RateController`) while the robot follows the newly computed path (`RecoveryNode` with `FollowPath`), so the path adapts to changes in the robot's position.
- **RateController** (Nav2) ticks its child at the frequency given by `hz`: `<RateController hz="1.0">` calls the `ComputePathToPose` RecoveryNode at 1 Hz.
- **SequenceStar** (BehaviorTree.CPP) works like a sequence with memory: it does not tick again the children that already finished with SUCCESS, and after a FAILURE the next tick resumes at the failed child. [changed in Jazzy: BT.CPP 4 name `SequenceWithMemory`]

## Ports and blackboard
Behavior nodes have **input ports** (the equivalent of parameters passed to the node) and **output ports** (results returned by the node). `RecoveryNode` has the input port `number_of_retries`; `name` exists for every node. Check the documentation of each node for its ports: [Nav2 BT nodes](https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/configuration_guide/core_servers/bt_plugins/index.md).

The **blackboard** is a space for variables that all the nodes can access, used to share information among them: one node puts a value there (`{path}` from `ComputePathToPose`) and another reads it (`FollowPath path="{path}"`) ([[nav2-bt-action-nodes]]).

## Pitfalls
- A tree that wraps everything in one `RecoveryNode` retries recoveries before failing: a condition placed inside it does not abort at once ([[nav2-bt-battery-abort]]).
- `SequenceStar` after a failure does not restart from its first child.
