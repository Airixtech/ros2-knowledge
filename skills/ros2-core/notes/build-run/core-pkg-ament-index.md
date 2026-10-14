---
id: core-pkg-ament-index
type: reference
owner: equipo-ros2
updated: 2026-10-14
review_by: 2027-04-12
source: manual
confidentiality: internal
title: "resource/ marker and the ament resource index"
domain: core
area: build-run
distro: humble
tested: false
audience: dev
summary: "Why every package has an empty resource/<pkg> file: the ament resource index marker; 'Package not found' when it is missing."
tags: [resource folder, ament_index, resource_index, package marker, Package not found, colcon-ros, ament_python]
see: ["[[core-pkg-setup-py-fields]]", "[[core-pkg-ament-python]]", "[[core-launch-testing]]", "[[core-colcon-errors]]"]
requires: []
version_notes:
  - "all: colcon-ros still installs the marker and package.xml implicitly when setup.py omits them, with a warning that the fallback will be removed — https://github.com/colcon/colcon-ros/blob/master/colcon_ros/task/ament_python/build.py (V82)"
---
# resource/ marker and the ament resource index

**TL;DR** Every generated package has two extra folders, `resource/` and `test/`. `resource/<pkg>` is an **empty** file: installed as `install/<pkg>/share/ament_index/resource_index/packages/<pkg>`, it is how ROS 2 tools know the package is installed. Keep its `data_files` line in `setup.py`. Tests: [[core-launch-testing]].

## How the index works
```bash
# Compile with or without softlink, doesn't matter
cd ~/ros2_ws/
rm -rf build install log
colcon build --symlink-install --packages-select build_test_pkg
source install/setup.bash
ls src/build_test_pkg/resource/                                     # build_test_pkg (empty file)
ls install/build_test_pkg/share/ament_index/resource_index/packages/ # build_test_pkg
```
Remove the installed marker and ROS no longer finds the package:
```bash
cd ~/ros2_ws/
rm -rf install/build_test_pkg/share/ament_index/resource_index/packages/build_test_pkg
ros2 run build_test_pkg script1_exe
```
```text
Package 'build_test_pkg' not found
```
The next build installs it again, with nothing to edit:
```bash
cd ~/ros2_ws/
colcon build --symlink-install --packages-select build_test_pkg
source install/setup.bash
ros2 run build_test_pkg script1_exe
```

## The setup.py line
```python
('share/ament_index/resource_index/packages', ['resource/' + package_name]),
```
This line installs the marker. If it (or the `package.xml` line) is missing, colcon-ros still installs both and prints a warning that this implicit fallback will be removed in the future: keep both lines.

## Why an index
- The index "registers" resources by folder: tools read one known directory instead of crawling the disk for packages.
- That makes lookups fast and avoids collisions between same-name packages.
- Other resource types use the same mechanism (for example the plugin descriptions registered by pluginlib).

## Pitfalls
- `Package '<pkg>' not found` right after a build → you did not source `install/setup.bash`, or the marker is missing ([[core-colcon-errors]]).
- The marker file name must equal the package name.
