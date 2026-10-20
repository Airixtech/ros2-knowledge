---
id: snap-confinement
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "Confinement, grade and interfaces (plugs, slots, snap connections, shared memory)"
domain: snap
area: runtime
distro: humble
tested: false
audience: dev
summary: "devmode, classic, strict; grade devel/stable; plugs and slots, network and network-bind, snap connections; Fast DDS shared memory in strict snaps."
tags: [confinement, strict, devmode, classic, grade, interfaces, plugs, slots, network, network-bind, snap connections, shared-memory, Fast DDS SHM]
see: ["[[snap-snapcraft-yaml]]", "[[snap-daemon]]", "[[snap-debug-app]]", "[[snap-ros2-architectures]]", "[[core-rmw-implementations]]"]
requires: [ros2-core]
version_notes:
  - "humble: the confined and daemon branches keep 'ros2 launch demo_nodes_cpp talker_listener.launch.py'; the course's 'talker-listener' package does not exist — https://github.com/ubuntu-robotics/ros2-humble-talker-listener-snap/blob/confined/snap/snapcraft.yaml (SNAP-V02)"
  - "humble: confinement devmode, classic (manual store approval), strict — https://github.com/canonical/snapcraft/blob/main/snapcraft/models/project.py (SNAP-V17)"
  - "humble: grade stable (default) or devel; a devel snap can only be released to beta and edge — https://github.com/canonical/snapcraft/blob/main/snapcraft/models/project.py (SNAP-V18)"
  - "humble: network and network-bind are implicit slots with no auto-connection restriction — https://github.com/canonical/snapd/blob/master/interfaces/builtin/network.go (SNAP-V19)"
  - "humble: Fast DDS shared memory fails in a strict snap and falls back to UDP; fixes: private shared-memory plug, slot+plug pair, or disable SHM — https://canonical-robotics.readthedocs-hosted.com/en/latest/how-to-guides/packaging/ros-2-shared-memory-in-snaps/ (SNAP-V20)"
---
# Confinement, grade and interfaces (plugs, slots, snap connections, shared memory)

**TL;DR** Ship snaps `strict`: isolated from the host, with access only through declared **interfaces** (plugs). A ROS 2 app needs at least `plugs: [network, network-bind]`. Add `grade: stable` for production. Expect a harmless Fast DDS shared-memory error until you configure shared memory.

## Confinement types
| Type | Behaviour | Install flag |
|---|---|---|
| `devmode` | for snap developers: runs like a strict snap but with full access to system resources, and logs the interfaces it would need | `--devmode` |
| `classic` | access to system resources like a traditional package; publishing needs manual store approval (typical: IDEs such as VS Code, Qt Creator); not possible with the ROS 2 extensions | `--classic` |
| `strict` | used by most snaps: complete isolation, nothing beyond a minimal safe level (files, network, processes, devices) without an interface | none (or `--dangerous` for a local file) |

## Grade
- `stable` (default): production quality, can be released to every channel.
- `devel`: development version; it can only go to the `beta` and `edge` channels, never `candidate` or `stable` ([[snap-channels-updates]]).

## Interfaces
An interface connects a **plug** (the consumer) to a **slot** (the provider); one slot can serve many plugs. Plugs are declared per app in `snapcraft.yaml`. Interfaces marked auto-connect connect at install time; the others must be connected by hand (`snap connect`, like an app asking for a permission). The list is in the [supported interfaces](https://snapcraft.io/docs/supported-interfaces) documentation (home directory, CAN bus, network…). `network` (network access) and `network-bind` (act as a network service) are both auto-connected.

## Confine the talker-listener
The `confined` branch of the example repository changes three lines:
```diff
-confinement: devmode
+confinement: strict
+grade: stable
 apps:
   ros2-talker-listener:
     command: opt/ros/humble/bin/ros2 launch demo_nodes_cpp talker_listener.launch.py
+    plugs: [network, network-bind]
```
(The course's diff writes `ros2 launch talker-listener …`: there is no such package, the branch keeps `demo_nodes_cpp`.)
```bash
git switch confined
snapcraft
sudo snap install ros2-talker-listener_0.1_amd64.snap --dangerous   # strict but not signed by a store
snap connections ros2-talker-listener
```
```text
Interface     Plug                               Slot           Notes
network       ros2-talker-listener:network       :network       -
network-bind  ros2-talker-listener:network-bind  :network-bind  -
```
Running it now prints errors, yet messages flow:
```text
[talker-1] 2022-07-13 15:47:10.570 [RTPS_TRANSPORT_SHM Error] Failed to create segment cbbe40933e75c60a: Permission denied -> Function compute_per_allocation_extra_size
[talker-1] 2022-07-13 15:47:10.657 [RTPS_MSG_OUT Error] Permission denied -> Function init
[talker-1] [INFO] [1657720031.730359135] [talker]: Publishing: 'Hello World: 1'
[listener-2] [INFO] [1657720031.730705569] [listener]: I heard: [Hello World: 1]
```

## Fast DDS shared memory in a strict snap
Fast DDS cannot create its shared-memory files in `/dev/shm` and falls back to UDP: communication works, only slower on the same host. Options:
- **Private shared memory** (inside one snap): add the plug below; `/dev/shm` calls go to `/dev/shm/snap.<snap>`. Nodes outside the snap on the same host can then no longer see its topics (other computers still can, over UDP).
```yaml
plugs:
  shared-memory:
    private: true
```
- **Shared memory across snaps**: declare a `shared-memory` slot (`write: ['*']`) and plug, add the plug to the apps, and connect them by hand: `sudo snap connect <snap>:shmem-plug <snap>:shmem-slot`.
- **Disable shared memory**: a Fast DDS XML profile that forces UDPv4, or rebuild Fast DDS with `-DSHM_TRANSPORT_DEFAULT=OFF`. Mixed users matter too: snap daemons run as root while CLI apps may not, which can break shared memory between them.

## Pitfalls
- An undeclared interface fails silently or with a permission error: check `snap connections` and use `snappy-debug` ([[snap-debug-app]]).
- `devmode` hides missing interfaces: always test the `strict` build before shipping.
