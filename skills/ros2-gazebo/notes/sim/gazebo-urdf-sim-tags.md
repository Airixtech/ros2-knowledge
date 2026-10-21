---
id: gazebo-urdf-sim-tags
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "<gazebo reference> tags: friction mu/mu2, contact kp/kd, Gazebo materials"
domain: gazebo
area: sim
distro: jazzy
tested: false
audience: dev
summary: "URDF <gazebo reference=link>: collision surface friction mu/mu2/fdir1, contact kp (stiffness) and kd (damping), short tags mu1/mu2/kp/kd, visual materials, selfCollide."
tags: [gazebo reference, surface, friction, mu, mu2, mu1, fdir1, contact, kp, kd, stiffness, damping, maxVel, minDepth, ambient, diffuse, selfCollide, turnGravityOff]
see: ["[[gazebo-spawn-urdf]]", "[[gazebo-sim-overview]]", "[[urdf-links]]", "[[gazebo-learn-unit4-sim]]"]
requires: [ros2-core, ros2-urdf]
version_notes:
  - "jazzy: mu and mu2 are Coulomb friction coefficients in the two friction-pyramid directions (fdir1 and its perpendicular), not static and dynamic friction — https://github.com/gazebosim/sdformat/blob/sdf14/sdf/1.11/surface.sdf (GZ-V01)"
  - "jazzy: kp = contact stiffness, kd = contact damping; SDF defaults kp 1e12, kd 1, mu 1 — https://github.com/gazebosim/sdformat/blob/sdf14/sdf/1.11/surface.sdf (GZ-V02)"
  - "jazzy: collision and visual blocks inside <gazebo reference> are added to every collision/visual of that link; short tags mu1, mu2, fdir1, kp, kd, maxVel, minDepth, selfCollide, turnGravityOff — https://github.com/gazebosim/sdformat/blob/sdf14/src/parser_urdf.cc (GZ-V16)"
  - "jazzy: the course's wheel kd = 1e7 is far above the default 1; effect not measured [verify] (GZ-V17)"
---
# <gazebo reference> tags: friction mu/mu2, contact kp/kd, Gazebo materials

**TL;DR** URDF has no friction or contact parameters. Add them per link in `<gazebo reference="<link>">` blocks: what is inside `<collision>` or `<visual>` is copied into every collision or visual of that link when the URDF is converted to SDF. Friction matters most for wheels and casters.

## Friction and contact
```xml
<gazebo reference="left_wheel">
  <collision>
    <surface>
      <friction>
        <ode>
          <mu>10.0</mu>      <!-- friction coefficient along fdir1 -->
          <mu2>10.0</mu2>    <!-- along the perpendicular direction -->
        </ode>
      </friction>
      <contact>
        <ode>
          <kp>10000000.0</kp>   <!-- contact stiffness -->
          <kd>10000000.0</kd>   <!-- contact damping -->
        </ode>
      </contact>
    </surface>
  </collision>
</gazebo>
```
| Element | Meaning | SDF default |
|---|---|---|
| `mu` | Coulomb friction coefficient in the first friction-pyramid direction (max ratio of friction force to normal force) | 1 |
| `mu2` | the same in the second, perpendicular direction | 1 |
| `fdir1` | first friction direction in the collision frame, e.g. `1 0 0` | 0 0 0 |
| `kp` | contact stiffness: high = rigid like marble, low = soft like rubber | 1e12 |
| `kd` | contact damping: how fast the contact stops bouncing | 1 |

Neither `mu` nor `mu2` is "static" or "dynamic" friction: they are two directions. Values are tuned until the robot behaves well, rarely measured. Short form, also accepted by the converter: `<gazebo reference="left_wheel"><mu1>10.0</mu1><mu2>10.0</mu2><kp>1e7</kp><kd>1.0</kd></gazebo>`.

box_bot (course): `left_wheel`, `right_wheel` mu = mu2 = 10; `front_pitch_link`, `back_pitch_link` (caster spheres) mu = mu2 = 0.5; all four kp = 1e7 and kd = 1e7. The section introducing the tags uses kd = 1.0, the course files 1e7 [verify].

## Gazebo colors
```xml
<gazebo reference="left_wheel">
  <visual>
    <material>
      <!-- Red -->
      <ambient>1 0 0 1</ambient>
      <diffuse>1 0 0 1</diffuse>
      <specular>0 0 0 1</specular>
      <emissive>0 0 0 1</emissive>
    </material>
  </visual>
</gazebo>
```
Without such a block the converter turns the URDF `<material><color>` into the SDF color. A Gazebo block wins over the URDF color in simulation; RViz keeps showing the URDF material.

## Other per-link tags
`<selfCollide>true</selfCollide>` (links of the same model collide with each other), `<turnGravityOff>true</turnGravityOff>` (written to SDF as `self_collide` and `gravity`). Per-joint: `<preserveFixedJoint>` ([[gazebo-spawn-urdf]]).

## Pitfalls
- Robot slides or spins in place → wheel `mu` too low, or caster `mu` too high (casters should slide).
- Robot jitters or sinks into the ground → `kp` too low, or tiny masses with stiff contacts: change one value at a time.
- A `<gazebo reference="…">` block applies only to the link or joint of exactly that name: check the spelling.
