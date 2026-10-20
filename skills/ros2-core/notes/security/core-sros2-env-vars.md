---
id: core-sros2-env-vars
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "Run nodes with security: ROS_SECURITY_* variables and enclave selection"
domain: core
area: security
distro: humble
tested: false
audience: dev
summary: "ROS_SECURITY_KEYSTORE/ENABLE/STRATEGY/ENCLAVE_OVERRIDE, --enclave, Enforce vs permissive, 'Found security directory', inspecting a secured graph."
tags: [ROS_SECURITY_KEYSTORE, ROS_SECURITY_ENABLE, ROS_SECURITY_STRATEGY, ROS_SECURITY_ENCLAVE_OVERRIDE, --enclave, Enforce, permissive, sros2]
see: ["[[core-sros2-enclaves]]", "[[core-sros2-overview]]", "[[core-env-variables]]", "[[core-ros-args]]", "[[core-ros2-daemon]]"]
requires: []
version_notes:
  - "humble: ROS_SECURITY_ENABLE must be 'true' and ROS_SECURITY_STRATEGY 'Enforce' (case-sensitive); override beats --enclave; default enclave '/' — https://github.com/ros2/rcl/blob/humble/rcl/src/rcl/security.c (V127)"
  - "humble: rcl logs '[rcl]: Found security directory: <path>' at INFO — https://github.com/ros2/rcl/blob/humble/rcl/src/rcl/security.c (V128)"
  - "humble: to inspect a secured graph, run ros2cli with the variables and an enclave, without the daemon — https://docs.ros.org/en/humble/Tutorials/Advanced/Security/Introducing-ros2-security.html (V129)"
---
# Run nodes with security: ROS_SECURITY_* variables and enclave selection

**TL;DR** Export the keystore, the master switch and the strategy in **every** shell that runs secured nodes. Then give each process its enclave with `--ros-args --enclave <path>` (or `ROS_SECURITY_ENCLAVE_OVERRIDE`). Check the log line `Found security directory`.

## The variables
| Variable | Value | Effect |
|---|---|---|
| `ROS_SECURITY_KEYSTORE` | keystore root, e.g. `~/security_ws/turtlebot_keystore` | where rcl looks for `enclaves/<path>` |
| `ROS_SECURITY_ENABLE` | `true` (exactly, case-sensitive) | master on/off switch; any other value or unset = security off, even if the files exist |
| `ROS_SECURITY_STRATEGY` | `Enforce` (exactly, case-sensitive) | the process fails to start if its security files cannot be found. Anything else, or unset, = permissive: a misconfigured participant starts **without** security |
| `ROS_SECURITY_ENCLAVE_OVERRIDE` | enclave path, e.g. `/teleop` | enclave for every process started from this shell; takes precedence over `--enclave` |

Enclave lookup per process: `ROS_SECURITY_ENCLAVE_OVERRIDE` → `--enclave`/`-e` → `/` (root enclave). The path maps to `<keystore>/enclaves/<path>`.

## Per process (preferred) or per shell
```bash
export ROS_SECURITY_KEYSTORE=~/security_ws/turtlebot_keystore
export ROS_SECURITY_ENABLE=true
export ROS_SECURITY_STRATEGY=Enforce

ros2 run turtlebot3_teleop teleop_keyboard --ros-args --enclave /teleop   # one process
export ROS_SECURITY_ENCLAVE_OVERRIDE=/gazebo                              # or: everything this shell starts,
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py                  # e.g. all nodes of a launch file
```
The course uses the override for both shells. That puts every node of the Gazebo launch in the `/gazebo` enclave, which grants the union of the Gazebo and TurtleBot3 profiles.

Each secured process logs the enclave it found:
```text
[INFO] [1665833657.588441208] [rcl]: Found security directory: /home/user/security_ws/turtlebot_keystore/enclaves/gazebo
```
No such line means that process runs without security: `ROS_SECURITY_ENABLE` is not exactly `true`, or (permissive mode) its enclave folder was not found.

## Look at a secured graph
A shell without the variables is not authenticated. It cannot discover the secured participants: `ros2 node list` prints nothing, and `ros2 topic list` shows only the CLI's own `/parameter_events` and `/rosout`. To inspect the graph, use the same variables, an enclave whose permissions cover what you want to see, and no daemon (it may run without an enclave):
```bash
export ROS_SECURITY_ENCLAVE_OVERRIDE=/teleop
ros2 node list --no-daemon --spin-time 3
ros2 topic list --no-daemon --spin-time 3
```

## Pitfalls
- `ROS_SECURITY_STRATEGY=enforce` (lower case) is **permissive**. A typo silently runs the robot without security: always use `Enforce`.
- Permissive mode plus a wrong enclave path → the node runs unsecured and cannot talk to the secured nodes. It is not an error, it is just silent.
- An override left in `~/.bashrc` applies to every node of every shell, `ros2` CLI tools included.
- These variables are read when the process starts: restart the nodes after changing them.
