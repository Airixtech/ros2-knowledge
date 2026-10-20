---
id: snap-ros2-architectures
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "ROS 2 robot stacks as snaps: monolithic vs multi-snap"
domain: snap
area: deployment
distro: humble
tested: false
audience: dev
summary: "One monolithic snap (recommended first) or several snaps talking over ROS 2: complexity, stability, size, updates, reuse; validation sets."
tags: [architecture, monolithic snap, multi-snap, content sharing, brain snap, validation set, Ubuntu Core, shared memory, reuse]
see: ["[[snap-ros2-content-sharing]]", "[[snap-robot-apps-design]]", "[[snap-confinement]]", "[[snap-channels-updates]]"]
requires: [ros2-core]
version_notes:
  - "humble: monolithic, multi-snap and multi-snap with content sharing; validation sets on Ubuntu Core prevent incompatible installs — https://canonical-robotics.readthedocs-hosted.com/en/latest/explanations/snaps/ros-architectures-with-snaps/ (SNAP-V38)"
---
# ROS 2 robot stacks as snaps: monolithic vs multi-snap

**TL;DR** Start with **one monolithic snap** that holds the whole stack and exposes several apps. Move to several snaps (one "Brain" snap plus application snaps that talk to it over ROS 2) when you need to reuse the Brain across robots and update parts separately; then content sharing removes the duplicated ROS libraries ([[snap-ros2-content-sharing]]).

Example robot: a **Brain** app (control, navigation: everything basic and reusable), a **Patrol** app and a **Clean** app that send commands to the Brain.

## Monolithic snap
All binaries, libraries, configuration and dependencies in one snap with one `snapcraft.yaml` (it may still have several parts, for dependencies to build). The three apps talk over ROS 2 inside it (network, shared memory…).

## Multi-snap
Each snap carries its own ROS installation and dependencies, and the apps talk over ROS 2 topics and services through the host. A snap must make sense as an application: do not snap a single library or ROS package.

## Comparison
| | Monolithic | Multi-snap | Multi-snap + content sharing |
|---|---|---|---|
| Complexity | one `snapcraft.yaml` | several to build and maintain; shared memory across snaps needs an extra interface ([[snap-confinement]]) | like multi-snap; the ROS foundation snap comes from the extensions |
| Stability | robust: immutable, tested as one unit | needs tests of the snaps together, especially across updates; channels or Ubuntu Core validation sets keep compatible versions | the app snaps must stay API/ABI compatible with the foundation snap |
| Size | no duplicated files | common libraries (ROS base) shipped in every snap | ROS shared once: the main gain |
| Updates | any change rebuilds the whole snap; even delta updates are in the order of the snap size | only the changed snap is redeployed | only the changed snap, but a foundation update may require rebuilding all app snaps |
| Reuse | a second robot needs a completely different snap | one Brain snap for all robots, application snaps on top (with standard interfaces: topic names, units…) | same as multi-snap |

- **Monolithic, pros**: easy to set up and maintain, self-sufficient, robust, space-efficient. **Cons**: heavy updates, little reuse, a whole new release for a small change. Recommended for a first snap.
- **Multi-snap, pros**: reuse, modular apps, smaller updates. **Cons**: less space-efficient, possible incompatibilities between snaps, harder to maintain, may need extra interfaces, releases must be coordinated.
- **With content sharing, pros**: as multi-snap, plus less bandwidth and disk. **Cons**: possible incompatibilities, harder maintenance, a tighter release schedule.

## Deploying a set of snaps
A set of snaps that must run together can be paired through a private (dedicated) Snap Store, or pinned in a custom Ubuntu Core image ([[snap-ubuntu-core-image]]); validation sets prevent installing incompatible versions.

## Pitfalls
- Multi-snap pays off when the number of robots, deployments and applications grows and the release coordination is in place; before that it only adds work.
- Snaps that talk over ROS 2 need the same domain and middleware settings ([[core-env-variables]]).

Adapted from the Canonical robotics documentation (CC-BY-SA 3.0).
