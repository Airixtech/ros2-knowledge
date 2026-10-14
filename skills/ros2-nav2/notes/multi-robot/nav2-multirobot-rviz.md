---
id: nav2-multirobot-rviz
type: reference
owner: equipo-ros2
updated: 2026-10-14
review_by: 2027-04-12
source: manual
confidentiality: internal
title: "RViz2 for several robots: per-robot displays and tool topics"
domain: nav2
area: multi-robot
distro: humble
tested: false
audience: dev
summary: "RViz2 for two robots: per-robot LaserScan, RobotModel TF prefix, Tool Properties topics, paths and costmaps."
tags: [multi-robot, RViz2, Tool Properties, 2D Pose Estimate, 2D Goal Pose, initialpose, RobotModel, TF prefix, Path, costmap]
see: ["[[nav2-rviz-displays]]", "[[nav2-multirobot-localization]]", "[[nav2-multirobot-planning-launch]]"]
requires: [ros2-core]
version_notes:
  - "lyrical: Nav2's RViz config uses relative topics and the RViz namespace (Kilted), so one config works per robot — https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/migration_guides/jazzy/Jazzy.md (NAV2-V25)"
---
# RViz2 for several robots: per-robot displays and tool topics

**TL;DR** Duplicate each robot-specific display (laser, robot model, path, costmaps) and point it to that robot's namespaced topic. The 2D Pose Estimate and 2D Goal Pose tools publish to one topic at a time: change it in **Tool Properties** before clicking for each robot.

## Build the config
```bash
rviz2 -d ~/ros2_ws/src/cartographer_slam/rviz/cartographer.rviz
```
Start from the mapping/localization config, add the new elements and save as `tb3_1_and_2.rviz` (the course also provides this file in its extra-material repository, link given in the course; put it in `cartographer_slam/rviz/`).
- `LaserScan` → `tb3_0/scan`, Color Transformer `FlatColor`, red. A second `LaserScan` → `tb3_1/scan`, blue.
- `RobotModel`: Description Source `Topic`, Description Topic `/tb3_0/robot_description` (the topic publishing the model), TF prefix `tb3_0`. A second `RobotModel` for `tb3_1`.
- Optional: group each robot's displays (e.g. its laser) in an RViz folder.
- Add the **Tool Properties** panel: it sets the topics of `2D Pose Estimate` and `2D Goal Pose`.

## Localize both robots
1. In Tool Properties set the 2D Pose Estimate topic to `/tb3_1/initialpose`, click **2D Pose Estimate** and give the first robot (`tb3_1`) its pose.
2. Repeat with `/tb3_0/initialpose` for `tb3_0`. Both robots are now localized.
3. Simulated robots **drift**: relaunch the simulation before doing the pose estimates.
Save the config again.

## Paths, costmaps and goals
| Display | Topic | Settings |
|---|---|---|
| `Path` | `/tb3_0/plan` | Billboards, red |
| `Path` | `/tb3_1/plan` | Billboards, green |
| `Map` | `/tb3_0/global_costmap/costmap`, `/tb3_1/global_costmap/costmap` | Color Scheme `costmap` |
| `Map` | `/tb3_0/local_costmap/costmap`, `/tb3_1/local_costmap/costmap` | Color Scheme `costmap` |

For each robot: set the 2D Goal Pose topic to `/tb3_0/goal_pose` (or `/tb3_1/goal_pose`), click **2D Goal Pose** and a destination: that robot moves and its path appears. Each robot avoids the other as a dynamic obstacle and replans.

## Pitfalls
- RobotModel without the TF prefix → the model is drawn at the origin or not at all.
- Forgetting to switch the tool topic → both clicks go to the same robot.
