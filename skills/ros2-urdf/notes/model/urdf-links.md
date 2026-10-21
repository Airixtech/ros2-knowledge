---
id: urdf-links
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "Link elements: visual, collision, inertial, geometry, origin, materials, meshes"
domain: urdf
area: model
distro: humble
tested: false
audience: dev
summary: "URDF link: visual/collision/inertial with own origin, box/cylinder/sphere/mesh geometry, package:// meshes and scale, named materials, RViz material override."
tags: [link, visual, collision, inertial, origin, geometry, box, cylinder, sphere, mesh, package://, scale, material, color, texture, dae, stl, obj]
see: ["[[urdf-joints]]", "[[urdf-inertia]]", "[[urdf-frames-rviz]]", "[[urdf-description-package]]", "[[core-urdf-basics]]"]
requires: [ros2-core]
version_notes:
  - "humble: a <material> in a <visual> replaces the colors of every submesh in RViz2; a mesh keeps its own colors only without <material> — https://github.com/ros2/rviz/blob/humble/rviz_default_plugins/src/rviz_default_plugins/robot/robot_link.cpp (URDF-V04)"
  - "humble: an undefined material name only logs 'material ... undefined' and the visual gets no color — https://github.com/ros/urdfdom/blob/humble/urdf_parser/src/model.cpp (URDF-V07)"
  - "humble: visual and collision take an optional name attribute — https://github.com/ros/urdfdom/blob/humble/urdf_parser/src/link.cpp (URDF-V08)"
  - "humble: geometries box, cylinder, sphere, mesh; lyrical adds capsule (needs <robot version=\"1.1\">) — https://github.com/ros/urdfdom/blob/lyrical/urdf_parser/src/link.cpp (URDF-V14)"
---
# Link elements: visual, collision, inertial, geometry, origin, materials, meshes

**TL;DR** A link is a rigid body with its own frame. It can hold a `visual` (what you see), a `collision` (what the physics engine touches) and an `inertial` (mass and inertia), each with its own `<origin>` relative to the link frame. A link with no elements (`<link name="base_link"/>`) is just a frame.

## Geometry
```xml
<box size="0.1 0.1 0.1"/>                <!-- x, y, z lengths -->
<cylinder radius="0.06" length="0.09"/>  <!-- axis along z of its origin frame -->
<sphere radius="0.06"/>
<mesh filename="package://urdfbot_description/meshes/urdfbot_head.dae" scale="0.1 0.1 0.1"/>
```
- `mesh`: `.dae`, `.stl`, `.obj`; `package://<pkg>/…` resolves to the installed share folder of `<pkg>` (install `meshes/`, [[urdf-description-package]]). `scale="0.1 0.1 0.1"` draws a mesh modelled 10× too big at its real size.
- A cylinder stands on z: a wheel that rolls about y needs a rotated origin, e.g. `<origin rpy="0 1.5707 1.5707"/>`.
- [Lyrical] `capsule` (needs `<robot version="1.1">`).

## Origin: the shape is not the frame
```xml
<link name="head_link">
  <visual>
    <origin xyz="0 0 0.1" rpy="0 0 0"/>  <!-- box drawn 0.1 m above the head_link frame -->
    <geometry><box size="0.1 0.1 0.1"/></geometry>
  </visual>
</link>
```
The link frame is set by its joint ([[urdf-joints]]); `visual`, `collision` and `inertial` origins only move the shape, the contact geometry or the center of mass inside that frame. They may differ, e.g. a lower center of mass for stability. A mesh whose own origin is not at its center needs no offset (or a different one) compared with a primitive.

## Materials
```xml
<robot name="urdfbot">
  <material name="blue"><color rgba="0.006 0.151 0.581 1"/></material>
  <material name="white"><color rgba="1.0 0.91 0.827 1"/></material>
  <link name="base_link">
    <visual>
      <geometry><box size="0.1 0.1 0.1"/></geometry>
      <material name="white"/>     <!-- after <geometry>, inside <visual> -->
    </visual>
  </link>
</robot>
```
- Names are free. Define them once at robot level (or inline with `<color>`/`<texture filename>`), then reference them by name. These are colors only; physical surface properties are simulator tags (ros2-gazebo skill).
- **Meshes:** in RViz2 a `<material>` in the visual replaces the DAE/OBJ colors of every submesh. Leave it out to keep the mesh's own colors and textures.

## Collision
```xml
<collision name="chassis_collision">           <!-- name optional; some plugins need it -->
  <geometry><box size="0.1 0.1 0.1"/></geometry>  <!-- bounding box of the 1 m mesh scaled by 0.1 -->
</collision>
```
Primitives are cheap; a mesh collision (`<mesh filename=…/>`) is exact but slow, so use a simplified STL when a primitive does not fit (car body, hand). Inertia: [[urdf-inertia]].

## Pitfalls
- A referenced but undefined material → warning "link '…' material '…' undefined" and an uncolored visual.
- The mesh appears white or in the wrong color → a URDF `<material>` overrides it; remove the material.
- `package://` mesh not found → `meshes/` not installed or the package not sourced.
