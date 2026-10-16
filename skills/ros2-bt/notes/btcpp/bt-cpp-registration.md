---
id: bt-cpp-registration
type: reference
owner: equipo-ros2
updated: 2026-10-15
review_by: 2027-04-13
source: manual
confidentiality: internal
title: "Registering nodes: registerNodeType, SimpleAction, SimpleCondition; XML-to-code mapping"
domain: bt
area: btcpp
distro: humble
tested: false
audience: dev
summary: "registerNodeType, registerSimpleCondition, registerSimpleAction, createTreeFromText: how each XML tag maps to a registration in main()."
tags: [registerNodeType, registerSimpleCondition, registerSimpleAction, SimpleActionNode, SimpleConditionNode, createTreeFromText, FileLogger, bt_u4_ex1]
see: ["[[bt-cpp-factory]]", "[[bt-cpp-first-program]]", "[[bt-cpp-sync-action-ports]]", "[[bt-cpp-groot-logging]]"]
requires: [ros2-core]
version_notes: []
---
# Registering nodes: registerNodeType, SimpleAction, SimpleCondition; XML-to-code mapping

**TL;DR** Every tag of the XML must exist in the factory before the tree is built. Built-in tags (`Sequence`) are registered by the factory's constructor; custom tags are registered in `main()`: classes with `registerNodeType<Class>("ID")`, plain functions or methods with `registerSimpleCondition` / `registerSimpleAction`. `createTreeFromText` then creates one instance per tag.

## Example (`bt_u4_ex1`)
```xml
<root main_tree_to_execute = "MainTree" >
  <BehaviorTree ID="MainTree">
    <Sequence name="root_sequence">
      <CheckBattery   name="battery_ok"/>
      <ApproachObject name="approach_object"/>
      <OpenGripper    name="open_gripper"/>
    </Sequence>
  </BehaviorTree>
</root>
```
One condition (`CheckBattery`) and two actions (`ApproachObject`, `OpenGripper`); the node definitions are the same as in [[bt-cpp-first-program]].
```cpp
int main()
{
  // We use the BehaviorTreeFactory to register our custom nodes
  BehaviorTreeFactory factory;

  factory.registerNodeType<ApproachObject>("ApproachObject");

  // Registering a SimpleActionNode using a function pointer.
  factory.registerSimpleCondition("CheckBattery", std::bind(CheckBattery));

  //You can also create SimpleActionNodes using methods of a class
  GripperInterface gripper;
  factory.registerSimpleAction("OpenGripper", std::bind(&GripperInterface::open, &gripper));

  auto tree = factory.createTreeFromText(xml_text);
  FileLogger logger_file(tree, "bt_trace_u4_ex1.fbl");
  tree.tickRoot();
  return 0;
}
```
```text
[ Battery: OK ]
ApproachObject: approach_object
GripperInterface::open
```
The robot checks the battery, approaches the object and opens the gripper. `FileLogger` writes the run to a file for Groot ([[bt-cpp-groot-logging]]).

## Node creation: which line creates which node
| XML element | Registered by | Node created |
|---|---|---|
| `<Sequence name="root_sequence">` | built-in, `BehaviorTreeFactory` constructor ([[bt-cpp-factory]]) | `SequenceNode` |
| `<CheckBattery name="battery_ok"/>` | `factory.registerSimpleCondition("CheckBattery", std::bind(CheckBattery));` | simple condition |
| `<ApproachObject name="approach_object"/>` | `factory.registerNodeType<ApproachObject>("ApproachObject");` | `ApproachObject` (custom class) |
| `<OpenGripper name="open_gripper"/>` | `factory.registerSimpleAction("OpenGripper", std::bind(&GripperInterface::open, &gripper));` | simple action |
| the whole `<root>…</root>` text | `auto tree = factory.createTreeFromText(xml_text);` | the tree |

The built-in nodes give the framework its primitives and the tree its logic; the factory object registers the custom nodes in `main()`, and the executor instantiates everything when `xml_text` is loaded.

## Pitfalls
- The course comments call the simple-node methods "not recommended": they work (they even accept a `PortsList` as third argument), but "the default (and recommended) way to create a TreeNode is by inheritance" ([tutorial 01](https://github.com/BehaviorTree/BehaviorTree.CPP/blob/v3.8/docs/tutorial_01_first_tree.md)): a class with `providedPorts()` ([[bt-cpp-sync-action-ports]]).
- `std::bind(&GripperInterface::open, &gripper)` keeps a pointer to `gripper`: the object must outlive the tree.
- Register before `createTreeFromText`: registering afterwards does not change an existing tree.
