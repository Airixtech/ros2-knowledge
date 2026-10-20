---
id: snap-learn-exercise
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "Snaps workshop exercise: add a ros2topic app"
domain: snap
area: learn
distro: humble
tested: false
audience: students
summary: "Exercise: expose ros2 topic as a second app (ros2-talker-listener.ros2topic hz /chatter): stage ros-humble-ros2topic, add the app, rebuild."
tags: [course, exercise, ros2topic, stage-packages, apps, ros2 topic hz, talker-listener]
see: ["[[snap-learn-start-here]]", "[[snap-snapcraft-yaml]]", "[[snap-daemon]]", "[[core-topic-cli]]"]
requires: [ros2-core]
version_notes:
  - "humble: the exercise diff writes 'ros2 launch talker-listener …'; the daemon branch keeps demo_nodes_cpp — https://github.com/ubuntu-robotics/ros2-humble-talker-listener-snap/blob/daemon/snap/snapcraft.yaml (SNAP-V02)"
  - "humble: ros2topic app with ros-humble-ros2topic in stage-packages; topic tools only know the message types inside the snap — https://canonical-robotics.readthedocs-hosted.com/en/latest/tutorials/snaps-core/packaging-ros-application-as-snap/ (SNAP-V23)"
---
# Snaps workshop exercise: add a ros2topic app

**TL;DR** The talker-listener snap has one app. Add a second one that exposes the ROS 2 topic tools, so you can introspect the snap's own topics.

## Assignment
Modify `snap/snapcraft.yaml` (start from the `daemon` branch):
- add a new app entry for `ros2topic`;
- add the corresponding dependencies.

Build and install the new snap. Expected new command:
```bash
ros2-talker-listener.ros2topic hz /chatter
```
The topic tools only work with message types included in the snap.

## Solution
1. Add `ros-humble-ros2topic` to the `stage-packages` of the existing part, so it is available at run time (a separate empty part with only `stage-packages` would also work):
```diff
 parts:
  ros-demos:
    plugin: colcon
    source: https://github.com/ros2/demos.git
    source-branch: humble
    source-subdir: demo_nodes_cpp
-   stage-packages: [ros-humble-ros2launch]
+   stage-packages: [ros-humble-ros2launch, ros-humble-ros2topic]
```
2. Add the app, with the same plugs and extension:
```diff
 apps:
  ros2-talker-listener:
    command: opt/ros/humble/bin/ros2 launch demo_nodes_cpp talker_listener.launch.py
    daemon: simple
    plugs: [network, network-bind]
    extensions: [ros2-humble]
+ ros2topic:
+   command: opt/ros/humble/bin/ros2 topic
+   plugs: [network, network-bind]
+   extensions: [ros2-humble]
```
(The workshop's diff writes `ros2 launch talker-listener …`: keep `demo_nodes_cpp` as in the repository.)
3. Build, install, check:
```bash
snapcraft
sudo snap install ros2-talker-listener_0.1_amd64.snap --dangerous
ros2-talker-listener.ros2topic hz /chatter
```
```text
average rate: 1.000 min: 0.999s max: 1.000s std dev: 0.00049s window: 3
```

## Pitfalls
- Without `ros-humble-ros2topic` in `stage-packages` the `topic` verb is missing at run time.
- The new app is `<snap>.<app>` (`ros2-talker-listener.ros2topic`): only an app named like the snap collapses to the snap name.
- [changed in Jazzy: `ros-jazzy-ros2topic`, `ros-jazzy-ros2launch` and the launch file `talker_listener_launch.py`.]
