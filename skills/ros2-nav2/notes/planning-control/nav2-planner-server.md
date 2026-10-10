---
id: nav2-planner-server
title: "planner_server and NavFn (A* vs Dijkstra) parameters"
domain: nav2
area: planning-control
distro: humble
tested: false
audience: dev
summary: "planner_server (global planner): launch, planner_server.yaml with NavFn GridBased plugin, tolerance/use_astar/allow_unknown, expected_planner_frequency meaning."
tags: [planner_server, nav2_planner, NavfnPlanner, GridBased, use_astar, Dijkstra, allow_unknown, expected_planner_frequency, planner_plugins]
see: ["[[nav2-global-costmap]]", "[[nav2-controller-server]]", "[[nav2-behavior-tree-xml]]", "[[core-nav2-tuning]]"]
requires: [ros2-core]
version_notes:
  - "humble: expected_planner_frequency defaults to 1.0 and only sets the overrun-warning threshold — https://github.com/ros-navigation/navigation2/blob/humble/nav2_planner/src/planner_server.cpp (NAV2-V06)"
  - "humble: planners NavFn, Smac (2D, Hybrid-A*, Lattice), Theta* are released (not only NavFn) — http://packages.ros.org/ros2/ubuntu/dists/jammy/main/binary-amd64/Packages.gz (NAV2-V04)"
  - "jazzy: plugin name nav2_navfn_planner::NavfnPlanner (the '/' form is Humble) — https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/migration_guides/iron/Iron.md (NAV2-V17)"
---
# planner_server and NavFn (A* vs Dijkstra) parameters

**TL;DR** The planner (ROS 1 "global planner") computes a path from the robot to the goal that avoids the **known** obstacles of the global costmap. Package `nav2_planner`, executable `planner_server`; the algorithm is a plugin (NavFn here).

## Launch and config
```python
        Node(package='nav2_planner', executable='planner_server', name='planner_server',
             output='screen', parameters=[planner_yaml]),
```
`config/planner_server.yaml` (a typical base config; the global costmap block goes in the same file, [[nav2-global-costmap]]):
```yaml
planner_server:
  ros__parameters:
    expected_planner_frequency: 10.0
    use_sim_time: True
    planner_plugins: ["GridBased"]
    GridBased:
      plugin: "nav2_navfn_planner/NavfnPlanner"
      tolerance: 0.5
      use_astar: false
      allow_unknown: true
```
The path is computed when a goal arrives (e.g. RViz **Nav2 Goal**) and re-computed as the behavior tree requests it (1 Hz in [[nav2-behavior-tree-xml]]).

## Planner server parameters
| Parameter | Default | Meaning |
|---|---|---|
| `expected_planner_frequency` | 1.0 Hz (Nav2's config: 20.0) | expected rate: a warning is printed when planning takes longer than 1/frequency. It does **not** trigger planning |
| `planner_plugins` | `["GridBased"]` | list of mapped plugin names; each name needs a `plugin` parameter with the type to load |

## NavFn (`nav2_navfn_planner/NavfnPlanner`)
NavFn uses **Dijkstra** or **A\*** on the costmap:
- `use_astar: false` (Dijkstra): finds the shortest path under any condition.
- `use_astar: true` (A\*): expands the potential field towards the goal with a heuristic, faster, but the path is not guaranteed to be the shortest.

| Parameter | Default | Meaning |
|---|---|---|
| `GridBased.tolerance` | 0.5 m | allowed distance between the goal and the end of the path |
| `GridBased.use_astar` | false | A\* instead of Dijkstra |
| `GridBased.allow_unknown` | true | allow planning through unknown space |
| `GridBased.use_final_approach_orientation` | false | set the last pose's orientation from the approach direction |

Other Humble planners (Smac 2D / Hybrid-A\* / Lattice, Theta\*) and how to choose: [[core-nav2-tuning]]. Docs: [planner server](https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/configuration_guide/core_servers/configuring_planner_server.md).

## Pitfalls
- `planner_id` in the BT XML must equal a name in `planner_plugins` (`GridBased`), or ComputePathToPose fails.
- "Failed to create plan" with the goal inside an inflated area → raise `tolerance` or reduce inflation.
