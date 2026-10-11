---
id: core-learn-start-here
type: reference
owner: equipo-ros2
updated: 2026-10-09
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "Learning path & course environment"
domain: core
area: learn
distro: humble
tested: false
audience: students
order: 1
summary: "Suggested reading order through concepts, technical notes and course units; rules of the course cloud environment."
tags: [course, learning path, cloud environment, Leo rover, students]
see: ["[[core-learn-concepts-callbacks]]", "[[core-learn-unit2-basics]]", "[[core-env-sourcing]]"]
requires: []
version_notes: []
---
# Learning path & course environment

**TL;DR** This is the learning track: concepts plus the course exercises and quizzes (Leo Mars rover simulation). Follow the order below, and keep your own environment changes at the end of `~/.bashrc`.

## Suggested order
1. Concepts: [[core-learn-concepts-callbacks]] · [[core-learn-concepts-async]] · [[core-learn-concepts-comm]]
2. Build & run: [[core-env-sourcing]] · [[core-pkg-workspace]] · [[core-pkg-ament-python]] · [[core-colcon-build]] · [[core-launch-basics]]
3. Nodes: [[core-node-skeleton]] · [[core-logging]] · [[core-time-timers]]
4. Topics: [[core-topic-cli]] · [[core-topic-pub-sub-py]] → exercises [[core-learn-unit2-basics]], [[core-learn-unit3-topics]]
5. Interfaces & services: [[core-iface-package]] · [[core-srv-server]] · [[core-srv-client-async]] → [[core-learn-unit4-services]]
6. Executors: [[core-exec-model]] · [[core-exec-callback-groups]] → [[core-learn-unit5-callbacks]], [[core-learn-unit6-multithreading]]
7. Actions: [[core-action-server]] · [[core-action-client]] → [[core-learn-unit7-actions]]
8. Debugging: [[core-debug-triage]] · [[core-debug-tools]] → [[core-learn-unit8-debugging]]
9. Then: [[core-tf-basics]] · [[core-urdf-basics]] · [[core-bag-record]] · [[core-lifecycle-concepts]] · architecture notes ([[core-arch-layers]]).

## Course cloud environment
- The platform-managed `~/.bash_aliases` sources `/opt/ros/$SELECTED_ROS_DISTRO`, `~/ros2_ws/install/local_setup.bash` and `/home/simulations/ros2_sims_ws/install/setup.bash` when `SOURCE_ROS2_WS` is set. Do NOT edit it: changes are not persisted.
- Put your custom exports at the END of `~/.bashrc`, which is saved with the course project.
- Simulation packages (e.g. `leo_description`) live in `/home/simulations/ros2_sims_ws`. Run `source /home/simulations/ros2_sims_ws/install/setup.bash` before building packages that depend on them ([[core-colcon-errors]]).
- Reset the simulation from the CLI: `ros2 service call /reset_world std_srvs/srv/Empty {}`.
