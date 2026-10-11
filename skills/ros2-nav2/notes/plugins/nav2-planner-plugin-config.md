---
id: nav2-planner-plugin-config
type: reference
owner: equipo-ros2
updated: 2026-10-10
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "Using a custom planner plugin: planner_plugins entry, launch, setup.py"
domain: nav2
area: plugins
distro: humble
tested: false
audience: dev
summary: "Load StraightLineCustomPlugin in planner_server.yaml under GridBased, pathplanner_straightlineplanner_plugin.launch.py, setup.py, test: straight paths through obstacles."
tags: [StraightLineCustomPlugin, planner_server.yaml, planner_plugins, GridBased, interpolation_resolution, pathplanner_straightlineplanner_plugin.launch.py, straightline_planner, setup.py]
see: ["[[nav2-planner-plugin-straight-line]]", "[[nav2-costmap-plugin-config]]", "[[nav2-planner-server]]", "[[nav2-plugins-overview]]"]
requires: [ros2-core]
version_notes:
  - "humble: the name GridBased can be changed if the BT's planner_id changes with it (course: 'if this is changed, it will give errors') — https://github.com/ros-navigation/navigation2/blob/humble/nav2_planner/src/planner_server.cpp (NAV2-V49)"
  - "humble: the course launch passes default_bt_xml_filename (Foxy name, ignored); use default_nav_to_pose_bt_xml — https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/configuration_guide/core_servers/configuring_bt_navigator.md (NAV2-V51)"
---
# Using a custom planner plugin: configure, compile, test

**TL;DR** Create a new path planning launch and only a new `planner_server.yaml`, because your plugin is for the planner server, which generates the **global paths**.
```bash
cd ~/ros2_ws/
touch ~/ros2_ws/src/nav2_pkgs/path_planner_server/launch/pathplanner_straightlineplanner_plugin.launch.py
mkdir ~/ros2_ws/src/nav2_pkgs/path_planner_server/config/straightline_planner
cd ~/ros2_ws/src/nav2_pkgs/path_planner_server/config/straightline_planner
touch planner_server.yaml
```

## config/straightline_planner/planner_server.yaml
```yaml
planner_server:
  ros__parameters:
    expected_planner_frequency: 20.0
    use_sim_time: True
    planner_plugins: ["GridBased"]
    GridBased:
      plugin: StraightLineCustomPlugin
      interpolation_resolution: 0.1
      tolerance: 0.5
      use_astar: false
      allow_unknown: true

global_costmap:
  global_costmap:
    ros__parameters:
      # the MP-400 global costmap with robot_base_frame: base_link, inflation_radius: 0.4 (see nav2-mp400-costmaps)
```
- The plugin is loaded with the name given in `straight_line_plugin_info.xml`, `StraightLineCustomPlugin` ([[nav2-plugin-description-xml]]). `tolerance`, `use_astar` and `allow_unknown` are NavFn parameters left from the original file; the straight-line planner ignores them.
- The course keeps the label `GridBased` and says renaming it gives errors: it does, unless you also change `planner_id` in the behavior tree, which asks for `GridBased` (NAV2-V49, [[nav2-plugins-overview]]).

## launch/pathplanner_straightlineplanner_plugin.launch.py
The launch of [[nav2-plugin-test-launch]] (map server, AMCL, controller, planner, behavior server, bt_navigator, RViz, lifecycle manager), with the default controller config and only the planner YAML changed:
```python
controller_yaml = os.path.join(get_package_share_directory('path_planner_server'), 'config', 'controller.yaml')
# Custom Plugin
planner_yaml = os.path.join(get_package_share_directory('path_planner_server'), 'config', 'straightline_planner', 'planner_server.yaml')
```
Pass the tree as `{'default_nav_to_pose_bt_xml': default_bt_xml_path}` (the course's `default_bt_xml_filename` is ignored in Humble, NAV2-V51).

## setup.py
Add the new folder and its files to the `data_files` of `setup.py` ([[nav2-plugin-test-launch]]):
```python
(os.path.join('share', package_name, 'config/straightline_planner'), glob('config/straightline_planner/*.yaml')),
```

## Compile and test
Compile the plugin and `path_planner_server` (`colcon build`, `source install/setup.bash`); no error should appear. Then:
```bash
ros2 launch path_planner_server pathplanner_straightlineplanner_plugin.launch.py
```
All the paths are now **straight lines**, even the ones that go **through obstacles**: the global path does not go around them. The robot stops because the local planning (the controller) kicks in, but it does not recover well, because in the end it is the global path that makes everything work and adapt.

## Pitfalls
- The YAML `plugin:` here has no quotes and no namespace: it is the XML `name`, any string.
- Forgetting the `setup.py` line → the launch file cannot find `config/straightline_planner/planner_server.yaml`.
