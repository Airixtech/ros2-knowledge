---
id: gazebo-world-sdf
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "SDF world file: physics, world systems, light, ground, model:// includes"
domain: gazebo
area: sim
distro: jazzy
tested: false
audience: dev
summary: "SDF world for Gazebo Sim: <world>, sun light, ground plane, <include> model:// with pose, default systems Physics/UserCommands/SceneBroadcaster, explicit Sensors."
tags: [sdf, world, .world, .sdf, light, ground_plane, include, model://, pose, server.config, physics system, scene broadcaster, user commands, sensors system]
see: ["[[gazebo-start-sim]]", "[[gazebo-resource-paths]]", "[[gazebo-spawn-urdf]]", "[[gazebo-sensors-lidar]]"]
requires: [ros2-core, ros2-urdf]
version_notes:
  - "jazzy: a world without <plugin> elements loads the defaults of server.config (Physics, UserCommands, SceneBroadcaster); same in Jetty — https://github.com/gazebosim/gz-sim/blob/gz-sim8/include/gz/sim/server.config (GZ-V13)"
  - "jazzy: the official template lists the world systems explicitly, Sensors included — https://github.com/gazebosim/ros_gz_project_template (GZ-V13, GZ-V35)"
  - "humble: Fortress loads the same plugin file names (the gz-sim prefix is translated) — https://github.com/gazebosim/gz-sim/blob/ign-gazebo6/src/SystemLoader.cc (GZ-V12)"
---
# SDF world file: physics, world systems, light, ground, model:// includes

**TL;DR** A world is an SDF file with one `<world>`: lights, models (a ground plane at least), included models and the world systems. Without any `<plugin>`, Gazebo loads its default systems (Physics, UserCommands, SceneBroadcaster); list them yourself when you add one, e.g. Sensors.

## worlds/box_bot_empty.world
```xml
<?xml version="1.0" ?>
<sdf version="1.8">
  <world name="demo">
    <light name="sun" type="directional">
      <cast_shadows>true</cast_shadows>
      <pose>0 0 10 0 0 0</pose>
      <diffuse>0.8 0.8 0.8 1</diffuse>
      <specular>0.2 0.2 0.2 1</specular>
      <attenuation>
        <range>1000</range>
        <constant>0.9</constant>
        <linear>0.01</linear>
        <quadratic>0.001</quadratic>
      </attenuation>
      <direction>-0.5 0.1 -0.9</direction>
    </light>
    <model name="ground_plane">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry><plane><normal>0 0 1</normal><size>100 100</size></plane></geometry>
        </collision>
        <visual name="visual">
          <geometry><plane><normal>0 0 1</normal><size>100 100</size></plane></geometry>
          <material>
            <ambient>0.8 0.8 0.8 1</ambient>
            <diffuse>0.8 0.8 0.8 1</diffuse>
            <specular>0.8 0.8 0.8 1</specular>
          </material>
        </visual>
      </link>
    </model>
  </world>
</sdf>
```

## Include a model folder
Before `</world>`:
```xml
<include>
  <uri>model://box_room</uri>
  <pose>0 0 -0.095708 0 0 0</pose>
</include>
```
`model://box_room` is a folder `box_room/` (with `model.config` and `model.sdf`) inside a directory listed in `GZ_SIM_RESOURCE_PATH`; installing `models/` and adding it to the path is what makes it work ([[gazebo-resource-paths]]).

## Explicit world systems
```xml
<world name="demo">
  <plugin filename="gz-sim-physics-system" name="gz::sim::systems::Physics"/>
  <plugin filename="gz-sim-user-commands-system" name="gz::sim::systems::UserCommands"/>
  <plugin filename="gz-sim-scene-broadcaster-system" name="gz::sim::systems::SceneBroadcaster"/>
  <plugin filename="gz-sim-sensors-system" name="gz::sim::systems::Sensors">
    <render_engine>ogre2</render_engine>
  </plugin>
  …
</world>
```
The defaults are loaded only when the world has no system at all (the server logs "No systems loaded from SDF, loading defaults"): once one `<plugin>` is in the world, list all you need. Plugins of a robot model do not count, so the course can load Sensors from the robot instead ([[gazebo-sensors-lidar]]).

## Pitfalls
- "Unable to find uri[model://box_room]" → the models folder is not installed or not on the resource path.
- A world with only a Sensors plugin → no Physics: nothing falls or moves.
- Stop Gazebo with Ctrl+C in its terminal before relaunching it.
