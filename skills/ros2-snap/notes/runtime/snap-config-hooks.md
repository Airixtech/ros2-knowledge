---
id: snap-config-hooks
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "Snap configuration and hooks: snap set/get, snapctl, install and configure hooks"
domain: snap
area: runtime
distro: humble
tested: false
audience: dev
summary: "snap/hooks/ scripts (install, configure, post-refresh…), snap set/get, snapctl get/set/stop/start; validate a parameter and restart the daemons."
tags: [hooks, configure hook, install hook, post-refresh, snapctl, snap set, snap get, configuration, parameters, gadget defaults]
see: ["[[snap-daemon]]", "[[snap-env-data]]", "[[snap-ubuntu-core-image]]", "[[core-param-api]]"]
requires: [ros2-core]
version_notes:
  - "humble: hooks live in snap/hooks/ (install, configure, pre-refresh, post-refresh, remove, interface hooks…); snapctl get/set/start/stop/restart; configuration survives updates — https://canonical-robotics.readthedocs-hosted.com/en/latest/explanations/snaps/snap-configurations-and-hooks/ (SNAP-V37)"
  - "humble: reject a value with exit 1 (the official example uses return 1 at the top level of the script, unspecified in POSIX sh) — https://pubs.opengroup.org/onlinepubs/9799919799/utilities/V3_chap02.html#return (SNAP-V32)"
---
# Snap configuration and hooks: snap set/get, snapctl, install and configure hooks

**TL;DR** A snap exposes parameters (e.g. which LIDAR device to use) through `snap set` / `snap get`. Every `snap set` runs the snap's `configure` hook, a script in `snap/hooks/` that validates the value and restarts the services. Inside the snap, `snapctl` reads and writes the same configuration. It is the snap version of a ROS dynamic parameter callback ([[core-param-api]]).

## Hooks
A hook is an executable that snapd runs inside the snap's confined environment when something happens. Typical uses: a data migration after an upgrade, or reacting to `snap set` / `snap unset`. Every file in `snap/hooks/` (usually POSIX shell scripts, named after the hook) is imported into the snap. Hooks get no arguments; they talk to snapd with `snapctl` (parameters, interface connections, control of the snap's daemons).

Available hooks: `install`, `configure`, `pre-refresh`, `post-refresh`, `remove`, interface hooks, `gate-auto-refresh`, `full-disk-encryption`, `install-device`, `prepare-device`.
```bash
chmod +x snap/hooks/*     # hooks must be executable
```

## Configuration from outside and inside
```bash
sudo snap set mysnap myconfig=2
sudo snap get mysnap myconfig        # 2
sudo snap get -d snapcraft           # all options as JSON, e.g. {"provider": "lxd"}
snapctl get myconfig                 # inside the snap (hooks, apps)
```

## Default value + validation + restart
`snap/hooks/install` (runs once, at install):
```bash
#!/bin/sh -e
# set default configuration value
snapctl set myconfig=false
```
`snap/hooks/configure` (runs after every `snap set`):
```bash
#!/bin/sh -e
MYCONFIG="$(snapctl get myconfig)"

case "$MYCONFIG" in
        "true") ;;
        "false") ;;
        *)
            >&2 echo "'$MYCONFIG is not a supported value for myconfig." \
        "Possible values are true, false"
            exit 1
            ;;
esac

snapctl stop "$SNAP_INSTANCE_NAME"
snapctl start "$SNAP_INSTANCE_NAME"
```
A failing configure hook (`exit 1`) makes `snap set` fail with the message. The official example uses `return 1`, which POSIX leaves unspecified outside a function: use `exit 1`. The apps then read the value with `snapctl get myconfig`.

## Pitfalls
- Configuration is kept over updates; write a `post-refresh` hook if an update must migrate or reset parameters.
- `snapctl stop/start "$SNAP_INSTANCE_NAME"` restarts all the snap's services; `snapctl restart "$SNAP_INSTANCE_NAME.<app>"` restarts one ([[snap-env-data]]).
- On Ubuntu Core, the gadget snap can preset these values on the first boot ([[snap-ubuntu-core-image]]).

Adapted from the Canonical robotics documentation (CC-BY-SA 3.0).
