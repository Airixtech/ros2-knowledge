---
id: cpp-learn-unit6-multithreading
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "C++ unit 6: multithreaded plant detector, callback groups, green detector in one executor"
domain: cpp
area: learn
distro: humble
tested: false
audience: students
summary: "Course unit 6 in C++: plant detector with MultiThreadedExecutor, Reentrant and MutuallyExclusive groups, GreenDetectorNode sharing an executor, green_test HSV tuner."
tags: [course, unit 6, multithreading, MultiThreadedExecutor, callback groups, plant_detector_multithreading, green_detector_node, green_test, basics_ros2_multithreading, students]
see: ["[[cpp-learn-start-here]]", "[[cpp-exec-multithreaded]]", "[[cpp-exec-callback-groups]]", "[[cpp-exec-groups-demo]]", "[[cpp-exec-multi-node]]", "[[core-learn-unit6-multithreading]]"]
requires: [ros2-core]
version_notes: []
---
# C++ unit 6: multithreading

**TL;DR** Unit 6 in C++ (the Python twin: [[core-learn-unit6-multithreading]]): make the plant detector of unit 5 see new images while it turns. Learning goals: executors (`SingleThreadedExecutor` vs `MultiThreadedExecutor`), callback groups, thread safety, responsiveness.

## Files (pkg `basics_ros2_multithreading`, created in unit 6.2)
- `src/plant_detector_multithreading.cpp` + `launch/plant_detector_multithreading.launch.py` (6.3): 2 threads, default group → still blind → [[cpp-exec-multithreaded]].
- `src/plant_detector_multithreading_callbackgroups.cpp` + `launch/plant_detector_multithreading_callbackgroups.launch.py` (6.5 Reentrant, then 6.6 two MutuallyExclusive groups) → [[cpp-exec-callback-groups]], [[cpp-exec-groups-demo]].
- `src/green_detector_node.cpp` + `launch/green_detector_node.launch.py` and `src/green_test.cpp` (6.7): two nodes in one executor, HSV trackbars → [[cpp-exec-multi-node]], [[cpp-recipe-cv-bridge]].

## What to remember
- Two ways to let callbacks overlap: one Reentrant group, or separate MutuallyExclusive groups (callbacks inside each group still exclude each other). Not universally interchangeable: choose by how the callbacks share data and resources.
- Shared data between callbacks that can overlap needs a lock (the course's code has none, CPP-V05).
- One executor can drive several nodes with one pool of threads; nodes in one process may share data directly when their design allows it.
- Real robot project part II (multithreaded executor, groups, several nodes, thread-safe sharing) runs on the course platform.
