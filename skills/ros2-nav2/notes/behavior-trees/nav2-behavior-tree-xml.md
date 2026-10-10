---
id: nav2-behavior-tree-xml
title: "Navigation behavior tree XML: replanning and recoveries"
domain: nav2
area: behavior-trees
distro: humble
tested: false
audience: dev
summary: "behavior.xml for bt_navigator: replan at 1 Hz (RateController, ComputePathToPose), FollowPath, RecoveryNode, clear costmaps, Spin, Wait; BT.CPP v4 changes."
tags: [behavior tree, BT XML, RecoveryNode, PipelineSequence, RateController, ComputePathToPose, FollowPath, ClearEntireCostmap, Spin, Wait, BehaviorTree.CPP]
see: ["[[nav2-bt-navigator]]", "[[nav2-bt-plugin-libs]]", "[[nav2-behavior-server]]", "[[core-nav2-tuning]]"]
requires: [ros2-core]
version_notes:
  - "humble: BehaviorTree.CPP 3.8; Nav2's default XML uses RoundRobin + BackUp for recoveries — https://github.com/ros-navigation/navigation2/blob/humble/nav2_bt_navigator/behavior_trees/navigate_to_pose_w_replanning_and_recovery.xml (NAV2-V20)"
  - "jazzy: BT.CPP 4.5: <root BTCPP_format=\"4\" …>, new SubTree syntax; SequenceStar still accepted as an alias of SequenceWithMemory — https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/migration_guides/iron/Iron.md (NAV2-V20)"
---
# Navigation behavior tree XML: replanning and recoveries

**TL;DR** The behavior of `bt_navigator` is an XML behavior tree: when to call the planner, when to call the controller and when to run a recovery. This tree (from the official Nav2 package) replans the global path at 1 Hz and has recovery actions.

## config/behavior.xml
```xml
<!--
  This Behavior Tree replans the global path periodically at 1 Hz, and has
  recovery actions. Obtained from the official Nav2 package
-->
<root main_tree_to_execute="MainTree">
  <BehaviorTree ID="MainTree">
    <RecoveryNode number_of_retries="6" name="NavigateRecovery">
      <PipelineSequence name="NavigateWithReplanning">
        <RateController hz="1.0">
          <RecoveryNode number_of_retries="1" name="ComputePathToPose">
            <ComputePathToPose goal="{goal}" path="{path}" planner_id="GridBased"/>
            <ClearEntireCostmap service_name="global_costmap/clear_entirely_global_costmap"/>
          </RecoveryNode>
        </RateController>
        <RecoveryNode number_of_retries="1" name="FollowPath">
          <FollowPath path="{path}" controller_id="FollowPath"/>
          <ClearEntireCostmap service_name="local_costmap/clear_entirely_local_costmap"/>
        </RecoveryNode>
      </PipelineSequence>
      <SequenceStar name="RecoveryActions">
        <ClearEntireCostmap service_name="local_costmap/clear_entirely_local_costmap"/>
        <ClearEntireCostmap service_name="global_costmap/clear_entirely_global_costmap"/>
        <Spin spin_dist="1.57"/>
        <Wait wait_duration="5"/>
      </SequenceStar>
    </RecoveryNode>
  </BehaviorTree>
</root>
```

## How it reads
- `RecoveryNode` (n retries): ticks its first child; if it fails, runs the second child (the recovery) and retries the first, up to `number_of_retries` times.
- `PipelineSequence`: keeps re-ticking earlier children (replanning) while a later one (following) runs.
- `RateController hz="1.0"`: computes a new path once per second.
- `ComputePathToPose` / `FollowPath`: call the planner and the controller; `planner_id` and `controller_id` must match the names in `planner_plugins` and `controller_plugins` ([[nav2-planner-server]], [[nav2-controller-server]]).
- Recovery actions when navigation keeps failing: clear both costmaps, spin 1.57 rad, wait 5 s (served by the behavior server, [[nav2-behavior-server]]).

Install it and point `default_nav_to_pose_bt_xml` to it ([[nav2-bt-navigator]]). Detailed BT customization: [Nav2 behavior trees](https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/getting_started/nav2_behavior_trees/index.md).

## Pitfalls
- Every node in the XML needs its library in `plugin_lib_names` (Humble) ([[nav2-bt-plugin-libs]]).
- [changed in Jazzy: add `BTCPP_format="4"` to `<root>` and migrate SubTrees; the script `convert_v3_to_v4.py` of BehaviorTree.CPP helps]
