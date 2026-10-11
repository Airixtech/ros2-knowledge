---
id: core-ros-args
type: reference
owner: equipo-ros2
updated: 2026-10-09
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "--ros-args (remap, namespace, params) & node CLI"
domain: core
area: core-api
distro: humble
tested: false
audience: dev
summary: "Rename, namespace, remap and parametrize a node at run time with --ros-args; list/inspect/kill nodes."
tags: [ros-args, remap, __node, __ns, ros2 node, params-file]
see: ["[[core-node-skeleton]]", "[[core-param-yaml-cli]]", "[[core-multi-robot-namespacing]]", "[[core-logging]]"]
requires: []
version_notes: []
---
# --ros-args (remap, namespace, params) & node CLI

**TL;DR** Everything after `--ros-args` configures the node without changing code: `-r` remaps names, `-p` sets parameters, `--params-file` loads YAML, and `--log-level` sets verbosity.

## `--ros-args` (after the executable)
| Flag | Effect | Example |
|---|---|---|
| `-r __node:=<name>` | rename node | `-r __node:=robot1_ctrl` |
| `-r __ns:=<ns>` | namespace | `-r __ns:=/robot1` |
| `-r <from>:=<to>` | remap topic/service | `-r cmd_vel:=/robot1/cmd_vel` |
| `-p <param>:=<val>` | set parameter | `-p max_speed:=1.0` |
| `--params-file <yaml>` | load params | `--params-file cfg.yaml` |
| `--log-level <lvl>` | log level | `--log-level debug` |
```bash
ros2 run my_pkg my_node --ros-args -r __node:=robot1 -r cmd_vel:=/robot1/cmd_vel -p max_speed:=1.0
ros2 run demo_nodes_cpp talker --ros-args -r __ns:=/robot1     # two instances: different ns
```
YAML format and the param CLI: [[core-param-yaml-cli]]. Per-logger levels: [[core-logging]].

## Node CLI
```bash
ros2 run <pkg> <exe>
ros2 node list            # -a / --all includes hidden
ros2 node info /my_node   # pubs, subs, services, actions
ros2 node list | sort | uniq -c | sort -rn   # spot duplicate names (zombies)
ps aux | grep ros2 ; kill -9 <PID> ; pkill -9 -f my_node ; pkill -9 -f ros2   # kill hung nodes
```

## Pitfalls
- `-r` applies to relative names. A topic created as `/cmd_vel` (absolute) is not moved by `__ns` ([[core-topic-pub-sub-py]]).
- Flags placed before `--ros-args` are passed to your program, not to ROS.
- Zombie processes from a previous run keep publishing under the same name. Check `ros2 node list` for duplicates.
