---
id: nav2-initial-pose-config
type: reference
owner: equipo-ros2
updated: 2026-10-10
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "Initial pose from the AMCL config file (set_initial_pose)"
domain: nav2
area: localization
distro: humble
tested: false
audience: dev
summary: "Start AMCL already localized: read the pose from RViz 2D Pose Estimate, then set_initial_pose + initial_pose x/y/yaw in amcl_config_initialized.yaml."
tags: [AMCL, set_initial_pose, initial_pose, 2D Pose Estimate, amcl_config_initialized.yaml, autonomous startup]
see: ["[[nav2-amcl-params-filter]]", "[[nav2-amcl-launch]]", "[[nav2-initial-pose-publisher]]", "[[nav2-rviz-displays]]"]
requires: [ros2-core]
version_notes:
  - "humble: set_initial_pose + initial_pose.{x,y,z,yaw}; same in Jazzy and Lyrical — https://github.com/ros-navigation/navigation2/blob/humble/nav2_amcl/src/amcl_node.cpp (NAV2-V34)"
---
# Initial pose from the AMCL config file (set_initial_pose)

**TL;DR** Every time the robot starts, AMCL needs its initial location. Without an operator running RViz, put that pose in the AMCL config file with `set_initial_pose: true`.

## 1. Get the pose once with RViz
1. Restart the simulation so the robot is at its start position, then launch the localization and RViz ([[nav2-amcl-launch]]).
2. Use **2D Pose Estimate** to localize the robot ([[nav2-rviz-displays]]).
3. In the terminal where RViz runs, the coordinates of the pose you set are printed: note x, y and the yaw.

## 2. Copy them into a config file
Duplicate `amcl_config.yaml` as `amcl_config_initialized.yaml` and add, inside `ros__parameters`:
```yaml
    set_initial_pose: true
    initial_pose:
      x: -4.44264
      y: 2.32243
      yaw: 0.328028
```
`initial_pose` also accepts `z` (default 0.0). Point the launch file to the new file:
```python
    nav2_yaml = os.path.join(get_package_share_directory('localization_server'), 'config', 'amcl_config_initialized.yaml')
```
Rebuild (`colcon build --packages-select localization_server`) and launch: the robot appears already localized at that pose, with no "Please set the initial pose" warning.

## Related options
- `always_reset_initial_pose` (bool): on a reset, require a new initial pose instead of reusing the last one ([[nav2-amcl-params-filter]]).
- AMCL also offers the service `set_initial_pose` (`nav2_msgs/srv/SetInitialPose`) and the topic `initialpose` for programs ([[nav2-initial-pose-publisher]]).

## Pitfalls
- The pose is only right if the robot really starts there (docking station, marked spot). If it can start anywhere, use global localization ([[nav2-global-localization]]).
- Editing the file in `src/` without rebuilding → the installed old file is used.
- Yaw is in radians, in the `map` frame.
