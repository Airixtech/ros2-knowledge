---
id: snap-snapcraft-yaml
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "snapcraft.yaml for a ROS 2 app: metadata, confinement, base, parts, apps"
domain: snap
area: basics
distro: humble
tested: false
audience: dev
summary: "snap/snapcraft.yaml keys for the ROS 2 Humble talker-listener: name/version/summary rules, devmode, base core22, colcon part, apps with ros2-humble."
tags: [snapcraft.yaml, name, version, summary, confinement, base, core22, parts, colcon, stage-packages, apps, extensions, snapcraft init]
see: ["[[snap-build-install-run]]", "[[snap-ros2-extensions-bases]]", "[[snap-confinement]]", "[[core-pkg-dependencies]]"]
requires: [ros2-core]
version_notes:
  - "humble: summary is limited to 78 characters (the course and the template comment say 79) — https://github.com/canonical/snapcraft/blob/main/schema/snapcraft.json (SNAP-V03)"
  - "humble: names: lower-case letters, digits and hyphens, at least one letter, no hyphen at start, end or twice in a row, max 40 characters; version max 32 — https://github.com/canonical/snapcraft/blob/main/snapcraft/models/project.py (SNAP-V08, SNAP-V09)"
  - "humble: demo_nodes_cpp exec-depends launch_ros and launch_xml but not ros2launch, hence stage-packages; other deps come from rosdep; current repo adds build-packages: [build-essential] — https://github.com/ros2/demos/blob/humble/demo_nodes_cpp/package.xml (SNAP-V11)"
  - "humble: snapcraft init --profile ros2 writes a template for the Snapcraft version installed (main: core24 + ros2-jazzy-ros-core); set base/extension/branch for Humble — https://github.com/canonical/snapcraft/blob/main/snapcraft/templates/ros2/snap/snapcraft.yaml.j2 (SNAP-V34)"
  - "jazzy: base core24, extension ros2-jazzy, stage ros-jazzy-ros2launch, launch file talker_listener_launch.py — https://github.com/canonical/snapcraft/blob/main/docs/how-to/integrations/craft-an-ros-2-app.rst (SNAP-V10, SNAP-V12)"
---
# snapcraft.yaml for a ROS 2 app: metadata, confinement, base, parts, apps

**TL;DR** A snap is defined by one file, `snap/snapcraft.yaml`, at the root of the project. For ROS 2 Humble: `base: core22`, a `colcon` part that builds the packages, and apps that use the `ros2-humble` extension. Start from the official example repository or from `snapcraft init --profile ros2`.

## The talker-listener snap (Humble)
From [ubuntu-robotics/ros2-humble-talker-listener-snap](https://github.com/ubuntu-robotics/ros2-humble-talker-listener-snap) (`main` branch):
```yaml
name: ros2-talker-listener
version: '0.1'
summary: ROS 2 Talker/Listener Example
description: |
 This example launches a ROS 2 talker and listener.

confinement: devmode
base: core22

parts:
 ros-demos:
   plugin: colcon
   source: https://github.com/ros2/demos.git
   source-branch: humble
   source-subdir: demo_nodes_cpp
   build-packages: [build-essential]
   stage-packages: [ros-humble-ros2launch]

apps:
 ros2-talker-listener:
   command: opt/ros/humble/bin/ros2 launch demo_nodes_cpp talker_listener.launch.py
   extensions: [ros2-humble]
```
```bash
cd ~/default_ws/src
git clone https://github.com/ubuntu-robotics/ros2-humble-talker-listener-snap.git
cd ros2-humble-talker-listener-snap
cat snap/snapcraft.yaml
```

## Metadata
- `name`: unique on the Snap Store if you publish there. Lower-case letters, digits and hyphens; at least one letter; no hyphen at the start, at the end or twice in a row; at most 40 characters.
- `version`: declarative, for humans; not linked to the snap's own revision. It can be computed by a script or taken from a git tag or commit. At most 32 characters.
- `summary`: at most **78** characters. `description`: a paragraph or two, under 100 words so it looks good in the store. Both are what the Snap Store shows (e.g. the PlotJuggler page).

## Confinement and base
- `confinement: devmode` = not confined yet, for a first build; `strict` for real use ([[snap-confinement]]).
- `base`: the run-time environment, a minimal Ubuntu with common libraries. It must match the ROS distro, not the user's OS: `core22` (Ubuntu 22.04) for Humble ([[snap-ros2-extensions-bases]]).

## Parts
Parts define how to build the app: programs, libraries or assets, from local folders, git repositories or tarballs; one snap can have several parts.
- `plugin: colcon` builds ROS 2 packages: it runs `rosdep`, installs the build dependencies, calls `colcon build` and stages the runtime dependencies of each `package.xml`.
- The packages need `install` rules (binaries, libraries, headers, launch files): snapcraft only ships what is installed ([[core-pkg-ament-cmake]]).
- `source-branch` picks the branch; `source-subdir` picks one package of a multi-package repository.
- `stage-packages`: run-time Debian packages a part needs that rosdep does not bring. Here `ros-humble-ros2launch` (the `ros2 launch` verb), which the `package.xml` of `demo_nodes_cpp` does not declare.

## Apps
- The key under `apps` is the command name users run. An app is called `<snap>.<app>`; when both names are equal, the command collapses to the snap name: `ros2-talker-listener`.
- `command` is relative to the root of the snap (no leading `/` before `opt`).
- `extensions: [ros2-humble]` sets up the ROS 2 build and run-time environment: no manual sourcing ([[snap-ros2-extensions-bases]]).

## Start from a template
```bash
snapcraft init --name my-ros2-project --profile ros2   # writes snap/snapcraft.yaml
```
The template follows the installed Snapcraft (with the current one: `base: core24`, `extensions: [ros2-jazzy-ros-core]`, `source-branch: jazzy`, `grade: devel`). For Humble change them to `core22`, `ros2-humble` and `humble`, and add `stage-packages: [ros-humble-ros2launch]`.

## Pitfalls
- [changed in Jazzy: `base: core24`, `extensions: [ros2-jazzy]`, `stage-packages: [ros-jazzy-ros2launch]`; the demo launch file is `talker_listener_launch.py`.]
- A package without install rules builds fine but its files are missing from the snap ([[snap-debug-build]]).
