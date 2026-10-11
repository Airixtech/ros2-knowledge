---
id: core-param-yaml-cli
type: reference
owner: equipo-ros2
updated: 2026-10-09
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "Parameter YAML files, passing params & param CLI"
domain: core
area: core-api
distro: humble
tested: false
audience: dev
summary: "ros__parameters YAML format, passing params via --ros-args and launch, ros2 param list/get/set/dump/load, rqt_reconfigure."
tags: [parameters, yaml, ros__parameters, params-file, ros2 param, dump]
see: ["[[core-param-api]]", "[[core-ros-args]]", "[[core-launch-args-include]]"]
requires: []
version_notes:
  - "jazzy: ros2 param dump --print/--output-dir removed, --timeout added (Iron); lyrical: get from all nodes, get/set several params — https://docs.ros.org/en/rolling/Releases/Release-Iron-Irwini.html (V39)"
---
# Parameter YAML files, passing params & param CLI

**TL;DR** The YAML top-level key is the node name (or `/**` for every node), followed by `ros__parameters:`. Pass the file with `--params-file` or through launch `parameters=[...]`. `ros2 param dump` prints YAML you can load back.

## YAML format
```yaml
controller:                  # node name (or /namespace/node, or /** wildcard for all nodes)
  ros__parameters:
    rate_hz: 20.0
    use_pid: true
    kp: 2.5
    frames: ["base_link", "laser", "camera"]
    controller:              # nested -> parameter name "controller.max_velocity"
      max_velocity: 0.5
```

## Passing params
```bash
ros2 run my_pkg controller --ros-args -p kp:=2.5 -p base_frame:=odom
ros2 run my_pkg controller --ros-args --params-file config/params.yaml -p debug:=true   # file + override
```
Launch: `Node(..., parameters=[{'kp': 2.5}, PathJoinSubstitution([pkg_share, 'config', 'params.yaml'])])`. Global: `SetParameter(name='use_sim_time', value=True)` ([[core-launch-args-include]]).

## CLI
```bash
ros2 param list [/controller]
ros2 param describe /controller kp
ros2 param get /controller kp
ros2 param set /controller kp 1.5          # triggers on_set_params; rejected if invalid
ros2 param dump /controller > controller.yaml
ros2 param load /controller controller.yaml
ros2 param delete /controller some_param   # only for undeclared/dynamic params
```
GUI: `ros2 run rqt_reconfigure rqt_reconfigure`.
[Humble] `dump` prints to stdout, and `--print`/`--output-dir` are deprecated [changed in Jazzy: removed (Iron); `--timeout` added] [≥Lyrical: get a parameter from all nodes; get/set several at once].

## Pitfalls
- The YAML node key must match the node's runtime name and namespace. Use `/**:` to apply it to all nodes.
- `ros2 param set` changes the value, but your code keeps the old one unless it re-reads it or handles it in the callback ([[core-param-api]]).
- YAML `1` is an int and `1.0` a double. A type mismatch with the declared parameter is rejected at startup.
