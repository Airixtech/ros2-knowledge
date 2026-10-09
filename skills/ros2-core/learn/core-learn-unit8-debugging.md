---
id: core-learn-unit8-debugging
title: "Unit 8 exercises: logs, RViz2, view_frames, ros2 doctor"
domain: core
area: learn
distro: humble
tested: false
audience: students
summary: "Course Unit 8 (pkg logs_test): logger levels, colored launch output, RViz2 rover displays, TF tree PDF, ros2 doctor."
tags: [course, unit 8, logging, RViz2, view_frames, ros2 doctor, students]
see: ["[[core-logging]]", "[[core-debug-tools]]", "[[core-debug-triage]]", "[[core-tf-basics]]"]
requires: []
version_notes: []
---
# Unit 8 exercises: logs, RViz2, view_frames, ros2 doctor

**TL;DR** Practice the debugging toolbox on the rover: log levels, RViz2 displays, the TF tree and `ros2 doctor`. Reference: [[core-logging]], [[core-debug-tools]], [[core-debug-triage]], [[core-tf-basics]].

## Unit 8 — Debugging tools
- **Ex 8.1/8.2** Pkg `logs_test`, `logger_example.py` (node `logger_example`, timer 0.2 s logging debug/info/warn/error/fatal). Change the level with `rclpy.logging.set_logger_level('logger_example', LoggingSeverity.<LEVEL>)`. Launch `logger_example.launch.py` with `emulate_tty=True` for colors. For WARN messages use `get_logger().warning(...)` ([[core-logging]]).
- **Example 8.1** RViz2: source the sims ws, run `rviz2`, add TF (Fixed Frame `base_link`), RobotModel (`/robot_description`) and LaserScan (`/laser_scan`, Best Effort, size 0.1). Move the rover with `ros2 topic pub /cmd_vel ...`.
- **Example 8.2** `cd ~ && ros2 run tf2_tools view_frames` → download `frames_*.pdf`.
- **Examples 8.3–8.5** `ros2 doctor` (ignore UserWarnings; "All 5 checks passed"). Detect a "Publisher without subscriber" (e.g. a wrong `/robot/cmd_vel` name). Read the `ros2 doctor --report` sections.
