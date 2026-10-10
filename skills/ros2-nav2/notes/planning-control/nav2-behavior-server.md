---
id: nav2-behavior-server
title: "behavior_server: spin, backup, wait and their parameters"
domain: nav2
area: planning-control
distro: humble
tested: false
audience: dev
summary: "Recovery behaviors (spin, backup, drive_on_heading, wait) in nav2_behaviors behavior_server: launch, Humble-correct YAML, parameters, node-name pitfall."
tags: [behavior_server, nav2_behaviors, recoveries_server, recovery behaviors, spin, backup, wait, drive_on_heading, behavior_plugins]
see: ["[[nav2-behavior-tree-xml]]", "[[nav2-bt-navigator]]", "[[nav2-local-costmap]]", "[[core-param-yaml-cli]]"]
requires: [ros2-core]
version_notes:
  - "humble: a YAML keyed behavior_server: is ignored by a node launched as recoveries_server (params match the node name) — https://github.com/ros2/rcl/blob/humble/rcl_yaml_param_parser/src/parse.c (NAV2-V01)"
  - "humble: no local_frame/transform_timeout; global_frame (default odom) + transform_tolerance; default plugins spin, backup, drive_on_heading, wait — https://github.com/ros-navigation/navigation2/blob/humble/nav2_behaviors/src/behavior_server.cpp (NAV2-V02, NAV2-V03)"
  - "jazzy: local_frame + global_frame, local/global costmap and footprint topics (Iron); plugin names nav2_behaviors::Spin… — https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/migration_guides/Humble.md (NAV2-V02, NAV2-V17)"
---
# behavior_server: spin, backup, wait and their parameters

**TL;DR** When the robot cannot find a valid path or gets stuck, the behavior tree calls **recovery behaviors**: simple, pre-defined movements that usually clear the situation. The `behavior_server` (`nav2_behaviors`; `recoveries_server`/`nav2_recoveries` before Humble) is the node responsible for executing them, e.g. when `bt_navigator` believes the robot is stuck.

The course launches it with `name='recoveries_server'` ([[nav2-path-planning-launch]]).

## config/recovery.yaml (Humble-correct)
```yaml
recoveries_server:          # must equal the launched node name (the course file said behavior_server:)
  ros__parameters:
    costmap_topic: local_costmap/costmap_raw
    footprint_topic: local_costmap/published_footprint
    cycle_frequency: 10.0
    behavior_plugins: ["spin", "backup", "wait"]
    spin:
      plugin: "nav2_behaviors/Spin"
    backup:
      plugin: "nav2_behaviors/BackUp"
    wait:
      plugin: "nav2_behaviors/Wait"
    global_frame: odom          # Humble: frame the behaviors work in (course: local_frame: odom + global_frame: map)
    robot_base_frame: base_link
    transform_tolerance: 0.1    # course: transform_timeout, not a Humble parameter
    use_sim_time: true
    simulate_ahead_time: 2.0
    max_rotational_vel: 1.0
    min_rotational_vel: 0.4
    rotational_acc_lim: 3.2
```
In the config file, indicate which behaviors to load: each is then ready to be called by `bt_navigator` as an action server with the same name.

## Behaviors and parameters (Humble)
| Behavior | Does |
|---|---|
| `spin` (`nav2_behaviors/Spin`) | in-place rotation by a given angle |
| `backup` (`nav2_behaviors/BackUp`) | linear translation backwards by a given distance |
| `drive_on_heading` (`nav2_behaviors/DriveOnHeading`) | drive straight at a given heading |
| `wait` (`nav2_behaviors/Wait`) | stay stationary for a given time |
| `assisted_teleop` (`nav2_behaviors/AssistedTeleop`) | teleop with collision checking |

| Parameter | Default | Meaning |
|---|---|---|
| `costmap_topic` | `local_costmap/costmap_raw` | raw costmap for collision checking |
| `footprint_topic` | `local_costmap/published_footprint` | footprint in the costmap frame |
| `cycle_frequency` | 10.0 Hz | rate at which behavior plugins run |
| `behavior_plugins` | `["spin", "backup", "drive_on_heading", "wait"]` | plugin names; they are also the action server names |
| `global_frame` | `odom` | frame the behaviors work in |
| `robot_base_frame` | `base_link` | robot base frame |
| `transform_tolerance` | 0.1 s | TF tolerance |

## Pitfalls
- YAML key ≠ node name → the whole file is ignored and defaults are used. With one robot it still works; with namespaced robots the default frames are wrong and recoveries fail ([[nav2-multirobot-bt-behavior-config]], [[core-param-yaml-cli]]).
