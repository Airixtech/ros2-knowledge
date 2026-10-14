---
id: core-learn-unit2-basics
type: reference
owner: equipo-ros2
updated: 2026-10-09
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "Unit 2 exercises: first programs & launch"
domain: core
area: learn
distro: humble
tested: false
audience: students
summary: "Course Unit 2 (pkg mars_rover_systems): heartbeat script, HeartbeatNode with timer, second rover entry point, two-rover launch file."
tags: [course, unit 2, mars_rover_systems, heartbeat, launch, students]
see: ["[[core-node-skeleton]]", "[[core-pkg-ament-python]]", "[[core-launch-basics]]", "[[core-learn-unit3-topics]]"]
requires: []
version_notes: []
---
# Unit 2 exercises: first programs & launch

**TL;DR** Mission-based exercises from the NASA Mars rover story (Leo rover simulation). The specs are kept exact because the graders check names. Reference: [[core-node-skeleton]], [[core-pkg-ament-python]], [[core-launch-basics]].

## Unit 2 — First programs (pkg `mars_rover_systems`)
- **Ex 2.1** `heartbeat.py`: `rclpy.init()` → print "Mars rover 1 is alive..." → `rclpy.shutdown()`. Add `main_shutdown()`, which prints "Shutting down Mars rover 1...", with entry point `heartbeat_executable_shutdown` (keep `heartbeat_executable = mars_rover_systems.heartbeat:main`).
- Upgrade: `HeartbeatNode(Node)` with `create_timer(timer_period, self.timer_callback)` logging `<rover_name> is alive...<ros time>`; `rclpy.spin(node)`.
- **Ex 2.2** Add `main2()`, which creates `mars_rover_2`, plus entry point `heartbeat_executable2`. Launch both with `launch/two_rover_heartbeat.launch.py` (two `Node(...)` entries, `output='screen'`), and install the launch dir in setup.py ([[core-pkg-ament-python]]).

## Checks
- After adding an entry point: rebuild + `source install/setup.bash`, then `ros2 pkg executables mars_rover_systems`.
- Timer period and logging: [[core-time-timers]], [[core-logging]].
