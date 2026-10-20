---
id: snap-ci-github-actions
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "Build and publish a ROS 2 snap with GitHub Actions (track and risk)"
domain: snap
area: deployment
distro: humble
tested: false
audience: dev
summary: "Reusable snap workflow (snap-track, snap-risk, snapstore-login) or a manual one: action-build, install test, artifacts v4, action-publish, export-login."
tags: [GitHub Actions, CI, CD, canonical/action-build, canonical/action-publish, robotics-actions-workflows, export-login, SNAPCRAFT_STORE_CREDENTIALS, edge, candidate]
see: ["[[snap-store-publish]]", "[[snap-channels-updates]]", "[[core-testing-ci-docker]]"]
requires: [ros2-core]
version_notes:
  - "humble: artifact actions v3 stopped working on GitHub.com on 2025-01-30 (use v4+); snapcore/action-build and action-publish now live at canonical/ (v1); key workflow_dispatch is lower case — https://github.blog/changelog/2024-04-16-deprecation-notice-v3-of-the-artifact-actions/ (SNAP-V30)"
  - "humble: reusable workflow inputs snap-track (latest), snap-risk (edge, candidate on tags), secret snapstore-login; the track must exist — https://github.com/canonical/robotics-actions-workflows/blob/main/.github/workflows/snap.yaml (SNAP-V41)"
  - "humble: snapcraft export-login --snaps=<snap> --acls package_access,package_push,package_update,package_release <file>; SNAPCRAFT_STORE_CREDENTIALS — https://github.com/canonical/snapcraft/blob/main/snapcraft/commands/account.py (SNAP-V42)"
---
# Build and publish a ROS 2 snap with GitHub Actions (track and risk)

**TL;DR** Keep deployment in sync with development: on every push to `main` build the snap, test that it installs and runs, and publish it to `edge`; on a tag, publish to `candidate`; promote to `stable` by hand after testing. The maintained way is Canonical's reusable workflow; the manual workflow below shows each step.

## Store credentials (both ways)
```bash
snapcraft export-login --snaps=my-ros2-snap --acls package_access,package_push,package_update,package_release exported.txt
```
It asks you to log in and writes a secret file. Store its content as a repository secret (Settings → Secrets → Actions → New repository secret).

## Option 1: reusable workflow (recommended)
`.github/workflows/snap.yaml`:
```yaml
jobs:
  snap:
    permissions:
      contents: read
    uses: canonical/robotics-actions-workflows/.github/workflows/snap.yaml@main
    with:
      snap-risk: beta          # optional; default: edge on pushes, candidate on tags
      snap-track: "5.x"        # optional; default: latest (the track must exist on the store)
    secrets:
      snapstore-login: ${{ secrets.SNAPSTORE_LOGIN }}
```
- Default channels: `latest/edge` on pushes, `latest/candidate` on tags.
- `snap-risk` overrides that rule completely: tag runs then also go to the given risk.
- `snap-track` keeps the edge/candidate rule on that track (`5.x/edge`, `5.x/candidate`); set both for a fixed channel. A new track is requested on the store-requests forum.
- All snaps built from one `git-ref` in a run go to the same channel. Without the `snapstore-login` secret the snap is built and tested, but not published.

## Option 2: manual workflow
Updated from the official 2022 example (artifact actions v4, actions under `canonical/`):
```yaml
name: snap
on:
  push:
    tags:
      - '*'
    branches:
      - main
  pull_request:
    branches:
      - main
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      snap-file: ${{ steps.build-snap.outputs.snap }}
    steps:
    - uses: actions/checkout@v4
    - uses: canonical/action-build@v1
      id: build-snap
    # Make sure the snap is installable
    - run: |
        sudo snap install --dangerous ${{ steps.build-snap.outputs.snap }}
    # Do some testing with the snap
    - run: |
        my-ros2-snap.my-launch --print-description
    - uses: actions/upload-artifact@v4
      with:
        name: my-ros2-snap
        path: ${{ steps.build-snap.outputs.snap }}

  publish:
    if: github.ref == 'refs/heads/main' || startsWith(github.ref, 'refs/tags/')
    runs-on: ubuntu-latest
    needs: build
    steps:
    - uses: actions/download-artifact@v4
      with:
        name: my-ros2-snap
        path: .
    - uses: canonical/action-publish@v1
      env:
        SNAPCRAFT_STORE_CREDENTIALS: ${{ secrets.STORE_LOGIN }}
      with:
        snap: ${{needs.build.outputs.snap-file}}
        release: ${{ startsWith(github.ref, 'refs/tags/') && 'candidate' || 'edge'}}
```
- Triggers: pushes and tags on `main`, pull requests against `main`, and `workflow_dispatch` (manual run from the API or the web).
- `build` job: check out, build with `action-build` (its output `snap` is the file name), install it with `--dangerous`, smoke-test it, upload it as an artifact (also downloadable from the run's page). The test here runs the snap's launch app with `--print-description`, which only prints the launch description: a minimal check; add real tests.
- `publish` job: runs only on `main` or a tag and only after `build` succeeds (`needs: build`); downloads the artifact to `.` and publishes it.

## Pitfalls
- `actions/upload-artifact@v3` / `download-artifact@v3` (still in the official page) fail on GitHub.com since 2025-01-30.
- YAML keys are case-sensitive: `Workflow_dispatch` (a typo in the official breakdown) is not a trigger.
- The exported login is a secret: never commit `exported.txt`.
- Real-world example with CI: the [ros-snaps-examples](https://github.com/ubuntu-robotics/ros-snaps-examples) repository.

Adapted from the Canonical robotics documentation (CC-BY-SA 3.0).
