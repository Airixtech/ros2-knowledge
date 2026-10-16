---
id: bt-cpp-subtrees-decorators
type: reference
owner: equipo-ros2
updated: 2026-10-15
review_by: 2027-04-13
source: manual
confidentiality: internal
title: "SubTrees and decorators: Inverter, RetryUntilSuccessful"
domain: bt
area: btcpp
distro: humble
tested: false
audience: dev
summary: "Two BehaviorTree definitions joined with <SubTree ID>, Inverter and RetryUntilSuccessful decorators, state walk-through, decorator XML syntax."
tags: [SubTree, BehaviorTree ID, Inverter, RetryUntilSuccessful, num_attempts, decorator, Condition, CheckOpposite, reuse, bt_trace.fbl]
see: ["[[bt-cpp-port-remapping]]", "[[bt-node-types]]", "[[bt-cpp-groot-logging]]", "[[bt-cpp-xml-schema]]"]
requires: [ros2-core]
version_notes:
  - "all: the course snippet <Inverter></Inverter><RetryUntilSuccessful num_attempts=\"4\"><RetryUntilSuccessful> is not well-formed; a decorator wraps exactly one child — https://github.com/BehaviorTree/BehaviorTree.CPP/blob/v3.8/docs/xml_format.md (BT-V10)"
  - "all: the 'States in BT' figure draws the last Inverter's child as an action Move Forward; the XML has the condition IsFreeToMoveForward (BT-V16)"
---
# SubTrees and decorators: Inverter, RetryUntilSuccessful

**TL;DR** A file can hold several `<BehaviorTree ID="…">`; `<SubTree ID="CheckOpposite"/>` inserts one tree inside another, so a branch can be reused and a big tree stays readable. Decorators change the result of their single child: `Inverter` swaps SUCCESS and FAILURE, `RetryUntilSuccessful num_attempts="4"` ticks a failing child up to 4 times.

## XML
```xml
<root main_tree_to_execute = "MainTree">
    <BehaviorTree ID="CheckOpposite">
        <Sequence name="opposite_turn_sequence">
            <Inverter>
                <Condition ID="IsFreeToMove"/>
            </Inverter>
            <RetryUntilSuccessful num_attempts="4">
                <Measuring/>
            </RetryUntilSuccessful>
            <MoveOpposite/>
        </Sequence>
    </BehaviorTree>

    <BehaviorTree ID="MainTree">
        <Sequence>
            <Fallback name="root_Fallback">
                <Sequence name="turn_sequence">
                    <IsFreeToMove/>
                    <Move/>
                </Sequence>
                <SubTree ID="CheckOpposite"/>
                <Inverter>
                    <Condition ID="IsFreeToMoveForward"/>
                </Inverter>
            </Fallback>
            <MoveBack/>
        </Sequence>
    </BehaviorTree>
</root>
```
`<SubTree ID="CheckOpposite"/>` marks where the subtree is inserted. The course separates the trees with `<!--------------------------------------->` lines; they are left out here (see [[bt-cpp-xml-schema]]).

## The run, node by node
Legend: `[→]` Sequence · `[?]` Fallback · `◇` decorator · `⤷` SubTree · `(Name?)` condition · ↑ returned status.
```text
Root                                                ↑ SUCCESS
└── [→] Sequence                                    ↑ SUCCESS
    ├── [?] Fallback name="root_Fallback"           ↑ SUCCESS
    │   ├── [→] Sequence name="turn_sequence"       ↑ FAILURE
    │   │   ├── (IsFreeToMove?)                     ↑ FAILURE
    │   │   └── Move                                not ticked
    │   ├── ⤷ SubTree "CheckOpposite"
    │   │   └── [→] Sequence name="opposite_turn_sequence"   ↑ FAILURE
    │   │       ├── ◇ Inverter                      ↑ SUCCESS
    │   │       │   └── (IsFreeToMove?)             ↑ FAILURE
    │   │       ├── ◇ RetryUntilSuccessful  num_attempts="4"   ↑ FAILURE
    │   │       │   └── Measuring                   ↑ FAILURE
    │   │       └── MoveOpposite                    not ticked
    │   └── ◇ Inverter                              ↑ SUCCESS
    │       └── (IsFreeToMoveForward?)              ↑ FAILURE
    └── MoveBack                                    ↑ SUCCESS
```
The robot tries to turn right and move, but the way is temporarily closed (`IsFreeToMove?` fails). It looks for alternatives in the subtree: before turning left it must read its radar and confirm the way is free, which takes four attempts (`RetryUntilSuccessful`) and still fails, so `MoveOpposite` is not run. The last branch inverts `IsFreeToMoveForward?`: the way forward is not free, the Inverter returns SUCCESS and the Fallback succeeds. Then the robot moves back. (The course figure draws that last child as an action "Move Forward"; the XML has the condition `IsFreeToMoveForward`.)

## Decorator syntax
A decorator wraps exactly one child:
```xml
<Inverter>
    <Condition ID="IsFreeToMove"/>
</Inverter>
<RetryUntilSuccessful num_attempts="4">
    <Measuring/>
</RetryUntilSuccessful>
```
The course writes it as `<Inverter></Inverter><RetryUntilSuccessful num_attempts="4"><RetryUntilSuccessful>`: an empty Inverter and a second opening tag instead of `</RetryUntilSuccessful>`, which is not valid XML.

`<Condition ID="X"/>` and `<X/>` are the same node; the explicit form shows the node type in the XML.

## Pitfalls
- Each SubTree has its own blackboard: to pass data in or out, remap its ports ([[bt-cpp-port-remapping]]).
- The program writes its run to `bt_trace.fbl`; open it in Groot with Log Replay to step through these states ([[bt-cpp-groot-logging]]).
