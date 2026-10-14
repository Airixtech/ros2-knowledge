---
id: nav2-global-localization
type: reference
owner: equipo-ros2
updated: 2026-10-10
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "Global localization: reinitialize_global_localization and particle count"
domain: nav2
area: localization
distro: humble
tested: false
audience: dev
summary: "When nobody knows where the robot is: spread AMCL particles with /reinitialize_global_localization (std_srvs/Empty), raise particle limits, move until they converge."
tags: [AMCL, global localization, reinitialize_global_localization, std_srvs/Empty, max_particles, min_particles, ParticleCloud, kidnapped robot]
see: ["[[nav2-amcl-params-filter]]", "[[nav2-amcl-concepts]]", "[[nav2-initial-pose-config]]", "[[core-srv-client-async]]"]
requires: [ros2-core]
version_notes:
  - "humble: service reinitialize_global_localization (std_srvs/srv/Empty); same in Jazzy and Lyrical — https://github.com/ros-navigation/navigation2/blob/humble/nav2_amcl/src/amcl_node.cpp (NAV2-V39)"
---
# Global localization: reinitialize_global_localization and particle count

**TL;DR** Use global localization when neither a person nor the robot knows where the robot is: spread the particles over the whole map, then move the robot until they converge on its real pose.

## Two steps
1. **Distribute all the particles across the map** by calling the AMCL service `/reinitialize_global_localization`:
```bash
ros2 service call /reinitialize_global_localization std_srvs/srv/Empty
```
2. **Move the robot until it detects where it is**: drive randomly while avoiding obstacles, or, if the environment is simple, rotate in place (the safe option). As sensor data arrives, the particles accumulate around the most likely pose, until they are all located at the robot.

## Raise the particle limits first
Spreading particles over a whole map needs many more of them. In `amcl_config.yaml` ([[nav2-amcl-launch]]):
```yaml
    max_particles: 80000
    min_particles: 2000
```
Rebuild so the new config file is installed in `install/`, run the localization, and add the **ParticleCloud** display in RViz (topic `particle_cloud`) to watch the particles spread after the call and converge while driving.

## From code
Call the same service with an `std_srvs.srv.Empty` client ([[core-srv-client-async]]), then command a slow in-place rotation and stop when the particle spread (the covariance of `amcl_pose`) is small.

## Pitfalls
- Symmetric environments (identical corridors or rooms) can converge to the wrong place: move more, or start from a known pose ([[nav2-initial-pose-config]]).
- Too few particles after the reset → the filter never finds the true pose.
- 80000 particles are expensive: lower `max_particles` again for normal tracking (KLD sampling reduces the count automatically once converged).
