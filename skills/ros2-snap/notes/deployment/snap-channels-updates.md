---
id: snap-channels-updates
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "Channels (track/risk/branch), revisions and updates (refresh)"
domain: snap
area: deployment
distro: humble
tested: false
audience: dev
summary: "track/risk/branch channels, latest track, a track per ROS distro, releasing an update, snap info, automatic refresh, snap refresh."
tags: [channels, track, risk, branch, stable, candidate, beta, edge, revision, snap refresh, OTA, delta updates, snap info]
see: ["[[snap-store-publish]]", "[[snap-ci-github-actions]]", "[[snap-confinement]]", "[[snap-ros2-architectures]]"]
requires: [ros2-core]
version_notes:
  - "humble: channel = track/risk/branch; default track latest; branches close after 30 days without new revisions; stable is the default install risk — https://github.com/canonical/snapcraft/blob/main/docs/reference/channels.rst (SNAP-V46)"
  - "humble: snapd refreshes automatically 4 times a day by default (00:00~24:00/4) — https://github.com/canonical/snapd/blob/master/overlord/snapstate/autorefresh.go (SNAP-V46)"
  - "humble: the official update diff still shows name: ros2-talker-listener after the rename: keep the renamed snap — https://canonical-robotics.readthedocs-hosted.com/en/latest/tutorials/snaps-core/distribute-ros-apps-with-snap-store/ (SNAP-V47)"
---
# Channels (track/risk/branch), revisions and updates (refresh)

**TL;DR** A release goes to a **channel**: `<track>/<risk>/<branch>`. Users follow a channel and get its new revisions automatically (snapd checks 4 times a day, with transactional delta updates). To ship an update: change the snap, bump `version`, upload and release to the same channel.

## Channels
| Part | Values | Use |
|---|---|---|
| track | `latest` (default) or tracks granted by the store team | major versions; for ROS: one track per ROS distro under the same name |
| risk | `stable`, `candidate`, `beta`, `edge` | stable promises reliability, edge has the latest features; installs use `stable` by default |
| branch | optional, e.g. `fix-bug123` | short-lived fixes or experiments; closed after 30 days without new revisions, then it follows the next safer risk of the same track |

A `devel` grade snap can only go to `beta` and `edge`.

## Ship an update (talker-listener example)
Switch the launch file to the XML version and bump the version:
```diff
name: yourname-test-ros2-snapstore
-version: '0.1'
+version: '0.2'
[...]
apps:
  ros2-talker-listener:
-  command: opt/ros/humble/bin/ros2 launch demo_nodes_cpp talker_listener.launch.py
+  command: opt/ros/humble/bin/ros2 launch demo_nodes_cpp talker_listener.launch.xml
```
(The official page keeps `name: ros2-talker-listener` in this diff: use the renamed snap.) The version bump is not required, but it helps users.
```bash
snapcraft pack
snapcraft upload --release=latest/stable yourname-test-ros2-snapstore_0.2_amd64.snap
```
Anyone installing from `latest/stable` now gets 0.2.

## Get the update
```bash
snap info yourname-test-ros2-snapstore
```
```text
tracking:  latest/stable
channels:
    latest/stable: 0.2 2023-10-24 (2) 69MB -
    latest/candidate: ↑
    latest/beta:  ↑
    latest/edge:  ↑
    installed:   0.1   (1) 69MB -
```
`↑` means "same as the safer risk above". The device tracks `latest/stable`, has 0.1 installed, and 0.2 is available. snapd refreshes on its own (by default 4 times a day; the timing can be changed); to update now:
```bash
sudo snap refresh yourname-test-ros2-snapstore
yourname-test-ros2-snapstore.ros2-talker-listener
```

## Pitfalls
- Moving revisions between channels (promote, close) works from the CLI (`snapcraft release`, `snapcraft close`) or the "Releases" tab of the web UI.
- Air-gapped robots and proxies need extra setup, not covered by the official guide.
- Several snaps that must stay compatible: tie them with channels or Ubuntu Core validation sets ([[snap-ros2-architectures]]).

Adapted from the Canonical robotics documentation, part 3 of the snaps series (CC-BY-SA 3.0).
