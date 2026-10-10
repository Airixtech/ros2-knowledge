---
id: nav2-keepout-filter
title: "Keepout zones: mask map, KeepoutFilter in both costmaps"
domain: nav2
area: costmaps
distro: humble
tested: false
audience: dev
summary: "Keepout zones and preferred lanes: black mask, map_keepout.yaml, KeepoutFilter in both costmaps, Trajectory Hits Obstacle near a zone."
tags: [keepout zones, KeepoutFilter, nav2_costmap_2d::KeepoutFilter, keepout mask, map_keepout.yaml, filters, preferred lanes, ObstacleFootprint, Trajectory Hits Obstacle, override_lethal_cost]
see: ["[[nav2-costmap-filters]]", "[[nav2-speed-filter]]", "[[nav2-mp400-costmaps]]", "[[nav2-global-costmap]]", "[[nav2-dwb-controller]]"]
requires: [ros2-core]
version_notes:
  - "humble: removing ObstacleFootprint (with BaseObstacle not listed) leaves DWB without any collision check — https://github.com/ros-navigation/navigation2/tree/humble/nav2_dwb_controller/dwb_critics/src (NAV2-V43)"
  - "humble: mask values 1–99 give non-lethal costs (mask 0–100 maps linearly to cost 0–254); jazzy: KeepoutFilter override_lethal_cost, lethal_override_cost — https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/tutorials/general_tutorials/navigation2_with_keepout_filter/navigation2_with_keepout_filter.md (NAV2-V61)"
---
# Keepout zones: mask map, KeepoutFilter in both costmaps

**TL;DR** The Keepout Mask is a file similar to a map, containing the mask to apply as the Keepout Zone. Paint the zones the robot must avoid in **black** on a copy of the map, publish it with the mask server ([[nav2-costmap-filters]]) and add a `KeepoutFilter` to **both** costmaps.

## 1. Edit the map
To apply a mask you need a map file of the environment: start from **map_rotated.pgm** and paint the map area you want your robot to avoid in **BLACK**.

Why black? The shade of each pixel on the mask means encoded information for the specific Costmap filter you will use. The incoming mask file is read by the map server and converted into OccupancyGrid values from the [0..100] range, where 0 means free cell and 100 means occupied cell. For the **Keepout Filter** mask, the higher the value, the more restricted the area: a black area corresponds to 100 (the robot can not navigate through it). For values in between, the robot is allowed to move in these areas, but its presence there is "undesirable" (the higher the value, the sooner planners will try to get the robot out of this area).

Rename the edited map file to **map_keepout.pgm**, put it in the **maps** folder of the **map_server** package and create its YAML:
```yaml
image: map_keepout.pgm
resolution: 0.050000
origin: [-7.000, -10.500000, 0.000000]
negate: 0
occupied_thresh: 0.65
free_thresh: 0.196
```

## 2. Costmap configuration (planner_server.yaml and controller.yaml)
Add a **`filters`** parameter and the configuration of the filter, which uses the plugin **`KeepoutFilter`**. Apply the changes to the global and the local Costmaps:
```yaml
global_costmap:
  global_costmap:
    ros__parameters:
      # ...
      plugins: ["static_layer", "obstacle_layer", "inflation_layer"]
      filters: ["keepout_filter"]
      # ...
      keepout_filter:
        plugin: "nav2_costmap_2d::KeepoutFilter"
        enabled: True
        filter_info_topic: "/costmap_filter_info"
```
```yaml
local_costmap:
  local_costmap:
    ros__parameters:
      # ...
      plugins: ["voxel_layer", "inflation_layer"]
      filters: ["keepout_filter"]
      # ...
      keepout_filter:
        plugin: "nav2_costmap_2d::KeepoutFilter"
        enabled: True
        filter_info_topic: "/costmap_filter_info"
```
Now, when you send a goal near the Keepout Zone, the plan avoids the zone (drawn in pink in the costmap).

## "Trajectory Hits Obstacle" near the zone
```
[controller_server-3] [ERROR] [1654803915.474550722] [DWBLocalPlanner]: 1.00: ObstacleFootprint/Trajectory Hits Obstacle.
```
The course suggests removing the critic named **`ObstacleFootprint`** from the list of `critics` in `controller.yaml`:
```yaml
#critics: ["RotateToGoal", "Oscillation", "ObstacleFootprint", "GoalAlign", "PathAlign", "PathDist", "GoalDist"]
critics: ["RotateToGoal", "Oscillation", "GoalAlign", "PathAlign", "PathDist", "GoalDist"]   # unsafe, see below
```
**Do not do this on a real robot**: only `BaseObstacle` and `ObstacleFootprint` reject trajectories through lethal cells, so without them DWB drives into walls and people too (NAV2-V43). The error means the footprint already touches a lethal cell of the zone. Humble options: paint a gray (1–99) margin around the zone, so the edge is undesirable instead of lethal; keep the robot's start pose away from zones; or apply the filter only to the global costmap (plans avoid the zone, but the controller may enter it). [≥Jazzy: `override_lethal_cost: true` lets the robot drive out of a zone it entered]

## Preferred lanes
You can also invert this logic for **preferred lanes** rather than Keepout Zones: e.g. set the main warehouse lane as the preferred lane of travel, while the robot can still navigate off of it for the final approach to the goal when necessary.

## Pitfalls
- Filter only in the local costmap → the robot does not enter the zone, but plans still go through it.
- `filter_info_topic` must equal the info server's `filter_info_topic` ([[nav2-costmap-filters]]).
