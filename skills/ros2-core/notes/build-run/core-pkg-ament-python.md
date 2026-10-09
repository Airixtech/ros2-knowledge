---
id: core-pkg-ament-python
title: "ament_python package: layout, setup.py, setup.cfg"
domain: core
area: build-run
distro: humble
tested: false
audience: dev
summary: "Canonical ament_python layout, setup.py template (entry points, data_files for launch/config) and setup.cfg."
tags: [ament_python, setup.py, setup.cfg, entry_points, data_files, console_scripts]
see: ["[[core-pkg-workspace]]", "[[core-launch-basics]]", "[[core-colcon-errors]]", "[[core-testing-ci-docker]]"]
requires: []
version_notes:
  - "humble: ros2 pkg create template switched tests_require -> extras_require (ros2cli#1103, 2025-09) — https://github.com/ros2/ros2cli/blob/humble/ros2pkg/ros2pkg/resource/ament_python/setup.py.em (V07)"
  - "all: setup.cfg keys use underscores (script_dir); dash form script-dir triggers setuptools deprecation — https://github.com/ros2/ros2cli/blob/humble/ros2pkg/ros2pkg/resource/ament_python/setup.cfg.em (V08)"
---
# ament_python package: layout, setup.py, setup.cfg

**TL;DR** The Python module has the same name as the package. Every executable is a `console_scripts` entry point, and every launch/config file must be listed in `data_files`. After adding either one, rebuild and re-source.

## Layout
```
my_pkg/
├── package.xml
├── setup.py
├── setup.cfg            # installs exes into lib/my_pkg (leave as generated)
├── resource/my_pkg      # empty marker file
├── my_pkg/              # Python module = SAME name as package
│   ├── __init__.py
│   └── my_node.py
├── launch/  config/  test/
```

## setup.py (canonical template)
```python
import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'my_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        # add urdf/, rviz/, meshes/ the same way
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='user',
    maintainer_email='user@todo.todo',
    description='TODO',
    license='Apache-2.0',
    extras_require={'test': ['pytest']},
    entry_points={
        'console_scripts': [
            # '<executable_name> = <python_module>.<file_without_py>:<function>'
            'my_node = my_pkg.my_node:main',
            'my_node_alt = my_pkg.my_node:main_alt',   # several entry points may share a file
        ],
    },
)
```
Run it with `ros2 run my_pkg my_node`. In the entry point path, `.` separates folders and `:` comes before the function.
A new entry point or a new data file ⇒ rebuild + re-source (even with `--symlink-install`).
[Humble] Packages generated before Sept 2025 have `tests_require=['pytest']` instead of `extras_require`. That still builds on Humble; the current template uses `extras_require`.

## setup.cfg (as generated)
```ini
[develop]
script_dir=$base/lib/my_pkg
[install]
install_scripts=$base/lib/my_pkg
```
This is what lets `ros2 run` find the executables in `lib/<pkg>`. Old templates used `script-dir` / `install-scripts` (dashes), which make setuptools print a deprecation warning. Rename them to underscores.

## Pitfalls
- `No executable found` → the entry point is missing or misspelled, or you did not rebuild and re-source ([[core-colcon-errors]]).
- A launch file that is not in `data_files` is not installed, so `ros2 launch` cannot find it ([[core-launch-basics]]).
- The Python module folder name differs from `package_name` → `ModuleNotFoundError` at run time.
