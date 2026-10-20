---
id: snap-env-data
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "Snap environment variables and data directories ($SNAP, SNAP_DATA, SNAP_COMMON…)"
domain: snap
area: runtime
distro: humble
tested: false
audience: dev
summary: "$SNAP (read-only snap root), $SNAP_INSTANCE_NAME, SNAP_DATA/SNAP_COMMON/SNAP_USER_DATA/SNAP_USER_COMMON: where a snap may write, and what survives updates."
tags: [SNAP, SNAP_INSTANCE_NAME, SNAP_DATA, SNAP_COMMON, SNAP_USER_DATA, SNAP_USER_COMMON, SNAP_REAL_HOME, ROS_HOME, refresh, revert]
see: ["[[snap-config-hooks]]", "[[snap-daemon]]", "[[snap-debug-app]]", "[[snap-ros2-extensions-bases]]"]
requires: [ros2-core]
version_notes:
  - "humble: on refresh snapd copies the old revision's SNAP_DATA/SNAP_USER_DATA into the new revision (old copy kept for revert); the common dirs are shared and never copied — the official page says the opposite — https://github.com/canonical/snapd/blob/master/overlord/snapstate/backend/copydata.go (SNAP-V29)"
---
# Snap environment variables and data directories ($SNAP, SNAP_DATA, SNAP_COMMON…)

**TL;DR** An installed snap is read-only (`$SNAP`). It may only write to its data directories: per revision (`SNAP_DATA`, `SNAP_USER_DATA`) or shared by all revisions (`SNAP_COMMON`, `SNAP_USER_COMMON`). Use these variables instead of fixed paths. Examples below: snap `hello-world`, revision 27.

## Identify the snap
| Variable | Value | Use |
|---|---|---|
| `SNAP` | `/snap/hello-world/27` (also `/snap/hello-world/current`) | where the snap is mounted, read-only: find an executable, a library or a config file of the snap; extend `$LD_LIBRARY_PATH` |
| `SNAP_INSTANCE_NAME` | `hello-world`, or the instance name of a parallel install | refer to *this* instance, e.g. from a hook: `snapctl restart $SNAP_INSTANCE_NAME.MY_APP` |

`SNAP` is set both by snapd (run time) and by snapcraft (build time).

## Where a snap can write
| Variable | Path | Per revision | Writable by | Other snaps |
|---|---|---|---|---|
| `SNAP_USER_DATA` | `$HOME/snap/hello-world/27` | yes | the user | no |
| `SNAP_USER_COMMON` | `$HOME/snap/hello-world/common` | no (shared) | the user | no |
| `SNAP_DATA` | `/var/snap/hello-world/27` | yes | root (readable by all) | no |
| `SNAP_COMMON` | `/var/snap/hello-world/common` | no (shared) | root (readable by all) | no |
| `SNAP_REAL_HOME` | the user's real home | no | the user, with the `home` interface | yes |

- On a refresh, snapd **copies** the data of the old revision into the new revision's directories, and keeps the old copy for `snap revert`. So per-revision data is still there after an update, and a revert brings back the old version's own copy.
- The `common` directories are shared by all revisions and are never copied or rolled back.
- `SNAP_USER_*` depend on the user: for daemons and commands run with `sudo`, `$HOME` is `/root`.

## What goes where
- Per revision (`SNAP_DATA`, `SNAP_USER_DATA`): files that must match the version and roll back with it: revision-specific configuration, logs, files created at run time.
- Shared (`SNAP_COMMON`, `SNAP_USER_COMMON`): files that must survive every update and revert unchanged: maps, recorded data, large caches.
- The `ros2-humble` extension sets `ROS_HOME=$SNAP_USER_DATA/ros`, so ROS logs land in the user's per-revision directory.

## Pitfalls
- Writing next to the executable (`$SNAP/...`) fails: the snap is read-only.
- A daemon writing to `SNAP_USER_DATA` writes into root's home, not yours.
- Large data in a per-revision directory is copied at every refresh: keep it in a `common` directory.

Adapted from the Canonical robotics documentation (CC-BY-SA 3.0); refresh behaviour from snapd.
