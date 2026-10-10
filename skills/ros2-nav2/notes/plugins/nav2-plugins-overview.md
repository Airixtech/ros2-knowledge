---
id: nav2-plugins-overview
title: "Nav2 plugins: where they are selected (YAML), base classes, override vs virtual"
domain: nav2
area: plugins
distro: humble
tested: false
audience: dev
summary: "Why Nav2 uses plugins; selecting them in YAML (plugins, planner_plugins, controller_plugins); free names; base classes; override."
tags: [Nav2 plugins, pluginlib, plugins, planner_plugins, controller_plugins, GridBased, FollowPath, critics, nav2_costmap_2d::Layer, nav2_core::GlobalPlanner, nav2_core::Controller, override, virtual]
see: ["[[nav2-costmap-layer-api]]", "[[nav2-plugin-description-xml]]", "[[nav2-planner-server]]", "[[nav2-controller-server]]", "[[nav2-costmap-layers]]"]
requires: [ros2-core]
version_notes:
  - "humble: plugin names in planner_plugins are free labels; the BT's planner_id must match one (course: 'it has to be GridBased') — https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/configuration_guide/core_servers/configuring_planner_server.md (NAV2-V49)"
  - "jazzy: plugin types use '::' everywhere (nav2_navfn_planner::NavfnPlanner) — https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/migration_guides/iron/Iron.md (NAV2-V17)"
---
# Nav2 plugins: where they are selected, base classes, override vs virtual

**TL;DR** Why **plugins** in Nav2? They make the pipeline flexible: you change only a `.yaml` file of the controller, planner, etc., and completely change the functionality without much compilation overhead. Costmaps benefit most, because their layers stack on top of each other. Nav2 has a huge selection of plug-and-play plugins ([Nav2 plugins list](https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/navigation_plugins.md)); developers create new ones following a basic API, and contributing them upstream is encouraged.

## Where you set the plugin: the YAML files
**Costmaps** (`planner_server.yaml`, full block in [[nav2-mp400-costmaps]]):
```yaml
global_costmap:
  global_costmap:
    ros__parameters:
      # ...
      plugins: ["static_layer", "obstacle_layer", "inflation_layer"]
      # ...
```
Inside `global_costmap/global_costmap/ros__parameters` the list `plugins` holds names. They can be whatever you want, because they are the namespaces you set afterwards (`static_layer:`, `inflation_layer:`, `obstacle_layer:`, each with its `plugin:` type and parameters): here `nav2_costmap_2d::StaticLayer`, `nav2_costmap_2d::InflationLayer`, `nav2_costmap_2d::ObstacleLayer` ([source (humble)](https://github.com/ros-navigation/navigation2/tree/humble/nav2_costmap_2d/plugins)).

**Planner** (`planner_server.yaml`, [[nav2-planner-server]]):
```yaml
planner_server:
  ros__parameters:
    expected_planner_frequency: 20.0
    use_sim_time: True
    planner_plugins: ["GridBased"]
    GridBased:
      plugin: "nav2_navfn_planner/NavfnPlanner"
      tolerance: 0.5
      use_astar: false
      allow_unknown: true
```
In this case, it is loading the `nav2_navfn_planner/NavfnPlanner` plugin ([nav2_navfn_planner code (humble)](https://github.com/ros-navigation/navigation2/tree/humble/nav2_navfn_planner)). The course claims, "after some tests", that the name **must be `GridBased`**, because renaming it gives:
```
planner GridBased is not a valid planner. Planner names are: WHATEVER_NAME_YOU_GAVE.
```
That error comes from the behavior tree, which asks for `planner_id="GridBased"` in `ComputePathToPose` ([[nav2-bt-action-nodes]]). Any name works if the BT uses the same one (or leaves `planner_id` empty with a single planner).

**Controller** (`controller.yaml`, [[nav2-controller-server]]): `controller_plugins: ["FollowPath"]` and `FollowPath: plugin: "dwb_core::DWBLocalPlanner"`. It loads **more plugins** inside: the critics, of base class `dwb_core::TrajectoryCritic` ([[nav2-dwb-generators-critics]]).
```yaml
critics: ["RotateToGoal", "Oscillation", "ObstacleFootprint", "GoalAlign", "PathAlign", "PathDist", "GoalDist"]
```

## Base classes and override
Plugins that regulate the same element (costmaps, planning, controllers, behavior trees) share a structure, fixed by their **base class**: `nav2_costmap_2d::Layer` ([[nav2-costmap-layer-api]]), `nav2_core::GlobalPlanner` ([[nav2-planner-plugin-straight-line]]), `nav2_core::Controller` ([[nav2-controller-plugin-rpp]]). NavFn declares its methods with `override` only:
```cpp
NavfnPlanner();
~NavfnPlanner();
void configure(
  const rclcpp_lifecycle::LifecycleNode::WeakPtr & parent,
  std::string name, std::shared_ptr<tf2_ros::Buffer> tf,
  std::shared_ptr<nav2_costmap_2d::Costmap2DROS> costmap_ros) override;
void cleanup() override;
void activate() override;
void deactivate() override;
nav_msgs::msg::Path createPlan(
  const geometry_msgs::msg::PoseStamped & start,
  const geometry_msgs::msg::PoseStamped & goal) override;
```
- `virtual` goes on the base class declaration, so a derived class may override it; it is needed **only in the base**.
- `override` marks a derived-class override: not compulsory, but it gives a **compilation error** if the signature does not match the base, which helps maintain the code.

Custom plugin creation follows the same steps for all three kinds; the details depend on the base class. Before starting, make sure a default navigation setup works ([[nav2-learn-adv-unit3-plugins]]).

## Pitfalls
- Renaming a plugin in one file only (YAML, BT XML or launch) → "is not a valid planner/controller".
- Without `override`, a mismatched signature of an optional method (e.g. `matchSize()`) compiles but is never called; for a required (pure virtual) method the class stays abstract and the plugin export fails to compile.
