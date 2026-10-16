---
id: bt-design-stack
type: reference
owner: equipo-ros2
updated: 2026-10-15
review_by: 2027-04-13
source: manual
confidentiality: internal
title: "BT design stack: robot task, XML, BehaviorTree.CPP, ROS 2 nodes, robot"
domain: bt
area: concepts
distro: humble
tested: false
audience: dev
summary: "Layers of a BT robot application and their data flow: tick down, callbacks call ROS 2 nodes, statuses back up."
tags: [design stack, layers, callback, black box, data flow, XML, ROS node, find path, move robot]
see: ["[[bt-app-architecture]]", "[[bt-cpp-factory]]", "[[bt-what-is-bt]]", "[[bt-ros2-shared-node]]"]
requires: [ros2-core]
version_notes: []
---
# BT design stack: robot task, XML, BehaviorTree.CPP, ROS 2 nodes, robot

**TL;DR** The robot task is written as a tree in XML; BehaviorTree.CPP parses it and ticks the BT nodes; each BT node runs a **callback** that may ask ROS 2 nodes to act on the robot; the feedback decides the status returned to the root (SUCCESS, FAILURE or RUNNING). When you design the tree, a ROS 2 node is a black box: you need to know what it does, not how.

## Layers and data flow
```text
1. Robot task
2. Behavior tree: logical flow in XML
3. BehaviorTree.CPP: links the XML to the node types and behaviors, invokes the callbacks
      Root ┬┄┄ BT node 1 / callback 1 ──▶◀╌╌ ROS node 1 / robot action 1 ◀──▶ Robot
           ├┄┄ BT node 2 / callback 2 ──▶◀╌╌ ROS node 2 / robot action 2 ◀──▶ Robot
           └┄┄ BT node N / callback N ──▶◀╌╌ ROS node N / robot action N ◀──▶ Robot
4. ROS 2 nodes (one per robot action)
5. Robot
```
Arrows: `┄┄` tick from the root (and status back) · `──▶` the callback asks the ROS 2 node to act · `◀╌╌` the ROS 2 node returns its result to the same BT node · `◀──▶` ROS 2 node and robot exchange commands and feedback.
- Top (BT execution): the root sends a tick to a BT node, which runs its callback; the callback returns SUCCESS, FAILURE or RUNNING.
- Middle (BT ↔ ROS 2): the callback can perform actions in ROS 2 nodes; they act and send a result back; that result decides the status returned to the root.
- Bottom (ROS 2 ↔ robot): ROS 2 nodes command the robot (or the Gazebo simulation) and receive its feedback.

## Example: pick and place
```text
Root
└── [→] Sequence
    ├── BT node "pick ball"    callback { find_path(ball); move_robot_to_target(ball); return SUCCESS or FAILURE or RUNNING; }
    └── BT node "place ball"   callback { find_path(target_place); move_robot_to_target(ball); return SUCCESS or FAILURE or RUNNING; }

ROS node "find path"   { actions: run A*; compute IK }                        ⇄ both BT nodes
ROS node "move robot"  { actions: send control signal to robot controller }   ⇄ both BT nodes
```
The callbacks are pseudo-code from the course. The main function reads the XML and manages the tree; the same tree in valid BehaviorTree.CPP XML:
```xml
<root main_tree_to_execute="MainTree">
  <BehaviorTree ID="MainTree">
    <Sequence>
      <PickBall/>
      <PlaceBall/>
    </Sequence>
  </BehaviorTree>
</root>
```
(The course draws it as `<root = "main tree"> <Sequence> <pick ball> <place ball> <\Sequence> <\root>`, which is a sketch, not parseable XML.)

## Design rules
- Model the actions and the auxiliary mechanisms (safety supervision, battery check) in the tree; the logical relations live in the XML.
- With BehaviorTree.CPP you declare the nodes (following the XML) and define them (the callbacks): [[bt-cpp-registration]].
- Design the tree at the high level only; the implementation of each ROS 2 node (path search, inverse kinematics) is not part of that reasoning.

## Pitfalls
- A callback that waits for a ROS 2 node inside `tick()` blocks the whole tree: return RUNNING and check again on the next tick ([[bt-concurrency]], [[bt-ros2-shared-node]]).
