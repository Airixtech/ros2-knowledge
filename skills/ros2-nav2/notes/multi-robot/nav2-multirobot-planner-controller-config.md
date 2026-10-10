---
id: nav2-multirobot-planner-controller-config
title: "Per-robot planner_server and controller_server YAML (costmaps, frames, map_topic)"
domain: nav2
area: multi-robot
distro: humble
tested: false
audience: dev
summary: "Per-robot copies of planner_server.yaml and controller.yaml: namespaced node and costmap keys, tb3_0 frames, absolute /map and /tb3_0/scan topics."
tags: [multi-robot, tb3_0_planner_server.yaml, tb3_0_controller.yaml, global_costmap, local_costmap, map_topic, robot_base_frame, namespace]
see: ["[[nav2-planner-server]]", "[[nav2-controller-server]]", "[[nav2-global-costmap]]", "[[nav2-local-costmap]]", "[[nav2-multirobot-planning-launch]]"]
requires: [ros2-core]
version_notes:
  - "humble: relative layer topics resolve inside the costmap namespace, so per-robot sources use absolute topics; lyrical: relative topics join the robot namespace and the global costmap map_topic moves into static_layer (Kilted) — https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/migration_guides/jazzy/Jazzy.md (NAV2-V24, NAV2-V25)"
  - "humble: controller_server has no cmd_vel_topic parameter; it publishes relative cmd_vel — https://github.com/ros-navigation/navigation2/blob/humble/nav2_controller/src/controller_server.cpp (NAV2-V41)"
---
# Per-robot planner_server and controller_server YAML (costmaps, frames, map_topic)

**TL;DR** Copy each config once per robot (`tb3_0_planner_server.yaml`, `tb3_0_controller.yaml`…) and change: the full node name in the first key, the same for the costmap keys, the robot frames, and force `/map`.

## Rules for every per-robot file
1. The first line holds the **full new node name**, e.g. `tb3_0/planner_server`.
2. All frames get the namespace, except the global frame (`map`), which is shared.
3. Topics are renamed by the launch namespace; frames are not.
4. Force `map_topic` to `/map`: the `/` means "do not apply the namespace", because the map is unique and shared.

## tb3_0_planner_server.yaml (complete)
```yaml
tb3_0/planner_server:
  ros__parameters:
    expected_planner_frequency: 10.0
    use_sim_time: True
    planner_plugins: ["GridBased"]
    GridBased:
      plugin: "nav2_navfn_planner/NavfnPlanner"
      tolerance: 0.5
      use_astar: false
      allow_unknown: true
tb3_0/global_costmap:
  global_costmap:
    ros__parameters:
      update_frequency: 1.0
      publish_frequency: 1.0
      global_frame: map
      # This has to be set
      map_topic: /map
      robot_base_frame: tb3_0/base_link
      use_sim_time: True
      robot_radius: 0.15
      resolution: 0.05
      track_unknown_space: true
      plugins: ["static_layer", "obstacle_layer", "inflation_layer"]
      static_layer:
        plugin: "nav2_costmap_2d::StaticLayer"
        map_subscribe_transient_local: True
      inflation_layer:
        plugin: "nav2_costmap_2d::InflationLayer"
        cost_scaling_factor: 3.0
        inflation_radius: 0.35
      always_send_full_costmap: True
      obstacle_layer:
        plugin: "nav2_costmap_2d::ObstacleLayer"
        enabled: True
        observation_sources: scan
        scan:
          topic: /tb3_0/scan    # absolute: in Humble a relative topic resolves inside the costmap namespace
          max_obstacle_height: 2.0
          clearing: True
          marking: True
          data_type: "LaserScan"
          raytrace_max_range: 3.0
          raytrace_min_range: 0.0
          obstacle_max_range: 2.5
          obstacle_min_range: 0.0
```

## tb3_0_controller.yaml (changes against controller.yaml)
```yaml
tb3_0/controller_server:          # was controller_server
  ros__parameters:
    # … same server, checker and FollowPath (DWB) parameters
tb3_0/local_costmap:              # was local_costmap
  local_costmap:
    ros__parameters:
      global_frame: tb3_0/odom        # was odom
      robot_base_frame: tb3_0/base_link
      # … same layers; voxel_layer scan source:
      voxel_layer:
        scan:
          topic: /tb3_0/scan
```
The course also adds `cmd_vel_topic: "cmd_vel"` to `controller_server`: Humble has no such parameter. The controller publishes the relative topic `cmd_vel`, which the namespace already turns into `/tb3_0/cmd_vel`.

## Pitfalls
- Costmap key not namespaced (`global_costmap:` under a `tb3_0` planner) → the costmap runs with default parameters.
- `robot_base_frame: base_link` left unprefixed → TF lookup errors: that frame does not exist.
