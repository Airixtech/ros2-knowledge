---
id: urdf-inertia
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "Inertia tensors for box/cylinder/sphere, inertial origin, xacro inertia macros"
domain: urdf
area: model
distro: humble
tested: false
audience: dev
summary: "URDF <inertial>: mass, origin as center of mass, inertia tensor; box, cylinder, sphere formulas; xacro macros; near-zero inertia; root link."
tags: [inertial, inertia, mass, ixx, iyy, izz, moment of inertia, box inertia, cylinder inertia, sphere inertia, center of mass, xacro macro, kdl_parser]
see: ["[[urdf-links]]", "[[urdf-xacro-macros]]", "[[urdf-onshape-export]]", "[[urdf-learn-unit3-box-bot]]"]
requires: [ros2-core]
version_notes:
  - "humble: box izz = m(x²+y²)/12 (the course printed x²+z²; its URDF values are right) — https://docs.ros.org/en/humble/Tutorials/Intermediate/URDF/Adding-Physical-and-Collision-Properties-to-a-URDF-Model.html (URDF-V01)"
  - "humble: every simulated link needs <inertial>; near-zero inertia can make the model unstable — https://docs.ros.org/en/humble/Tutorials/Intermediate/URDF/Adding-Physical-and-Collision-Properties-to-a-URDF-Model.html (URDF-V33, URDF-V34)"
  - "humble: kdl_parser warns when the root link has an inertia: keep an empty root (base_link) — https://github.com/ros/kdl_parser/blob/humble/kdl_parser/src/kdl_parser.cpp (URDF-V32)"
---
# Inertia tensors for box/cylinder/sphere, inertial origin, xacro inertia macros

**TL;DR** A simulator needs each link's mass, center of mass and inertia tensor (how hard it is to spin the link about each axis). For a first model, compute them as if the link were the primitive that matches its collision shape; the off-diagonal terms are 0 for those shapes. RViz ignores `<inertial>`.

## The element
```xml
<inertial>
  <origin rpy="0 1.5707 1.5707" xyz="0 0 0"/>   <!-- center of mass + axes of the tensor -->
  <mass value="0.05"/>
  <inertia ixx="1.531666666666667e-05" ixy="0" ixz="0" iyy="1.531666666666667e-05" iyz="0" izz="3.0625000000000006e-05"/>
</inertial>
```
- `<origin>`: the center of mass and the orientation of the frame in which the tensor is written. A wheel cylinder rotated by `rpy="0 1.5707 1.5707"` uses the same rotation here, so `izz` stays the cylinder's own axis. A lower center of mass makes a robot more stable.
- `ixx`, `iyy`, `izz` (kg·m²): resistance to rotation about x, y, z, i.e. the torque the simulator needs for a given angular acceleration about each axis. `ixy`, `ixz`, `iyz`: cross terms, needed only for an exact model of real parts (a CAD export gives them, [[urdf-onshape-export]]).

## Formulas (solid, uniform mass)
| Shape | `ixx` | `iyy` | `izz` |
|---|---|---|---|
| box x·y·z | m(y²+z²)/12 | m(x²+z²)/12 | **m(x²+y²)/12** |
| cylinder r, length l (axis z) | m(3r²+l²)/12 | m(3r²+l²)/12 | m r²/2 |
| sphere r | 2 m r²/5 | 2 m r²/5 | 2 m r²/5 |

Check against box_bot: chassis 0.5 kg, 0.1 m cube → 0.5·(0.01+0.01)/12 = 8.33e-4; wheel 0.05 kg, r 0.035, l 0.001 → 1.5317e-05 / 3.0625e-05; caster sphere 0.001 kg, r 0.01 → 4e-08.

## xacro macros
```xml
<xacro:macro name="box_inertia" params="mass x y z">
  <inertia ixx="${mass*(y*y+z*z)/12}" ixy="0" ixz="0"
           iyy="${mass*(x*x+z*z)/12}" iyz="0"
           izz="${mass*(x*x+y*y)/12}"/>
</xacro:macro>
<xacro:macro name="cylinder_inertia" params="mass r l">
  <inertia ixx="${mass*(3*r*r+l*l)/12}" ixy="0" ixz="0"
           iyy="${mass*(3*r*r+l*l)/12}" iyz="0"
           izz="${mass*(r*r)/2}"/>
</xacro:macro>
<xacro:macro name="sphere_inertia" params="mass r">
  <inertia ixx="${2*mass*r*r/5}" ixy="0" ixz="0"
           iyy="${2*mass*r*r/5}" iyz="0"
           izz="${2*mass*r*r/5}"/>
</xacro:macro>
```
Use inside `<inertial>`: `<xacro:box_inertia mass="0.5" x="0.1" y="0.1" z="0.1"/>`. Macros: [[urdf-xacro-macros]].

## Pitfalls
- Tiny links (caster parts) still need a mass and an inertia: the course uses 0.001 kg; values near zero can make the simulation unstable.
- Mass and inertia from different assumptions (0.2 kg in a calculation, 0.5 kg in the file) → inconsistent dynamics: compute both from the same numbers.
- An inertia on the root link triggers the kdl_parser warning "KDL does not support a root link with an inertia": keep `base_link` empty and put the mass on `chassis`.
