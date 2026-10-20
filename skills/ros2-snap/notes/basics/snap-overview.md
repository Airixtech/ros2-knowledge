---
id: snap-overview
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "Snaps for ROS 2: what they are, what they are for, what they are not for"
domain: snap
area: basics
distro: humble
tested: false
audience: dev
summary: "Snaps bundle a ROS 2 app with its dependencies: confinement, OTA updates, channels, daemons; not for debugging or cloud services."
tags: [snap, snapd, snapcraft, deployment, packaging, containerised, OTA, delta updates, channels, Ubuntu Core]
see: ["[[snap-install-tools]]", "[[snap-snapcraft-yaml]]", "[[snap-ros2-architectures]]", "[[core-testing-ci-docker]]"]
requires: [ros2-core]
version_notes:
  - "humble: the current official series is 'From zero to hero: deploy a robot with snaps and Ubuntu Core' (5 parts) — https://canonical-robotics.readthedocs-hosted.com/en/latest/tutorials/snaps-core/ (SNAP-V28)"
---
# Snaps for ROS 2: what they are, what they are for, what they are not for

**TL;DR** A snap is a containerised package that bundles an application and all its dependencies (for a ROS 2 app: ROS itself too). It installs on many Linux distributions and versions, runs isolated from the host, and updates itself. Use snaps to **deploy** software that is already developed and tested.

## Why snaps for robots
Deploying robot software by compiling on the robot or copying built packages ends with unknown software versions and "it works on my machine". Snaps give a controlled, stable environment, even with hundreds of dependencies:

| Feature | What it gives a robot |
|---|---|
| Containerised | one package with all dependencies and assets; nothing else to install on the robot, not even ROS |
| Strict confinement | isolated from the host and from other apps; access only through declared interfaces ([[snap-confinement]]) |
| CI/CD | snap builds fit a CI pipeline ([[snap-ci-github-actions]]) |
| OTA and delta updates | automatic, transactional updates: a failed update never leaves the device broken |
| Multi-architecture | build the same snap for several architectures |
| Managed updates | automatic or controlled refreshes (hours, holds, history) and release channels for versions and roles ([[snap-channels-updates]]) |
| Daemons | an app can start at boot as a service ([[snap-daemon]]) |

## What snaps are for, and what they are not for
- **For:** distributing and deploying developed, tested software, like a package manager (an alternative to APT) that tracks the installed version without ever breaking the installation. Sharing an app with all users or devices, and running it on any distro with secure, declared access to the host.
- **Not for:** testing and debugging. A snap does not embed the source code, so it is not the tool for trying fresh code or for early debugging sessions. It is also not meant for cloud web services (that is Docker's use case). Snaps fit where secure access to the host machine and its resources matters, such as a robot.

## Two tools
- `snapd`: the daemon that downloads, installs and runs snaps, plus the `snap` command.
- `snapcraft`: the developer tool that builds, uploads and shares snaps ([[snap-install-tools]]).

## Pitfalls
- A snap packages *what you built*: debug the ROS code before snapping it, then debug only the packaging ([[snap-debug-build]], [[snap-debug-app]]).
- For many robots and production images, look at Ubuntu Core ([[snap-ubuntu-core-image]]).
