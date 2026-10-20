---
id: snap-store-publish
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "Publish a ROS 2 snap on the Snap Store: account, login, register, upload, release"
domain: snap
area: deployment
distro: humble
tested: false
audience: dev
summary: "Ubuntu One account, snapcraft login, register a unique name, upload (automated review), release to latest/stable, visibility, install from the store."
tags: [Snap Store, snapcraft login, snapcraft register, snapcraft upload, snapcraft release, Ubuntu One, unlisted, private, dedicated store]
see: ["[[snap-channels-updates]]", "[[snap-ci-github-actions]]", "[[snap-confinement]]", "[[snap-ubuntu-core-image]]"]
requires: [ros2-core]
version_notes:
  - "humble: snapcraft login (on the host), register, upload (automated review), release <snap> <revision> <channel>, upload --release=<channel>; also status, revisions, close — https://github.com/canonical/snapcraft/tree/main/snapcraft/commands (SNAP-V45)"
  - "humble: the official guide asks Ubuntu 20.04 'still under maintenance'; 20.04 is ESM since May 2025: use 22.04 LTS or later — https://ubuntu.com/blog/ubuntu-20-04-lts-end-of-life-standard-support-is-coming-to-an-end-heres-how-to-prepare (SNAP-V33)"
---
# Publish a ROS 2 snap on the Snap Store: account, login, register, upload, release

**TL;DR** Give the snap a unique name, log in with an Ubuntu One account, `snapcraft register` the name, `snapcraft upload` the `.snap` (it goes through automated review) and `snapcraft release` it to a channel. From then on, `sudo snap install <name>` works anywhere, without `--dangerous`.

## Requirements
- An Ubuntu Desktop 22.04 LTS or later (the official guide still says 20.04, out of standard support since May 2025); the guide cannot be followed in a container or a headless environment.
- LXD and snapcraft installed ([[snap-install-tools]]).
- An [Ubuntu One](https://login.ubuntu.com/+description) account for the store (snapcraft.io/account → "I don't have an Ubuntu One account").
- A strictly confined snap: the guide reuses the `confined` branch of the talker-listener ([[snap-confinement]]).

## 1. A unique name, then a local test
```bash
git clone https://github.com/ubuntu-robotics/ros2-humble-talker-listener-snap.git -b confined
```
Every snap on the public store needs a unique name; prefix it with your pseudonym in `snap/snapcraft.yaml`:
```diff
- name: ros2-talker-listener
+ name: yourname-test-ros2-snapstore
```
```bash
snapcraft pack       # a new name rebuilds from the beginning
sudo snap install yourname-test-ros2-snapstore_0.1_amd64.snap --dangerous
yourname-test-ros2-snapstore.ros2-talker-listener
sudo snap remove yourname-test-ros2-snapstore
```
The command is now `<snap>.<app>` because the snap and the app no longer share a name.

## 2. Log in and register
```bash
snapcraft login                                # on the host, not in a container or headless server
snapcraft register yourname-test-ros2-snapstore
```
`register` asks you to confirm that users will expect this name to stand for your snap. The web UI does the same: snapcraft.io → account menu → "My published snaps" → "Register a snap name".

## 3. Upload and release
```bash
snapcraft upload yourname-test-ros2-snapstore_0.1_amd64.snap
snapcraft release yourname-test-ros2-snapstore 1 latest/stable     # revision 1 → track latest, risk stable
# or both at once:
snapcraft upload --release=latest/stable yourname-test-ros2-snapstore_0.1_amd64.snap
```
The upload triggers automated security and integrity reviews; the snap becomes installable when they pass. An uploaded revision is not public until it is released to a channel ([[snap-channels-updates]]). `snapcraft status <snap>` and `snapcraft revisions <snap>` show what is where; the "Releases" tab of the web UI does the same.

## 4. Visibility and install
- A snap can be public, private or unlisted: snapcraft.io/snaps → your snap → "Settings" → "Unlisted" for a test snap.
- Install it like any store snap; `--dangerous` is no longer needed, because the store reviewed and signed it:
```bash
sudo snap install yourname-test-ros2-snapstore
```
- The same command deploys it on a robot fleet. For production-grade device images: [[snap-ubuntu-core-image]].

## Pitfalls
- A `devel` grade snap cannot be released to `candidate` or `stable` ([[snap-confinement]]).
- Dedicated (private, commercial) Snap Stores add their own features; this note covers the public store.
- Manual steps can move to CI ([[snap-ci-github-actions]]).

Adapted from the Canonical robotics documentation, part 3 of the snaps series (CC-BY-SA 3.0).
