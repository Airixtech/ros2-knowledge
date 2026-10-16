---
id: bt-cpp-xml-schema
type: reference
owner: equipo-ros2
updated: 2026-10-15
review_by: 2027-04-13
source: manual
confidentiality: internal
title: "XML schema: root, BehaviorTree ID, main_tree_to_execute, ports, nesting"
domain: bt
area: btcpp
distro: humble
tested: false
audience: dev
summary: "BehaviorTree.CPP XML rules: root and BehaviorTree tags, main_tree_to_execute, node tags = registered IDs, name, ports, children counts, nesting."
tags: [XML, root, BehaviorTree, main_tree_to_execute, ID, name, ports, nested nodes, createTreeFromFile, BTCPP_format]
see: ["[[bt-cpp-first-program]]", "[[bt-cpp-subtrees-decorators]]", "[[bt-cpp-blackboard]]", "[[bt-sequence-fallback]]"]
requires: [ros2-core]
version_notes:
  - "v4: <root BTCPP_format=\"4\"> (missing → warning) — https://github.com/BehaviorTree/BehaviorTree.CPP/blob/master/src/xml_parsing.cpp (BT-V25)"
  - "all: main_tree_to_execute mandatory with several trees; children counts — https://github.com/BehaviorTree/BehaviorTree.CPP/blob/v3.8/docs/xml_format.md (BT-V41)"
---
# XML schema: root, BehaviorTree ID, main_tree_to_execute, ports, nesting

**TL;DR** The XML is the human-readable model of the tree. The library is C++, but trees are created at runtime: from a string in the code (`createTreeFromText`) or from a file (`createTreeFromFile`). `<root>` holds one or more `<BehaviorTree ID="…">`; each node is one tag whose name is the ID registered in the factory; `name` is the optional instance name; ports are attributes. [v4: `<root BTCPP_format="4">`]

## Example
```xml
<root main_tree_to_execute = "MainTree" >
  <BehaviorTree ID="MainTree">
    <Sequence name="root_sequence">
      <SaySomething   name="action_hello" message="Hello"/>
      <OpenGripper    name="open_gripper"/>
      <ApproachObject name="approach_object"/>
      <CloseGripper   name="close_gripper"/>
    </Sequence>
  </BehaviorTree>
</root>
```

## Rules
- The first tag is `<root>`; it contains one or more `<BehaviorTree>` tags, each with the attribute `ID`.
- `<root>` should have the attribute `main_tree_to_execute`: mandatory when the file has several `<BehaviorTree>`, optional otherwise.
- One tag per tree node: the tag name is the ID used to register the node in the factory; `name` names the instance (optional); ports are configured with attributes (`message="Hello"`).
- Children: ControlNodes have 1 to N; DecoratorNodes and SubTrees exactly 1; ActionNodes and ConditionNodes none.

## Nested nodes
Trees run from top to bottom and from left to right; nesting in the XML follows the drawing. Tree generated from the course XML (leaves named `Condition…` are conditions in the course's design; the XML alone does not say it). Legend: `[→]` Sequence · `[?]` Fallback.
```text
BehaviorTree "MainTree"
└── [→] Sequence name="root_sequence"
    ├── [→] Sequence name="sequence_1"
    │   ├── [→] Sequence name="sequence_1"
    │   │   ├── Condition1 name="condition_1"
    │   │   └── Action1 name="action_1"
    │   └── [?] Fallback name="fallback_1"
    │       ├── Action2 name="action_2"
    │       └── Action3 name="action_3"
    └── [?] Fallback name="fallback_2"
        ├── [→] Sequence name="sequence_3"
        │   ├── Condition2 name="condition_2"
        │   └── Action4 name="action_4"
        └── [→] Sequence name="sequence_4"
            ├── Condition3 name="condition_3"
            └── Action5 name="action_5"
```
```xml
<root main_tree_to_execute = "MainTree" >
  <BehaviorTree ID="MainTree">
    <Sequence name="root_sequence">
      <Sequence name="sequence_1">
        <Sequence name="sequence_1">
          <Condition1   name="condition_1"/>
          <Action1      name="action_1"/>
        </Sequence>
        <Fallback name="fallback_1">
          <Action2      name="action_2"/>
          <Action3      name="action_3"/>
        </Fallback>
      </Sequence>
      <Fallback name="fallback_2">
        <Sequence name="sequence_3">
          <Condition2   name="condition_2"/>
          <Action4      name="action_4"/>
        </Sequence>
        <Sequence name="sequence_4">
          <Condition3   name="condition_3"/>
          <Action5      name="action_5"/>
        </Sequence>
      </Fallback>
    </Sequence>
  </BehaviorTree>
</root>
```
The course reuses the instance name `sequence_1` for two different Sequences: instance names are labels for logs and Groot, so give each node its own.

## Pitfalls
- A tag must match the registered ID exactly (case included): otherwise the parser throws `Node not recognized: <tag>`.
- XML comments are `<!-- … -->`; the course's separators `<!--------------------------------------->` put `--` inside a comment, which the XML standard forbids: other tools (Python's `xml` module, linters) reject them even if BehaviorTree.CPP loads the file.
- An XML string that is read at runtime can change without recompiling; a string inside the `.cpp` needs a rebuild.
