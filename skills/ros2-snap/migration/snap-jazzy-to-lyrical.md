---
id: snap-jazzy-to-lyrical
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "Snaps: Jazzy (core24) → Kilted → Lyrical (core26) changes"
domain: snap
area: migration
distro: humble
tested: false
audience: dev
summary: "Kilted has no snapcraft extension; Lyrical: base core26, experimental ros2-lyrical extension, Snapcraft 9+, Python 3.14, suite resolute."
tags: [migration, Kilted, Lyrical, core26, ros2-lyrical, experimental, Snapcraft 9, Python 3.14, resolute]
see: ["[[snap-humble-to-jazzy]]", "[[snap-ros2-no-extension]]", "[[snap-ros2-extensions-bases]]", "[[core-jazzy-to-lyrical]]"]
requires: [ros2-core]
version_notes:
  - "lyrical: base core26, extension ros2-lyrical is experimental and needs Snapcraft 9+ (SNAPCRAFT_ENABLE_EXPERIMENTAL_EXTENSIONS=1) — https://github.com/canonical/snapcraft/blob/main/docs/reference/extensions/ros-2-extensions.rst (SNAP-V01, SNAP-V10)"
  - "lyrical: Kilted has no extension; build it by hand on core24 (noble) [verify] — https://canonical-robotics.readthedocs-hosted.com/en/latest/how-to-guides/packaging/ros-distributions-with-no-extensions/ (SNAP-V40)"
  - "lyrical: content extensions ros2-lyrical-ros-core/-ros-base/-desktop need Snapcraft 9+ — https://github.com/canonical/snapcraft/blob/main/docs/reference/extensions/ros-2-content-extensions.rst (SNAP-V39)"
---
# Snaps: Jazzy (core24) → Kilted → Lyrical (core26) changes

**TL;DR** Kilted (non-LTS) has no snapcraft extension: snap it by hand. Lyrical uses `base: core26` and the `ros2-lyrical` extension, which is still **experimental** and needs Snapcraft 9 or later. Generic ROS 2 changes: [[core-jazzy-to-lyrical]].

| Item | Jazzy | Kilted | Lyrical |
|---|---|---|---|
| `base` | `core24` | `core24` (Ubuntu 24.04) | `core26` (Ubuntu 26.04) |
| extension | `ros2-jazzy` | none: [[snap-ros2-no-extension]] | `ros2-lyrical` (experimental) |
| Snapcraft | ≥ 7.3 | — | ≥ 9 |
| build command | `snapcraft` | `snapcraft` | `SNAPCRAFT_ENABLE_EXPERIMENTAL_EXTENSIONS=1 snapcraft` |
| ROS apt suite | `noble` | `noble` | `resolute` |
| Python in `PYTHONPATH` | 3.12 | 3.12 | 3.14 |
| content-sharing extensions | `ros2-jazzy-*` (≥ 8) | — | `ros2-lyrical-*` (≥ 9) |
| demo launch file | `talker_listener_launch.py` | same | same |

## Pitfalls
- Experimental extensions can change between Snapcraft releases: pin the snapcraft channel in CI (the reusable workflow has a `snapcraft-channel` input, [[snap-ci-github-actions]]).
- A Lyrical snap needs the `core26` base snap on the device: add it to an Ubuntu Core model ([[snap-ubuntu-core-image]]).
