---
id: core-arch-failure-rt
title: "Failure handling, diagnostics, real-time & anti-patterns"
domain: core
area: architecture
distro: humble
tested: false
audience: dev
summary: "Bonds, watchdogs, BT recoveries, diagnostic_updater, what real-time ROS 2 needs, and system-level anti-patterns."
tags: [diagnostics, diagnostic_updater, watchdog, real-time, PREEMPT_RT, anti-patterns]
see: ["[[core-arch-layers]]", "[[core-exec-model]]", "[[core-production-checklist]]"]
requires: []
version_notes:
  - "lyrical: StaticSingleThreadedExecutor deprecated in Kilted and removed; use SingleThreadedExecutor — https://github.com/ros2/rclcpp/blob/kilted/rclcpp/include/rclcpp/executors/static_single_threaded_executor.hpp (V32)"
---
# Failure handling, diagnostics, real-time & anti-patterns

**TL;DR** Detect dead nodes (bonds, watchdogs on topic rates), recover with BT behaviors, and report health with `diagnostic_updater`. ROS 2 is not hard real-time by default: run the fast loops on an MCU or in the ros2_control RT thread.

## Failure handling
- Bonds (lifecycle_manager ↔ servers) detect dead nodes. Put watchdog timers on the rates of critical topics.
- BT recoveries: Spin, BackUp, Wait, ClearCostmap, AssistedTeleop. Degrade gracefully (e.g. slow down without a global map).
- Diagnostics: `diagnostic_updater` per driver → `diagnostic_aggregator` → `rqt_robot_monitor`.
```cpp
diagnostic_updater::Updater updater_(this);
updater_.setHardwareID("hokuyo_ust10");
updater_.add("connection", this, &LidarDriver::check_conn);
```

## Real-time
ROS 2 is not hard-RT by default. It needs: a PREEMPT_RT kernel · no dynamic allocation in the hot path (TLSF) · `mlockall` · SCHED_FIFO · isolated CPUs/IRQ affinity · `StaticSingleThreadedExecutor` · callbacks without I/O or heavy logging.
[changed in Lyrical: `StaticSingleThreadedExecutor` was deprecated in Kilted and removed; the default `SingleThreadedExecutor` has adopted its approach since Jazzy]
Pragmatic split: 1–10 kHz loops in MCU/FPGA or the ros2_control RT thread; planning, SLAM and UI non-RT.

## Anti-patterns
God node · over-composition · chatty topics (throttle: `ros2 run topic_tools throttle messages /in 5.0 /out`) · sync service call in a same-group callback ([[core-exec-callback-groups]]) · TF spam or duplicate TF publishers · default QoS everywhere · magic absolute names · undeclared params · sleeps instead of timers · leaks of dynamic entities · monolithic launch files.
