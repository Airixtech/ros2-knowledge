---
id: nav2-learn-unit6-multirobot
title: "Unit 6 exercises: multi-robot mapping, localization, planning (6.1-6.2)"
domain: nav2
area: learn
distro: humble
tested: false
audience: students
summary: "Unit 6 (tb3_0, tb3_1): cartographer_multi mapping, clean shared map, multi_localization and multi_pathplanner launches, per-robot configs, multi_main.launch.xml."
tags: [course, students, unit 6, multi-robot, tb3_0, tb3_1, multi_cartographer.launch.py, multi_localization.launch.py, multi_pathplanner.launch.py, multi_main.launch.xml]
see: ["[[nav2-multirobot-namespaces]]", "[[nav2-multirobot-mapping]]", "[[nav2-multirobot-localization]]", "[[nav2-multirobot-planning-launch]]", "[[nav2-multirobot-single-launch]]"]
requires: [ros2-core]
version_notes: []
---
# Unit 6 exercises: multi-robot mapping, localization, planning (6.1-6.2)

**TL;DR** Two namespaced TurtleBot3 (`tb3_0`, `tb3_1`) share one map: map with `tb3_0`, run one AMCL per robot, then one path planning stack per robot, and finally start everything from one XML launch. Setup and checks: [[nav2-multirobot-namespaces]].

## Exercise 6.1 — Multi-robot mapping
- In `cartographer_slam` (Unit 2), create **`cartographer_multi.lua`** in `config` with the same content, changed to use the laser, odometry, `tracking_frame`, `published_frame` and `odom_frame` of `tb3_0`.
- Create **`multi_cartographer.launch.py`** in `launch` (copy of the previous launch) using the new config; remap the topics in `cartographer_node` if needed (tip).
- Compile and launch; open RViz with `cartographer.rviz` (the mapping unit's RViz file); drive `tb3_0` with teleop remapped to `/tb3_0/cmd_vel` (robot models may not appear yet).
- Create the map **`turtlebot_area_two_robots`** and save it directly in the `config` folder of the `map_server` package; then kill Cartographer.
- Remove the second robot from the map (it was mapped as an obstacle): edit the `.pgm` (e.g. GIMP) or use the clean map from the course's extra material, named **`turtlebot_area_two_robots_clean`** ([[nav2-multirobot-mapping]]).

## Exercise 6.2 — Multi-robot localization
1. In `localization_server`, create **`multi_localization.launch.py`** launching **two** `amcl` nodes with namespaces `tb3_0` and `tb3_1`, the map `turtlebot_area_two_robots_clean.yaml`, and a lifecycle manager with the full node names and `bond_timeout: 0.0`.
2. Create **`tb3_0_amcl_config.yaml`** and **`tb3_1_amcl_config.yaml`**: full node name on the first line, namespaced frames (except `global_frame_id`), `map_topic` forced to `/map`.
3. Add `topic_name` and `frame_id` to the map server.
4. Compile, source, launch: both AMCL nodes wait for their initial pose.
5. Configure RViz for two robots and save it as **`tb3_1_and_2.rviz`**; set each robot's pose with 2D Pose Estimate (relaunch the sim first: robots drift); check the TF with `view_frames` ([[nav2-multirobot-localization]], [[nav2-multirobot-rviz]]).

## Path planning for both robots
- Create **`multi_pathplanner.launch.py`** in `path_planner_server`: two `planner_server`, `controller_server`, `recoveries_server` and `bt_navigator`, each with its namespace, and one lifecycle manager with all full names and `bond_timeout: 0.0` ([[nav2-multirobot-planning-launch]]).
- Per robot, create `tb3_0_planner_server.yaml`, `tb3_0_controller.yaml`, `tb3_0_bt_navigator.yaml`, `tb3_0_recovery.yaml` (and the same for `tb3_1`) ([[nav2-multirobot-planner-controller-config]], [[nav2-multirobot-bt-behavior-config]]). `behavior.xml` is the same as for one robot.
- Launch localization, then path planning, then RViz with paths and costmaps per robot; send goals to each robot through the Tool Properties topics.

## Single launch
In `path_planner_server` create **`multi_main.launch.xml`**, and in `cartographer_slam` create **`start_rviz.launch.py`** to start RViz without terminal commands ([[nav2-multirobot-single-launch]]).
