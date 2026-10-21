---
id: core-gazebo-bridge
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "Gazebo with ROS 2: versions, ros_gz bridge, Gazebo vs Isaac"
domain: core
area: architecture
distro: humble
tested: false
audience: dev
summary: "Gazebo pairing per distro (Fortress for Humble), starting the sim, ros_gz_bridge YAML, Gazebo Classic EOL, Gazebo vs Isaac Sim."
tags: [Gazebo, ros_gz, Fortress, Harmonic, parameter_bridge, Gazebo Classic]
see: ["[[core-isaac-sim-ros]]", "[[core-time-timers]]", "[[core-launch-basics]]", "[[core-urdf-basics]]"]
requires: []
version_notes:
  - "humble: official Gazebo = Fortress ('ign gazebo'); Harmonic via packages.osrfoundation.org; jazzy Harmonic, kilted Ionic, lyrical Jetty — https://www.ros.org/reps/rep-2000.html (V64, V20)"
  - "humble: ros_gz_bridge accepts ignition.msgs.* and gz.msgs.* type names — https://github.com/gazebosim/ros_gz/blob/humble/ros_gz_bridge/resource/get_mappings.cpp.em (V66)"
  - "all: Gazebo Classic 11 EOL 2025-01-31 — https://discourse.openrobotics.org/t/gazebo-classic-end-of-life/48748 (V65)"
---
# Gazebo with ROS 2: versions, ros_gz bridge, Gazebo vs Isaac

**TL;DR** The official Gazebo for Humble is **Fortress** (`ign gazebo`, `sudo apt install ros-humble-ros-gz`). ROS and Gazebo topics are connected by `ros_gz_bridge` with a YAML file. Seed note for a future simulation skill.

## Versions
| | Classic 11 | Modern Gazebo |
|---|---|---|
| ROS pkgs | gazebo_ros_pkgs | ros_gz (`ros_gz_bridge`, `ros_gz_sim`) |
| Status | EOL 2025-01-31; not available for Jazzy | Humble: Fortress (official; Harmonic only via packages.osrfoundation.org, "use with caution") · Jazzy: Harmonic · Kilted: Ionic · Lyrical: Jetty |

## Start the simulator
- Fortress (Humble): `ign gazebo world.sdf`. Garden/Harmonic and newer: `gz sim world.sdf`.
- Portable, picks the right one: `ros2 launch ros_gz_sim gz_sim.launch.py gz_args:=world.sdf`.
- Every node must use sim time: `use_sim_time:=true` and a `/clock` bridge ([[core-time-timers]]).

## Bridge YAML
`ros2 run ros_gz_bridge parameter_bridge --ros-args -p config_file:=bridge.yaml`
```yaml
- ros_topic_name: "/cmd_vel"
  gz_topic_name: "/model/my_robot/cmd_vel"
  ros_type_name: "geometry_msgs/msg/Twist"
  gz_type_name: "gz.msgs.Twist"
  direction: ROS_TO_GZ
```
With Fortress the canonical type name is `ignition.msgs.Twist`; the Humble bridge accepts both `ignition.msgs.*` and `gz.msgs.*` names.

## Gazebo vs Isaac Sim
Gazebo: DART/ODE/Bullet, no GPU required, classic navigation, CI, large multi-robot setups. Isaac Sim: PhysX 5 GPU, RTX rendering, Replicator synthetic data, DNN perception + TensorRT, sim-to-real (Isaac Lab for RL) ([[core-isaac-sim-ros]]).

## Pitfalls
- Links without `<inertial>` are dropped or unstable in Gazebo ([[core-urdf-basics]]).
- Mixing a Harmonic install with `ros-humble-ros-gz` (built for Fortress) → bridge and plugin mismatches. Use `ros-humble-ros-gzharmonic` from the OSRF repo.
