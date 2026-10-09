---
id: core-lifecycle-concepts
title: "Lifecycle states, transitions, CLI & orchestration"
domain: core
area: tools
distro: humble
tested: false
audience: dev
summary: "Managed node state machine, what each transition should do, ros2 lifecycle CLI, lifecycle_manager orchestration, when to use."
tags: [lifecycle, managed node, configure, activate, ros2 lifecycle, lifecycle_manager]
see: ["[[core-lifecycle-node]]", "[[core-nav2-overview]]", "[[core-arch-layers]]"]
requires: []
version_notes:
  - "jazzy: launch_ros LifecycleTransition action (Iron) — https://docs.ros.org/en/rolling/Releases/Release-Iron-Irwini.html (V51)"
---
# Lifecycle states, transitions, CLI & orchestration

**TL;DR** A managed node goes unconfigured → (configure) → inactive → (activate) → active. Configure allocates, activate starts, deactivate stops (keeping resources), and cleanup frees. Lifecycle publishers only publish while active.

## States & transitions
```
unconfigured --configure--> inactive --activate--> active
     ^           <--cleanup--    |  ^  <--deactivate--  |
     +------------ shutdown (from any primary state) --> finalized
```
| Transition | From → To | Typical work |
|---|---|---|
| `configure` | unconfigured → inactive | read params, allocate pubs/subs/resources |
| `activate` | inactive → active | start timers, enable publishers, start HW |
| `deactivate` | active → inactive | stop timers/HW, keep resources |
| `cleanup` | inactive → unconfigured | release resources |
| `shutdown` | any → finalized | final release |
Lifecycle publishers only publish while `active`.

## CLI
```bash
ros2 lifecycle nodes
ros2 lifecycle get /lc_talker
ros2 lifecycle list /lc_talker [-a]          # available (or all) transitions
ros2 lifecycle set /lc_talker configure
ros2 lifecycle set /lc_talker activate
ros2 lifecycle set /lc_talker deactivate | cleanup | shutdown
ros2 run lifecycle lifecycle_talker          # demo node (/lc_talker)
ros2 run nav2_util lifecycle_bringup <node>  # configure+activate helper
```

## Orchestration
- `nav2_lifecycle_manager` (the `lifecycle_manager` node, with params `node_names` and `autostart: true`) configures and activates a list of nodes in order and monitors them with bonds.
- In launch: `launch_ros.actions.LifecycleNode` + event handlers, or Nav2's manager. [≥Jazzy (since Iron): the `LifecycleTransition` launch action]
- When to use: drivers with costly init (cameras, LIDAR), safety-critical stacks, certification contexts, controlled debugging.
Implementation in rclpy/rclcpp: [[core-lifecycle-node]].
