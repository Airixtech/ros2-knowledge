---
id: snap-install-tools
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "Install snapd, snapcraft and the LXD build provider"
domain: snap
area: basics
distro: humble
tested: false
audience: dev
summary: "apt install snapd, snap help, snap install snapcraft --classic, LXD as default build provider (lxd group, lxd init --auto), --destructive-mode."
tags: [snapd, snapcraft, LXD, Multipass, build provider, destructive-mode, snap help, classic]
see: ["[[snap-overview]]", "[[snap-build-install-run]]", "[[snap-debug-build]]"]
requires: [ros2-core]
version_notes:
  - "humble: snapcraft needs a build provider: LXD by default on Linux since Snapcraft 7 (snap install lxd, lxd group, lxd init --auto); Multipass on macOS/Windows — https://github.com/canonical/snapcraft/blob/main/docs/how-to/set-up-snapcraft.rst (SNAP-V06)"
  - "humble: snapcraft is installed as a classic snap; the old Debian package is not updated — https://github.com/canonical/snapcraft/blob/main/docs/how-to/set-up-snapcraft.rst (SNAP-V07)"
  - "humble: the current guide asks Ubuntu 22.04 LTS or similar as the development host (16.04 is ESM); running a snap only needs snapd — https://canonical-robotics.readthedocs-hosted.com/en/latest/tutorials/snaps-core/packaging-ros-application-as-snap/ (SNAP-V05)"
---
# Install snapd, snapcraft and the LXD build provider

**TL;DR** `snapd` runs snaps, `snapcraft` builds them, and snapcraft builds inside an isolated **LXD** container by default. On a fresh Ubuntu 22.04: install snapcraft as a classic snap, install and initialise LXD, add your user to the `lxd` group.

## snapd (run snaps)
`snapd` comes pre-installed on most Ubuntu flavours; elsewhere:
```bash
sudo apt update
sudo apt install snapd
snap --version
snap help
```
`snap help` groups the commands:
```text
Commonly used commands can be classified as follows:
Basics: find, info, install, remove, list
...more: refresh, revert, switch, disable, enable, create-cohort
History: changes, tasks, abort, watch
Daemons: services, start, stop, restart, logs
Permissions: connections, interface, connect, disconnect
Configuration: get, set, unset, wait
App Aliases: alias, aliases, unalias, prefer
Account: login, logout, whoami
Snapshots: saved, save, check-snapshot, restore, forget
Device: model, reboot, recovery
... Other: warnings, okay, known, ack, version
Development: download, pack, run, try
```

## snapcraft (build snaps)
snapcraft builds, uploads and shares snaps. If an old Debian `snapcraft` is installed, remove it first (it is no longer updated):
```bash
sudo apt remove snapcraft --purge
sudo snap install snapcraft --classic
```
`--classic` is a confinement type: snapcraft needs normal access to the system ([[snap-confinement]]).

## LXD (where snapcraft builds)
For core22 and newer bases, snapcraft builds in an LXD container on Linux (Multipass VMs on macOS and Windows). Set LXD up once:
```bash
sudo snap install lxd
sudo usermod -a -G lxd $USER      # log out and back in
groups $USER                      # must list lxd
sudo lxd init --auto
```
Other providers: `snapcraft --use-lxd`, `SNAPCRAFT_BUILD_ENVIRONMENT=<provider>` or `snap set snapcraft provider=<provider>`. `--destructive-mode` builds directly on the host, without a container: not recommended (snapcraft cannot control the environment and adds package repositories to your machine); the host must then match the base (Ubuntu 22.04 for core22).

## Pitfalls
- Building in a container (Docker, a CI runner) needs systemd, snapd and snaps to run in it, or `--destructive-mode` on a matching Ubuntu.
- Without the `lxd` group, the first build fails to reach the LXD daemon.
