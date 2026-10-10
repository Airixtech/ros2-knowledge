---
id: nav2-bt-action-nodes
title: "Nav2 BT action nodes: ComputePathToPose, FollowPath, ClearEntireCostmap, Spin, Wait"
domain: nav2
area: behavior-trees
distro: humble
tested: false
audience: dev
summary: "Nav2 BT action nodes and their servers: ComputePathToPose (planner_id), FollowPath (controller_id), ClearEntireCostmap, Spin (radians), Wait."
tags: [ComputePathToPose, FollowPath, ClearEntireCostmap, Spin, Wait, spin_dist, wait_duration, planner_id, controller_id, service_name, clear_entirely_global_costmap, behavior_server, BT action nodes]
see: ["[[nav2-bt-control-nodes]]", "[[nav2-behavior-tree-xml]]", "[[nav2-planner-server]]", "[[nav2-controller-server]]", "[[nav2-behavior-server]]"]
requires: [ros2-core]
version_notes:
  - "humble: spin_dist is in radians (default 1.57), wait_duration in seconds (int, default 1); both actions are served by behavior_server (nav2_behaviors), not nav2_recoveries — https://github.com/ros-navigation/navigation2/blob/humble/nav2_behavior_tree/include/nav2_behavior_tree/plugins/action/spin_action.hpp (NAV2-V46, NAV2-V31, NAV2-V62)"
  - "jazzy: BT.CPP 4.5 XML format; Nav2 BT nodes load without plugin_lib_names — https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/migration_guides/iron/Iron.md (NAV2-V19, NAV2-V20)"
---
# Nav2 BT action nodes: ComputePathToPose, FollowPath, ClearEntireCostmap, Spin, Wait

**TL;DR** The leaves of the navigation tree call the Nav2 servers: the planner, the controller, the costmap clear services and the behavior server. Ports pass data through the blackboard ([[nav2-bt-control-nodes]]).

## ComputePathToPose (Nav2)
Calls the `ComputePathToPose` action server of the **planner server** (`nav2_planner`) to compute the path to the goal. The goal comes in a **blackboard variable** (`{goal}`); the result of the planner goes to another blackboard variable (`{path}`):
```xml
<RecoveryNode number_of_retries="1" name="ComputePathToPose">
  <ComputePathToPose goal="{goal}" path="{path}" planner_id="GridBased"/>
  <ClearEntireCostmap service_name="global_costmap/clear_entirely_global_costmap"/>
</RecoveryNode>
```
Someone put the value of `{goal}` on the blackboard (bt_navigator, from the NavigateToPose goal), and the node fills `{path}`. `goal` and `planner_id` are input ports, `path` is an output port. `planner_id` must be a name in `planner_plugins` ([[nav2-planner-server]]).

## ClearEntireCostmap (Nav2)
Calls the service that clears a costmap; `service_name` chooses the local or the global one:
```xml
<ClearEntireCostmap service_name="global_costmap/clear_entirely_global_costmap"/>
<ClearEntireCostmap service_name="local_costmap/clear_entirely_local_costmap"/>
```

## FollowPath (Nav2)
Calls the `FollowPath` action server of the **controller server**, which sends commands to the robot's wheels to follow the computed path:
```xml
<FollowPath path="{path}" controller_id="FollowPath"/>
```
`controller_id` must be a name in `controller_plugins` ([[nav2-controller-server]]).

## Spin and Wait (Nav2)
```xml
<SequenceStar name="RecoveryActions">
  <ClearEntireCostmap service_name="local_costmap/clear_entirely_local_costmap"/>
  <ClearEntireCostmap service_name="global_costmap/clear_entirely_global_costmap"/>
  <Spin spin_dist="1.57"/>
  <Wait wait_duration="5"/>
</SequenceStar>
```
- `Spin` calls the `spin` action of the **behavior server** (`nav2_behaviors`, [[nav2-behavior-server]]): the robot rotates in place by `spin_dist` **radians** (1.57 = 90°; the course said degrees).
- `Wait` calls the `wait` action of the behavior server: it waits `wait_duration` seconds.

## Further reading
There are many other nodes you can use: [Nav2 BT nodes](https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/configuration_guide/core_servers/bt_plugins/index.md). To work heavily with behaviors, learn behavior trees in general and the BehaviorTree.CPP library: [Behavior Trees in Robotics and AI](https://arxiv.org/pdf/1709.00084.pdf), [BehaviorTree.CPP documentation](https://www.behaviortree.dev/) (it documents version 4; Humble uses 3.8).

## Pitfalls
- A node whose library is missing from `plugin_lib_names` (Humble) → "node not registered" ([[nav2-bt-plugin-libs]]).
- Wrong `service_name` → while the tree is created, the node waits `wait_for_service_timeout` and throws "service server … not available": the tree does not load and the goal fails.
