---
id: nav2-controller-plugin-config
type: reference
owner: equipo-ros2
updated: 2026-10-10
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "Using the custom controller plugin: FollowPath parameters, launch, setup.py"
domain: nav2
area: plugins
distro: humble
tested: false
audience: dev
summary: "Load custom_nav2_controller_plugin::RegulatedPurePursuitController as FollowPath: parameters it really reads, pathplanner_purepursuit_controller_plugin.launch.py, setup.py, test at 2.5 m/s."
tags: [custom_nav2_controller_plugin::RegulatedPurePursuitController, FollowPath, controller_plugins, desired_linear_vel, lookahead_dist, max_allowed_time_to_collision, pure_pursuit_controller, pathplanner_purepursuit_controller_plugin.launch.py, setup.py]
see: ["[[nav2-controller-plugin-rpp]]", "[[nav2-controller-plugin-rpp-algorithm]]", "[[nav2-costmap-plugin-config]]", "[[nav2-rpp-controller-params]]", "[[nav2-controller-server]]"]
requires: [ros2-core]
version_notes:
  - "humble: this plugin (Galactic code) reads max_allowed_time_to_collision; the course's _up_to_carrot key, max_linear_accel and max_linear_decel are ignored; lookahead_dist is not a collision distance — https://github.com/ros-navigation/navigation2/blob/1.0.12/nav2_regulated_pure_pursuit_controller/src/regulated_pure_pursuit_controller.cpp (NAV2-V53)"
  - "humble: pass the tree as default_nav_to_pose_bt_xml (the course's default_bt_xml_filename is ignored) — https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/configuration_guide/core_servers/configuring_bt_navigator.md (NAV2-V51)"
---
# Using the custom controller plugin: configure, compile, test

**TL;DR** Load your controller as `FollowPath` in a new `controller.yaml`, in a new path planning launch, install the config folder, compile both packages and send a goal: the robot moves really fast.
```bash
cd ~/ros2_ws/
touch ~/ros2_ws/src/nav2_pkgs/path_planner_server/launch/pathplanner_purepursuit_controller_plugin.launch.py
mkdir ~/ros2_ws/src/nav2_pkgs/path_planner_server/config/pure_pursuit_controller
cd ~/ros2_ws/src/nav2_pkgs/path_planner_server/config/pure_pursuit_controller
touch controller.yaml
```
(The course's first version used the package path `~/ros2_ws/src/neobotix_mp_400_navigation/path_planner_server/`.)

## config/pure_pursuit_controller/controller.yaml
The `controller_server` block and checkers of [[nav2-controller-server]] and the MP-400 local costmap of [[nav2-mp400-costmaps]] (`controller_frequency: 5.0`, local costmap with `voxel_layer` and `inflation_layer`), with this controller:
```yaml
    controller_plugins: ["FollowPath"]
    # ...
    # Custom Pure Pusuit Params
    FollowPath:
      plugin: "custom_nav2_controller_plugin::RegulatedPurePursuitController"
      desired_linear_vel: 2.5
      # max_linear_accel: 2.5      # course; not read by this plugin
      # max_linear_decel: 2.5      # course; not read by this plugin
      lookahead_dist: 0.6
      min_lookahead_dist: 0.3
      max_lookahead_dist: 0.9
      lookahead_time: 1.5
      rotate_to_heading_angular_vel: 1.8
      transform_tolerance: 0.1
      use_velocity_scaled_lookahead_dist: false
      min_approach_linear_velocity: 0.05
      use_approach_linear_velocity_scaling: true
      max_allowed_time_to_collision: 1.0   # course: max_allowed_time_to_collision_up_to_carrot (Humble RPP name, not read here)
      use_regulated_linear_velocity_scaling: true
      use_cost_regulated_linear_velocity_scaling: false
      regulated_linear_scaling_min_radius: 0.9
      regulated_linear_scaling_min_speed: 0.25
      use_rotate_to_heading: true
      rotate_to_heading_min_angle: 0.785
      max_angular_accel: 3.2
      cost_scaling_dist: 0.3
      cost_scaling_gain: 1.0
      inflation_cost_scaling_factor: 3.0
```
The plugin type is the `class type` of the description XML, which has no `name` ([[nav2-plugin-description-xml]]). The plugin has many parameters ([[nav2-controller-plugin-rpp]]); the ones that change the behavior fastest:
- `desired_linear_vel`: 2.5 m/s makes the robot move very fast.
- `lookahead_dist`: the distance to the point on the path the robot steers to. The higher, the smoother the trajectories but the less precisely the path is followed. `min_lookahead_dist`/`max_lookahead_dist` bound it only with `use_velocity_scaled_lookahead_dist: true`. The course says it sets "until what distance you check for collisions": collisions use `max_allowed_time_to_collision` (NAV2-V53).

## launch/pathplanner_purepursuit_controller_plugin.launch.py
The launch of [[nav2-plugin-test-launch]] with the default `planner_server.yaml` and `behavior.xml`, the lifecycle manager named `lifecycle_manager_pathplanner`, the RViz config `pathplanning.rviz`, and:
```python
# Custom Plugin
controller_yaml = os.path.join(get_package_share_directory('path_planner_server'), 'config', 'pure_pursuit_controller', 'controller.yaml')
```
Pass the tree as `{'default_nav_to_pose_bt_xml': default_bt_xml_path}` (NAV2-V51).

## setup.py, compile and test
Add `(os.path.join('share', package_name, 'config/pure_pursuit_controller'), glob('config/pure_pursuit_controller/*.yaml')),` to the `data_files` of `setup.py` ([[nav2-plugin-test-launch]]), then:
```bash
cd ~/ros2_ws/
colcon build --packages-select custom_nav2_controller_plugin path_planner_server
source install/setup.bash
ros2 launch path_planner_server pathplanner_purepursuit_controller_plugin.launch.py
```
No error should appear. Send a **Nav2 Goal**: the robot moves **really fast**, because of the high speed of 2.5 m/s.

## Pitfalls
- Keys copied from Humble's RPP docs (`max_allowed_time_to_collision_up_to_carrot`) are silently ignored by this Galactic-based plugin, and the other way around.
- 2.5 m/s is far above a small robot's limits: keep `desired_linear_vel` within what the base can do.
