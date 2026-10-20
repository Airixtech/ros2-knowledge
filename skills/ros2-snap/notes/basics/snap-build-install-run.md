---
id: snap-build-install-run
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "Build, install and run a snap: lifecycle steps, --devmode, --dangerous, snap info"
domain: snap
area: basics
distro: humble
tested: false
audience: dev
summary: "snapcraft (= snapcraft pack) pull/build/stage/prime, the .snap file, snap install --devmode or --dangerous, running the app, snap info."
tags: [snapcraft pack, pull, build, stage, prime, snap install, devmode, dangerous, snap info, .snap]
see: ["[[snap-snapcraft-yaml]]", "[[snap-install-tools]]", "[[snap-confinement]]", "[[snap-debug-build]]"]
requires: [ros2-core]
version_notes:
  - "humble: ros2-humble is not experimental since Snapcraft 7.3: build with snapcraft (= snapcraft pack), no SNAPCRAFT_ENABLE_EXPERIMENTAL_EXTENSIONS=1 — https://github.com/canonical/snapcraft/blob/main/snapcraft/extensions/ros2_humble.py (SNAP-V01)"
  - "humble: lifecycle steps pull, build, stage, prime (+ pack) — https://github.com/canonical/snapcraft/blob/main/docs/explanation/parts-lifecycle.rst (SNAP-V14)"
  - "humble: 'Unable to determine library dependencies' warnings for ROS libraries had no impact in the course; the official how-to calls missing-library warnings false positives — https://github.com/canonical/snapcraft/blob/main/docs/how-to/integrations/craft-an-ros-2-app.rst (SNAP-V15)"
  - "humble: --devmode installs an unconfined snap, --dangerous a local unsigned file; snap info lists commands and services — https://canonical-robotics.readthedocs-hosted.com/en/latest/tutorials/snaps-core/packaging-ros-application-as-snap/ (SNAP-V16)"
  - "lyrical: ros2-lyrical is still experimental: build with SNAPCRAFT_ENABLE_EXPERIMENTAL_EXTENSIONS=1 snapcraft — https://github.com/canonical/snapcraft/blob/main/snapcraft/extensions/ros2_lyrical.py (SNAP-V01)"
---
# Build, install and run a snap: lifecycle steps, --devmode, --dangerous, snap info

**TL;DR** Run `snapcraft` at the root of the project (where `snap/` is). It builds the parts in an LXD container and writes `<name>_<version>_<arch>.snap`. Install that file with `--devmode` (not confined yet) or `--dangerous` (confined but not signed by the store), then run the app by its name.

## Build
```bash
cd ~/default_ws/src/ros2-humble-talker-listener-snap
snapcraft                 # same as: snapcraft pack
```
```text
Created snap package ros2-talker-listener_0.1_amd64.snap
```
Steps of each part:
1. **pull**: download or retrieve the components needed to build the part.
2. **build**: build the part from what was pulled, as its plugin says.
3. **stage**: copy the built components into the staging area, where all the parts first come together.
4. **prime**: copy the staged components to their final place in the snap; files needed only at build time stay behind.

The first build pulls all the ROS dependencies and takes a while. A rebuild is much faster: unchanged steps are skipped ("Already done"). A warning like `Unable to determine library dependencies for 'opt/ros/humble/local/lib/python3.10/dist-packages/action_msgs/libaction_msgs__rosidl_generator_py.so'` comes from the library check (`ldd`) and does not affect the snap.

## Install and run
```bash
sudo snap install ros2-talker-listener_0.1_amd64.snap --devmode   # confinement: devmode
ros2-talker-listener                                              # talker and listener exchange messages; Ctrl+C stops
snap info ros2-talker-listener
```
```text
name:      ros2-talker-listener
summary:   ROS 2 Talker/Listener Example
publisher: –
license:   unset
description: |
  This example launches a ROS 2 talker and listener.
commands:
  - ros2-talker-listener
refresh-date: today at 10:54 CEST
installed:    0.1 (x1) 64MB devmode
```
The host needs neither Ubuntu 22.04 nor ROS 2: the snap carries its dependencies and its `core22` base, so it installs on any distro with snapd. A snap can expose as many apps (commands) as needed; `snap info` lists them.

| Install flag | When |
|---|---|
| `--devmode` | the snap declares `confinement: devmode` |
| `--dangerous` | a local, strictly confined snap not signed by a store ([[snap-confinement]]) |
| none | the snap comes from the Snap Store ([[snap-store-publish]]) |

## Pitfalls
- Run `snapcraft` where `snap/snapcraft.yaml` is; it looks for that path.
- [changed in Lyrical: `ros2-lyrical` is still experimental: `SNAPCRAFT_ENABLE_EXPERIMENTAL_EXTENSIONS=1 snapcraft`.] Older guides use this variable for Humble too: since Snapcraft 7.3 it is not needed.
- Build problems: [[snap-debug-build]].
