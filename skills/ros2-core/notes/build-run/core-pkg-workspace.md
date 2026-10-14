---
id: core-pkg-workspace
type: reference
owner: equipo-ros2
updated: 2026-10-14
review_by: 2027-04-12
source: manual
confidentiality: internal
title: "Workspaces, overlays & package creation"
domain: core
area: build-run
distro: humble
tested: false
audience: dev
summary: "Workspace layout, underlay/overlay, ros2 pkg create for ament_python and ament_cmake, inspecting installed packages."
tags: [workspace, overlay, underlay, ros2 pkg create, REP 144, get_package_share_directory]
see: ["[[core-pkg-ament-python]]", "[[core-pkg-ament-cmake]]", "[[core-pkg-dependencies]]", "[[core-colcon-build]]"]
requires: []
version_notes:
  - "humble: the command is ros2 pkg create --build-type ament_python <name> --dependencies <deps> (a course wrote 'ros pkg create') — https://github.com/ros2/ros2cli/blob/humble/ros2pkg/ros2pkg/verb/create.py (V103)"
  - "lyrical: the ament_python template adds test_mypy.py, test_xmllint.py and py.typed (Kilted); Humble/Jazzy create test_copyright, test_flake8, test_pep257 — https://github.com/ros2/ros2cli/tree/kilted/ros2pkg/ros2pkg/resource/ament_python (V101)"
---
# Workspaces, overlays & package creation

**TL;DR** You only edit `~/ros2_ws/src`. Run `ros2 pkg create` from `src/` and `colcon build` from the workspace root. The overlay `install/` shadows same-name packages in `/opt/ros/humble`.

## Workspace
```bash
mkdir -p ~/ros2_ws/src && cd ~/ros2_ws && colcon build && source install/setup.bash
```
```
ros2_ws/
├── src/      # ONLY dir you edit/commit
├── build/    # generated
├── install/  # generated (source install/setup.bash)
└── log/      # generated
```
Overlay and underlay: `/opt/ros/humble` is the underlay and `~/ros2_ws/install` is the overlay (it shadows same-name pkgs). Never edit `install/`, and never run `colcon build` from `src/`.

## Create package (always from ws/src)
```bash
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_python my_pkg --dependencies rclpy std_msgs geometry_msgs sensor_msgs
ros2 pkg create --build-type ament_cmake  my_cpp_pkg --dependencies rclcpp std_msgs
ros2 pkg create --build-type ament_python my_pkg --node-name my_node --dependencies rclpy   # + sample exe
```
Build right after creating a package: it is the quickest check that the listed dependencies resolve. `my_node.py` appears in the output only with `--node-name`.
Naming (REP 144): `snake_case`, `[a-z0-9_]`, starts with a letter. `--license Apache-2.0` fills the license field. Full naming rules: [[core-bp-naming]].
Layouts: [[core-pkg-ament-python]] · [[core-pkg-ament-cmake]] · interface packages: [[core-iface-package]].

## Inspect packages
```bash
ros2 pkg list | grep my
ros2 pkg executables my_pkg
ros2 pkg prefix my_pkg               # install prefix; share dir = $(ros2 pkg prefix my_pkg)/share/my_pkg
ros2 pkg xml my_pkg
colcon list   ·   colcon list -t (topological)   ·   colcon info my_pkg
```
From Python: `from ament_index_python.packages import get_package_share_directory` → `get_package_share_directory('my_pkg')`.

## Pitfalls
- A package created outside `src/`, or a build run from `src/`, produces nested `build/install/log` dirs and "package not found" errors.
- A pure-Python package cannot generate `.msg/.srv/.action`. Use a dedicated ament_cmake interface package ([[core-iface-package]]).
- Same package name in the overlay and the underlay → the overlay wins. That is useful for patching, and confusing when it happens by accident.
