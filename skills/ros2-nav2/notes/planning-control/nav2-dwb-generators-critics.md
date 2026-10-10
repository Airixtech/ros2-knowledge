---
id: nav2-dwb-generators-critics
title: "DWB trajectory generators and the full list of critics"
domain: nav2
area: planning-control
distro: humble
tested: false
audience: dev
summary: "DWB plugins: trajectory_generator_name (StandardTrajectoryGenerator, LimitedAccelGenerator) and the 10 dwb_critics; which critics check obstacles."
tags: [DWB, DWBLocalPlanner, trajectory_generator_name, StandardTrajectoryGenerator, LimitedAccelGenerator, critics, BaseObstacle, ObstacleFootprint, PathAlign, PreferForward, Twirling, dwb_critics]
see: ["[[nav2-dwb-controller]]", "[[nav2-goal-progress-checkers]]", "[[nav2-dwb-critic-tuning]]", "[[nav2-keepout-filter]]", "[[nav2-robot-footprint]]"]
requires: [ros2-core]
version_notes:
  - "humble: generators StandardTrajectoryGenerator (default), LimitedAccelGenerator; 10 critics; only BaseObstacle and ObstacleFootprint reject colliding trajectories — https://github.com/ros-navigation/navigation2/tree/humble/nav2_dwb_controller/dwb_critics/src (NAV2-V66, NAV2-V43)"
  - "humble: the course wrote trajectory_generator_name with typographic quotes, which stay in the string — https://github.com/ros-navigation/navigation2/blob/humble/nav2_dwb_controller/dwb_plugins/plugins.xml (NAV2-V54)"
---
# DWB trajectory generators and the full list of critics

**TL;DR** `DWBLocalPlanner` (provided by `dwb_core`) is the DWA-style controller of Nav2 ([[nav2-dwb-controller]] has the full `FollowPath` block). The most important parts of its configuration are the **trajectory generator plugin** and the **trajectory critics**. Every parameter: [DWB controller docs](https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/configuration_guide/controller_plugins/dwb_controller/index.md).

## Trajectory generator plugin
```yaml
    FollowPath:
      plugin: "dwb_core::DWBLocalPlanner"
      debug_trajectory_details: True
      trajectory_generator_name: "dwb_plugins::StandardTrajectoryGenerator"   # course: “…” typographic quotes
```
The generator computes the local trajectories. Two plugins are available (definitions from the official documentation):
- **StandardTrajectoryGenerator** (default): similar to the trajectory rollout algorithm used in `base_local_planner` in ROS 1.
- **LimitedAccelGenerator**: similar to DWA used in ROS 1.

Copying YAML from a rich-text page can turn `"` into `“ ”`: YAML keeps them inside the string, the class name no longer matches and the plugin fails to load (NAV2-V54).

## Trajectory critics
Critics are small plugins that make DWB follow the global path more or less tightly, especially in front of unexpected obstacles not yet in the global costmap. Each critic scores the trajectories computed by the trajectory generator plugin (definitions from the official documentation):

| Critic | Scores a trajectory by… |
|---|---|
| `BaseObstacle` | where the path passes over the costmap; use the inflation layer to expand obstacles by the robot's radius |
| `ObstacleFootprint` | verifying all points along the robot's footprint don't touch an obstacle marked in the costmap |
| `GoalAlign` | how well aligned the trajectory is with the goal pose |
| `GoalDist` | how close the trajectory gets the robot to the goal pose |
| `PathAlign` | how well it is aligned to the path provided by the global planner |
| `PathDist` | how far it ends up from the path provided by the global planner |
| `Oscillation` | preventing the robot from moving backward and forward |
| `PreferForward` | scoring trajectories that move the robot forwards more highly |
| `RotateToGoal` | only allowing rotation to the goal orientation when sufficiently close to the goal location |
| `Twirling` | preventing holonomic robots from spinning as they progress to the goal |

Critics are of base class `dwb_core::TrajectoryCritic`. Only `BaseObstacle` and `ObstacleFootprint` reject trajectories through obstacles: keep one of them in `critics` (NAV2-V43, [[nav2-keepout-filter]]).

## Pitfalls
- Which obstacle critic goes with `robot_radius` and which with a `footprint` polygon: [[nav2-robot-footprint]].
- A strong `PathAlign` can keep the robot stuck behind an obstacle that is not in the global costmap ([[nav2-dwb-critic-tuning]]).
