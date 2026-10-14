---
id: core-symlink-install
type: reference
owner: equipo-ros2
updated: 2026-10-14
review_by: 2027-04-12
source: manual
confidentiality: internal
title: "--symlink-install: what is linked, what still needs a rebuild"
domain: core
area: build-run
distro: humble
tested: false
audience: dev
summary: "What colcon build --symlink-install links for ament_python packages (module, data_files), the entry-point wrapper, when to rebuild."
tags: [symlink-install, colcon, ament_python, data_files, entry point, develop, build folder, install folder, No executable found]
see: ["[[core-colcon-build]]", "[[core-pkg-setup-py-fields]]", "[[core-learn-inter-unit2-build]]", "[[core-colcon-errors]]"]
requires: []
version_notes:
  - "all distros: depends on colcon-core, not on ROS; >= 0.16 symlinks data_files too (Jammy ROS repo: 0.21.3); older colcon copied them — https://github.com/colcon/colcon-core/pull/592 (V81)"
---
# --symlink-install: what is linked, what still needs a rebuild

**TL;DR** `colcon build --symlink-install` makes an ament_python package run from `src/`: the Python module is linked, and with colcon-core ≥ 0.16 every `data_files` entry (launch, params, RViz) is a symlink in `install/` too. Edits to existing files apply without a rebuild. A **new** file, script or entry point still needs `colcon build` (the `glob()` runs at build time).

## What is linked (current colcon)
| File | Without `--symlink-install` | With it |
|---|---|---|
| Python module (`build_test_pkg/`) | copied through `build/<pkg>/build/lib/` into `install/<pkg>/lib/python3.10/site-packages/` | `build/<pkg>/<pkg> -> src/.../<pkg>/` |
| `data_files` (launch, yaml) in `install/<pkg>/share/<pkg>/` | copies | symlinks to `src/` [colcon-core ≥ 0.16] |
| entry-point wrapper `install/<pkg>/lib/<pkg>/<exe>` | generated file | generated file (not a link) |
| `setup.py`, `setup.cfg` in `build/<pkg>/` | — | symlinks |
For ament_cmake packages, `--symlink-install` also turns the `install()` calls into symlinks.

[Older colcon, as in the course (2022)] The experiment below found hard copies in `install/` even with the flag: launch and params files were only linked inside `build/`, so editing them in `src/` did nothing until the next build. Check your version: `ls -l install/<pkg>/share/<pkg>/launch/` shows `->` arrows when they are linked.

## The experiment (package `build_test_pkg`, files in [[core-learn-inter-unit2-build]])
```bash
# Now we remove all the build and install folders and compile
cd ~/ros2_ws/
rm -rf build install log
colcon build --symlink-install --packages-select build_test_pkg
source install/setup.bash
```
```bash
cd ~/ros2_ws/
ll install                                       # setup.bash, local_setup.*, build_test_pkg/ ...
ll build/build_test_pkg                          # with the flag: build_test_pkg -> src/..., launch/, params_files/, setup.cfg ->, setup.py ->
ll build/build_test_pkg/launch/                  # test.launch.py -> /home/user/ros2_ws/src/.../launch/test.launch.py
ll build/build_test_pkg/params_files/            # params.yaml -> /home/user/ros2_ws/src/.../params_files/params.yaml
ls build/build_test_pkg/build/lib/build_test_pkg/   # without the flag: __init__.py  script1.py (hard copy)
```

## The entry-point wrapper
`ros2 run build_test_pkg script1_exe` executes the script that setuptools generated from the entry point:
```bash
cat install/build_test_pkg/lib/build_test_pkg/script1_exe
```
```python
#!/usr/bin/python3
# EASY-INSTALL-ENTRY-SCRIPT: 'build-test-pkg','console_scripts','script1_exe'
__requires__ = 'build-test-pkg'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('build-test-pkg', 'console_scripts', 'script1_exe')()
    )
```
Without the flag it imports the installed copy, so source edits need a rebuild. With the flag it reaches `src/` through the module link, so `script1.py` edits apply at once. Delete the wrapper and nothing works:
```bash
cd ~/ros2_ws/install/build_test_pkg/lib/build_test_pkg
rm -rf script1_exe
ros2 run build_test_pkg script1_exe
```
```text
No executable found
```
The wrapper text depends on the setuptools version of your Ubuntu.

## Pitfalls
- New launch file or new entry point → `colcon build` and `source install/setup.bash`, with or without the flag.
- When you switch between symlink and copy builds, delete `build/ install/ log/` first, as above.
- `install/` with symlinks cannot be copied to another machine or Docker stage ([[core-colcon-build]]).
