---
id: core-isaac-sim-ros
title: "Isaac Sim with ROS 2 Humble: setup, Fast DDS, troubleshooting"
domain: core
area: architecture
distro: humble
tested: false
audience: dev
summary: "Environment for Isaac Sim + ROS 2 (version-dependent), minimal Action Graph, UDP-only Fast DDS profile for Docker, troubleshooting."
tags: [Isaac Sim, ROS2 bridge, Action Graph, Fast DDS, Cyclone DDS, Docker]
see: ["[[core-gazebo-bridge]]", "[[core-time-timers]]", "[[core-multi-pc-dds]]", "[[core-perception-basics]]"]
requires: []
version_notes:
  - "isaac: current Isaac Sim (Python 3.11/3.12) uses internal ROS libs, not system Humble rclpy; docs default to Fast DDS [verify per version] — https://docs.isaacsim.omniverse.nvidia.com/latest/installation/install_ros.html (V67)"
  - "humble: UDP-only Fast DDS profile needs <transport_descriptors>; env FASTRTPS_DEFAULT_PROFILES_FILE (FASTDDS_ in Kilted+) (V58)"
---
# Isaac Sim with ROS 2 Humble: setup, Fast DDS, troubleshooting

**TL;DR** Use the same `ROS_DOMAIN_ID` and RMW in Isaac Sim and in every ROS terminal, publish `/clock` from the Action Graph, and set `use_sim_time` globally. How the ROS libraries are loaded depends on the Isaac Sim version. Seed note for a future simulation skill.

## Environment
```bash
sudo apt install ros-humble-rmw-cyclonedds-cpp
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp     # same on all ROS terminals
export ROS_DOMAIN_ID=30
source /opt/ros/humble/setup.bash                # BEFORE launching Isaac Sim, same shell
$ISAAC_SIM_PATH/isaac-sim.sh
```
- Version-dependent [verify]: current Isaac Sim (Python 3.11/3.12) cannot load the system Humble rclpy (Python 3.10). It uses its **internal** ROS libraries: `ROS_DISTRO`, `RMW_IMPLEMENTATION` and `LD_LIBRARY_PATH` pointing to `exts/isaacsim.ros2.*`, set once per terminal. Its docs default to Fast DDS.
- Never put Isaac Sim's internal `LD_LIBRARY_PATH` in `~/.bashrc`: it breaks the system rviz2/rqt.

## Minimal Action Graph
On Playback Tick → Isaac Read Simulation Time + ROS2 Context → ROS2 Publish Clock, ROS2 Publish Joint State, ROS2 Subscribe Joint State, ROS2 Publish Transform Tree. Sensors: ROS2 Camera Helper, ROS2 RTX Lidar Helper, ROS2 Publish IMU.

## Docker / multi-host with Fast DDS
Disable SHM and use UDP only. Save as `fastdds.xml`, then `export FASTRTPS_DEFAULT_PROFILES_FILE=/path/fastdds.xml` [≥Kilted: `FASTDDS_DEFAULT_PROFILES_FILE`]:
```xml
<?xml version="1.0" encoding="UTF-8" ?>
<profiles xmlns="http://www.eprosima.com/XMLSchemas/fastRTPS_Profiles">
  <transport_descriptors>
    <transport_descriptor><transport_id>UdpTransport</transport_id><type>UDPv4</type></transport_descriptor>
  </transport_descriptors>
  <participant profile_name="udp_transport_profile" is_default_profile="true">
    <rtps><userTransports><transport_id>UdpTransport</transport_id></userTransports>
    <useBuiltinTransports>false</useBuiltinTransports></rtps>
  </participant>
</profiles>
```
The `<participant>` block alone is not enough: `UdpTransport` must be declared in `<transport_descriptors>`.

## Troubleshooting (Isaac ↔ ROS)
| Symptom | Fix |
|---|---|
| no topics across | same `ROS_DOMAIN_ID` + `RMW_IMPLEMENTATION` |
| "Could not load ROS2 Bridge" | source `/opt/ros/humble/setup.bash` before isaac-sim.sh (older versions) / internal-libs env (newer) |
| TF in echo, not in RViz | RViz display QoS → Best Effort |
| /clock arrives, nodes use wall time | global `use_sim_time` ([[core-time-timers]]) |
| FastDDS deadlock in Docker | UDP-only profile or Cyclone |
Checklist: ROS env set before Isaac · same RMW + domain on both sides · Publish Clock in the graph · global `use_sim_time` · NITROS GEMs for GPU perception ([[core-perception-basics]]).
