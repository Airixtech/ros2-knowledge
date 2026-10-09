---
id: core-pkg-dependencies
title: "Dependencies: package.xml tags, rosdep, vcstool"
domain: core
area: build-run
distro: humble
tested: false
audience: dev
summary: "package.xml format 3 dependency tags, installing deps with rosdep, multi-repo workspaces with vcstool .repos files."
tags: [package.xml, depend, exec_depend, rosdep, vcstool, repos]
see: ["[[core-pkg-ament-python]]", "[[core-pkg-ament-cmake]]", "[[core-colcon-errors]]"]
requires: []
version_notes: []
---
# Dependencies: package.xml tags, rosdep, vcstool

**TL;DR** Every import or `find_package` needs a matching `package.xml` tag. `rosdep install` turns those tags into apt/pip packages, and `vcs import` pulls source repositories.

## package.xml (format 3) dependency tags
| Tag | Use |
|---|---|
| `<buildtool_depend>` | `ament_cmake` / `ament_python` / `rosidl_default_generators` |
| `<depend>` | build+export+exec; default for ROS deps (`rclpy`, `rclcpp`, `*_msgs`) |
| `<build_depend>` / `<build_export_depend>` | compile-time only / exported headers |
| `<exec_depend>` | runtime only (pure Python libs, launch deps, `rosidl_default_runtime`) |
| `<test_depend>` | `ament_lint_auto`, `ament_lint_common`, `ament_cmake_gtest`, `python3-pytest` |

Every import / `find_package` needs a matching tag, or rosdep and other machines break.

## Dependencies (rosdep)
```bash
sudo rosdep init && rosdep update                      # once per machine
cd ~/ros2_ws && rosdep install --from-paths src --ignore-src -r -y   # --rosdistro humble optional
```
`--from-paths src`: scan src/ · `--ignore-src`: skip deps that are pkgs in src · `-r`: continue on errors · `-y`: auto-yes.

## Multi-repo (vcstool)
```yaml
# my_project.repos
repositories:
  navigation2: {type: git, url: https://github.com/ros-navigation/navigation2.git, version: humble}
```
```bash
vcs import src < my_project.repos && vcs pull src && vcs status src
```

## Pitfalls
- A dependency missing from `package.xml` still builds on your machine if it happens to be installed. It fails on CI, in Docker and for your students.
- Pure-Python libraries go in `<exec_depend>` with their rosdep key (e.g. `python3-numpy`), not as pip-installed packages.
- `Dependency not found at build` → add the tag, then run `rosdep install …` ([[core-colcon-errors]]).
