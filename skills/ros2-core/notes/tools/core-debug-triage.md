---
id: core-debug-triage
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "Debug triage, symptom table & ros2 doctor"
domain: core
area: tools
distro: humble
tested: false
audience: dev
summary: "Ordered 'it doesn't work' checklist, symptom→cause→fix table, ros2 doctor checks/report, health and bug-report scripts."
tags: [debug, triage, ros2 doctor, troubleshooting, checklist]
see: ["[[core-debug-tools]]", "[[core-qos-usage]]", "[[core-tf-basics]]", "[[core-env-variables]]"]
requires: []
version_notes:
  - "lyrical: ros2 doctor --report also lists Actions, Services and environment variables — https://docs.ros.org/en/rolling/Releases/Release-Lyrical-Luth.html (V77)"
  - "humble: ros2doctor registers five checks (PlatformCheck, NetworkCheck, TopicCheck, QoSCompatibilityCheck, PackageCheck); the RMW appears only in the report — https://github.com/ros2/ros2cli/blob/humble/ros2doctor/setup.py (CPP-V44)"
---
# Debug triage, symptom table & ros2 doctor

**TL;DR** Go top-down: sourced/env → node running → publishing → content → QoS/connection → names → TF → params → logs → `ros2 doctor --report`. Most silent failures are QoS, domain/namespace or `use_sim_time` mismatches.

## Triage checklist (in order)
1. Sourced? `echo $ROS_DISTRO` → `humble`; same `ROS_DOMAIN_ID` / `RMW_IMPLEMENTATION` everywhere ([[core-env-variables]]).
2. Node running? `ros2 node list`
3. Publishing? `ros2 topic hz /t`
4. Content OK? `ros2 topic echo /t --once`
5. Connected / QoS? `ros2 topic info /t --verbose`
6. Names right? (namespace/remap) `ros2 node info /n`
7. TF OK? `ros2 run tf2_tools view_frames`
8. Params loaded? `ros2 param list /n`
9. Logs? raise to `--log-level debug` ([[core-logging]])
10. Overall: `ros2 doctor --report`

## Symptom → cause → fix
| Symptom | Cause | Fix |
|---|---|---|
| Topic listed, echo silent | QoS mismatch | [[core-qos-usage]] (`--qos-reliability best_effort`) |
| Node can't see others | different domain / localhost-only / firewall | [[core-env-variables]], [[core-multi-pc-dds]] |
| `Package not found` / old code runs | not sourced / no symlink | `source install/setup.bash`, `--symlink-install` |
| Duplicate node name | two instances | `-r __node:=other` |
| Robot ignores `ros2 topic pub` | wrong topic name (e.g. `/robot/cmd_vel` vs `/cmd_vel`) | `ros2 topic list`, `ros2 doctor` (pub without sub warning) |
| TF extrapolation | `use_sim_time` inconsistent / bag w/o `--clock` | [[core-tf-basics]], [[core-bag-play]] |
| Callbacks frozen / stale data | single thread + long callback | [[core-exec-model]] |
| High lag | RELIABLE sensor data over Wi-Fi | BEST_EFFORT ([[core-qos-usage]]) |
| Weird build errors | stale build cache | delete build/ install/ log/ |

## ros2 doctor
```bash
ros2 doctor                      # Humble checks: platform, network, topic, QoS compatibility, package -> "All 5 checks passed"
                                 #   or "N/5 checks failed" + "Failed modules: network"
ros2 doctor --report             # sections: NETWORK CONFIGURATION, PACKAGE VERSIONS, PLATFORM INFORMATION,
                                 #   QOS COMPATIBILITY LIST, RMW MIDDLEWARE, ROS 2 INFORMATION, TOPIC LIST
ros2 doctor --include-warnings   # fail on warnings too
ros2 wtf                         # alias of doctor
```
Warnings have the form `<path>: <line>: UserWarning: <message>`. `UserWarning: X has been updated to a new version. local: … < latest: …` = an outdated pkg (usually harmless). The tool is the package `ros2doctor` of the ros2cli repository; its report also shows the RMW in use. `Publisher without subscriber detected on /t` = nobody listens, or you used the wrong name. [≥Lyrical: the report also lists actions, services and env vars]

## Scripts
```bash
# rate of every topic
for t in $(ros2 topic list); do echo -n "$t: "; timeout 2 ros2 topic hz $t 2>&1 | grep "average rate" | head -1 || echo "no data"; done
# bug report bundle
OUT="ros_debug_$(date +%H%M%S).txt"
{ ros2 doctor --report; ros2 node list; ros2 topic list -t; env | grep -E 'ROS|RMW'; } > "$OUT"
```
GUI tools (rqt, RViz2, tracing): [[core-debug-tools]].
