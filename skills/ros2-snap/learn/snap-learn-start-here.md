---
id: snap-learn-start-here
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "Snaps workshop: learning path, requirements and next steps"
domain: snap
area: learn
distro: humble
tested: false
audience: students
order: 1
summary: "Map of the snaps workshop (ROS 2 Humble talker-listener snap): sections, requirements, notes behind each step, next steps."
tags: [course, snaps workshop, learning path, talker-listener, students, requirements]
see: ["[[snap-overview]]", "[[snap-learn-exercise]]", "[[snap-store-publish]]", "[[core-learn-start-here]]"]
requires: [ros2-core]
version_notes:
  - "humble: the workshop is part 1 of Canonical's series; the current version asks Ubuntu 22.04, LXD, and builds with snapcraft pack — https://canonical-robotics.readthedocs-hosted.com/en/latest/tutorials/snaps-core/packaging-ros-application-as-snap/ (SNAP-V05, SNAP-V28)"
---
# Snaps workshop: learning path, requirements and next steps

**TL;DR** The workshop packages a first ROS 2 app, the Humble talker-listener demo, as a snap: build it, install it, confine it, run it as a daemon, and add a second app as an exercise. No previous experience with snaps is needed. Read the technical note of each step.

## What you learn
- Package a ROS 2 application as a snap, and the main concepts behind snaps.
- Confine the application and make it installable on dozens of Linux distributions.
- See what snaps do for a robot: the workshop starts with a [video](https://youtu.be/T3ZzrT7M8wc?t=18) comparing the APT and snap installation of the TurtleBot3 software (snap: one line, faster).

## Requirements
- Ubuntu 22.04 LTS or similar, native or in a VM. In a container, systemd, snapd and snaps must be able to install and run.
- Basic ROS 2 knowledge ([[core-learn-start-here]]) and basic Linux (Ubuntu).
- The workshop was written for robotics developers who want to deploy their software.

## Path
| Section | Topic | Notes |
|---|---|---|
| 1.1–1.2 | why snaps, what they can and cannot do | [[snap-overview]] |
| 1.3 | install snapd, snapcraft (and LXD) | [[snap-install-tools]] |
| 1.4 | first ROS 2 snap: `snapcraft.yaml`, build, install, run | [[snap-snapcraft-yaml]], [[snap-build-install-run]] |
| 1.5 | confinement, grade, interfaces | [[snap-confinement]] |
| 1.6 | run the snap as a daemon | [[snap-daemon]] |
| 1.7 | exercise: add `ros2topic` | [[snap-learn-exercise]] |
| 1.9 | appendix: plugins, extensions, bases | [[snap-ros2-extensions-bases]] |

The example repository [ubuntu-robotics/ros2-humble-talker-listener-snap](https://github.com/ubuntu-robotics/ros2-humble-talker-listener-snap) has one branch per step: `main`, `confined`, `daemon`.

## Next steps
The workshop is the first part of a series on robot deployment. This skill also covers the next topics with the current official material:
- Snap Store, channels and updates: [[snap-store-publish]], [[snap-channels-updates]].
- A whole robot stack: [[snap-robot-apps-design]], [[snap-config-hooks]], [[snap-ros2-architectures]], [[snap-ros2-content-sharing]].
- Ubuntu Core, a secure, application-centric OS for embedded devices: [[snap-ubuntu-core-image]].
- More: the [snapcraft robotics documentation](https://snapcraft.io/docs/robotics) and the [snapcraft forum](https://forum.snapcraft.io/) for questions.

## Pitfalls
- Older copies of the workshop use `SNAPCRAFT_ENABLE_EXPERIMENTAL_EXTENSIONS=1`: not needed for Humble today ([[snap-build-install-run]]).
- The confined and daemon diffs of the workshop name a `talker-listener` package: keep `demo_nodes_cpp` ([[snap-confinement]]).
