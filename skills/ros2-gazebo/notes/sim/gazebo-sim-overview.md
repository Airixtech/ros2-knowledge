---
id: gazebo-sim-overview
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "Gazebo Sim with ROS 2: packages, what a robot needs, plugin vs ros2_control approaches"
domain: gazebo
area: sim
distro: jazzy
tested: false
audience: dev
summary: "Gazebo Sim (Harmonic) with ROS 2: ros_gz_sim, ros_gz_bridge, gz_ros2_control; what a URDF needs; systems + bridge vs ros2_control; Humble Fortress sources."
tags: [gazebo sim, harmonic, fortress, jetty, ros_gz, ros_gz_sim, ros_gz_bridge, gz_ros2_control, gazebo transport, systems, ros-jazzy-ros-gz]
see: ["[[core-gazebo-bridge]]", "[[gazebo-start-sim]]", "[[gazebo-spawn-urdf]]", "[[gazebo-joint-state-diffdrive]]", "[[gazebo-ros2-control-urdf]]", "[[gazebo-migration-fortress]]"]
requires: [ros2-core, ros2-urdf]
version_notes:
  - "humble: official pairing Fortress (binaries on packages.ros.org, ros-humble-ros-gz); Harmonic only from packages.osrfoundation.org (ros-humble-ros-gzharmonic, 'use with caution') — https://github.com/gazebosim/ros_gz/blob/humble/README.md (GZ-V45)"
  - "humble: Fortress EOL May 2027 (same as Humble); Harmonic May 2029; Jetty May 2031 — https://gazebosim.org/docs/latest/releases/"
  - "lyrical: official pairing Jetty, ros_gz branch lyrical — https://github.com/gazebosim/ros_gz/blob/lyrical/README.md (GZ-V44)"
  - "jazzy: systems DiffDrive, MecanumDrive, JointPositionController, JointTrajectoryController, JointStatePublisher — https://github.com/gazebosim/gz-sim/tree/gz-sim8/src/systems (GZ-V22)"
---
# Gazebo Sim with ROS 2: packages, what a robot needs, plugin vs ros2_control approaches

**TL;DR** Gazebo Sim (Harmonic for Jazzy) is a separate program that talks over **Gazebo Transport**, not ROS topics. `ros_gz_sim` starts it and spawns robots, `ros_gz_bridge` translates topics, `gz_ros2_control` runs ros2_control inside it. A URDF that is fine for RViz also needs collisions, inertia and physical properties to behave in simulation.

## Packages
```bash
sudo apt install ros-jazzy-ros-gz            # ros_gz_sim, ros_gz_bridge, … + Harmonic
sudo apt install ros-jazzy-gz-ros2-control   # only for the ros2_control approach
```
[Humble] `sudo apt install ros-humble-ros-gz` installs Fortress, the official pairing; the same packages and launch files exist (ros_gz `humble` branch). Names, versions and where to read the Humble/Fortress docs: [[gazebo-migration-fortress]]. Versions per distro and Classic vs Sim: [[core-gazebo-bridge]].

## What the robot model needs
| For | Add to the URDF | Note |
|---|---|---|
| contacts | `<collision>` on every link that touches something | [[urdf-links]] |
| dynamics | `<inertial>` on every simulated link | [[urdf-inertia]] |
| grip, bounce | `<gazebo reference="link">` friction and contact | [[gazebo-urdf-sim-tags]] |
| motion, sensors | `<gazebo>` system plugins or `<ros2_control>` | below |

Gazebo simulates rigid bodies only: every link keeps its shape whatever force acts on it.

## Two ways to move joints and read their state
1. **Gazebo systems** in the model (`<gazebo><plugin filename="gz-sim-…-system" …/>`): DiffDrive and MecanumDrive bases, JointPositionController and JointTrajectoryController joints, JointStatePublisher for joint states. They use Gazebo topics: bridge them with `ros_gz_bridge` ([[gazebo-joint-state-diffdrive]], [[gazebo-ros-gz-bridge]]).
2. **ros2_control** through the `gz_ros2_control` system: a controller_manager runs inside the simulation, controllers such as diff_drive_controller, joint_trajectory_controller and joint_state_broadcaster publish native ROS 2 topics. More to learn, but the same controllers run on the real robot ([[gazebo-ros2-control-urdf]]).

Both load when the model is spawned ([[gazebo-spawn-urdf]]). The course uses DiffDrive + JointStatePublisher for the base and ros2_control for a laser mount.

## Pitfalls
- Robot spawned but nothing moves from ROS → Gazebo systems publish and subscribe on Gazebo Transport: no bridge, no ROS topics.
- Mixing a Harmonic install with `ros-humble-ros-gz` (built for Fortress) → plugin and bridge mismatches.
- A link on a movable joint without `<inertial>` (or with mass 0) → "urdf2sdf: link[…] has no <inertial> block defined" and its joint is dropped from the simulated model. Empty frame links on fixed joints are fine: they are merged into their parent ([[gazebo-spawn-urdf]]).
