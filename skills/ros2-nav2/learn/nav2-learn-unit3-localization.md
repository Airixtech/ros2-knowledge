---
id: nav2-learn-unit3-localization
title: "Unit 3 exercises: AMCL launch, initial pose, global localization (3.1-3.5)"
domain: nav2
area: learn
distro: humble
tested: false
audience: students
summary: "Unit 3 (pkg localization_server): localization.launch.py + amcl_config.yaml, RViz pose estimate, initial pose from config and from a node, global localization."
tags: [course, students, unit 3, localization_server, localization.launch.py, amcl_config.yaml, initial_pose_pub.py, init_robot.launch.py, reinitialize_global_localization]
see: ["[[nav2-amcl-launch]]", "[[nav2-initial-pose-config]]", "[[nav2-initial-pose-publisher]]", "[[nav2-global-localization]]", "[[nav2-rviz-displays]]"]
requires: [ros2-core]
version_notes: []
---
# Unit 3 exercises: AMCL launch, initial pose, global localization (3.1-3.5)

**TL;DR** Localize the robot on your `turtlebot_area` map with AMCL, then make the initial pose automatic (config file, then a node), and finally localize without knowing the start pose. Concepts: [[nav2-amcl-concepts]].

## Exercise 3.1 — Localization launch
1. Create the package **`localization_server`** with `config` and `launch` directories.
2. In `launch`, create **`localization.launch.py`** launching `map_server`, `amcl` and a lifecycle manager ([[nav2-amcl-launch]]).
3. In `config`, create **`amcl_config.yaml`** with the given content.
4. Compile: for an `ament_python` package, install `launch` and `config` in `setup.py`, then `colcon build --packages-select localization_server` (always in `~/ros2_ws`) and source.
5. Run `ros2 launch localization_server localization.launch.py`. The warning "…Please set the initial pose…" is expected.
6. Set the pose manually in RViz: displays Map, TF, RobotModel (`/robot_description`), LaserScan, PoseWithCovariance, ParticleCloud. **Save the RViz configuration in `ros2_ws/src` as `localizer_rviz_config`**, then use **2D Pose Estimate** and drive with the keyboard to see the particles converge ([[nav2-rviz-displays]]). Finally save the config in your home directory as `localization_rviz_config` (File → Save Config As).

## Exercise 3.2 — Initial pose from the config file
1. Kill all programs (Ctrl+C in each terminal) and relaunch the simulation (robot back at its start).
2. Launch `localization_server` and RViz; do a 2D Pose Estimate and note the coordinates printed in the RViz terminal.
3. Duplicate `amcl_config.yaml` as **`amcl_config_initialized.yaml`**, add `set_initial_pose` and `initial_pose` with your values ([[nav2-initial-pose-config]]).
4. Make `localization.launch.py` use the new file, recompile (`colcon build --packages-select localization_server`) and launch: the robot appears localized.

## Exercise 3.4 — Initial pose from a node
1. In the `localization_server` package, create the Python program **`initial_pose_pub.py`** (inside `localization_server/localization_server`).
2. It subscribes to `/clicked_point` and publishes the X and Y coordinates as the initial pose on `/initialpose` (the course text writes `/initial_pose`; AMCL listens on `/initialpose`).
3. Create **`init_robot.launch.py`** to launch it; add the entry point `initial_pose_pub = <package-name>.<file-name>:main` in `setup.py`.
4. Launch it and publish a point with RViz's **Publish Point** ([[nav2-initial-pose-publisher]]).

## Exercise 3.5 — Global localization
a) In `amcl_config`, set `max_particles: 80000` and `min_particles: 2000`; recompile so the file is installed.
b) Run the localization. c) Launch RViz with the `ParticleCloud` display. d) Do a 2D Pose Estimate and look at the particles.
e) Call `ros2 service call /reinitialize_global_localization std_srvs/srv/Empty` and watch the particles spread; then drive with the keyboard until they gather at the robot ([[nav2-global-localization]]).

## Course project
Finish Section II of the course project ([[nav2-learn-course-project]]).
