---
id: nav2-costmap-filters
title: "Costmap filters: filter info server, mask server, filters.yaml, launch"
domain: nav2
area: costmaps
distro: humble
tested: false
audience: dev
summary: "Costmap filters (keepout, speed, binary): costmap_filter_info_server + mask map_server, CostmapFilterInfo, filters.yaml (type, base, multiplier, mask_topic), launch and lifecycle."
tags: [costmap filters, costmap_filter_info_server, CostmapFilterInfo, filter_mask_server, map_server, filters.yaml, mask_topic, filter_info_topic, base, multiplier, type, BinaryFilter, toggle_filter]
see: ["[[nav2-keepout-filter]]", "[[nav2-speed-filter]]", "[[nav2-costmap-layers]]", "[[nav2-map-server]]", "[[nav2-lifecycle-manager]]"]
requires: [ros2-core]
version_notes:
  - "humble: filter types 0 keepout/preferred lanes, 1 speed %, 2 speed m/s, 3 binary (BinaryFilter); toggle_filter service (Iron backports in 1.1.20); info server defaults type 0, base 0.0, multiplier 1.0, mask_topic filter_mask — https://github.com/ros-navigation/navigation2/blob/humble/nav2_costmap_2d/include/nav2_costmap_2d/costmap_filters/filter_values.hpp (NAV2-V61)"
  - "lyrical: keepout and speed zones in the default bringup, vector object server for masks (Kilted); zone parameter filter (type 4) — https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/migration_guides/kilted/Kilted.md (NAV2-V61)"
---
# Costmap filters: filter info server, mask server, filters.yaml, launch

**TL;DR** Nav2 offers a powerful set of features known as **Costmap filters**, which allow you to modify the robot's navigation behavior based on specific areas of the map. A Costmap filter acts as an additional layer (or mask) applied to your existing Costmaps, enabling more dynamic and context-aware navigation strategies. For example, **Keepout Zones** prevent the robot from entering restricted areas ([[nav2-keepout-filter]]), and in **Speed Restricted Zones** the robot's speed is automatically adjusted depending on the designated region ([[nav2-speed-filter]]).

## The two extra nodes
- **Costmap Filter Info Server** (`nav2_map_server`, executable `costmap_filter_info_server`): publishes `nav2_msgs/CostmapFilterInfo` messages with metadata such as the filter type or data conversion coefficients.
- **Mask Map Server** (`nav2_map_server`, executable `map_server`, here named `filter_mask_server`): publishes the mask as an `OccupancyGrid`.

Both messages are required to be published as a pair to generate the Costmap filter. Design: [CostmapFilters_design.pdf](https://github.com/ros-navigation/navigation2/blob/humble/doc/design/CostmapFilters_design.pdf).

## config/filters.yaml (keepout version)
```yaml
costmap_filter_info_server:
  ros__parameters:
    use_sim_time: true
    filter_info_topic: "/costmap_filter_info"
    type: 0
    mask_topic: "/keepout_filter_mask"
    base: 0.0
    multiplier: 1.0
filter_mask_server:
  ros__parameters:
    use_sim_time: true
    frame_id: "map"
    topic_name: "/keepout_filter_mask"
    yaml_filename: "/home/user/ros2_ws/src/nav2_pkgs/map_server/maps/map_keepout.yaml"
```
- **`type`**: 0 for Keepout Zones/preferred lanes filter, 1 for speed filter (speed limit in % of maximum speed), 2 for speed filter (speed limit in absolute value, m/s). Humble also has 3, the `BinaryFilter` (publishes a `std_msgs/Bool` when the robot enters or leaves a marked area).
- **`mask_topic`** sets the topic of the filter mask: it must be the same as the **`topic_name`** parameter of the mask map server.
- **`base`** and **`multiplier`** are coefficients used for applying the mask: `filter_space_value = base + multiplier * mask_value`. For Keepout Zones set them to 0.0 and 1.0: a one-to-one conversion from OccupancyGrid values to the filter value space.
- The filter plugin in the costmap reads `filter_info_topic`, the same topic as the info server ([[nav2-keepout-filter]]).

## Add the nodes to navigation.launch.py
```python
filters_yaml = os.path.join(get_package_share_directory('path_planner_server'), 'config', 'filters.yaml')
```
```python
Node(package='nav2_map_server', executable='map_server', name='filter_mask_server',
     output='screen', emulate_tty=True, parameters=[filters_yaml]),
Node(package='nav2_map_server', executable='costmap_filter_info_server', name='costmap_filter_info_server',
     output='screen', emulate_tty=True, parameters=[filters_yaml]),
```
Finally, and important, add the new nodes to be started on the lifecycle manager:
```python
{'node_names': ['map_server', 'amcl', 'controller_server', 'planner_server', 'recoveries_server',
                'bt_navigator', 'waypoint_follower', 'filter_mask_server', 'costmap_filter_info_server']}
```
Compile, then test with `ros2 launch path_planner_server navigation.launch.py`.

## Pitfalls
- `mask_topic` ≠ `topic_name` → the filter never receives a mask and has no effect.
- Both servers are lifecycle nodes: missing from `node_names` → nothing is published.
- The absolute `yaml_filename` is the course environment's path; you can pass it from the launch file instead (`os.path.join(get_package_share_directory('map_server'), 'maps', 'map_keepout.yaml')`).
