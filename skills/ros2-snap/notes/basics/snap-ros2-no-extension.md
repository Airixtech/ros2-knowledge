---
id: snap-ros2-no-extension
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "Snap a ROS 2 distro without an extension (e.g. Kilted)"
domain: snap
area: basics
distro: humble
tested: false
audience: dev
summary: "Rebuild a ROS 2 extension by hand: ROS apt repository, nil part with ros-environment packages, ros2-launch script, command-chain."
tags: [no extension, Kilted, package-repositories, nil plugin, build-environment, command-chain, ros2-launch, override-build, non-LTS]
see: ["[[snap-ros2-extensions-bases]]", "[[snap-snapcraft-yaml]]", "[[snap-robot-apps-design]]"]
requires: [ros2-core]
version_notes:
  - "humble: an extension = ROS apt repo + 4 build packages + build-environment ROS_VERSION/ROS_DISTRO + ros2-launch command-chain + PYTHONPATH/ROS_DISTRO/ROS_VERSION; all can be written by hand — https://canonical-robotics.readthedocs-hosted.com/en/latest/how-to-guides/packaging/ros-distributions-with-no-extensions/ (SNAP-V40)"
  - "humble: the official example's YAML is mis-indented (build-packages and override-build under plugin; command not under the app) and says roslaunch for ros2launch; rebuilt here — https://canonical-robotics.readthedocs-hosted.com/en/latest/how-to-guides/packaging/ros-distributions-with-no-extensions/ (SNAP-V31)"
---
# Snap a ROS 2 distro without an extension (e.g. Kilted)

**TL;DR** A ROS 2 extension only writes common YAML for you. For a distro without one (Kilted, non-LTS), write that YAML yourself: add the ROS 2 apt repository, a `nil` part with the ROS workspace packages and the `ros2-launch` script, the ROS variables, and a `command-chain` on each app. `snapcraft expand-extensions` on a Humble snap shows the model to copy.

## What an extension adds
- The ROS apt package repository and its GPG key.
- The build packages `ros-<distro>-ros-environment`, `ros-<distro>-ros-workspace`, `ros-<distro>-ament-index-cpp`, `ros-<distro>-ament-index-python`.
- The build environment `ROS_VERSION`, `ROS_DISTRO`.
- A `command-chain` script that sources the ROS environment before the app's command.

## The same by hand (Kilted values)
Kilted runs on Ubuntu 24.04, so `base: core24`, apt suite `noble` and Python 3.12. Adapted from the official Galactic example [verify: build it on Kilted]:
```yaml
base: core24

# Add the ROS 2 repository
package-repositories:
  - components: [main]
    formats: [deb]
    key-id: C1CF6E31E6BADE8868B172B4F42ED6FBAB17C654
    key-server: keyserver.ubuntu.com
    suites: [noble]
    type: apt
    url: http://repo.ros2.org/ubuntu/main

parts:
  ros2-kilted-extension:
    plugin: nil
    build-packages:
      - ros-kilted-ros-environment
      - ros-kilted-ros-workspace
      - ros-kilted-ament-index-cpp
      - ros-kilted-ament-index-python
    override-build: |
      install -D -m 0755 $SNAP/share/snapcraft/extensions/ros2/launch ${SNAPCRAFT_PART_INSTALL}/snap/command-chain/ros2-launch

  ros-demos:
    after: [ros2-kilted-extension]
    plugin: colcon
    source: https://github.com/ros2/demos.git
    source-branch: kilted
    source-subdir: demo_nodes_cpp
    stage-packages: [ros-kilted-ros2launch]
    # Define the ROS 2 environment variables needed at install and build time
    build-environment:
      - ROS_VERSION: '2'
      - ROS_DISTRO: kilted

apps:
  ros2-talker-listener:
    command-chain: [snap/command-chain/ros2-launch]
    command: opt/ros/kilted/bin/ros2 launch demo_nodes_cpp talker_listener_launch.py
    plugs: [network, network-bind]
    environment:
      PYTHONPATH: $SNAP/opt/ros/kilted/lib/python3.12/site-packages:$SNAP/usr/lib/python3/dist-packages:${PYTHONPATH}
      ROS_DISTRO: kilted
      ROS_VERSION: '2'
```
- `nil` plugin: the part builds nothing, it only installs Debian packages. `build-packages` are used to build and are **not** shipped in the snap.
- `override-build` copies snapcraft's own launcher script (`$SNAP` here is the snapcraft snap) into the part, at `snap/command-chain/ros2-launch`.
- `stage-packages: [ros-<distro>-ros2launch]`: `ros2 launch` is a run-time dependency the demo's `package.xml` does not declare.
- `network` and `network-bind`: a ROS 2 app that talks over topics needs both; other host resources (cameras, GPIO pins, drivers) need their own plugs ([[snap-confinement]]).

## Pitfalls
- Every key of a part (and of an app) needs the same indentation: a key indented under `plugin:` makes the file invalid (the official page has this mistake).
- Keep the Python version in `PYTHONPATH` equal to the base's Python (3.10 on core22, 3.12 on core24).
- The `command` path contains the distro (`opt/ros/kilted/...`): change it together with the rest.

Adapted from the Canonical robotics documentation (CC-BY-SA 3.0).
