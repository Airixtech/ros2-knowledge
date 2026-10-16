---
id: nav2-bt-battery-abort
type: reference
owner: equipo-ros2
updated: 2026-10-16
review_by: 2027-04-14
source: manual
confidentiality: internal
title: "Custom BT: abort navigation on low battery (IsBatteryLow + Inverter)"
domain: nav2
area: behavior-trees
distro: humble
tested: false
audience: dev
summary: "abort_when_low_battery.xml: IsBatteryLow ports, Inverter, why the course tree retries 6 recoveries first, immediate-abort variant, test."
tags: [IsBatteryLow, Inverter, low battery, abort_when_low_battery.xml, battery_topic, min_battery, is_voltage, sensor_msgs/BatteryState, PipelineSequence, RecoveryNode]
see: ["[[nav2-bt-control-nodes]]", "[[nav2-behavior-tree-xml]]", "[[nav2-bt-navigator]]", "[[nav2-learn-adv-unit2-behaviors]]"]
requires: [ros2-core, ros2-bt]
version_notes:
  - "humble: IsBatteryLow ports battery_topic (default /battery_status), min_battery, is_voltage (default false); percentage is compared as 0–1; same in Jazzy and Lyrical — https://github.com/ros-navigation/navigation2/blob/humble/nav2_behavior_tree/plugins/condition/is_battery_low_condition.cpp (NAV2-V62)"
  - "humble: inside RecoveryNode number_of_retries=6 a low battery triggers 6 recovery rounds before the goal aborts — https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/configuration_guide/core_servers/bt_plugins/controls/RecoveryNode.md (NAV2-V47)"
---
# Custom BT: abort navigation on low battery (IsBatteryLow + Inverter)

**TL;DR** Nav2 has a behavior node for battery status detection: **`IsBatteryLow`** ([docs](https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/configuration_guide/core_servers/bt_plugins/conditions/IsBatteryLow.md)). It returns FAILURE while the battery level is OK (it checks "is the battery low?"), so negate it with an **`<Inverter>`** to use it as a "keep going" condition.

## Course solution (abort_when_low_battery.xml)
```xml
<!--
  This Behavior Tree replans the global path periodically at 1 Hz, and it also has
  recovery actions.
-->
<root main_tree_to_execute="MainTree">
  <BehaviorTree ID="MainTree">
    <RecoveryNode number_of_retries="6" name="NavigateRecovery">
      <PipelineSequence name="NavigateWithReplanning">
        <Inverter>
          <IsBatteryLow battery_topic="/battery" is_voltage="false" min_battery="0.25" />
        </Inverter>
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
- `IsBatteryLow` reads `sensor_msgs/BatteryState` on `battery_topic`; with `is_voltage="false"` it compares `percentage` (0–1) with `min_battery`: `0.25` = 25 %.
- Because the battery check is inside `RecoveryNode number_of_retries="6"`, a low battery fails the pipeline and the RecoveryNode runs `RecoveryActions` (clear, spin, wait 5 s) and retries: the goal aborts only after six recovery rounds (NAV2-V47).

## Immediate abort `[verify]`
Put the check outside the RecoveryNode, as the first child of a top-level `PipelineSequence`: a PipelineSequence re-ticks earlier children while a later one runs, and a FAILURE stops all children.
```xml
<root main_tree_to_execute="MainTree">
  <BehaviorTree ID="MainTree">
    <PipelineSequence name="AbortWhenLowBattery">
      <Inverter>
        <IsBatteryLow battery_topic="/battery" is_voltage="false" min_battery="0.25"/>
      </Inverter>
      <RecoveryNode number_of_retries="6" name="NavigateRecovery">
        <!-- the NavigateWithReplanning PipelineSequence and RecoveryActions of behavior.xml -->
      </RecoveryNode>
    </PipelineSequence>
  </BehaviorTree>
</root>
```

## Test it
Pass the file to `bt_navigator` with `default_nav_to_pose_bt_xml` ([[nav2-bt-navigator]]), send a goal, and publish the battery state (100 % first, then 20 %):
```bash
ros2 topic pub /battery sensor_msgs/BatteryState '{voltage: 12.0, percentage: 1.0, power_supply_status: 3}'
ros2 topic pub /battery sensor_msgs/BatteryState '{voltage: 12.0, percentage: 0.2, power_supply_status: 3}'
```

## Pitfalls
- `min_battery="25"` with `is_voltage="false"`: percentage is 0–1, so the battery is always "low".
- `nav2_is_battery_low_condition_bt_node` must be in `plugin_lib_names` in Humble ([[nav2-bt-plugin-libs]]).
- To write a similar condition yourself: the C++ of `IsBatteryLow` (shared node from the blackboard, own callback group, `spin_some()` in `tick()`) is the pattern in [[bt-ros2-shared-node]].
