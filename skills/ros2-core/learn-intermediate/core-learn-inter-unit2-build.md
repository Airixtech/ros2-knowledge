---
id: core-learn-inter-unit2-build
type: reference
owner: equipo-ros2
updated: 2026-10-14
review_by: 2027-04-12
source: manual
confidentiality: internal
title: "Intermediate Unit 2: build_test_pkg experiment files"
domain: core
area: learn-intermediate
distro: humble
tested: false
audience: students
summary: "Unit 2 package build_test_pkg: params.yaml, test launch, script1.py that reads YAML from share, minimal setup.py, run output."
tags: [course, unit 2, build_test_pkg, symlink-install, params.yaml, get_package_share_directory, yaml.safe_load, students]
see: ["[[core-symlink-install]]", "[[core-pkg-ament-index]]", "[[core-launch-testing]]", "[[core-learn-inter-start-here]]"]
requires: []
version_notes:
  - "all: with colcon-core >= 0.16 the data files of this package are symlinked in install/ (the course saw copies) — https://github.com/colcon/colcon-core/pull/592 (V81)"
---
# Intermediate Unit 2: build_test_pkg experiment files

**TL;DR** `build_test_pkg` is the package of the `--symlink-install` experiment ([[core-symlink-install]]), of the ament index test ([[core-pkg-ament-index]]) and of the launch test ([[core-launch-testing]]). `script1.py` finds `params_files/params.yaml` in the installed share folder and prints its content.

## Create it
```bash
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_python build_test_pkg --dependencies rclpy
cd build_test_pkg
mkdir params_files
touch params_files/params.yaml
mkdir launch
touch launch/test.launch.py
touch build_test_pkg/script1.py
```

## params_files/params.yaml
```yaml
robot_name: "Marceline"
serial_num: 123456789
```

## launch/test.launch.py
```python
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='build_test_pkg',
            executable='script1_exe',
            output='screen'),
    ])
```

## build_test_pkg/script1.py
```python
import rclpy
import os
from ament_index_python.packages import get_package_share_directory
import yaml


def open_yaml_file(yaml_path):
    with open(yaml_path, "r") as stream:
        contents = None
        try:
            contents = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
        print(contents)
    return contents


def main(args=None):
    # initialize the ROS communication
    rclpy.init(args=args)
    package_description = "build_test_pkg"
    yaml_file_path = os.path.join(get_package_share_directory(package_description), "params_files", "params.yaml")
    print("Path to files=="+str(yaml_file_path))
    yaml_data = open_yaml_file(yaml_file_path)
    print("YAML DATA XXXXX="+str(yaml_data))
    rclpy.shutdown()


if __name__ == '__main__':
    main()  # call the main function
```

## setup.py (minimum on purpose)
```python
from setuptools import setup
import os
from glob import glob

package_name = 'build_test_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        # ('share/ament_index/resource_index/packages',
        #     ['resource/' + package_name]),
        # ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'params_files'), glob('params_files/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='your_name',
    maintainer_email='you@example.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'script1_exe = build_test_pkg.script1:main'
        ],
    },
)
```
Only the launch and `params_files` folders are listed in `data_files`. The `package.xml` and the `resource/build_test_pkg` marker lines are commented out to keep the minimum number of files: colcon-ros installs them anyway, with a warning ([[core-pkg-ament-index]]).

## Run
```bash
cd ~/ros2_ws/
rm -rf build install log
colcon build --symlink-install --packages-select build_test_pkg
source install/setup.bash
ros2 run build_test_pkg script1_exe
```
```text
Path to files==/home/user/ros2_ws/install/build_test_pkg/share/build_test_pkg/params_files/params.yaml
{'robot_name': 'Marceline', 'serial_num': 123456789}
YAML DATA YYYY={'robot_name': 'Marceline', 'serial_num': 123456789}
```
The course output shows `YAML DATA YYYY`; the code above prints `XXXXX` (the text changed between the course versions).

## Earlier Unit 2 examples (recap)
- Example 2.1: create `my_package` with `ros2 pkg create --build-type ament_python my_package --dependencies rclpy`, then build and source ([[core-pkg-workspace]]).
- Example 2.2: `colcon build --packages-select my_package` from `~/ros2_ws`, never from `src/` ([[core-colcon-build]]).
- Example 2.3: `ros2 pkg list | grep my_package` confirms it is installed.
