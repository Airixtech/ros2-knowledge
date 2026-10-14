---
id: core-env-sourcing
type: reference
owner: equipo-ros2
updated: 2026-10-09
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "Sourcing & ~/.bashrc setup"
domain: core
area: build-run
distro: humble
tested: false
audience: dev
summary: "Source underlay then overlay in every terminal; recommended ~/.bashrc block, install check, CLI helpers."
tags: [setup.bash, bashrc, underlay, overlay, colcon_cd, argcomplete]
see: ["[[core-env-variables]]", "[[core-pkg-workspace]]", "[[core-colcon-build]]"]
requires: []
version_notes:
  - "jazzy: Ubuntu 24.04 / Python 3.12; lyrical: Ubuntu 26.04 / Python 3.14 — https://www.ros.org/reps/rep-2000.html (V04)"
  - "jazzy: ROS_LOCALHOST_ONLY deprecated, removed in Kilted — https://docs.ros.org/en/jazzy/Tutorials/Beginner-CLI-Tools/Configuring-ROS2-Environment.html (V01)"
---
# Sourcing & ~/.bashrc setup

**TL;DR** In every new terminal, source `/opt/ros/humble/setup.bash` (underlay) first and then `~/ros2_ws/install/setup.bash` (overlay). Humble targets Ubuntu 22.04 with Python 3.10.

## Sourcing (every new terminal)
```bash
source /opt/ros/humble/setup.bash        # underlay (always first)
source ~/ros2_ws/install/setup.bash      # overlay (after each build that adds pkgs/executables/interfaces)
```
Rule: source the underlay BEFORE the overlay. Never re-source the underlay after the overlay, because that breaks precedence.

## ~/.bashrc block (recommended)
```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash 2>/dev/null   # silent if ws not built yet
export ROS_DOMAIN_ID=42                           # same value on every machine/terminal that must talk
# export ROS_LOCALHOST_ONLY=1                     # isolate on shared Wi-Fi [Humble; ≥Jazzy: ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST]
export RCUTILS_COLORIZED_OUTPUT=1                 # colored logs
# export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp    # alt DDS (needs ros-humble-rmw-cyclonedds-cpp)
source /usr/share/colcon_cd/function/colcon_cd.sh
export _colcon_cd_root=/opt/ros/humble/
source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash   # Tab-complete colcon/ros2 args
```
To apply it without reopening the terminal: `source ~/.bashrc`. Variable meanings are in [[core-env-variables]].

Multi-workspace alternative (source on demand):
```bash
ros2_humble() {
  source /opt/ros/humble/setup.bash
  [ -f ~/ros2_ws/install/setup.bash ] && source ~/ros2_ws/install/setup.bash
  echo "ROS 2 Humble active"
}
```

## Verify install
```bash
printenv | grep -E 'ROS|RMW'
ros2 doctor                      # see core-debug-triage
ros2 run demo_nodes_cpp talker   # T1
ros2 run demo_nodes_py listener  # T2 -> must print "I heard: ..."
```
`ros2 doctor` output is explained in [[core-debug-triage]].

## Helpers
```bash
colcon_cd my_pkg          # jump to package source dir (needs colcon_cd setup above)
ros2 <cmd> --help         # list verbs; ros2 <cmd> <verb> --help for args
```
CLI grammar: `ros2 <command> <verb> <args>` (e.g. `ros2 topic list`, `ros2 node info /n`).

## Pitfalls
- `echo $ROS_DISTRO` must print `humble`. If it is empty, the terminal is not sourced.
- New packages, executables or interfaces only show up after a rebuild **and** re-sourcing the overlay ([[core-colcon-errors]]).
- On the course cloud platform, `~/.bash_aliases` is platform-managed. Put your own exports at the end of `~/.bashrc` ([[core-learn-start-here]]).
