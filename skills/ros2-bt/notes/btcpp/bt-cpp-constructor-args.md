---
id: bt-cpp-constructor-args
type: reference
owner: equipo-ros2
updated: 2026-10-15
review_by: 2027-04-13
source: manual
confidentiality: internal
title: "Passing constructor arguments: registerBuilder, init() before the first tick"
domain: bt
area: btcpp
distro: humble
tested: false
audience: dev
summary: "Give nodes constant setup values: NodeBuilder + registerBuilder, or an init() method called on tree.nodes before the first tick."
tags: [registerBuilder, NodeBuilder, constructor arguments, init, tree.nodes, dynamic_cast, Sensor, Compute, applyVisitor, bt_u4_ex4]
see: ["[[bt-cpp-registration]]", "[[bt-cpp-blackboard]]", "[[bt-ros2-shared-node]]", "[[bt-learn-unit4]]"]
requires: [ros2-core]
version_notes:
  - "v4: registerNodeType<T>(ID, args...) passes extra constructor arguments; tree.applyVisitor() replaces iterating tree.nodes — https://github.com/BehaviorTree/BehaviorTree.CPP/blob/master/include/behaviortree_cpp/bt_factory.h (BT-V29)"
  - "all: the 'passing arguments' figure names the ports usage, the Groot tree of the same program names them range, brain_input, brain_output, input (BT-V19)"
---
# Passing constructor arguments: registerBuilder, init() before the first tick

**TL;DR** Every node is built with the constructor `(name, config)`. Values that are known at deployment time, never change at runtime and need not be set from the XML should **not** go through ports or the blackboard (laborious and discouraged). BehaviorTree.CPP 3.8 offers two ways: (1) register a builder lambda that calls a constructor with extra arguments (`registerBuilder`); (2) call an `init()` method on each node after creating the tree and before the first tick. [v4: `registerNodeType<T>("ID", args…)` and `tree.applyVisitor()`]

## Both mechanisms
```cpp
//mechanism 1
NodeBuilder builder_A = [](const std::string& name, const NodeConfiguration& config)
{
  return std::make_unique<Sensor>( name, config, 10, 30);
};
// BehaviorTreeFactory::registerBuilder is the more general way to register a custom node.
// Not the most user friendly, but definitely the most flexible one.
factory.registerBuilder<Sensor>( "Sensor", builder_A);

//mechanism 2
for( auto& node: tree.nodes )
{
  if( auto Compute_node = dynamic_cast<Compute*>( node.get() ))
  {
    Compute_node->init( 1.1, 1.2, 1.3 );
  }
}
```
Mechanism 1 is plain OOP (constructor arguments); mechanism 2 is a class method called before the first `tick()`. Only the registration changes; the nodes themselves are ordinary C++ classes.

## The course program (`bt_u4_ex4`)
The sensor is built with its working range (low 10, high 30) and sends it through an output port; `Compute` gets three factors from `init()`, computes a measurement and passes it to `AnalyzeMeasurement`, which prints it.
```text
[→] Sequence
├── Sensor               [OUT] range = {range}
├── Compute              [IN]  brain_input = {range}   [OUT] brain_output = {meas}
└── AnalyzeMeasurement   [IN]  input = {meas}
```
```text
main():  init Sensor (int, int)          ──▶ Sensor()  { range (int, int) }      → output port → {range}
         init Compute (float, float, float) ──▶ Compute() { meas = brain(float, float, float, range) } ⇄ RobotBrain()
                                                 {range} → input port … output port → {meas}
AnalyzeMeasurement: {meas} → input port → prints "Measurement ::: 140.564"
(pseudo-code from the course figure)
```
Port names are taken from the Groot tree of the program; the course figure labels them `usage`.

Groot log of the run:
| Time | Node | Previous | Status |
|---|---|---|---|
| 0.000 | Sequence | IDLE | RUNNING |
| 0.000 | Sensor | IDLE | SUCCESS |
| 0.000 | Compute | IDLE | SUCCESS |
| 0.000 | AnalyzeMeasurement | IDLE | SUCCESS |
| 0.000 | Sensor | SUCCESS | IDLE |
| 0.000 | Compute | SUCCESS | IDLE |
| 0.000 | AnalyzeMeasurement | SUCCESS | IDLE |
| 0.000 | Sequence | RUNNING | SUCCESS |
| 0.000 | Sequence | SUCCESS | IDLE |
```text
sensor range low : 10 high :30
Compute init factors: 1.1 : 1.2 : 1.3
 Measurements ::: 140.564
[ Analysis process: FINISHED ]
```
When the Sequence finishes, its children are reset to IDLE (rows 5–7) and then the Sequence itself.

## Pitfalls
- With mechanism 2 the node exists without its values until `init()` runs: never tick the tree before initializing, and check in `tick()` that `init()` was called.
- The builder must return the exact class registered under that ID; a typo in the ID makes the XML tag unknown.
- Shared objects (a ROS 2 node, a driver) can be passed the same way, or through the blackboard as Nav2 does ([[bt-ros2-shared-node]]).
