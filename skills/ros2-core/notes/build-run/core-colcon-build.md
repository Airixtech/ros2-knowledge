---
id: core-colcon-build
type: reference
owner: equipo-ros2
updated: 2026-10-14
review_by: 2027-04-12
source: manual
confidentiality: internal
title: "colcon build: commands, flags, tests"
domain: core
area: build-run
distro: humble
tested: false
audience: dev
summary: "Daily colcon build commands, useful flags (symlink-install, packages-select, parallel-workers, cmake-args) and colcon test."
tags: [colcon, build, symlink-install, packages-select, colcon test, test-result]
see: ["[[core-colcon-errors]]", "[[core-shell-workflow]]", "[[core-testing-ci-docker]]", "[[core-env-sourcing]]"]
requires: []
version_notes:
  - "all: --packages-select builds only the listed packages (not their dependencies); --packages-up-to adds them — https://github.com/colcon/colcon-package-selection/blob/master/colcon_package_selection/package_selection/select_skip.py (V105)"
---
# colcon build: commands, flags, tests

**TL;DR** Run colcon from the workspace root. The daily command is `colcon build --symlink-install --packages-select my_pkg && source install/setup.bash`. colcon replaces ROS 1 `catkin_make`.

## Core commands
```bash
cd ~/ros2_ws
colcon build                                        # all
colcon build --symlink-install --packages-select my_pkg   # THE daily combo
colcon build --packages-up-to my_pkg                # pkg + its deps
colcon build --packages-skip bad_pkg
source install/setup.bash                           # after every build that adds exes/pkgs/interfaces
```

## Flags
| Flag | Purpose |
|---|---|
| `--symlink-install` | symlink instead of copy → Python/launch/YAML edits apply without rebuild (new entry points still need rebuild) |
| `--packages-select <p..>` | only these |
| `--packages-up-to <p>` | p + deps |
| `--parallel-workers 2` / `--executor sequential` | limit RAM/CPU (Jetson, RPi, small VMs) |
| `--event-handlers console_direct+` | live compiler output |
| `--continue-on-error` | do not stop on first failing pkg |
| `--cmake-args -DCMAKE_BUILD_TYPE=Release` | optimized (prod) · `Debug` for gdb symbols |
| `--mixin release` | needs colcon-mixin |

## Tests
```bash
colcon test --packages-select my_pkg
colcon test-result --verbose            # details
colcon test-result --all --verbose | grep -A 10 FAIL
```
How to write the tests (pytest, gtest, launch_testing, linters): [[core-testing-ci-docker]].
Shell shortcuts (`cbs my_pkg` = build one package and source): [[core-shell-workflow]].

## Pitfalls
- `--packages-select` builds **only** the listed packages, not their dependencies: those must already be built or installed. Use `--packages-up-to` to include them.
- `--symlink-install` only covers edits to files that already exist. A new entry point, script or data file still needs a rebuild.
- Do not use `--symlink-install` when `install/` will be copied elsewhere, such as another Docker stage ([[core-testing-ci-docker]]).
- Build errors and their fixes: [[core-colcon-errors]].
