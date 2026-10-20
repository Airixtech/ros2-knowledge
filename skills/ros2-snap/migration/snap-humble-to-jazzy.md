---
id: snap-humble-to-jazzy
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "Snaps: Humble (core22) → Jazzy (core24) changes"
domain: snap
area: migration
distro: humble
tested: false
audience: dev
summary: "Port a Humble snap to Jazzy: base core24, ros2-jazzy extension, ros-jazzy-* packages, Python 3.12, renamed demo launch files, content extensions."
tags: [migration, Jazzy, core24, ros2-jazzy, ros-jazzy-ros2launch, talker_listener_launch.py, Python 3.12, ros2-jazzy-ros-base]
see: ["[[snap-ros2-extensions-bases]]", "[[snap-snapcraft-yaml]]", "[[snap-jazzy-to-lyrical]]", "[[core-humble-to-jazzy]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: base core24, extension ros2-jazzy (Snapcraft 7.3+), stage ros-jazzy-ros2launch; demo launch file talker_listener_launch.py — https://github.com/canonical/snapcraft/blob/main/docs/how-to/integrations/craft-an-ros-2-app.rst (SNAP-V10, SNAP-V12)"
  - "jazzy: content extensions ros2-jazzy-ros-core/-ros-base/-desktop (experimental, Snapcraft 8+) — https://github.com/canonical/snapcraft/blob/main/docs/reference/extensions/ros-2-content-extensions.rst (SNAP-V39)"
---
# Snaps: Humble (core22) → Jazzy (core24) changes

**TL;DR** Change the base, the extension and every `ros-humble-*` package name together; check launch file names, which changed in the ROS 2 demos. The snap structure (parts, apps, plugs, daemons, hooks) stays the same. Generic ROS 2 changes: [[core-humble-to-jazzy]].

| Item | Humble | Jazzy |
|---|---|---|
| `base` | `core22` (Ubuntu 22.04) | `core24` (Ubuntu 24.04) |
| extension | `ros2-humble` | `ros2-jazzy` |
| ROS packages | `ros-humble-ros2launch`, `ros-humble-ros2topic`… | `ros-jazzy-ros2launch`, `ros-jazzy-ros2topic`… |
| `source-branch` of ros2/demos | `humble` | `jazzy` |
| demo launch file | `talker_listener.launch.py` | `talker_listener_launch.py` |
| Python in `PYTHONPATH` (no extension) | 3.10 | 3.12 |
| ROS apt suite (no extension) | `jammy` | `noble` |
| content-sharing extensions | `ros2-humble-ros-core`, `-ros-base`, `-desktop` | `ros2-jazzy-ros-core`, `-ros-base`, `-desktop` |
| host for `--destructive-mode` | Ubuntu 22.04 | Ubuntu 24.04 |

Jazzy talker-listener (official how-to):
```yaml
base: core24
parts:
  ros-demos:
    plugin: colcon
    source: https://github.com/ros2/demos.git
    source-branch: jazzy
    source-subdir: demo_nodes_cpp
    stage-packages: [ros-jazzy-ros2launch]
apps:
  ros2-talker-listener:
    command: ros2 launch demo_nodes_cpp talker_listener_launch.py
    extensions: [ros2-jazzy]
```

## Pitfalls
- The official Jazzy example writes `command: ros2 launch …` without `opt/ros/jazzy/bin/` [verify: that the extension's command chain resolves it; the explicit path `opt/ros/jazzy/bin/ros2` is the safe form].
- `snapcraft init --profile ros2` already writes a Jazzy template (with the content extension `ros2-jazzy-ros-core`).
- Kilted (between Jazzy and Lyrical) has no extension: [[snap-ros2-no-extension]].
