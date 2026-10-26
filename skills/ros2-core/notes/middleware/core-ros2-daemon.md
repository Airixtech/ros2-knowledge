---
id: core-ros2-daemon
type: reference
owner: equipo-ros2
updated: 2026-10-26
review_by: 2027-04-24
source: manual
confidentiality: internal
title: "The ros2 daemon: discovery cache, start/stop/status, stale RMW"
domain: core
area: middleware
distro: humble
tested: false
audience: dev
summary: "What the ros2 daemon caches for the CLI, when it starts, stop/start/status, and restarting it after an RMW change."
tags: [ros2 daemon, discovery, CLI, ros2 daemon stop, ros2 daemon status, rmw-implementation, _ros2_daemon, ROS_DOMAIN_ID, roscore]
see: ["[[core-rmw-implementations]]", "[[core-dds-overview]]", "[[core-debug-triage]]", "[[core-env-variables]]"]
requires: []
version_notes:
  - "humble: the daemon serves the command-line tools only (nodes never use it) and keeps its RMW until restarted — https://docs.ros.org/en/humble/Concepts/Basic/About-Command-Line-Tools.html (V91)"
  - "humble: spawn_daemon runs 'python3 -c from ros2cli.daemon.daemonize import main; main() --name ros2-daemon …' (same in Jazzy); this note called the _ros2_daemon form the newer one, it is the older — https://github.com/ros2/ros2cli/blob/humble/ros2cli/ros2cli/node/daemon.py (CPP-V75)"
---
# The ros2 daemon: discovery cache, start/stop/status, stale RMW

**TL;DR** ROS 2 has no `roscore`: each node discovers the others through DDS, which takes time in large systems. To answer `ros2 node list`, `ros2 topic list` and other CLI queries quickly, the first such command starts a background **daemon** that keeps the ROS graph. Only the command-line tools use it; launching nodes does not start it. It keeps the RMW and `ROS_DOMAIN_ID` it was started with.

## Commands
```bash
ros2 daemon stop
ros2 daemon status       # The daemon is not running.
ros2 topic list          # any introspection command starts it again
ros2 daemon status       # The daemon is running.
ros2 daemon start        # The daemon has been started.
ps faux | grep "rmw-implementation"
```
```text
user  6819 ... /usr/bin/python3 -c from ros2cli.daemon.daemonize import main; main() --name ros2-daemon --ros-domain-id 0 --rmw-implementation rmw_cyclonedds_cpp
```
Humble and Jazzy start the daemon in this `daemonize` form (`--name ros2-daemon`), so `grep "ros2_daemon"` finds only the grep itself; the form `_ros2_daemon --rmw-implementation … --ros-domain-id …` is from an older ros2cli (CPP-V75). Starting the daemon before a node system does not speed up the nodes: only the CLI uses it (CPP-V76).

## After changing the RMW
The daemon does not change its RMW when you export a new one: the CLI then shows an empty graph or fails. Stop it and start it again from a shell with the new export:
```bash
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
ros2 daemon stop
ros2 daemon start
ps faux | grep "rmw-implementation"     # ... --rmw-implementation rmw_fastrtps_cpp
```
Each `ROS_DOMAIN_ID` gets its own daemon (it is a port offset): `ros2 daemon stop` acts on the daemon of your current domain. Official description: [CLI tools (humble)](https://docs.ros.org/en/humble/Concepts/Basic/About-Command-Line-Tools.html).

## Pitfalls
- `ros2 node list` misses a node that clearly runs → stale daemon (old RMW, other domain): `ros2 daemon stop`, then retry ([[core-debug-triage]]).
- Start the daemon (`ros2 daemon start`) before introspecting a big system so the first CLI command is not slow.
