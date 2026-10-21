---
id: urdf-description-package
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "A *_description package: layout, install dirs, visualize launch file, saved .rviz"
domain: urdf
area: workflow
distro: humble
tested: false
audience: dev
summary: "Create <robot>_description (ament_cmake, urdf + xacro deps), install urdf/meshes/rviz/launch, launch robot_state_publisher with xacro Command and RViz2 -d config."
tags: [description package, ament_cmake, CMakeLists, install DIRECTORY, urdf, meshes, rviz, launch, robot_state_publisher, Command, xacro, ParameterValue, rviz2 -d]
see: ["[[core-robot-state-publisher]]", "[[urdf-frames-rviz]]", "[[urdf-joint-state-publisher]]", "[[core-pkg-ament-cmake]]", "[[core-colcon-build]]", "[[urdf-xacro-workflow]]"]
requires: [ros2-core]
version_notes:
  - "humble: wrap the xacro Command in ParameterValue(..., value_type=str) as the official tutorials do — https://docs.ros.org/en/humble/Tutorials/Intermediate/URDF/Using-Xacro-to-Clean-Up-a-URDF-File.html (URDF-V17)"
  - "humble: use_sim_time True only matters when a simulator publishes /clock [verify] (URDF-V49)"
  - "humble: launch files need no executable bit (URDF-V51)"
---
# A *_description package: layout, install dirs, visualize launch file, saved .rviz

**TL;DR** Keep everything that describes a robot in a `<robot>_description` package (ament_cmake, depends on `urdf` and `xacro`): `urdf/`, `meshes/`, `rviz/`, `launch/`, all installed to `share/<pkg>`. A launch file runs robot_state_publisher with the expanded file and RViz2 with a saved config. Generic launch with arguments and the GUI: [[core-robot-state-publisher]].

## Create it
```bash
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_cmake urdfbot_description --dependencies urdf xacro
cd urdfbot_description && mkdir launch rviz urdf meshes
```

`CMakeLists.txt` (the generated file plus the install rule):
```cmake
cmake_minimum_required(VERSION 3.8)
project(urdfbot_description)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(urdf REQUIRED)
find_package(xacro REQUIRED)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

install(
  DIRECTORY urdf rviz launch meshes
  DESTINATION share/${PROJECT_NAME}/
)

ament_package()
```
Rebuild after every change (`colcon build --packages-select urdfbot_description && source install/setup.bash`), or build once with `--symlink-install` so edits to installed files apply directly ([[core-colcon-build]]).

## Visualize launch file
`launch/urdf_visualize_rviz.launch.py`:
```python
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


# this is the function launch system will look for
def generate_launch_description():
    ####### DATA INPUT ##########
    urdf_file = 'urdfbot_simple.urdf'
    # xacro_file = "urdfbot.xacro"
    package_description = "urdfbot_description"
    ####### DATA INPUT END ##########
    print("Fetching URDF ==>")
    robot_desc_path = os.path.join(get_package_share_directory(package_description), "urdf", urdf_file)

    # Robot State Publisher
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher_node',
        emulate_tty=True,
        parameters=[{'use_sim_time': True,  # needed with a simulator (/clock); False for RViz only [verify]
                     'robot_description': ParameterValue(Command(['xacro ', robot_desc_path]), value_type=str)}],
        output="screen")

    # RVIZ Configuration
    rviz_config_dir = os.path.join(get_package_share_directory(package_description), 'rviz', 'urdf_vis.rviz')
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        output='screen',
        name='rviz_node',
        parameters=[{'use_sim_time': True}],
        arguments=['-d', rviz_config_dir])

    # create and return launch description object
    return LaunchDescription([robot_state_publisher_node, rviz_node])
```
- `Command(['xacro ', path])` runs the `xacro` executable at launch time; it processes plain `.urdf` files too, so one launch file serves both. Check what will be published with `xacro <path to urdf>`.
- Without the `rviz_node` the same file only publishes the model (`urdf_visualize.launch.py` in the course); start RViz2 by hand then.
- Run: `ros2 launch urdfbot_description urdf_visualize_rviz.launch.py` plus `ros2 run joint_state_publisher_gui joint_state_publisher_gui` for movable joints ([[urdf-joint-state-publisher]]).
- RViz config: set it up once and save it as `rviz/urdf_vis.rviz` ([[urdf-frames-rviz]]).

## Pitfalls
- `get_package_share_directory` finds the old file → the package was not rebuilt (or not sourced) after the edit.
- Renaming the node (`robot_state_publisher_node`) is fine for RViz; with gz_ros2_control on Humble it must be declared to the plugin (ros2-gazebo skill).
- A launch file does not need `chmod +x`: `ros2 launch` reads it.
