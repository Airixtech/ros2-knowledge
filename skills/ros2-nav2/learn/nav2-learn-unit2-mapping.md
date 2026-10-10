---
id: nav2-learn-unit2-mapping
title: "Unit 2 exercises: Cartographer, map saving, map server (2.1-2.3)"
domain: nav2
area: learn
distro: humble
tested: false
audience: students
summary: "Unit 2 (pkgs cartographer_slam, map_server): Cartographer launch + Lua, RViz map display, teleop mapping, save turtlebot_area, map server launch."
tags: [course, students, unit 2, cartographer_slam, cartographer.launch.py, cartographer.lua, map_server, nav2_map_server.launch.py, turtlebot_area]
see: ["[[nav2-cartographer-launch]]", "[[nav2-cartographer-lua]]", "[[nav2-map-saver]]", "[[nav2-map-server]]", "[[nav2-rviz-displays]]"]
requires: [ros2-core]
version_notes: []
---
# Unit 2 exercises: Cartographer, map saving, map server (2.1-2.3)

**TL;DR** Build a map of the simulated environment with Cartographer, save it as `turtlebot_area`, and serve it with a map server. Concepts: [[nav2-map-concepts]].

## Exercise 2.1 — Mapping with Cartographer
a) Create the package **`cartographer_slam`** in `ros2_ws/src`.
b) Create the **`launch`** and **`config`** directories in `ros2_ws/src/cartographer_slam`.
c) Write **`cartographer.launch.py`** launching the two nodes (`cartographer_node`, `occupancy_grid_node`) ([[nav2-cartographer-launch]]).
   - Note 1: get the config directory with `os.path.join(get_package_share_directory('cartographer_slam'), 'config')` (import `os` and `get_package_share_directory` from `ament_index_python.packages`).
   - Note 2: put two `Node(...)` calls in the list, separated by commas.
d) Create **`cartographer.lua`** in `config` ([[nav2-cartographer-lua]]).
e) Compile: install `launch` and `config` from `setup.py` (`data_files` + `import os`, `from glob import glob`) and build **only from `~/ros2_ws`**: `colcon build --packages-select cartographer_slam`, then `source ~/ros2_ws/install/setup.bash`.
f) Run `ros2 launch cartographer_slam cartographer.launch.py`.
g) Run `rviz2` in another terminal (if you minimize its window, reopen it from the graphical tools icon).
h) In RViz: **Add** → `Map` on `/map` (fix its QoS if nothing shows), `TF`, `LaserScan` (Reliability Best Effort) ([[nav2-rviz-displays]]). **Save this RViz configuration in `ros2_ws/src` as `mapper_rviz_config.rviz`.**
i) Move the robot with `ros2 run teleop_twist_keyboard teleop_twist_keyboard` until the map is complete. In Gazebo, zoom out and orbit the view (press the scroll wheel and move the mouse) to find the robot; check the progress in RViz.

## Exercise 2.2 — Save the map
Save the map you created as `turtlebot_area` with `map_saver_cli`, from `~/ros2_ws/src/cartographer_slam/config`, **before** closing Cartographer ([[nav2-map-saver]]).

## Exercise 2.3 — Map server
- Create a package **`map_server`** in `ros2_ws`.
- Create a `launch` directory with the launch file **`nav2_map_server.launch.py`** that launches `map_server` and `nav2_lifecycle_manager` ([[nav2-map-server]]).
- Create a `config` directory and put the TurtleBot area map files in it.
- Launch the map server with the map in `config` and visualize it in RViz.
- Notes: edit `setup.py` as in Exercise 2.1; check the QoS of `/map` in RViz.

## Course project
After this unit, start the course project, Section I ([[nav2-learn-course-project]]).
