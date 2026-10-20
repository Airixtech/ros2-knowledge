---
id: snap-debug-app
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "Debug an installed snap: logs, snap run --shell, libraries, connections, snappy-debug"
domain: snap
area: runtime
distro: humble
tested: false
audience: dev
summary: "snap logs and journalctl, /snap/<snap>/current, snap run --shell, ldd and LD_LIBRARY_PATH, snap connections/connect, snappy-debug for AppArmor denials."
tags: [debug, snap logs, journalctl, snap run --shell, ldd, LD_LIBRARY_PATH, snap connections, snap connect, snappy-debug, AppArmor]
see: ["[[snap-debug-build]]", "[[snap-daemon]]", "[[snap-confinement]]", "[[snap-env-data]]"]
requires: [ros2-core]
version_notes:
  - "humble: snap logs -n/-f, journalctl -u snap.<snap>.<app>.service, snap run --shell, ldd, snap connect/disconnect, snappy-debug — https://canonical-robotics.readthedocs-hosted.com/en/latest/explanations/snaps/debug-a-snap-application/ (SNAP-V44)"
---
# Debug an installed snap: logs, snap run --shell, libraries, connections, snappy-debug

**TL;DR** Debug the **packaging**, not your code (debug the code before snapping it). Order: read the logs, look at the snap's files, open a shell inside the snap's environment, check the interface connections, and catch confinement denials with `snappy-debug`.

## 1. Logs
```bash
sudo snap logs SNAP_NAME.DAEMON_NAME -n 100   # last 100 lines; -f to follow
sudo snap logs SNAP_NAME -f                   # all daemons of the snap
journalctl -u snap.SNAP_NAME.DAEMON_NAME.service
```
CLI apps print to the terminal; daemons are systemd services, so their output (your launch files' output) is only in the logs. When the robot misbehaves, this is the first step.

## 2. The snap's files
```bash
ls /snap/SNAP_NAME/current        # etc/ lib/ meta/ opt/ usr/ var/
```
A strict snap sees only this tree and its data directories ([[snap-env-data]]); a missing file is often visible here.

## 3. A shell inside the snap
```bash
snap run --shell SNAP_NAME.APP_NAME
```
It opens a shell with the app's exact environment, `command-chain` included, with the snap's permissions, in the current directory. From there, run the app by hand, or check variables, paths and permissions. A missing library:
```bash
ldd $SNAP/opt/ros/humble/lib/librmw.so          # "not found" → $LD_LIBRARY_PATH is wrong
find $SNAP -type f -name "librmw.so"            # where the library really is
```

## 4. Interfaces
```bash
snap connections SNAP_NAME              # plug and slot per interface
sudo snap connect SNAP_NAME:camera :camera
sudo snap disconnect SNAP_NAME:camera
```
A connected interface lists both a plug and a slot. Some interfaces auto-connect, others must be connected by hand; for a store snap you can request auto-connection on the snapcraft forum.

## 5. Confinement denials
```bash
sudo snap install snappy-debug
snappy-debug          # then run the app in another terminal
```
It watches the system log for AppArmor policy violations, shows them readably and suggests fixes:
```text
mars 02 17:27:39 user-computer audit[721546]: AVC apparmor="DENIED" operation="open" profile="snap.SNAP_NAME" name="/dev/video0" pid=721546 comm="APP" requested_mask="c" denied_mask="c" fsuid=1000 ouid=1000
```
Here `/dev/video0` was denied: the snap lacks the `camera` plug, or it is not connected.

## Pitfalls
- `snap run --shell` keeps the snap's confinement: a command that fails there fails for the app too.
- Shell variables set by hand in that shell do not change the app: fix them in `snapcraft.yaml` (`environment:`) and rebuild.

Adapted from the Canonical robotics documentation (CC-BY-SA 3.0).
