---
id: gazebo-start-sim
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "Start Gazebo from launch: gz_sim.launch.py gz_args, resource path variable"
domain: gazebo
area: sim
distro: jazzy
tested: false
audience: dev
summary: "Gazebo package layout, start_world.launch.py including ros_gz_sim gz_sim.launch.py with gz_args -r and a world, GZ_SIM_RESOURCE_PATH, package.xml export, env hook."
tags: [gz_sim.launch.py, gz_args, ros_gz_sim, start_world, GZ_SIM_RESOURCE_PATH, IGN_GAZEBO_RESOURCE_PATH, gazebo_model_path, ament_environment_hooks, model://, SetParameter, use_sim_time]
see: ["[[gazebo-world-sdf]]", "[[gazebo-spawn-urdf]]", "[[gazebo-sim-overview]]", "[[core-launch-args-include]]", "[[core-time-timers]]"]
requires: [ros2-core, ros2-urdf]
version_notes:
  - "humble: the same gz_sim.launch.py runs 'ign gazebo' for Fortress; current Fortress reads IGN_GAZEBO_RESOURCE_PATH and also GZ_SIM_RESOURCE_PATH — https://github.com/gazebosim/ros_gz/blob/humble/ros_gz_sim/launch/gz_sim.launch.py.in , https://github.com/gazebosim/gz-sim/blob/ign-gazebo6/include/gz/sim/Util.hh (GZ-V10, GZ-V11)"
  - "jazzy: gz_sim.launch.py adds the <gazebo_ros gazebo_model_path> exports of all packages to GZ_SIM_RESOURCE_PATH — https://github.com/gazebosim/ros_gz/blob/jazzy/ros_gz_sim/launch/gz_sim.launch.py.in (GZ-V11)"
  - "jazzy: SetParameter(use_sim_time) applies to the ROS nodes started after it, not to Gazebo; bridge /clock (GZ-V27)"
---
# Start Gazebo from launch: gz_sim.launch.py gz_args, resource path variable

**TL;DR** Keep simulation files in their own package (`<robot>_gazebo` with `launch/`, `worlds/`, `models/`). Start Gazebo by including `ros_gz_sim`'s `gz_sim.launch.py` with `gz_args` = `-r` (run, not paused) + the world file. Gazebo finds meshes and `model://` folders only through `GZ_SIM_RESOURCE_PATH`.

## Package
```bash
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_cmake my_box_bot_gazebo --dependencies rclpy my_box_bot_description
cd my_box_bot_gazebo && mkdir launch worlds models
```
Install `launch worlds models` in `CMakeLists.txt` (`install(DIRECTORY launch worlds models DESTINATION share/${PROJECT_NAME}/)`).

## start_world.launch.py
```python
import os
from ament_index_python.packages import get_package_prefix, get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.substitutions import PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import SetParameter


# ROS2 Launch System will look for this function definition #
def generate_launch_description():
    # Get Package Directory #
    pkg_box_bot_gazebo = get_package_share_directory('my_box_bot_gazebo')
    pkg_box_bot_description = get_package_share_directory('my_box_bot_description')
    gz_sim_pkg = get_package_share_directory("ros_gz_sim")

    # Set the Path to Robot Mesh Models for Loading in Gazebo Sim #
    # NOTE: Do this BEFORE launching Gazebo Sim #
    install_dir_path_gazebo = (get_package_prefix('my_box_bot_gazebo') + "/share")
    install_dir_path_description = (get_package_prefix('my_box_bot_description') + "/share")
    gazebo_models_path = os.path.join(pkg_box_bot_gazebo, "models")
    description_meshes_path = os.path.join(pkg_box_bot_description, "meshes")
    gazebo_resource_paths = [install_dir_path_gazebo, install_dir_path_description,
                             gazebo_models_path, description_meshes_path]
    if "GZ_SIM_RESOURCE_PATH" in os.environ:
        for resource_path in gazebo_resource_paths:
            if resource_path not in os.environ["GZ_SIM_RESOURCE_PATH"]:
                os.environ["GZ_SIM_RESOURCE_PATH"] += (':' + resource_path)
    else:
        os.environ["GZ_SIM_RESOURCE_PATH"] = (':'.join(gazebo_resource_paths))

    # Setup to launch the simulator and Gazebo world
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(gz_sim_pkg, 'launch', 'gz_sim.launch.py')),
        launch_arguments={'gz_args': ['-r ',  # <-- start unpaused
                                      PathJoinSubstitution([pkg_box_bot_gazebo, 'worlds', 'box_bot_empty.world'])]}.items(),
    )

    # Create and Return the Launch Description Object #
    return LaunchDescription([
        # Sets use_sim_time for all nodes started below (Gazebo itself is not a ROS node) #
        SetParameter(name="use_sim_time", value=True),
        gz_sim,
    ])
```
- `<pkg>/share` (the install prefix's `share`) lets `package://my_box_bot_description/meshes/…` resolve; `models/` lets the world use `model://box_room`.
- First version of this file (before a robot is spawned) needs only the two `my_box_bot_gazebo` paths.
- Run: `colcon build && source install/setup.bash && ros2 launch my_box_bot_gazebo start_world.launch.py`.
- Other arguments of `gz_sim.launch.py`: `gz_version`, `on_exit_shutdown` (stop the launch when Gazebo closes), `debugger`.

## Official alternatives to editing os.environ
- **package.xml export**, read by `gz_sim.launch.py` (Humble and Jazzy):
  ```xml
  <export>
    <build_type>ament_cmake</build_type>
    <gazebo_ros gazebo_model_path="${prefix}/../"/>   <!-- ${prefix} = the package's share directory -->
  </export>
  ```
- **Environment hook** (ros_gz_project_template): a file `hooks/<pkg>.dsv.in` with `prepend-non-duplicate;GZ_SIM_RESOURCE_PATH;share;@CMAKE_INSTALL_PREFIX@/share` and `ament_environment_hooks("${CMAKE_CURRENT_SOURCE_DIR}/hooks/${PROJECT_NAME}.dsv.in")` in `CMakeLists.txt`; sourcing the workspace then sets the variable.

## Pitfalls
- Meshes white or missing, "Unable to find uri[model://…]" → the folder is not in `GZ_SIM_RESOURCE_PATH` (set it before Gazebo starts).
- `-r` missing → Gazebo starts paused; press play or nothing moves.
- [Humble] the variable name in old Fortress tutorials is `IGN_GAZEBO_RESOURCE_PATH`; a current Fortress reads both.
