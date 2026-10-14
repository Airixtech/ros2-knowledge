---
id: nav2-multirobot-amcl-config
type: reference
owner: equipo-ros2
updated: 2026-10-10
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "Per-robot AMCL YAML: namespaced node key, frames, scan and map topics"
domain: nav2
area: multi-robot
distro: humble
tested: false
audience: dev
summary: "tb3_0_amcl_config.yaml: full node name as key, tb3_0 frames, global_frame_id map, scan_topic, map_topic /map, initial pose per robot."
tags: [multi-robot, AMCL, tb3_0_amcl_config.yaml, tb3_0/amcl, base_frame_id, odom_frame_id, map_topic, scan_topic, namespace]
see: ["[[nav2-amcl-launch]]", "[[nav2-multirobot-localization]]", "[[nav2-multirobot-planner-controller-config]]"]
requires: [ros2-core]
version_notes:
  - "humble: flat YAML keys like tb3_0/amcl: are valid (rcl adds the leading '/') — https://github.com/ros2/rcl/blob/humble/rcl_yaml_param_parser/src/parse.c (NAV2-V39)"
---
# Per-robot AMCL YAML: namespaced node key, frames, scan and map topics

**TL;DR** A launch `namespace` renames the node, its topics and services, but **not the frames inside its config file**. Give each robot its own copy of `amcl_config.yaml` ([[nav2-amcl-launch]]) with namespaced frames.

## What to change in each copy
Copy it to `tb3_0_amcl_config.yaml` and `tb3_1_amcl_config.yaml`, then:
1. The first line: the **full node name** (`tb3_0/amcl`).
2. Every frame gets the namespace, except `global_frame_id`: there is a single global frame (the map) for all robots.
3. Topics need no change: the `namespace` argument of the launch renames them. Frames are not renamed.
4. Force `map_topic` to `/map`: without the `/` it becomes `tb3_0/map`, which no map server publishes.

## tb3_0_amcl_config.yaml
```yaml
tb3_0/amcl:
  ros__parameters:
    # … all keys of amcl_config.yaml, with these values:
    base_frame_id: "tb3_0/base_footprint"
    odom_frame_id: "tb3_0/odom"
    global_frame_id: "map"
    scan_topic: "/tb3_0/scan"
    map_topic: "/map"
    set_initial_pose: true
    initial_pose:
      x: 0.0
      y: 0.0
      yaw: 0.0
```
`tb3_1_amcl_config.yaml` is identical with `tb3_1/…` frames, `/tb3_1/scan` and its own start pose (`y: -0.5`). Activate `set_initial_pose` only when you have a proper initial pose for that robot ([[nav2-initial-pose-config]]).

Launch file and lifecycle manager: [[nav2-multirobot-localization]].

## Pitfalls
- `map_topic: map` (relative) → AMCL waits forever for `/tb3_0/map`.
- Forgetting one frame (e.g. `odom_frame_id: "odom"`) → AMCL looks for a frame that does not exist and never publishes `map → tb3_0/odom`.
