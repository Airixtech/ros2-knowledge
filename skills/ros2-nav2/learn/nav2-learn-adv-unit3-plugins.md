---
id: nav2-learn-adv-unit3-plugins
title: "Advanced Unit 3 exercises: custom costmap, planner and controller plugins"
domain: nav2
area: learn
distro: humble
tested: false
audience: students
summary: "Advanced Unit 3: Examples 3.1–3.3 and exercises EX.1 (moving obstacle layer), EX.2 (wavy planner) with exact names."
tags: [course, students, advanced unit 3, plugins, EX.1, EX.2, my_custom_costmap, MyCrazyCustomCostmapLayer_Plugin_Name, wavy_line_planner, WavyLineCustomPlugin, Example 3.1, Example 3.2, Example 3.3]
see: ["[[nav2-plugins-overview]]", "[[nav2-costmap-plugin-moving-obstacle]]", "[[nav2-planner-plugin-wavy]]", "[[nav2-controller-plugin-rpp]]", "[[nav2-learn-adv-start-here]]"]
requires: [ros2-core]
version_notes: []
---
# Advanced Unit 3 exercises: custom costmap, planner and controller plugins

**TL;DR** Unit 3 shows the default plugins and how to create **Costmap**, **Planner** and **Controller** plugins ([[nav2-plugins-overview]]). Each example follows the same five steps: package, source and header files, plugin description XML, `CMakeLists.txt` and `package.xml`, configure-compile-test.

## Navigation setup (before any plugin)
Make sure your Nav2 system works: start it, check that the costmaps appear, and send a goal: a path must be generated and followed, both in RViz and in the simulation.
```bash
source ~/ros2_ws/install/setup.bash
ros2 launch path_planner_server navigation.launch.py
```

## Examples
| Example | Plugin | Notes |
|---|---|---|
| 3.1 | `GradientLayer` costmap layer | [[nav2-costmap-plugin-package]], [[nav2-costmap-plugin-gradient-layer]], [[nav2-costmap-plugin-config]] — when it works: "GREAT, you created your first Nav2 Plugin!" |
| 3.2 | `StraightLine` global planner | [[nav2-planner-plugin-package]], [[nav2-planner-plugin-straight-line]], [[nav2-planner-plugin-config]] |
| 3.3 | Regulated Pure Pursuit controller | [[nav2-controller-plugin-package]], [[nav2-controller-plugin-rpp]], [[nav2-controller-plugin-config]] |

## Exercise EX.1 — moving obstacle costmap
Better understand Example 3.1 and use a costmap plugin to simulate a person walking around, so that your robot has to plan around it dynamically.
- Create a new costmap plugin based on Example 3.1.
- Change the `updateCosts()` method to generate a small box area that moves around, simulating a person or object moving around the scene.
- Only add this costmap plugin to the **global** costmap configuration.

Names to use (so you can follow the solution):
- `my_custom_costmap.cpp`, `my_custom_costmap.hpp`
- custom class `MyCustomCostmap`, namespace `my_custom_costmap_namespace_name`
- library in `CMakeLists.txt`: `my_custom_costmap_core`
- name of the plugin in the info.xml file: `MyCrazyCustomCostmapLayer_Plugin_Name`; name of the info.xml file: `my_custom_costmap_plugininfo.xml`
- planner config folder `my_custom_crazy_costmap`; launch `pathplanner_custom_crazy_costmap.launch.py`
- `package.xml`: add `<costmap_2d plugin="${prefix}/my_custom_costmap_plugininfo.xml" />`

Suggestion: select the cells inside the moving obstacle with a `pointInsideCircle(i, j)` helper and assign `master_array[index] = 200` inside, `1` outside; you are free to do it another way. Expected result: the path planner replans when the moving square is in the path. Try it yourself before the solution: [[nav2-costmap-plugin-moving-obstacle]] (full solutions in the course repository).

## Exercise EX.2 — wavy planner
Generate a path following a pattern different from a straight line.
- Create a new **planner** plugin based on Example 3.2 (the course text says "Costmap plugin").
- Change the `createPlan()` method to generate wavy paths, like a sine wave or zig zag.

Names: `wavy_line_planner.cpp`, `wavy_line_planner.hpp`; class `WavyLine`, namespace `nav2_wavyline_planner_namespace_name`; library `wavy_line_planner_core`; name of the plugin in the info.xml file `WavyLineCustomPlugin`; name of the info.xml file `wavy_line_plugin_info.xml`; config folder `wavyline_planner`; launch `pathplanner_wavyline_planner_plugin.launch.py`. Expected result: the global path is wavy and changes with the distance to the goal. Solution: [[nav2-planner-plugin-wavy]].

## Running the controller example (course's first version)
```bash
cd ~/ros2_ws
source install/setup.bash
ros2 launch localization_server localization.launch.py
# second terminal
cd ~/ros2_ws
source install/setup.bash
ros2 launch path_planner_server pathplanner_purepursuit_controller_plugin.launch.py
```
Then change the RViz config file for path planning: in RViz, **File → Open Config** and select `path_planner_server/rviz_config/pathplanning.rviz`.
