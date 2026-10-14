---
id: core-production-checklist
type: reference
owner: equipo-ros2
updated: 2026-10-09
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "Level-up & production checklist"
domain: core
area: architecture
distro: humble
tested: false
audience: dev
summary: "Twelve level-up practices and a production-readiness checklist (QoS, TF, lifecycle, diagnostics, CI, Docker, multi-robot)."
tags: [best practices, checklist, production, review, deployment]
see: ["[[core-arch-layers]]", "[[core-arch-failure-rt]]", "[[core-testing-ci-docker]]", "[[core-isaac-sim-ros]]"]
requires: []
version_notes: []
---
# Level-up & production checklist

**TL;DR** Use this list for code reviews and before a deployment. Each line links to the note that explains it.

## Level-up list
1. Declare params with descriptor + range + validation ([[core-param-api]]).
2. SensorDataQoS for sensors; verify with `topic info -v` ([[core-qos-usage]]).
3. try/except + throttled logs in callbacks ([[core-bp-code-rules]]).
4. Composition + intra-process for perception ([[core-composition]]).
5. MT executor + separate groups for timers+clients ([[core-exec-callback-groups]]).
6. Lifecycle nodes for drivers ([[core-lifecycle-concepts]]).
7. BehaviorTree.CPP for missions with recovery ([[core-arch-layers]]).
8. Strict REP 105/144, `PushRosNamespace` ([[core-bp-naming]], [[core-multi-robot-namespacing]]).
9. Foxglove for remote observability.
10. Isaac Sim: Cyclone, source ROS first, Publish Clock ([[core-isaac-sim-ros]], version-dependent).
11. Docker multi-stage, per-stack `ROS_DOMAIN_ID` ([[core-testing-ci-docker]]).
12. CI from day 1 (action-ros-ci, launch_testing).

## Production checklist
- Global `use_sim_time` in sim, never on the real robot ([[core-time-timers]]).
- SensorDataQoS + RViz Best Effort; extrinsics in URDF; optical frames per REP 103.
- Perception in one `component_container_mt` with intra-process.
- Multi-robot: `PushRosNamespace` + `/tf→tf` remaps + xacro `ns` ([[core-multi-robot-namespacing]]).
- Critical nodes are lifecycle + lifecycle_manager. Params are declared with type/description/range. QoS is explicit. Names are relative, plus remaps.
- One publisher per TF; `diagnostic_updater` in drivers + an aggregator; BT RecoveryNode (Spin/BackUp/Clear/Wait) ([[core-arch-failure-rt]]).
- No `time.sleep` in callbacks; no sync service call in a same-group callback.
- Separate real/sim launch files; CI (action-ros-ci/industrial_ci) with build + tests + linters on every PR.
- Docker multi-stage; compose with the domain, Cyclone XML and `ipc: host` for SHM; kernel net buffers tuned ([[core-multi-pc-dds]]); fleets >10: discovery server / Open-RMF.
- Simulator-specific items: [[core-isaac-sim-ros]], [[core-gazebo-bridge]].
