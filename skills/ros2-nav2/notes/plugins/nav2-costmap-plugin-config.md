---
id: nav2-costmap-plugin-config
type: reference
owner: equipo-ros2
updated: 2026-10-10
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "Using a custom costmap layer: plugins list in both costmaps, launch, setup.py"
domain: nav2
area: plugins
distro: humble
tested: false
audience: dev
summary: "Load custom_gradient_layer in local and global costmaps, pathplanner_custom_costmap_plugin.launch.py (BT via default_nav_to_pose_bt_xml), setup.py, compile and test."
tags: [custom_gradient_layer, costmap plugin config, plugins, pathplanner_custom_costmap_plugin.launch.py, custom_costmap, setup.py, data_files, default_nav_to_pose_bt_xml, behavior_server, lifecycle_manager]
see: ["[[nav2-costmap-plugin-gradient-layer]]", "[[nav2-costmap-plugin-package]]", "[[nav2-mp400-costmaps]]", "[[nav2-plugin-test-launch]]"]
requires: [ros2-core]
version_notes:
  - "humble: the course passes the BT as default_bt_xml_filename, a Foxy name Humble ignores; use default_nav_to_pose_bt_xml — https://github.com/ros-navigation/navigation2/blob/humble/nav2_bt_navigator/src/navigators/navigate_to_pose.cpp (NAV2-V51)"
  - "humble: the course's controller.yaml for this test drops BaseObstacle, leaving DWB without collision checks; keep it — https://github.com/ros-navigation/navigation2/tree/humble/nav2_dwb_controller/dwb_critics/src (NAV2-V43)"
---
# Using a custom costmap layer: configure, compile, test

**TL;DR** Create a new path planning launch that loads your plugin, with its own `controller.yaml` and `planner_server.yaml` in `config/custom_costmap/`, add the plugin to **both** costmaps, install the folder from `setup.py`, compile and test.
```bash
cd ~/ros2_ws/
touch ~/ros2_ws/src/nav2_pkgs/path_planner_server/launch/pathplanner_custom_costmap_plugin.launch.py
mkdir ~/ros2_ws/src/nav2_pkgs/path_planner_server/config/custom_costmap   # course: …/path_planner_server/custom_costmap
cd ~/ros2_ws/src/nav2_pkgs/path_planner_server/config/custom_costmap
touch controller.yaml
touch planner_server.yaml
```

## config/custom_costmap/controller.yaml (local costmap)
Copy your `controller.yaml` ([[nav2-controller-server]], [[nav2-dwb-controller]], MP-400 local costmap in [[nav2-mp400-costmaps]]) and replace the **inflation_layer** with the **custom_gradient_layer**, using the **name** `custom_nav2_costmap_plugin/GradientLayer` of `gradient_layer.xml`:
```yaml
      # plugins: ["voxel_layer", "inflation_layer"]
      plugins: ["voxel_layer", "custom_gradient_layer"]
      # ...
      # inflation_layer:
      #   plugin: "nav2_costmap_2d::InflationLayer"
      #   cost_scaling_factor: 3.0
      #   inflation_radius: 0.55
      # ...
      custom_gradient_layer:
        plugin: "custom_nav2_costmap_plugin/GradientLayer"
        enabled: True
```
The course's file also sets `controller_frequency: 10.0` and comments out `BaseObstacle` in `critics`; keep `BaseObstacle`, or DWB has no collision check (NAV2-V43).

## config/custom_costmap/planner_server.yaml (global costmap)
Same procedure in the global costmap:
```yaml
      #plugins: ["static_layer", "obstacle_layer", "inflation_layer"]
      plugins: ["static_layer", "obstacle_layer", "custom_gradient_layer"]
      custom_gradient_layer:
        plugin: "custom_nav2_costmap_plugin/GradientLayer"
        enabled: True
```
Same procedure here: you replaced the `inflation_layer` with your `custom_gradient_layer`. You would not need any of the other plugins added, because the way you defined `updateCosts()` overwrites their data ([[nav2-costmap-plugin-gradient-layer]]).

## Launch and setup.py
`launch/pathplanner_custom_costmap_plugin.launch.py` is the path planning launch of [[nav2-plugin-test-launch]], with `controller_yaml` and `planner_yaml` from `config/custom_costmap/` and the tree passed as `default_nav_to_pose_bt_xml` (NAV2-V51). To find the new **config/custom_costmap** folder and its files, add it to the `data_files` of `setup.py` ([[nav2-plugin-test-launch]]).

## Compile and test
Compile the plugin and also `path_planner_server`, so the changes are installed and accessible (`colcon build`, `source install/setup.bash`); no error should appear. Then:
```bash
ros2 launch path_planner_server pathplanner_custom_costmap_plugin.launch.py
```
The controller **cannot move the robot**: the costmap now has a configuration that does not allow the robot to move freely (lethal gradient stripes).

## Pitfalls
- `mkdir` outside `config/` (as in the course) → `setup.py` installs nothing and the launch file cannot find the YAML files.
- YAML `plugin:` must be the XML `name` (`custom_nav2_costmap_plugin/GradientLayer`).
