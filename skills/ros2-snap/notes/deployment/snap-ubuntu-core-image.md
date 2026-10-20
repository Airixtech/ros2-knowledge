---
id: snap-ubuntu-core-image
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "Ubuntu Core for robots: model assertion, signing, gadget defaults and connections, image"
domain: snap
area: deployment
distro: humble
tested: false
audience: dev
summary: "Ubuntu Core robot image: model JSON with your snaps and core22, create-key/register-key, snap sign, ubuntu-image, gadget defaults/connections."
tags: [Ubuntu Core, model assertion, snap sign, snapcraft create-key, register-key, ubuntu-image, gadget snap, gadget.yaml, defaults, connections, validation set]
see: ["[[snap-ros2-architectures]]", "[[snap-config-hooks]]", "[[snap-store-publish]]", "[[snap-overview]]"]
requires: [ros2-core]
version_notes:
  - "humble: image pipeline model → create-key/register-key → snap sign → ubuntu-image snap; gadget defaults applied when each snap installs (system: at once), connections on first boot only — https://documentation.ubuntu.com/core/tutorials/build-your-first-image/ (SNAP-V48)"
  - "humble: Ubuntu Core: snaps only, automatic transactional updates with rollback, delta updates, full disk encryption — https://canonical-robotics.readthedocs-hosted.com/en/latest/explanations/ubuntu-core/ (SNAP-V49)"
---
# Ubuntu Core for robots: model assertion, signing, gadget defaults and connections, image

**TL;DR** Ubuntu Core is the all-snaps Ubuntu for embedded devices: it updates itself and its apps transactionally, rolls back failed updates, and supports full disk encryption. A custom robot image is built from a signed **model assertion** that lists every snap (gadget, kernel, base, snapd, your ROS 2 snaps and the bases they need), using `ubuntu-image`. The gadget snap presets configuration and interface connections at the first boot.

## Steps (current tutorial: Ubuntu Core 26 on a Raspberry Pi)
1. Account: an Ubuntu One account; `snapcraft export-login credentials.txt` and `snapcraft whoami` give the account id used in the model.
2. Model: a JSON file; `authority-id` and `brand-id` = your account id, `timestamp` = a time after your key was created.
3. Key: create and register a signing key.
4. Sign: `snap sign` turns the JSON into a model assertion.
5. Build: `ubuntu-image` downloads the listed snaps and writes a bootable image.
6. Flash and boot (e.g. Raspberry Pi Imager), configure the network, connect over SSH.

## Model (shortened)
```json
{
    "type": "model",
    "series": "16",
    "model": "ubuntu-core-26-pi-arm64",
    "architecture": "arm64",
    "authority-id": "<your account id>",
    "brand-id": "<your account id>",
    "timestamp": "2026-05-07T08:42:32+00:00",
    "base": "core26",
    "grade": "signed",
    "snaps": [
        {"name": "pi", "type": "gadget", "default-channel": "26/stable", "id": "YbGa9O3dAXl88YLI6Y1bGG74pwBxZyKg"},
        {"name": "pi-kernel", "type": "kernel", "default-channel": "26/stable", "id": "jeIuP6tfFrvAdic8DMWqHmoaoukAPNbJ"},
        {"name": "core26", "type": "base", "default-channel": "latest/stable", "id": "cUqM61hRuZAJYmIS898Ux66VY61gBbZf"},
        {"name": "snapd", "type": "snapd", "default-channel": "latest/stable", "id": "PMrrV4ml8uWuEUDBT8dSGnKUYbevVhc4"},
        {"name": "console-conf", "type": "app", "default-channel": "26/stable", "id": "ASctKBEHzVt3f1pbZLoekCvcigRjtuqw"},
        {"name": "<your-ros2-snap>", "type": "app", "default-channel": "latest/stable", "id": "<snap id from snap info>"},
        {"name": "core22", "type": "base", "default-channel": "latest/stable", "id": "amcUKQILKXHHTlmSa7NMdnXSx02dNeeT"}
    ]
}
```
List the base of every app snap: a Humble snap needs `core22` even on an Ubuntu Core 26 image (the official model does the same for its core22 app). From Ubuntu Core 24, `console-conf` (first-boot network and user setup) is a separate, optional snap.

## Keys, signing, image
```bash
snapcraft keys                                   # none yet
snapcraft create-key my-model-key                # asks for a passphrase
snapcraft register-key my-model-key              # links the key to your Ubuntu One account
date -Iseconds --utc                             # new timestamp for the model
snap sign -k my-model-key my-model.json > my-model.model
sudo snap install ubuntu-image --classic --edge
ubuntu-image snap --allow-snapd-kernel-mismatch my-model.model   # -> pi.img
```
The flags (`--edge`, `--allow-snapd-kernel-mismatch`) are the ones the current tutorial uses for Ubuntu Core 26; the same key is usually reused across all models of a family.

## Gadget snap: defaults and connections
The gadget defines the storage volumes and boot assets, and can preset a robot's setup in `gadget.yaml`:
```yaml
defaults:
  <snap id>:
    <key>: <value>       # read by the snap's configure hook when it installs (snap-config-hooks)
  system:
    <key>: <value>       # system options, applied at once
connections:
  - plug: <plug snap id>:<plug>
    slot: <slot snap id>:<slot>   # omit slot = system:<plug>
```
- `defaults` take effect only during the first boot: a gadget refresh or a remodel ignores them.
- `connections` are made on the first boot only; later changes in a refreshed gadget are not applied.
- For store deployment, the gadget must come from the device brand (the model's brand) or be a reference gadget.

## Pitfalls
- The model `timestamp` must be later than the creation of the signing key: set it (`date -Iseconds --utc`) after `create-key`, as the tutorial does.
- Validation sets keep incompatible snap versions off a device ([[snap-ros2-architectures]]).
- Board-specific parts (gadget, kernel, flashing tool) change per hardware: start from the [certified Ubuntu Core images](https://ubuntu.com/certified) and the Ubuntu Core docs for your board [verify on your hardware].

Adapted from the Ubuntu Core documentation (CC-BY-SA 4.0) and the Canonical robotics documentation (CC-BY-SA 3.0).
