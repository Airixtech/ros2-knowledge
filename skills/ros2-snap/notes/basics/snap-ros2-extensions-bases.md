---
id: snap-ros2-extensions-bases
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "ROS 2 extensions, the colcon plugin and bases per ROS 2 distro"
domain: snap
area: basics
distro: humble
tested: false
audience: dev
summary: "Which base and ros2-<distro> extension per ROS 2 distro, what the extension adds, colcon plugin keys, snapcraft expand-extensions, list-plugins."
tags: [ros2-humble, ros2-jazzy, ros2-lyrical, ros2-foxy, core22, core24, core26, extension, colcon plugin, expand-extensions, list-plugins]
see: ["[[snap-snapcraft-yaml]]", "[[snap-ros2-no-extension]]", "[[snap-ros2-content-sharing]]", "[[snap-humble-to-jazzy]]"]
requires: [ros2-core]
version_notes:
  - "humble: ros2-humble supports base core22 and confinement strict/devmode only; adds the ROS 2 apt repo, a ros2-launch command-chain, ROS_DISTRO, PYTHONPATH, ROS_HOME=$SNAP_USER_DATA/ros — https://github.com/canonical/snapcraft/blob/main/snapcraft/extensions/ros2_humble.py (SNAP-V13)"
  - "humble: newer bases core24 and core26 exist; core22 stays the base for Humble — https://github.com/canonical/snapcraft/blob/main/docs/reference/bases.rst (SNAP-V10)"
  - "humble: ROS 2 extensions ros2-foxy, ros2-humble, ros2-jazzy, ros2-lyrical and content-sharing variants; none for Dashing (core18) — https://github.com/canonical/snapcraft/blob/main/docs/reference/extensions/ros-2-extensions.rst (SNAP-V26)"
  - "humble: ros2-foxy (core20) is still documented but Foxy is EOL since May 2023 — https://www.ros.org/reps/rep-2000.html (SNAP-V25)"
  - "humble: list plugins with snapcraft list-plugins (or plugins --base <base>); snapcraft help <plugin> --base <base> is documented for the core20 migration [verify on Snapcraft 9] — https://github.com/canonical/snapcraft/blob/main/snapcraft/commands/plugins.py (SNAP-V24)"
  - "humble: snapcraft expand-extensions shows what an extension adds — https://github.com/canonical/snapcraft/blob/main/snapcraft/commands/extensions.py (SNAP-V27)"
---
# ROS 2 extensions, the colcon plugin and bases per ROS 2 distro

**TL;DR** The base must match the ROS 2 distro inside the snap (not the host). Humble = `base: core22` + `extensions: [ros2-humble]` on each app + `plugin: colcon` on the parts. The extension writes the ROS boilerplate for you; `snapcraft expand-extensions` shows it.

## Base and extension per distro
| ROS 2 | Base (Ubuntu) | Extension | Snapcraft |
|---|---|---|---|
| Humble | `core22` (22.04) | `ros2-humble` | ≥ 7.3 |
| Jazzy | `core24` (24.04) | `ros2-jazzy` | ≥ 7.3 |
| Kilted | — | none (non-LTS): build it by hand, [[snap-ros2-no-extension]] | — |
| Lyrical | `core26` (26.04) | `ros2-lyrical` (experimental) | ≥ 9 |
| Foxy (EOL May 2023) | `core20` | `ros2-foxy` | ≥ 7.3 |
| Dashing (EOL May 2021) | `core18` | none; `colcon` keys `colcon-rosdistro`, `colcon-source-space` | — |

A base is a special snap with a minimal set of common libraries. Users never see it, but the developer must pick it when building. Once built, a Humble snap runs on many distros (an older Ubuntu, a recent Manjaro…). Content-sharing variants (`ros2-humble-ros-core`, `-ros-base`, `-desktop`): [[snap-ros2-content-sharing]].

## What `ros2-humble` adds
- The ROS 2 apt repository (`jammy`) and its key, so `stage-packages: [ros-humble-…]` resolve.
- A part `ros2-humble/ros2-launch` with the build packages `ros-humble-ros-environment`, `ros-humble-ros-workspace`, `ros-humble-ament-index-cpp`, `ros-humble-ament-index-python`.
- `build-environment` `ROS_VERSION=2`, `ROS_DISTRO=humble` for the parts.
- On each app: `command-chain: [snap/command-chain/ros2-launch]` (sources the ROS environment), `ROS_VERSION`, `ROS_DISTRO`, `PYTHONPATH` and `ROS_HOME=$SNAP_USER_DATA/ros`.
- Supported confinement: `strict` and `devmode` (not `classic`).
```bash
snapcraft expand-extensions        # print snapcraft.yaml with the extension applied
```

## colcon plugin keys
| Key | Use |
|---|---|
| `colcon-packages` | packages to build (default: all; `[]` builds none, e.g. only Debian packages) |
| `colcon-packages-ignore` | packages to skip |
| `colcon-cmake-args` / `colcon-ament-cmake-args` | arguments for CMake / ament_cmake packages (prefix a value that looks like a colcon flag with a space) |

The plugin runs `rosdep init` and `rosdep update`, sources the workspaces of build and stage snaps, installs the build packages, calls `colcon build`, then stages the run-time packages. Without an extension, set `ROS_DISTRO` in the part's `build-environment`.
```bash
snapcraft list-plugins             # or: snapcraft plugins --base core22
```

## Pitfalls
- The extension decides the base: `ros2-humble` with `base: core24` fails.
- `classic` confinement is not possible with the ROS 2 extensions.
- Per-plugin help: the colcon plugin reference; `snapcraft help colcon` is from older Snapcraft versions [verify on Snapcraft 9].
