---
id: nav2-robot-footprint
type: reference
owner: equipo-ros2
updated: 2026-10-10
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "Robot shape: robot_radius vs footprint and the matching DWB critic"
domain: nav2
area: costmaps
distro: humble
tested: false
audience: dev
summary: "Robot shape in both costmaps: robot_radius or a footprint polygon, never both; DWB BaseObstacle vs ObstacleFootprint critic."
tags: [footprint, robot_radius, costmap, BaseObstacle, ObstacleFootprint, DWB critics, TurtleBot3 Burger]
see: ["[[nav2-global-costmap]]", "[[nav2-local-costmap]]", "[[nav2-dwb-controller]]", "[[nav2-costmap-layers]]"]
requires: [ros2-core]
version_notes:
  - "humble: the course labels ±0.089 × ±0.069 as the TurtleBot3 Waffle footprint; those are Burger-sized values (Waffle Pi ≈ 0.28 × 0.31 m); ROBOTIS's own Burger params use robot_radius 0.1 — https://github.com/ROBOTIS-GIT/turtlebot3/blob/humble/turtlebot3_navigation2/param/humble/burger.yaml (NAV2-V13)"
---
# Robot shape: robot_radius vs footprint and the matching DWB critic

**TL;DR** The robot's shape decides how much obstacles are inflated and whether a path fits through a gap. Set it in **both** costmaps (local and global): `robot_radius` for round robots, `footprint` for any other shape. **Never both.**

## Round robots: robot_radius
Most robots are round (or close to it). Use the parameter `robot_radius` (meters) in the costmap parameters:
```yaml
robot_radius: 0.3
```

## Other shapes: footprint
For rectangular, big square or strangely shaped robots, use `footprint`: the projection of the robot on the ground, as the list of its corner points (meters, in the robot base frame). For a square robot of 65 cm per side:
```yaml
footprint: '[[0.325, 0.325], [0.325, -0.325], [-0.325, -0.325], [-0.325, 0.325]]'
```
Footprint for the TurtleBot3 **Burger** (0.178 × 0.138 m; the course solution called it "Waffle"; axis order `[verify]`):
```yaml
footprint: '[ [0.089, 0.069], [0.089, -0.069], [-0.089, -0.069], [-0.089, 0.069] ]'
```
Steps: identify the robot dimensions → list the corner points → set the parameter in both costmaps → check that navigation still works.

## Matching DWB critic
In the controller's `critics` list ([[nav2-dwb-controller]]):
- `robot_radius` → use the `BaseObstacle` critic.
- `footprint` → use the `ObstacleFootprint` critic (it checks the whole polygon, not only the center cost).

## Pitfalls
- Both `footprint` and `robot_radius` set → a non-empty footprint wins and the radius is ignored; set only one to avoid confusion.
- A footprint without padding in tight spaces → the robot scrapes walls; Nav2 adds `footprint_padding` (0.01 m by default).
- Footprint set only in the global costmap → the local costmap (controller) still uses a radius.
