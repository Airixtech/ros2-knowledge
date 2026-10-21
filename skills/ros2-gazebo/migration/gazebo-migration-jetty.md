---
id: gazebo-migration-jetty
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "Harmonic to Jetty (Lyrical) changes"
domain: gazebo
area: migration
distro: jazzy
tested: false
audience: dev
summary: "Jazzy+Harmonic to Kilted+Ionic and Lyrical+Jetty: pairings and binaries, no changes for this course's systems and elements, gz_ros2_control lyrical, sources."
tags: [lyrical, jetty, kilted, ionic, migration, ros_gz lyrical, gz-sim10, gz_ros2_control lyrical, ign_ros2_control]
see: ["[[gazebo-migration-fortress]]", "[[gazebo-sim-overview]]", "[[urdf-migration]]"]
requires: [ros2-core, ros2-urdf]
version_notes:
  - "lyrical: Jetty from packages.ros.org (ros_gz lyrical branch); Harmonic and Ionic only from source — https://github.com/gazebosim/ros_gz/blob/lyrical/README.md (GZ-V44)"
  - "lyrical: DiffDrive and JointStatePublisher elements, default world systems and the DART default are unchanged from Harmonic — https://github.com/gazebosim/gz-sim/blob/gz-sim10/Migration.md (GZ-V44)"
  - "lyrical: gz_ros2_control exports only gz_ros2_control/GazeboSimSystem (no ign_ros2_control alias) — https://github.com/ros-controls/gz_ros2_control/blob/lyrical/gz_ros2_control/src/gz_system.cpp (GZ-V28)"
---
# Harmonic to Jetty (Lyrical) changes

**TL;DR** Lyrical pairs with Gazebo **Jetty** (LTS, EOL May 2031); Kilted pairs with Ionic (EOL Dec 2026). For the files of this skill nothing changes: same plugin file names, system names, elements, bridge types and gz_ros2_control names. Move to the new binaries and drop any `ign_…` leftovers.

## Pairings
| ROS 2 | Gazebo | Binaries |
|---|---|---|
| Jazzy | Harmonic | packages.ros.org (`ros-jazzy-ros-gz`) |
| Kilted | Ionic | packages.ros.org |
| Lyrical | Jetty | packages.ros.org (`ros-lyrical-ros-gz`); Harmonic or Ionic only from source |

## What changed
- **Nothing for the course's models:** the DiffDrive and JointStatePublisher elements, the default world systems (Physics, UserCommands, SceneBroadcaster) and the DART physics default are the same in gz-sim 10.
- **Plugin writers only:** since Ionic the Physics system deletes `*VelocityCmd` components after each step (re-send velocity commands every step); Jetty removed some CMake macros and deprecated parts of the hydrodynamics API.
- **gz_ros2_control (lyrical):** `gz_ros2_control/GazeboSimSystem` only; the old `ign_ros2_control/IgnitionSystem` name is gone.
- **URDF side:** Lyrical's urdfdom adds the capsule geometry ([[urdf-migration]]).

## Sources
gz-sim `Migration.md` (gz-sim10 branch), ros_gz `lyrical` README, gz_ros2_control `lyrical` branch, Gazebo release table (https://gazebosim.org/docs/latest/releases/), Jetty docs (https://gazebosim.org/docs/jetty/).
