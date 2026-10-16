---
id: bt-app-architecture
type: reference
owner: equipo-ros2
updated: 2026-10-15
review_by: 2027-04-13
source: manual
confidentiality: internal
title: "BT application architecture with and without ROS 2"
domain: bt
area: concepts
distro: humble
tested: false
audience: dev
summary: "How a C++ BT application is organized: node classes, XML tree, factory, tick; same structure with ROS 2 nodes."
tags: [architecture, BehaviorTreeFactory, XML, tickRoot, ROS 2 integration, abstraction, path planner, game AI]
see: ["[[bt-design-stack]]", "[[bt-cpp-first-program]]", "[[bt-ros2-node-pattern]]", "[[bt-what-is-bt]]"]
requires: [ros2-core]
version_notes:
  - "v4: tree.tickRoot() is replaced by tickOnce()/tickWhileRunning() — https://github.com/BehaviorTree/BehaviorTree.CPP/blob/master/include/behaviortree_cpp/bt_factory.h (BT-V21)"
---
# BT application architecture with and without ROS 2

**TL;DR** A BT application has C++ classes for the tree nodes, the tree logic in XML (inside the `.cpp` or read at runtime) and a `main()` that registers the classes in a `BehaviorTreeFactory`, builds the tree and ticks it. With ROS 2 the structure is the same: some node classes talk to ROS 2 nodes, and `main()` also creates and spins them.

## Two applications, same skeleton
```text
C++ application WITHOUT ROS 2                      C++ application WITH ROS 2
#include BT headers  → BT framework                #include BT headers  → BT framework
class A { methods_A() }  → BT framework            class A { methods_A_calling_back_ros_node() }  → BT framework
class B { methods_B() }  → BT framework            class B { methods_B_calling_back_ros_node() }  → BT framework
class C { methods_C() }  → BT framework            class C { methods_C() }  supports the BT, calls no ROS node
class D { methods_D() }  auxiliary, not in the BT  class D { methods_D() }  auxiliary, not in the BT
BT definition (XML in the .cpp or read at runtime) → feeds main() step 3 in both
main():                                            main():
  1. BehaviorTreeFactory factory;                    1–5. same as on the left
  2. register the BT nodes (classes A, B, C)         6. create the ROS node shared pointers
  3. read the tree (XML file or string)              7. spin the ROS nodes
  4. tree.tickRoot()                                 ROS node 1 … ROS node N ⇄ classes A, B
  5. the application runs as the XML tree says
```
The **BT framework** (BehaviorTree.CPP, `.cpp` + `.h`) is the shared part: it runs the application according to the logical relations written in the tree.

## From low-level to high-level design
At a low level you think about motors, drives, sensors, robot controllers and software, and the robot performs its programmed task (a manipulator picks and places, a cleaning robot cleans floors). A simple pick-and-place description (capture the object's position, compute a short collision-free path to the destination, perform the task) leaves out many tasks: optimizing the grasp position, strategies when grasping fails, motion planning with the robot's dynamic model, motion supervision, safety. A BT is where these pieces are composed.

## Why separate logic from code
- Without ROS the framework still works: BTs model game characters or any C++ application. The course's exercises without ROS use this layout ([[bt-cpp-first-program]]).
- With ROS 2, think of a node class as a ROS 2 node that talks to the robot; auxiliary classes support it and are never called from the tree ([[bt-ros2-node-pattern]], [[bt-ros2-shared-node]]).
- Higher abstraction: a path planning task contains many low-level modules (robot pose, object and target positions, obstacles, an algorithm such as Dijkstra, A* or RRT, heuristics, CPU/GPU/FPGA targets). Optimize them, but architect the application with the planner as **one** component (one BT node).
- BTs let robot architects orchestrate the decision making; the designer works on the logical flow (XML), the developer on the node callbacks ([[bt-design-stack]]).

## Pitfalls
- One `tickRoot()` is one traversal of the tree: a tree with RUNNING nodes must be ticked in a loop ([[bt-concurrency]]). [v4: `tickOnce()` / `tickWhileRunning()`]
- Every node used in the XML must be registered in the factory; auxiliary classes (D) need not be.
