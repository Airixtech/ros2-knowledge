---
id: perception-python-deps
type: reference
owner: equipo-ros2
updated: 2026-10-27
review_by: 2027-04-25
source: manual
confidentiality: internal
title: "Python perception packages: data_files for models and cascades, share paths, installing OpenCV, PCL, YOLO libraries"
domain: perception
area: setup
distro: humble
tested: false
audience: dev
summary: "setup.py data_files for cascades, photos, .pt models; share paths; rosdep keys; apt, pip, venv; numpy<2 with cv_bridge; PEP 668."
tags: [setup.py, data_files, glob, entry_points, console_scripts, get_package_share_directory, package.xml, rosdep, python3-opencv, cv_bridge, ultralytics, numpy<2, PEP 668, venv, externally-managed-environment, dlib, imutils]
see: ["[[core-pkg-setup-py-fields]]", "[[core-pkg-dependencies]]", "[[perception-pcl-python]]", "[[perception-humble-to-jazzy]]"]
requires: [ros2-core]
version_notes:
  - "rosdep keys: python3-opencv, python3-numpy, python3-ultralytics-pip, python3-imutils-pip, python3-dlib-pip; none for face_recognition or python-pcl — https://github.com/ros/rosdistro/blob/master/rosdep/python.yaml (PERC-V41)"
  - "ultralytics 8.4.190 requires numpy>=1.23.0 and opencv-python>=4.7.0; Ubuntu 22.04 has numpy 1.21.5, 24.04 1.26.4, 26.04 2.3.5; 'Wheels built against NumPy 1.xx will not work with NumPy 2.0 or later' — https://github.com/ultralytics/ultralytics/blob/main/pyproject.toml , https://numpy.org/doc/stable/dev/depending_on_numpy.html (PERC-V39) [verify]"
  - "jazzy/kilted (24.04) and lyrical (26.04): EXTERNALLY-MANAGED marker (PEP 668); pip ≥23.0 refuses system and --user installs; humble (22.04): no marker, pip 22.0.2 — https://peps.python.org/pep-0668/ , https://docs.ros.org/en/jazzy/How-To-Guides/Using-Python-Packages.html (PERC-V40)"
  - "course: model paths and the segmentation output folder were absolute paths of the course machine (PERC-V33)"
---
# Python perception packages: data files and libraries

**TL;DR** Everything a node loads at run time (cascades, reference photos, `.pt` models) goes into the package's `data/` folder, is installed by `data_files` in `setup.py`, and is found with `get_package_share_directory('<pkg>')`. Libraries: apt or rosdep keys first; pip only where needed, with `"numpy<2"` on Humble and Jazzy, and inside a virtualenv on Ubuntu 24.04 and later.

## `setup.py` of the course's `hri` package
Update it before running any node of the package: `data_files` copies the listed folders to `install/hri/share/hri/`, where the nodes look for them at run time.
```python
from setuptools import setup
from glob import glob

package_name = 'hri'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Include the data directory
        (f'share/{package_name}/data', glob('data/*.*')),
        # Include the data/person1 directory
        (f'share/{package_name}/data/person1', glob('data/person1/*.*')),
        # Include the data/mona_lisa directory
        (f'share/{package_name}/data/mona_lisa', glob('data/mona_lisa/*.*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='user',
    maintainer_email='user@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'face_detection = hri.face_detection:main',
            'eye_detection = hri.eye_detection:main',
            'face_recognition = hri.face_recognition:main',
            'human_tracking = hri.human_tracking:main'
        ],
    },
)
```
`glob('data/*.*')` takes the files of `data/` (not its sub-folders, hence one entry per sub-folder). The other course packages need the same two parts: a `console_scripts` line per node (`ros2 run <pkg> <name>`), and for `advanced_perception` its models: `(f'share/{package_name}/data', glob('data/*.pt'))`. Field reference: [[core-pkg-setup-py-fields]].

In the node:
```python
data_folder = os.path.join(get_package_share_directory('hri'), 'data')
```
Never an absolute path of one machine (the course's YOLO nodes had one, PERC-V33); files the node **writes** (the segmentation image) go to a folder given by a parameter or under `~`, not to `share/`.

## Libraries and how to install them
| Library | Import | Route | rosdep key (`package.xml`) |
|---|---|---|---|
| OpenCV | `cv2` | apt `python3-opencv` | `python3-opencv` |
| cv_bridge | `cv_bridge` | ROS package | `cv_bridge` |
| NumPy | `numpy` | apt `python3-numpy` | `python3-numpy` |
| sensor_msgs_py, tf2_sensor_msgs | | ROS packages | `sensor_msgs_py`, `tf2_sensor_msgs` |
| python-pcl | `pcl` | apt `python3-pcl`, **Humble only** ([[perception-pcl-python]]) | none |
| Haar cascades | | apt `opencv-data` (`/usr/share/opencv4/haarcascades/`) or the package's `data/` | none |
| imutils | `imutils` | pip | `python3-imutils-pip` |
| face_recognition (+ dlib) | `face_recognition` | pip; dlib with Python bindings first | `python3-dlib-pip`; none for face_recognition |
| Ultralytics YOLO | `ultralytics` | pip (pulls `torch`, `opencv-python`) | `python3-ultralytics-pip` |

With keys in `package.xml`, `rosdep install -yr --from-paths src` installs apt and pip dependencies together ([[core-pkg-dependencies]]).

### pip on a ROS machine
- **NumPy**: Ultralytics needs `numpy>=1.23`, Ubuntu 22.04 ships 1.21.5, so pip installs a newer one. Modules built against NumPy 1.x (cv_bridge's `cv_bridge_boost`, apt's OpenCV, `python3-pcl`) do not work with NumPy 2: keep it below 2 (1.x minor versions stay compatible) (PERC-V39 `[verify]`):
```bash
python3 -m pip install ultralytics "numpy<2"
```
- **Ubuntu 24.04 / 26.04** (Jazzy, Kilted, Lyrical): the system Python is "externally managed" (PEP 668): `pip install` and `pip install --user` stop with `externally-managed-environment`. Use the official ROS 2 route, a virtualenv made with the system interpreter (PERC-V40):
```bash
mkdir -p ~/colcon_venv/src
cd ~/colcon_venv/
virtualenv -p python3 ./venv  # Make a virtual env and activate it
source ./venv/bin/activate
touch ./venv/COLCON_IGNORE  # Make sure that colcon does not try to build the venv
python3 -m pip install ultralytics "numpy<2"
source /opt/ros/jazzy/setup.bash
colcon build
```
Ubuntu 24.04's apt NumPy is 1.26.4, so the `"numpy<2"` pin still matters there; on Lyrical (26.04) the system NumPy is already 2.3.5 and cv_bridge is built against it.
- Conda environments use another interpreter than the ROS 2 binaries and are likely incompatible (official guide).

## Pitfalls
- `FileNotFoundError` / "Cascade xml file not found" after editing `data/` → rebuild: `glob()` lists the files when `colcon build` runs.
- Running a node file directly (`python3 face_recognition.py`) puts its own folder first on `sys.path`, so `import face_recognition` imports the node itself; start it with `ros2 run hri face_recognition`.
- cv_bridge, `cv2` or `pcl` fail to import (or crash) right after a pip install → check `python3 -c "import numpy; print(numpy.__version__)"`; if it is 2.x on Humble or Jazzy, `python3 -m pip install "numpy<2"` (PERC-V39 `[verify]`).
