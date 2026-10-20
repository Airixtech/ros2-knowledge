---
id: snap-daemon
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "Run a snap app as a daemon: service types, restart, logs, start/stop/enable/disable"
domain: snap
area: runtime
distro: humble
tested: false
audience: dev
summary: "daemon: simple/oneshot/forking/notify/dbus, enabled vs active, restart-condition on-failure, snap logs, journalctl unit, snap stop/disable/start/enable."
tags: [daemon, service, systemd, simple, oneshot, restart-condition, snap logs, journalctl, snap stop, snap disable, enabled, active]
see: ["[[snap-confinement]]", "[[snap-robot-apps-design]]", "[[snap-debug-app]]", "[[snap-config-hooks]]"]
requires: [ros2-core]
version_notes:
  - "humble: enabled = started at boot; restart after a failure is the default restart-condition (on-failure; no for oneshot), enabled or not — https://github.com/canonical/snapd/blob/master/wrappers/internal/service_unit_gen.go (SNAP-V04)"
  - "humble: daemon types simple, forking, oneshot, notify and dbus — https://github.com/canonical/snapcraft/blob/main/snapcraft/models/project.py (SNAP-V21)"
  - "humble: systemd unit name snap.<snap>.<app>.service — https://github.com/canonical/snapd/blob/master/snap/info.go (SNAP-V22)"
---
# Run a snap app as a daemon: service types, restart, logs, start/stop/enable/disable

**TL;DR** Add `daemon: simple` to an app and it becomes a systemd service: it starts at boot, runs in the background and stops at shutdown (it can also start on demand through socket activation, the app's `sockets:` key). The daemon setting is per app, so one snap can mix services and plain commands. Read its output with `snap logs`.

## Daemon types
| `daemon:` | Behaviour |
|---|---|
| `simple` | runs as long as the service is active; the most common choice |
| `oneshot` | runs once and exits, notifying systemd |
| `forking` | the command calls `fork()` at start-up and the parent exits when start-up is done (legacy Unix daemons) |
| `notify` | the command signals its state to systemd (needs the `daemon-notify` plug) |
| `dbus` | registers a D-Bus name to notify systemd (needs `bus-name` or `activates-on`) |

## The talker-listener as a service
`daemon` branch of the example repository:
```yaml
apps:
  ros2-talker-listener:
    command: opt/ros/humble/bin/ros2 launch demo_nodes_cpp talker_listener.launch.py
    daemon: simple
    plugs: [network, network-bind]
    extensions: [ros2-humble]
```
```bash
git switch daemon
snapcraft
sudo snap install ros2-talker-listener_0.1_amd64.snap --dangerous
snap info ros2-talker-listener
```
```text
services:
  ros2-talker-listener: simple, enabled, active
installed:    0.1 (x9) 64MB -
```
- `active`: running now, in the background.
- `enabled`: started automatically at boot.
- Restart after a crash is separate: snap services default to `restart-condition: on-failure` (`no` for `oneshot`), whether enabled or not. Change it with `restart-condition:` (`always`, `never`, `on-abnormal`…).

## Logs
```bash
sudo snap logs ros2-talker-listener          # add -f to follow, -n 100 for more lines
sudo journalctl -fu snap.ros2-talker-listener.ros2-talker-listener.service   # -f follow, -u this unit only
```
```text
ros2-talker-listener.ros2-talker-listener[970635]: [talker-1] [INFO] [1657724117.996643358] [talker]: Publishing: 'Hello World: 957'
```
Snap services are systemd units named `snap.<snap>.<app>.service`.

## Control the service
```bash
sudo snap stop ros2-talker-listener      # stops now; still enabled, so it starts again at boot
sudo snap disable ros2-talker-listener   # does not start again
sudo snap start ros2-talker-listener
sudo snap enable ros2-talker-listener
```
More in the snapcraft service-management documentation; stop scripts and orchestration: [[snap-robot-apps-design]].

## Pitfalls
- A daemon runs as root: its `$HOME` and `SNAP_USER_DATA` are root's, not yours ([[snap-env-data]]).
- A daemon's output is not on your terminal: check `snap logs` first when the robot misbehaves ([[snap-debug-app]]).
