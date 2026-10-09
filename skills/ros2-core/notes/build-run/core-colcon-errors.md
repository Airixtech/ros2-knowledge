---
id: core-colcon-errors
title: "colcon build errors, fixes & cleaning"
domain: core
area: build-run
distro: humble
tested: false
audience: dev
summary: "Symptom-to-fix table for common build/run errors (package not found, stale code, OOM, setuptools warning) and how to clean."
tags: [colcon, errors, ModuleNotFoundError, setuptools, clean, rosdep]
see: ["[[core-colcon-build]]", "[[core-pkg-ament-python]]", "[[core-pkg-dependencies]]", "[[core-debug-triage]]"]
requires: []
version_notes:
  - "jazzy: pip install into system Python is blocked by PEP 668 on Ubuntu 24.04; do not downgrade setuptools — https://peps.python.org/pep-0668/ (V13)"
---
# colcon build errors, fixes & cleaning

**TL;DR** Most "not found" errors mean the terminal is not sourced, or the executable or file was never installed. Stale or weird errors after renames go away after deleting `build/ install/ log/`.

## Errors → fix
| Symptom | Fix |
|---|---|
| `Package 'X' not found` / `No executable found` | `source install/setup.bash`; check entry point in setup.py / `install(PROGRAMS...)`; rebuild |
| Python change not applied | build with `--symlink-install` (once), or rebuild |
| `ModuleNotFoundError: custom_interfaces` | build interface pkg, then source in EVERY terminal |
| Build hangs / OOM | `--parallel-workers 2` or `--executor sequential` |
| `SetuptoolsDeprecationWarning: setup.py install is deprecated` | harmless in Humble; ignore it (see note below) |
| Weird errors after renames/moves | delete build/ install/ log/ and rebuild |
| Dependency not found at build | add to package.xml + `rosdep install --from-paths src --ignore-src -r -y` |
| Pkg depends on sim pkg (e.g. leo_description) | source that ws (e.g. `/home/simulations/ros2_sims_ws/install/setup.bash`) before building |

The setuptools warning: on Humble the common workaround is `pip install setuptools==58.2.0`. That is a community answer (answers.ros.org), not an official recommendation. [≥Jazzy: `pip install` into the system Python is blocked by PEP 668 on Ubuntu 24.04, so just ignore the warning]

## Clean (colcon has no `clean`)
```bash
rm -rf build/ install/ log/              # whole ws
rm -rf build/my_pkg install/my_pkg       # one pkg
```

## Pitfalls
- Sourcing only in the terminal where you built: every other terminal still runs the old install or cannot find the package.
- Deleting `install/` while a terminal still has it sourced leaves broken paths. Open a new terminal or re-source.
- Runtime problems (QoS, TF, names) are not build errors. Use [[core-debug-triage]].
