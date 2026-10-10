---
id: nav2-speed-filter
title: "Speed limit zones: scale-mode mask, SpeedFilter, speed_limit topic"
domain: nav2
area: costmaps
distro: humble
tested: false
audience: dev
summary: "Speed limit zones: gray mask in scale mode, nav2_costmap_2d::SpeedFilter, filters.yaml type 1 (base 100, multiplier -1), speed_limit_topic in controller_server, /speed_limit."
tags: [speed limits, speed restricted zones, SpeedFilter, nav2_costmap_2d::SpeedFilter, speed_limit_topic, speed_limit, SpeedLimit, mode scale, map_speed.yaml, filters.yaml]
see: ["[[nav2-costmap-filters]]", "[[nav2-keepout-filter]]", "[[nav2-controller-server]]", "[[nav2-map-server]]"]
requires: [ros2-core]
version_notes:
  - "humble: the course's filters.yaml loads map_speeds.yaml but the mask is map_speed.yaml; fixed below — https://github.com/ros-navigation/navigation2/blob/humble/nav2_map_server/src/map_server/map_server.cpp (NAV2-V44)"
  - "humble: mask 0 = no limit, 1–100 → speed_limit = mask * multiplier + base; a result of 0.0 is published as no limit; controller_server speed_limit_topic default speed_limit — https://github.com/ros-navigation/navigation2/blob/humble/nav2_costmap_2d/plugins/costmap_filters/speed_filter.cpp (NAV2-V61)"
---
# Speed limit zones: scale-mode mask, SpeedFilter, speed_limit topic

**TL;DR** The **Speed Limits Filter** works on the same principle as the **Keepout Zones Filter** ([[nav2-keepout-filter]]), but with a different interpretation of the mask values: the mask encodes **speed limits** for the map areas corresponding to each cell.

## 1. Edit the map
OccupancyGrid values fall within the `[0..100]` range. For the Speed Filter:
- A value of `0` indicates **no speed limit** in the corresponding map area.
- Values from `1` to `100` are **linearly converted** into a speed limit: `speed_limit = filter_mask_data * multiplier + base`.

With the coefficients below, **lighter shades of gray correspond to higher speed limits** and **darker shades to lower speed limits**. Start again from **map_rotated.pgm** and paint in **GREY** (different tones for different areas) where the robot must have speed limits. Rename it **map_speed.pgm**, put it in the **maps** folder of the **map_server** package and create **map_speed.yaml**:
```yaml
image: map_speed.pgm
resolution: 0.050000
origin: [-7.000, -10.500000, 0.000000]
negate: 0
occupied_thresh: 1.0
free_thresh: 0.0
mode: scale
```
Besides the map name, these values changed: with `mode: scale` the map server uses the grayscale intensity directly as a numeric value (dark = 100, white = 0), instead of only free/occupied, and `occupied_thresh: 1.0` with `free_thresh: 0.0` keep the **full range** available for scaling. This lets you encode **speed limits smoothly** across the map (darker = slower, lighter = faster) instead of having only binary free/blocked regions.

## 2. Configure the speed filter
In this unit the speed filter is applied only to the global Costmap (`planner_server.yaml`):
```yaml
# For Keepout Zones
#filters: ["keepout_filter"]
# For Speed Limits
filters: ["speed_filter"]
speed_filter:
  plugin: "nav2_costmap_2d::SpeedFilter"
  enabled: True
  filter_info_topic: "/costmap_filter_info"
  speed_limit_topic: "/speed_limit"
```
Specify the same **`speed_limit_topic`** in the **`controller_server`** configuration (`controller.yaml`):
```yaml
controller_server:
  ros__parameters:
    # ...
    # For Speed Limits
    speed_limit_topic: "/speed_limit"
```
Update **filters.yaml** ([[nav2-costmap-filters]]):
```yaml
costmap_filter_info_server:
  ros__parameters:
    use_sim_time: true
    filter_info_topic: "/costmap_filter_info"
    # For Keepout Zones
    #type: 0
    #mask_topic: "/keepout_filter_mask"
    #base: 0.0
    #multiplier: 1.0
    # For Speed Limits
    type: 1
    mask_topic: "/speed_filter_mask"
    base: 100.0
    multiplier: -1.0
filter_mask_server:
  ros__parameters:
    use_sim_time: true
    frame_id: "map"
    # For Keepout Zones
    #topic_name: "/keepout_filter_mask"
    #yaml_filename: "/home/user/ros2_ws/src/map_server/maps/map_keepout.yaml"
    # For Speed Limits
    topic_name: "/speed_filter_mask"
    yaml_filename: "/home/user/ros2_ws/src/nav2_pkgs/map_server/maps/map_speed.yaml"   # course: map_speeds.yaml
```
`type: 1` with `base: 100.0`, `multiplier: -1.0` gives a limit in % of the maximum speed: `100 − mask`. Compile and launch `navigation.launch.py`; to see the mask, add a **Map** display on `/speed_filter_mask`. Send a Nav2 Goal and check how the speed limit changes with the area: each time the robot enters a new speed-limited area, a `nav2_msgs/msg/SpeedLimit` message (`percentage`, `speed_limit`) is published on **`/speed_limit`**.

## Pitfalls
- Pure black (100) gives 0 %, and 0.0 is the "no limit" value: the robot drives at full speed. Use dark gray, not black.
- A transparent or unknown mask cell is an error for this filter: the previous limit is kept.
- `speed_limit_topic` different in the costmap and the controller → the limit is computed but never applied.
