---
id: bt-learn-start-here
type: reference
owner: equipo-ros2
updated: 2026-10-15
review_by: 2027-04-13
source: manual
confidentiality: internal
title: "Behavior Trees in ROS 2 course: start here"
domain: bt
area: learn
distro: humble
tested: false
audience: students
summary: "Course map: units 1–5 and project, prerequisites, course files, TurtleBot3 simulation, references; links each unit to its notes."
tags: [course, behavior trees, BehaviorTree.CPP, TurtleBot3, units, prerequisites, course files, students]
see: ["[[bt-learn-unit1-demo]]", "[[bt-what-is-bt]]", "[[bt-cpp-first-program]]", "[[bt-learn-project]]"]
requires: [ros2-core]
version_notes: []
order: 1
---
# Behavior Trees in ROS 2 course: start here

**TL;DR** The course teaches behavior trees (BT) at a high level of abstraction: the concept, how to architect (model) robot behavior with them, and how to implement them in C++ with the BehaviorTree.CPP framework ([behaviortree.dev](https://www.behaviortree.dev/)), first without ROS and then with a TurtleBot 3 simulation in ROS 2. "BT" always means behavior tree.

## Units
| Unit | Topic | Technical notes | Exercises |
|---|---|---|---|
| 1 | Introduction and demo | [[bt-what-is-bt]] | [[bt-learn-unit1-demo]] |
| 2 | Introduction to BTs: architecture, Sequence, Fallback, node types, BT vs FSM | [[bt-app-architecture]], [[bt-sequence-fallback]], [[bt-reactive-async]], [[bt-node-types]], [[bt-vs-fsm]], [[bt-cpp-first-program]], [[bt-ros2-node-pattern]] | [[bt-learn-unit2]] |
| 3 | Design principles: design stack, sequence types, XML, async nodes, concurrency, blackboard, SubTrees, Groot | [[bt-design-stack]], [[bt-sequence-variants]], [[bt-cpp-xml-schema]], [[bt-concurrency]], [[bt-cpp-blackboard]], [[bt-cpp-subtrees-decorators]], [[bt-cpp-port-remapping]], [[bt-cpp-groot-logging]] | [[bt-learn-unit3]] |
| 4 | BehaviorTree.CPP as a library: factory, registration, ports, async nodes, constructor arguments | [[bt-cpp-factory]], [[bt-cpp-registration]], [[bt-cpp-sync-action-ports]], [[bt-cpp-async-action]], [[bt-cpp-constructor-args]] | [[bt-learn-unit4]] |
| 5 | Stochastic BTs and automated planning | [[bt-planning-acting]], [[bt-stochastic]] | [[bt-learn-unit5]] |
| — | Course project | [[bt-ros2-shared-node]] (a cleaner way to write the ROS 2 nodes) | [[bt-learn-project]] |

## What you need
- ROS 2 basics with C++ (Humble).
- Knowing how to write programs in C++.

## Course files and robot
The course files (a repository you clone into `~/ros2_ws/src`, folder `bt_course_files`) contain two folders:
- `BehaviorTree.CPP`: the BehaviorTree.CPP v3 source plus the course's C++ exercises (`course_bt/`, programs `bt_u2_ex1` … `bt_u4_ex4`).
- `behaviortree_ros2`: a ROS 2 package that connects the BT framework with ROS 2 and holds the simulation programs (`test/test_unit1.cpp` … `test_unit5.cpp`, `test_project.cpp`).

The robot is a simulated **TurtleBot 3**; the simulation worlds come from the course's `my_package` (`launch_world_unitN.launch.py`).

## References
- [behaviortree.dev](https://www.behaviortree.dev/) (BehaviorTree.CPP documentation).
- *Behavior Trees in Robotics and AI: An Introduction*, Michele Colledanchise and Petter Ögren.

## Pitfalls
- The course uses BehaviorTree.CPP **v3** (`behaviortree_cpp_v3`), the version Nav2 Humble uses; v4 renames several nodes and methods ([[bt-humble-to-jazzy]]).
- Several course figures disagree with their own XML; the notes follow the XML and mark each difference.
