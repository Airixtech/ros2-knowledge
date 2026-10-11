---
id: core-nav2-tuning
type: reference
owner: equipo-ros2
updated: 2026-10-10
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "Nav2 tuning: costmaps, planners, controllers, BT, AMCL"
domain: core
area: architecture
distro: humble
tested: false
audience: dev
summary: "Global vs local costmap settings, inflation, planner/controller choice, plugin naming, BT XML customization, AMCL params, anti-patterns."
tags: [Nav2, costmap, inflation, SmacPlanner, MPPI, RPP, DWB, behavior tree, AMCL]
see: ["[[core-nav2-overview]]", "[[core-nav2-python-client]]", "[[core-arch-layers]]"]
requires: []
version_notes:
  - "jazzy: BehaviorTree.CPP 4.5 (XML migration), plugin names standardized to '::' — https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/migration_guides/iron/Iron.md (V56, V57)"
---
# Nav2 tuning: costmaps, planners, controllers, BT, AMCL

**TL;DR** The global costmap is in `map` (static, ~1 Hz) and the local one in `odom` (rolling, ~5 Hz). The inflation radius must be larger than the robot radius. Start with SmacPlanner2D + RPP for diff-drive, and use MPPI for dynamic obstacles.

Parameter-by-parameter detail and complete course configs: skill ros2-nav2.

## Costmaps
Global (`global_frame: map`, `rolling_window: false`, 1 Hz, static+obstacle+inflation) vs local (`odom`, rolling 3×3 m, 5 Hz, obstacle/voxel+inflation).
```yaml
inflation_layer:
  plugin: "nav2_costmap_2d::InflationLayer"
  inflation_radius: 0.55        # > robot radius (indoor corridors: 1.0-1.75 with soft decay)
  cost_scaling_factor: 3.0      # higher = sharper decay
```

## Planners & controllers
- Planners: SmacPlanner2D (holonomic/diff, NavFn replacement) · SmacPlannerHybrid (Ackermann, long robots) · SmacPlannerLattice (arbitrary shapes).
- Controllers: RPP (default choice for diff-drive) · MPPI (dynamic obstacles; omni/diff/ackermann) · DWB (needs tuning; not for Ackermann). MPPI is available as a Humble binary through a later backport.
- Plugin names in Humble mix `/` and `::` [changed in Jazzy: all `::`, e.g. `nav2_navfn_planner::NavfnPlanner`, `nav2_behaviors::Spin`].

## Behavior trees
Copy the default XML into your pkg and set `default_nav_to_pose_bt_xml`. Useful nodes: PipelineSequence, RecoveryNode+RoundRobin, ReactiveFallback+GoalUpdated. [changed in Jazzy: BehaviorTree.CPP v3 → 4.5, so XML and SubTree syntax must be migrated, and custom control/decorator nodes must handle `SKIPPED`]

## Localization
AMCL (`min_particles 500`, `max_particles 2000`, `update_min_d 0.25`). SLAM Toolbox async for mapping, or in localization mode.

## Anti-patterns
Duplicate TF publishers · inflation_radius < robot radius · same frequency for global and local costmaps · `transform_tolerance > 1 s` to hide drift · missing TRANSIENT_LOCAL on /map · inconsistent `use_sim_time` · AMCL without an initial pose ([[core-nav2-python-client]]) · heavy logging in the controller loop.
