---
id: nav2-learn-unit4-path-planning
type: reference
owner: equipo-ros2
updated: 2026-10-10
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "Unit 4 exercises: path planning stack and goals (4.1-4.4)"
domain: nav2
area: learn
distro: humble
tested: false
audience: students
summary: "Unit 4 (pkg path_planner_server): pathplanner.launch.py, YAML files, RViz path, parameter experiments, goals by topic and action client."
tags: [course, students, unit 4, path_planner_server, pathplanner.launch.py, planner_server.yaml, controller.yaml, goal_pose, nav_to_pose_action_client.py]
see: ["[[nav2-path-planning-launch]]", "[[nav2-planner-server]]", "[[nav2-dwb-controller]]", "[[nav2-send-goal-cli]]", "[[nav2-send-goal-action-client]]"]
requires: [ros2-core]
version_notes: []
---
# Unit 4 exercises: path planning stack and goals (4.1-4.4)

**TL;DR** Launch planner, controller, behavior server and bt_navigator on top of your localization, then send goals from RViz, the terminal and a Python program. Concepts: [[nav2-architecture]].

## Exercise 4.1 — Path planning launch
a) Create the package **`path_planner_server`** in `ros2_ws`.
b) Create **`launch`** and **`config`** in `ros2_ws/src/path_planner_server`.
c) Write **`pathplanner.launch.py`** that launches **all the path planner nodes** ([[nav2-path-planning-launch]]).
d) Create a YAML file for each node that needs one in `config` (`planner_server.yaml`, `controller.yaml`, `bt_navigator.yaml`, `recovery.yaml`; base configs in [[nav2-planner-server]], [[nav2-controller-server]], [[nav2-bt-plugin-libs]], [[nav2-behavior-server]]; behavior tree in [[nav2-behavior-tree-xml]]).
e) Compile (update `setup.py`) and source the new `install`.
f) Launch the localization system from Unit 3.
g) Open `rviz2`, load `localization_rviz_config`, add a `Path` display on `/plan` with Line Style **Billboards** and Line Width **0.05**, and save it in `ros2_ws/src` as **`pathplanning_rviz_config`**.
h) Set the initial robot location in RViz. i) Launch your new path planner launch file.
- Note: include a `nav2_lifecycle_manager` for all path planner nodes, **with a different name than the one in localization**.
j) Click the RViz **Navigation2 Goal** (Nav2 Goal) button and a point on the map: a green line shows the path and the robot moves to the goal.

## Exercise 4.2 — Play with the parameters
Change planner and controller parameters and watch the robot: `min_vel_x`, `max_vel_theta`, `use_astar` and all the goal tolerances ([[nav2-dwb-controller]], [[nav2-planner-server]]).

## Exercise 4.3 — Goal through a topic
1. Get a point's coordinates with RViz **Publish Point** (they appear in the RViz terminal).
2. Publish them with `ros2 topic pub` to `/goal_pose`; the robot moves there ([[nav2-send-goal-cli]]).

## Exercise 4.4 — Goal from a program
1. In the path planning package (the course text calls it `pathplanner_server`), create **`nav_to_pose_action_client.py`** and add its entry point in `setup.py`.
2. It subscribes to `/clicked_point` and, for each new point, sends a navigation goal to the navigation action server with an action client.
3. Create a launch file for it; compile and install; launch it and use **Publish Point** in RViz ([[nav2-send-goal-action-client]]).

## Course project
Finish Section III of the course project ([[nav2-learn-course-project]]).
