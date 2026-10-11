---
id: nav2-learn-unit5-costmaps
type: reference
owner: equipo-ros2
updated: 2026-10-10
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "Unit 5 exercises: costmaps, footprint, single launch (5.1-5.5)"
domain: nav2
area: learn
distro: humble
tested: false
audience: students
summary: "Unit 5: global costmap in planner_server.yaml, obstacle layer, local costmap in controller.yaml, footprint instead of robot_radius, navigation.launch.py."
tags: [course, students, unit 5, global_costmap, obstacle_layer, local_costmap, footprint, navigation.launch.py, gas bottle]
see: ["[[nav2-global-costmap]]", "[[nav2-costmap-layers]]", "[[nav2-local-costmap]]", "[[nav2-robot-footprint]]", "[[nav2-single-launch]]"]
requires: [ros2-core]
version_notes:
  - "humble: the 5.4 solution values (±0.089 × ±0.069) are Burger-sized although labeled Waffle; axis order [verify] — https://github.com/ROBOTIS-GIT/turtlebot3/blob/humble/turtlebot3_navigation2/param/humble/burger.yaml (NAV2-V13)"
---
# Unit 5 exercises: costmaps, footprint, single launch (5.1-5.5)

**TL;DR** Add the global and local costmaps to your planner and controller configs, see why an obstacle layer is needed, describe the robot's shape, and merge everything into one launch. Concepts: [[nav2-costmap-concepts]].

## Exercise 5.1 — Global costmap
- Add the global costmap settings at the bottom of the `planner_server.yaml` from Unit 4. **Very important:** the `global_costmap` block must start at the first column of the file ([[nav2-global-costmap]]).
- Compile and source; launch the whole path planning system (with `map_server` and AMCL).
- Open RViz, load the path planner config, localize the robot, add a `costmap` (Map) display for `/global_costmap/costmap` (Color Scheme *map*) and save the config.
- Spawn an extra **gas bottle** in the simulation (the spawn command is in [[nav2-global-costmap]]) and send a 2D Goal Pose to its other side: the laser sees it, the costmap does not, the path crosses it and the robot crashes.

## Exercise 5.2 — Obstacle layer
1. Add `obstacle_layer` to the global costmap `plugins`, **before** `"inflation_layer"`.
2. Add its configuration to `planner_server.yaml` at the same indentation as `static_layer` ([[nav2-costmap-layers]]).
3. Relaunch and repeat the paths: new obstacles now enter the path computation and are avoided.

## Exercise 5.3 — Local costmap
- Add the local costmap settings at the bottom of the `controller.yaml` from Unit 4 (first column) ([[nav2-local-costmap]]).
- Compile, source and launch the path planning systems (with `map_server` and AMCL).
- In RViz load `pathplanning_rviz_config`, localize the robot, add another `costmap` display for the `local_costmap` (Color Scheme *Costmap*) and save the config so you do not lose the changes.
- Add the gas bottle (if not there yet) and ask the robot to move to its other side: the colored local costmap covers only `width` × `height` meters around the robot.

## Exercise 5.4 — Footprint
Change both costmaps from `robot_radius` to `footprint` for the TurtleBot3: identify the robot dimensions, list the corner points, modify both costmaps' parameters and check that navigation still works. Solution and DWB critic change: [[nav2-robot-footprint]].

## Exercise 5.5 — Single navigation launch
Inside the path planning package (`pathplanner_server` in the course text), create **`navigation.launch.py`** that launches `map_server`, localization, planner, controller, `bt_navigator` and `recoveries_server`, all managed by **one** `nav2_lifecycle_manager` named **`lifecycle_manager`**, each with its config file ([[nav2-single-launch]]).

## Course project
Finish Section IV of the course project; then you are ready for the live presentation ([[nav2-learn-course-project]]).
