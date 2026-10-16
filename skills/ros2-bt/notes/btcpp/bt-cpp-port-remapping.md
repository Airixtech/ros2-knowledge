---
id: bt-cpp-port-remapping
type: reference
owner: equipo-ros2
updated: 2026-10-15
review_by: 2027-04-13
source: manual
confidentiality: internal
title: "Remapping ports between a tree and its SubTrees"
domain: bt
area: btcpp
distro: humble
tested: false
audience: dev
summary: "Each SubTree has its own blackboard; connect entries with SubTree attributes (targetXY=\"move_goalXY\"); blackboard debugMessage; bt_u3_ex4."
tags: [SubTree, port remapping, blackboard, targetXY, outputXY, MoveRobotXY, SequenceStar, ForceFailure, debugMessage, _autoremap]
see: ["[[bt-cpp-blackboard]]", "[[bt-cpp-subtrees-decorators]]", "[[bt-humble-to-jazzy]]", "[[bt-learn-unit3]]"]
requires: [ros2-core]
version_notes:
  - "v4: remapping values need braces, target=\"{move_goal}\"; __shared_blackboard → _autoremap; SubTreePlus removed — https://github.com/BehaviorTree/BehaviorTree.CPP/blob/master/convert_v3_to_v4.py (BT-V26)"
  - "all: the shown output prints 'mission OK' while the XML sets 'mission accomplished' (BT-V18)"
---
# Remapping ports between a tree and its SubTrees

**TL;DR** Every tree and every SubTree has its **own** blackboard, so large trees do not clash on names. To pass data, remap the SubTree's internal keys to the parent's keys in the `<SubTree>` tag: `<SubTree ID="MoveRobotXY" targetXY="move_goalXY" outputXY="move_resultXY"/>` (attribute = internal key, value = parent key). [v4: values need braces, `targetXY="{move_goalXY}"`]

## XML
```xml
<root main_tree_to_execute = "MainTree">
    <BehaviorTree ID="MainTree">
        <Sequence name="main_sequence">
            <SetBlackboard output_key="move_goalXY" value="1;2;3" />
            <SubTree ID="MoveRobotXY" targetXY="move_goalXY" outputXY="move_resultXY" />
            <RobotTarget     input="{move_resultXY}" />
            <SetBlackboard output_key="move_goal" value="1;2;3" />
            <SubTree ID="MoveRobot" target="move_goal" output="move_result" />
            <SaySomething message="{move_result}"/>
        </Sequence>
    </BehaviorTree>

    <BehaviorTree ID="MoveRobotXY">
        <Fallback name="move_robot_main">
            <SequenceStar>
                <MoveBase       goal="{targetXY}"/>
                <SetBlackboard output_key="outputXY" value="8;9" />
            </SequenceStar>
            <ForceFailure>
                <SetBlackboard output_key="outputXY" value="0;0" />
            </ForceFailure>
        </Fallback>
    </BehaviorTree>

    <BehaviorTree ID="MoveRobot">
        <Fallback name="move_robot_main">
            <SequenceStar>
                <MoveBase       goal="{target}"/>
                <SetBlackboard output_key="output" value="mission accomplished" />
            </SequenceStar>
            <ForceFailure>
                <SetBlackboard output_key="output" value="mission failed" />
            </ForceFailure>
        </Fallback>
    </BehaviorTree>
</root>
```
Trees generated from that XML. Legend: `[→]` Sequence · `[→*]` SequenceStar · `[?]` Fallback · `◇` decorator · `⤷` SubTree.
```text
BehaviorTree "MainTree"
└── [→] Sequence name="main_sequence"
    ├── SetBlackboard  output_key="move_goalXY" value="1;2;3"
    ├── ⤷ SubTree "MoveRobotXY"  targetXY="move_goalXY" outputXY="move_resultXY"
    ├── RobotTarget  input="{move_resultXY}"
    ├── SetBlackboard  output_key="move_goal" value="1;2;3"
    ├── ⤷ SubTree "MoveRobot"  target="move_goal" output="move_result"
    └── SaySomething  message="{move_result}"

BehaviorTree "MoveRobotXY"
└── [?] Fallback name="move_robot_main"
    ├── [→*] SequenceStar
    │   ├── MoveBase  goal="{targetXY}"
    │   └── SetBlackboard  output_key="outputXY" value="8;9"
    └── ◇ ForceFailure
        └── SetBlackboard  output_key="outputXY" value="0;0"

BehaviorTree "MoveRobot"  (same shape: goal="{target}", output = "mission accomplished" / "mission failed")
```

## What is connected
| MainTree blackboard (parent) | SubTree "MoveRobotXY" blackboard (internal) | Direction |
|---|---|---|
| `move_goalXY` (written by SetBlackboard, "1;2;3") | `targetXY` → read by `MoveBase goal="{targetXY}"` | into the subtree |
| `move_resultXY` → read by `RobotTarget input="{move_resultXY}"` | `outputXY` (written by SetBlackboard, "8;9", or "0;0" on failure) | out of the subtree |

The mapping lives only in the parent's `<SubTree>` tag: it creates a link between the two blackboards, not a copy.

## Output (`bt_u3_ex4`)
```text
[ MoveBase: STARTED ]. goal: x=1 y=2.0 theta=3.00
[ MoveBase: FINISHED ]
Converting string: "8;9"
Target positions: [ 8.0, 9.0 ]
[ MoveBase: STARTED ]. goal: x=1 y=2.0 theta=3.00
[ MoveBase: FINISHED ]
Robot says: mission OK
--------------
move_result (std::string) -> full
move_goal (Pose2D) -> full
move_resultXY (Position2D) -> full
move_goalXY (Pose2D) -> full
--------------
outputXY (Position2D) -> remapped to parent [move_resultXY]
targetXY (Pose2D) -> remapped to parent [move_goalXY]
```
- `MoveBase` reads the remapped goal 1;2;3 (x, y, theta); the subtree writes "8;9", which `RobotTarget` reads through `move_resultXY` (converted from text, [[bt-cpp-blackboard]]).
- The two blocks after `----` are the blackboards' `debugMessage()` (as in BehaviorTree.CPP [tutorial 06](https://github.com/BehaviorTree/BehaviorTree.CPP/blob/v3.8/docs/tutorial_06_subtree_ports.md)): the main tree's entries, then the subtree's remapped ones.
- The output says `mission OK` while this XML writes `mission accomplished`: the program that produced the output used another string.

## Pitfalls
- Without remapping, a key written inside a SubTree is invisible to the parent (separate blackboards).
- The same XML in v4 needs braces in the SubTree attributes; v3 SubTree attributes are plain key names ([[bt-humble-to-jazzy]]).
