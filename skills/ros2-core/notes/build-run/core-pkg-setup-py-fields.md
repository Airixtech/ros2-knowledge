---
id: core-pkg-setup-py-fields
type: reference
owner: equipo-ros2
updated: 2026-10-14
review_by: 2027-04-12
source: manual
confidentiality: internal
title: "setup.py and setup.cfg of ament_python: fields, entry points, data_files"
domain: core
area: build-run
distro: humble
tested: false
audience: dev
summary: "setuptools keywords of an ament_python setup.py, entry point syntax and naming, data_files destinations, glob(), setup.cfg."
tags: [setup.py, setuptools, entry_points, console_scripts, data_files, glob, setup.cfg, install_requires, zip_safe]
see: ["[[core-pkg-ament-python]]", "[[core-symlink-install]]", "[[core-pkg-ament-index]]", "[[core-launch-basics]]"]
requires: []
version_notes:
  - "humble: newer templates use extras_require={'test': ['pytest']} instead of tests_require — https://github.com/ros2/ros2cli/blob/humble/ros2pkg/ros2pkg/resource/ament_python/setup.py.em (V07)"
  - "all: setup.cfg keys with underscores (script_dir, install_scripts) — https://github.com/ros2/ros2cli/blob/humble/ros2pkg/ros2pkg/resource/ament_python/setup.cfg.em (V08)"
---
# setup.py and setup.cfg of ament_python: fields, entry points, data_files

**TL;DR** `setup.py` calls Python's `setuptools.setup()`: it is the ament_python counterpart of a C++ `CMakeLists.txt`. `entry_points` turns `main()` functions into executables, and `data_files` copies launch/config files into `install/<pkg>/share/<pkg>/`. The canonical template is in [[core-pkg-ament-python]].

## A setup.py with launch files installed
```python
from setuptools import setup
import os
from glob import glob

package_name = 'my_package'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py'))
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='somebody very awesome',
    maintainer_email='user@user.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'simple = my_package.simple:main'
        ],
    },
)
```
[Humble] `tests_require` comes from older templates; the current one uses `extras_require={'test': ['pytest']}`. Both build.

## Entry points
`'<executable_name> = <package_name>.<script_name>:main'`: run `main()` of `<script_name>.py` (the file name without `.py`) inside the Python module of the package. One convention keeps the executable and the file apart: add `_exe` to the file name (`'simple_exe = my_package.simple:main'`). Launch files and `ros2 run` use the **executable** name.

## data_files
Each tuple is `(destination relative to install/<pkg>, [source files relative to the package])`. The line above installs every `launch/*.launch.py` into `~/ros2_ws/install/my_package/share/my_package/launch/`, where `ros2 launch` finds it. `glob()` matches a shell pattern when `colcon build` runs:
```python
import glob
# in a folder with test0.py, test7, test11.py and bob.py this prints only test0.py:
# [0-9] is exactly one digit, and test7 has no .py
for py in glob.glob("test[0-9].py"):
    print(py)
```
`glob('launch/*')` installs every file of the folder (Python, XML and YAML launch files, [[core-launch-xml-yaml]]).

## setuptools keywords
| Keyword | Meaning |
|---|---|
| `name` (essential) | package name |
| `version` | package version |
| `data_files` (essential) | files to install: `package.xml`, `launch/`, `config/`… |
| `install_requires` (essential) | other distributions needed; always contains `setuptools` |
| `zip_safe` | the project can be installed and run from a zip file |
| `author`, `author_email`, `maintainer`, `maintainer_email` | contact data |
| `keywords`, `classifiers` | descriptive metadata, package categories |
| `description`, `license` | one-line description, license |
| `entry_points` (essential) | group → entry points; `console_scripts` makes `ros2 run <pkg> <exe>` work |

ROS 2 uses only a fraction of setuptools: [setuptools documentation](https://setuptools.pypa.io/en/latest/).

## setup.cfg
```ini
[develop]
script_dir=$base/lib/my_package
[install]
install_scripts=$base/lib/my_package
```
`$base` is `~/ros2_ws/install/my_package`: the entry point scripts land in `install/my_package/lib/my_package/`, where `ros2 run` looks for them.

## Pitfalls
- A new entry point or a new file in `data_files` needs `colcon build` and a re-source, even with `--symlink-install` ([[core-symlink-install]]).
- Removing the `resource_index` or `package.xml` lines only works because colcon-ros installs them implicitly, with a warning ([[core-pkg-ament-index]]).
