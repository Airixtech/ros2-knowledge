---
id: gazebo-migration-fortress
type: reference
owner: equipo-ros2
updated: 2026-10-21
review_by: 2027-04-19
source: manual
confidentiality: internal
title: "Humble + Fortress: names, packages, env vars, and the official Humble sources"
domain: gazebo
area: migration
distro: jazzy
tested: false
audience: dev
summary: "Humble with Gazebo Fortress: ign commands, env var, plugin and message names, robot_param_node, install, official Humble sources."
tags: [humble, fortress, ignition, ign gazebo, ign topic, IGN_GAZEBO_RESOURCE_PATH, ignition-gazebo, ignition.msgs, ignition_frame_id, ros-humble-ros-gz, gz_ros2_control humble, robot_param_node, ros-humble-ros-gzharmonic]
see: ["[[gazebo-sim-overview]]", "[[gazebo-resource-paths]]", "[[core-gazebo-bridge]]", "[[gazebo-ros2-control-urdf]]", "[[gazebo-migration-jetty]]"]
requires: [ros2-core, ros2-urdf]
version_notes:
  - "humble/fortress: Fortress is the official pairing (packages.ros.org), EOL May 2027 — https://github.com/gazebosim/ros_gz/blob/humble/README.md , https://gazebosim.org/docs/latest/releases/ (GZ-V45)"
  - "humble/fortress: current Fortress translates gz-sim plugin file names, registers gz::sim::systems aliases (NavSat from 6.18.0) and reads GZ_SIM_RESOURCE_PATH — https://github.com/gazebosim/gz-sim/blob/ign-gazebo6/src/SystemLoader.cc (GZ-V11, GZ-V12)"
  - "humble/fortress: gz_ros2_control reads robot_description from the parameter of node robot_state_publisher — https://github.com/ros-controls/gz_ros2_control/blob/humble/doc/index.rst (GZ-V29)"
  - "humble/fortress: Fortress sensors read ignition_frame_id and gz_frame_id — https://github.com/gazebosim/gz-sensors/blob/ign-sensors6/src/Sensor.cc (GZ-V36)"
---
# Humble + Fortress: names, packages, env vars, and the official Humble sources

**TL;DR** This skill is written for Jazzy + Harmonic. On Humble the official Gazebo is **Fortress**. With current packages most of the code works as it is: Fortress translates the `gz-sim` plugin names, accepts `GZ_SIM_RESOURCE_PATH`, `gz_frame_id` and the `gz.msgs` bridge names, and gz_ros2_control keeps the same names. The one change you must make is `<robot_param_node>` for gz_ros2_control. When in doubt, read the Humble source listed below.

## Install
```bash
sudo apt install ros-humble-ros-gz              # ros_gz (humble branch) + Fortress
sudo apt install ros-humble-gz-ros2-control     # gz_ros2_control 0.7.21 (also ign_ros2_control)
sudo apt install ros-humble-ros2-controllers
```
Harmonic on Humble exists only from packages.osrfoundation.org as `ros-humble-ros-gzharmonic` ("use with caution"); never mix it with `ros-humble-ros-gz`.

## Jazzy/Harmonic name → Humble/Fortress
| This skill (Jazzy + Harmonic) | Humble + Fortress | Works as written? |
|---|---|---|
| `gz sim world.sdf`, `gz topic -l` | `ign gazebo world.sdf`, `ign topic -l` | use `ros_gz_sim gz_sim.launch.py` (picks the right one) |
| `GZ_SIM_RESOURCE_PATH` | `IGN_GAZEBO_RESOURCE_PATH` | yes: current Fortress reads both |
| `filename="gz-sim-diff-drive-system"` | `ignition-gazebo-diff-drive-system` | yes: the `gz-sim` prefix is translated |
| `name="gz::sim::systems::DiffDrive"` | `ignition::gazebo::systems::DiffDrive` | yes (aliases); NavSat needs Fortress ≥ 6.18.0 [verify installed version] |
| `<gz_frame_id>` | `<ignition_frame_id>` | yes: both are read |
| bridge `gz.msgs.Twist` | `ignition.msgs.Twist` | yes: both accepted |
| `gz_ros2_control/GazeboSimSystem`, `gz_ros2_control-system`, `gz_ros2_control::GazeboSimROS2ControlPlugin` | same (0.7.21) | yes |
| controller manager reads `/robot_description` (topic) | reads the **parameter** of node `robot_state_publisher` | **no**: if the node has another name add `<robot_param_node>robot_state_publisher_node</robot_param_node>` to the plugin |
| `ros2_controllers` parameters (JTC, JointGroupVelocityController) | same names | yes |

## Official sources for Humble / Fortress
| Topic | Source |
|---|---|
| Pairing, install, branches | ros_gz README, humble branch: https://github.com/gazebosim/ros_gz/blob/humble/README.md |
| ROS 2 integration (launch, bridge, spawn) | Gazebo Fortress docs: https://gazebosim.org/docs/fortress/ros2_integration/ |
| First simulation with Humble | ROS 2 Humble docs, "Setting up a robot simulation (Gazebo)": https://docs.ros.org/en/humble/Tutorials/Advanced/Simulators/Gazebo/Gazebo.html |
| Systems (DiffDrive, JointStatePublisher, Imu, Sensors…) | gz-sim `ign-gazebo6` branch: https://github.com/gazebosim/gz-sim/tree/ign-gazebo6/src/systems |
| Sensors (lidar, camera, IMU) | gz-sensors `ign-sensors6` branch: https://github.com/gazebosim/gz-sensors/tree/ign-sensors6/src |
| Bridge types | https://github.com/gazebosim/ros_gz/blob/humble/ros_gz_bridge/README.md |
| gz_ros2_control | https://github.com/ros-controls/gz_ros2_control/blob/humble/doc/index.rst |
| Controllers | ros2_controllers `humble` branch: https://github.com/ros-controls/ros2_controllers/tree/humble |
| Release dates | https://gazebosim.org/docs/latest/releases/ (Fortress EOL May 2027) |

To have the skill check a Humble detail, ask for it and point to the source of this table.

## Pitfalls
- Old Fortress install (before the gz renaming) → `gz-sim-…` names not found: update Fortress, or use the `ignition-gazebo-…` / `ignition::gazebo::systems::…` names.
- gz_ros2_control on Humble starts but no controller loads → robot description not found: check `<robot_param_node>`.
