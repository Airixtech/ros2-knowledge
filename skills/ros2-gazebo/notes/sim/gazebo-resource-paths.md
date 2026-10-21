---
id: gazebo-resource-paths
type: reference
owner: equipo-ros2
updated: 2026-10-21
review_by: 2027-04-19
source: manual
confidentiality: internal
title: "Gazebo resource path: GZ_SIM_RESOURCE_PATH, package:// and model://, package.xml export, env hook"
domain: gazebo
area: sim
distro: jazzy
tested: false
audience: dev
summary: "How Gazebo finds meshes and models: GZ_SIM_RESOURCE_PATH, package:// and model://, the course block, package.xml export, env hook."
tags: [GZ_SIM_RESOURCE_PATH, IGN_GAZEBO_RESOURCE_PATH, resource path, package://, model://, meshes, gazebo_model_path, ament_environment_hooks, dsv, ros_gz_project_template]
see: ["[[gazebo-start-sim]]", "[[gazebo-world-sdf]]", "[[gazebo-spawn-urdf]]", "[[urdf-links]]", "[[gazebo-migration-fortress]]"]
requires: [ros2-core, ros2-urdf]
version_notes:
  - "humble/fortress: current Fortress reads IGN_GAZEBO_RESOURCE_PATH and also GZ_SIM_RESOURCE_PATH — https://github.com/gazebosim/gz-sim/blob/ign-gazebo6/include/gz/sim/Util.hh (GZ-V11)"
  - "jazzy/harmonic: gz_sim.launch.py adds the <gazebo_ros gazebo_model_path> exports of all packages to GZ_SIM_RESOURCE_PATH (humble too) — https://github.com/gazebosim/ros_gz/blob/jazzy/ros_gz_sim/launch/gz_sim.launch.py.in (GZ-V11)"
  - "jazzy/harmonic: the official template sets the variable with an ament environment hook — https://github.com/gazebosim/ros_gz_project_template (GZ-V11)"
---
# Gazebo resource path: GZ_SIM_RESOURCE_PATH, package:// and model://, package.xml export, env hook

**TL;DR** Gazebo is not a ROS node: it does not know the ament index. It finds a mesh (`package://my_box_bot_description/meshes/cute_cube.dae`) or a model folder (`model://box_room`) only if the folder that contains it is listed in `GZ_SIM_RESOURCE_PATH`, set **before** Gazebo starts.

## What to put on the path
| Entry | Makes this work |
|---|---|
| `<install>/share` of a package (`get_package_prefix(pkg) + "/share"`) | `package://<pkg>/…` paths of the URDF meshes |
| `<share>/<pkg>/models` | `model://<model_name>` includes of the world |
| `<share>/<pkg>/meshes` | added by the course too; `package://` paths need only the `share` entry |

The course's `start_world.launch.py` appends these four paths for `my_box_bot_gazebo` and `my_box_bot_description` to `os.environ["GZ_SIM_RESOURCE_PATH"]` (or creates it) before including `gz_sim.launch.py` ([[gazebo-start-sim]]). It worked in unit 4 because `CMakeLists.txt` installs `models/` into the package's share folder and that folder is on the path.

## Official alternatives to editing os.environ
- **package.xml export**, read by `gz_sim.launch.py` (Humble and Jazzy):
  ```xml
  <export>
    <build_type>ament_cmake</build_type>
    <gazebo_ros gazebo_model_path="${prefix}/../"/>   <!-- ${prefix} = the package's share directory -->
  </export>
  ```
  `${prefix}/../` is the `share` folder, so `package://` and `model://` both resolve; install the folders from `CMakeLists.txt`.
- **Environment hook** (ros_gz_project_template): a file `hooks/<pkg>.dsv.in` with
  `prepend-non-duplicate;GZ_SIM_RESOURCE_PATH;share;@CMAKE_INSTALL_PREFIX@/share`
  and `ament_environment_hooks("${CMAKE_CURRENT_SOURCE_DIR}/hooks/${PROJECT_NAME}.dsv.in")` in `CMakeLists.txt`. Sourcing the workspace then sets the variable for every terminal, also for `gz sim` started by hand.

## Pitfalls
- Meshes white or missing, "Unable to find uri[model://…]" → the folder is not on the path, or it was added after Gazebo started.
- Path added but still missing → the folder is not installed (check `install/<pkg>/share/<pkg>/`), or the workspace is not sourced.
- [Humble + Fortress] old Fortress tutorials use `IGN_GAZEBO_RESOURCE_PATH`; a current Fortress reads both names ([[gazebo-migration-fortress]]).
