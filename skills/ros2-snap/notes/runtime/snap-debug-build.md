---
id: snap-debug-build
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "Debug the build of a snap: build instance, --debug, --shell-after, snapcraft try"
domain: snap
area: runtime
distro: humble
tested: false
audience: dev
summary: "Inside the build instance (/root: parts, stage, prime, project), snapcraft --debug on errors, --shell-after, snapcraft try with snap try prime."
tags: [debug, snapcraft --debug, shell-after, snapcraft try, snap try, parts, stage, prime, build instance, LXD]
see: ["[[snap-build-install-run]]", "[[snap-debug-app]]", "[[snap-install-tools]]", "[[core-colcon-errors]]"]
requires: [ros2-core]
version_notes:
  - "humble: snapcraft --debug, --shell-after and snapcraft try exist on core22; build instance dirs parts, stage, prime, project — https://github.com/canonical/snapcraft/blob/main/snapcraft/commands/core22/lifecycle.py (SNAP-V43)"
---
# Debug the build of a snap: build instance, --debug, --shell-after, snapcraft try

**TL;DR** snapcraft builds inside an isolated instance (an LXD container or a VM; the host with `--destructive-mode`). When a build fails, step into that instance with `snapcraft --debug`; when the result is wrong, use `--shell-after`. `snapcraft try` + `snap try prime` lets you edit the files of a built snap without rebuilding.

## The build instance
The working directory is `/root`:
```text
├── parts/
├── prime/
├── project/
├── snap/
└── stage/
```
| Directory | Lifecycle step | What to check |
|---|---|---|
| `project/` | — | your project, mounted from where you ran `snapcraft` |
| `parts/<part>/` | pull, build | a copy of the sources and the build artefacts: the ROS workspace with `build/`, `install/`, `log/` |
| `stage/` | stage | everything built and installed, plus `stage-packages` and the `depend`/`exec_depend` of your `package.xml` |
| `prime/` | prime | exactly what the snap will contain (often `stage` minus headers) |
| `snap/` | — | snaps installed in the instance: the base and the parts' `build-snaps` |

The instance itself builds the parts, so build-time APT packages are installed there: `apt` and `dpkg` show what is available.

## Step in
```bash
snapcraft --debug         # on the first error, open a shell in /root/project inside the instance
snapcraft --shell-after   # build completely, then open a shell
```
The shell is not set up for any part: export the variables or source the scripts the part would use. Keep `--debug` on while developing a snap.

## Try without rebuilding
```bash
snapcraft try             # build up to prime and expose prime/ in the project directory
snap try prime            # install from that directory
```
Edit `prime/` (a launch file, a Python script…) and test again at once.

## Pitfalls
- A package that builds but has no `install` rule is missing from `stage/` and `prime/`: check there first ([[snap-snapcraft-yaml]]).
- Colcon errors inside a part look like normal colcon errors: read `parts/<part>/build/log` ([[core-colcon-errors]]).

Adapted from the Canonical robotics documentation (CC-BY-SA 3.0).
