---
id: core-multi-robot-namespacing
title: "Multi-robot namespacing & per-robot TF"
domain: core
area: architecture
distro: humble
tested: false
audience: dev
summary: "Namespace N robots with __ns or PushRosNamespace, remap /tf per robot, frame prefixes via xacro or frame_prefix, anti-patterns."
tags: [multi-robot, namespace, PushRosNamespace, tf remap, frame_prefix, xacro]
see: ["[[core-launch-args-include]]", "[[core-multi-pc-dds]]", "[[core-xacro]]", "[[core-tf-basics]]"]
requires: []
version_notes:
  - "jazzy: PushROSNamespace (Iron rename; old name = alias) — https://docs.ros.org/en/rolling/Releases/Release-Iron-Irwini.html (V15)"
---
# Multi-robot namespacing & per-robot TF

**TL;DR** `tf_prefix` does NOT exist in ROS 2. Give each robot a namespace, remap `/tf` and `/tf_static` to relative names (per-robot TF trees), and keep frame names unique or prefixed.

## Namespacing
A node namespace prefixes its relative topics, services, actions and params.
```bash
ros2 run pkg driver --ros-args -r __ns:=/robot1
```
```python
GroupAction([
    PushRosNamespace('robot1'),                 # first action in group
    SetRemap(src='/tf', dst='tf'),              # per-robot TF tree (/robot1/tf)
    SetRemap(src='/tf_static', dst='tf_static'),
    IncludeLaunchDescription(PythonLaunchDescriptionSource(robot_launch),
                             launch_arguments={'namespace': 'robot1'}.items()),
])
```
`PushRosNamespace` [changed in Jazzy: `PushROSNamespace`, old name kept as alias] ([[core-launch-args-include]]).
- Frames: xacro `<xacro:arg name="ns" default=""/>` → `<link name="$(arg ns)/base_link"/>`, or the `frame_prefix` param of robot_state_publisher ([[core-xacro]]). Simulators: unique entity names per spawn.
- TF options: (a) per-robot `/robotN/tf` (recommended, needs the remaps) (b) a shared `/tf` with prefixed frames.

## Anti-patterns
Same namespace for all robots · relying on `tf_prefix` · no `/tf` remap in namespaced stacks · multicast over Wi-Fi · leaving the domain plan to the end · duplicate entity names in sim · TRANSIENT_LOCAL on high-rate streams · RViz over Wi-Fi with raw camera · Isaac Sim without Publish Clock.
Networking several PCs or robots: [[core-multi-pc-dds]].
