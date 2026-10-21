---
id: urdf-migration
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "Humble to Jazzy to Lyrical: urdfdom 3/4/6, capsule and URDF 1.1, RSP description topic, pip on 24.04"
domain: urdf
area: migration
distro: humble
tested: false
audience: dev
summary: "URDF tooling per distro: urdfdom 3.0 (Humble), 4.0 (Jazzy), 6.0 with capsule (Lyrical); robot_state_publisher use_robot_description_topic (Kilted+); pip on Ubuntu 24.04."
tags: [migration, humble, jazzy, kilted, lyrical, urdfdom, capsule, urdf version 1.1, robot_state_publisher, use_robot_description_topic, pep 668, pipx]
see: ["[[urdf-links]]", "[[urdf-frames-rviz]]", "[[urdf-onshape-export]]", "[[core-ros2-control-overview]]"]
requires: [ros2-core]
version_notes:
  - "humble: urdfdom 3.0.2; jazzy: 4.0.2; kilted: 5.0.0; lyrical: 6.0.0 — https://github.com/ros/urdfdom (branches humble, jazzy, kilted, lyrical)"
  - "lyrical: capsule geometry, only for <robot version=\"1.1\"> — https://github.com/ros/urdfdom/blob/lyrical/urdf_parser/src/link.cpp (URDF-V14)"
  - "humble/jazzy: any <robot version> other than 1.0 makes the parser reject the file — https://github.com/ros/urdfdom/blob/jazzy/urdf_parser/src/model.cpp (URDF-V52)"
  - "kilted/lyrical: robot_state_publisher parameter use_robot_description_topic — https://github.com/ros/robot_state_publisher/blob/lyrical/src/robot_state_publisher.cpp (URDF-V16)"
---
# Humble to Jazzy to Lyrical: urdfdom 3/4/6, capsule and URDF 1.1, RSP description topic, pip on 24.04

**TL;DR** URDF files written for Humble load unchanged in Jazzy and Lyrical. What changes is around them: a new geometry in Lyrical, a new way to feed robot_state_publisher from Kilted on, and Python tool installs on Ubuntu 24.04.

## Per distro
| | Humble | Jazzy | Lyrical (incl. Kilted) |
|---|---|---|---|
| urdfdom | 3.0.2 | 4.0.2 (tinyxml2 inside, same XML) | 6.0.0 (Kilted 5.0.0) |
| geometries | box, cylinder, sphere, mesh | same | + `capsule` with `<robot version="1.1">` |
| robot_state_publisher | `robot_description` parameter | same | + `use_robot_description_topic` (subscribe to `/robot_description` instead) |
| xacro, joint_state_publisher(_gui), `check_urdf` | same commands | same | same |
| pip tools (onshape-to-robot) | pip in a venv | Ubuntu 24.04: system pip blocked (PEP 668) → venv or pipx | same (26.04) |

## Capsule [Lyrical]
```xml
<robot name="r" version="1.1">
  …
  <geometry><capsule radius="0.05" length="0.2"/></geometry>
  …
</robot>
```
With the default version 1.0 the capsule is skipped with the warning "Ignoring capsule attribute minimum required version URDF version 1.1". Humble and Jazzy refuse the whole file as soon as it says `version="1.1"` ("Invalid 'version' specified; only version 1.0 is currently supported"), and without the attribute a capsule is an "Unknown geometry type": keep cylinders for portable files.

## Feeding robot_state_publisher [≥Kilted]
`use_robot_description_topic: true` makes robot_state_publisher subscribe (Transient Local) to the description published by another node, instead of reading its own parameter. Humble and Jazzy keep the parameter only.

## Related changes outside this skill
- ros2_control reads `robot_description` from a parameter in Humble and from the topic in Jazzy+ ([[core-ros2-control-overview]]).
- Gazebo versions per distro: ros2-gazebo skill.

## Pitfalls
- A capsule (and `version="1.1"`) in a shared model → Humble/Jazzy users cannot load the robot at all.
- Installing a tool with `sudo pip` on 24.04 → "externally-managed-environment" ([[urdf-onshape-export]]).
