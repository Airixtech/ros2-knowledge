---
id: snap-ros2-content-sharing
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "Content sharing for ROS 2 snaps: the ros2-<distro>-ros-base/-desktop extensions"
domain: snap
area: deployment
distro: humble
tested: false
audience: dev
summary: "Share one ROS 2 install between snaps: ros2-humble-ros-core/-ros-base/-desktop (experimental), content plug, provider snap, rebuild on updates."
tags: [content sharing, content interface, ros2-humble-ros-base, ros2-humble-ros-core, ros2-humble-desktop, underlay_ws, default-provider, experimental, multi-snap]
see: ["[[snap-ros2-architectures]]", "[[snap-ros2-extensions-bases]]", "[[snap-build-install-run]]"]
requires: [ros2-core]
version_notes:
  - "humble: ros2-humble-ros-core/-ros-base/-desktop are experimental and need Snapcraft 8+; content plug at $SNAP/opt/ros/underlay_ws with a default provider snap (ros-humble-ros-base on the store) — https://github.com/canonical/snapcraft/blob/main/docs/reference/extensions/ros-2-content-extensions.rst (SNAP-V39)"
  - "jazzy: ros2-jazzy-ros-core/-ros-base/-desktop (Snapcraft 8+) — https://github.com/canonical/snapcraft/blob/main/docs/reference/extensions/ros-2-content-extensions.rst (SNAP-V39)"
  - "lyrical: ros2-lyrical-ros-core/-ros-base/-desktop (Snapcraft 9+) — https://github.com/canonical/snapcraft/blob/main/docs/reference/extensions/ros-2-content-extensions.rst (SNAP-V39)"
---
# Content sharing for ROS 2 snaps: the ros2-<distro>-ros-base/-desktop extensions

**TL;DR** In a multi-snap robot every snap carries the same ROS libraries. With **content sharing**, one provider snap (e.g. `ros-humble-ros-base`, maintained on the store) holds ROS, and your app snaps mount it through the content interface. In `snapcraft.yaml` you only change the extension (`ros2-humble` → `ros2-humble-ros-base`) and drop the ROS stage packages.

## The change for Humble
```diff
     source-subdir: demo_nodes_cpp
-    stage-packages: [ros-humble-ros2launch]
 apps:
   ros2-talker-listener:
     command: ros2 launch demo_nodes_cpp talker_listener.launch.py
-    extensions: [ros2-humble]
+    extensions: [ros2-humble-ros-base]
```
```bash
SNAPCRAFT_ENABLE_EXPERIMENTAL_EXTENSIONS=1 snapcraft      # the content extensions are experimental
```

## The extensions
| Extension (Humble) | Provider content | Also for |
|---|---|---|
| `ros2-humble-ros-core` | ROS 2 `ros-core` metapackage | `ros2-jazzy-ros-core` (Snapcraft ≥ 8), `ros2-lyrical-ros-core` (≥ 9) |
| `ros2-humble-ros-base` | `ros-base` | `ros2-jazzy-ros-base`, `ros2-lyrical-ros-base` |
| `ros2-humble-desktop` | `desktop` | `ros2-jazzy-desktop`, `ros2-lyrical-desktop` |

Each one adds, on top of the normal ROS 2 extension:
- a **content plug** that mounts the provider's content at `$SNAP/opt/ros/underlay_ws`, with that provider as default provider (installed automatically with your snap);
- build settings: stage packages for the ROS environment, workspace and ament index libraries, `CMAKE_SYSTEM_PREFIX_PATH` pointing at the mounted path, and the provider's build-time snap (`ros-humble-ros-base-dev`) as a ROS build snap;
- run-time settings that chain the provider's ROS workspace, like an underlay workspace.

`snapcraft expand-extensions` shows the result.

## What it changes for deployment
- Size: ROS libraries and executables are shared, not copied in every snap; less disk and bandwidth.
- Updates: only the changed snap is redeployed. But the provider packages upstream ROS without extra API/ABI guarantees: when the provider updates, rebuild and redeploy the app snaps that use it.
- To pin the provider at a known version for your apps: a private Snap Store or a custom Ubuntu Core image ([[snap-ubuntu-core-image]]).

## Pitfalls
- Without `SNAPCRAFT_ENABLE_EXPERIMENTAL_EXTENSIONS=1` snapcraft refuses these extensions.
- A message type that is not in the provider (or in your snap) is unknown to your apps.
- Content sharing keeps the complexity of multi-snap ([[snap-ros2-architectures]]): start monolithic unless you already have several snaps.

Adapted from the Canonical robotics documentation (CC-BY-SA 3.0) and the snapcraft documentation.
