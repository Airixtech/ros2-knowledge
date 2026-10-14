---
id: core-learn-unit6-multithreading
type: reference
owner: equipo-ros2
updated: 2026-10-09
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "Unit 6 exercises: multithreading & callback groups"
domain: core
area: learn
distro: humble
tested: false
audience: students
summary: "Course Unit 6: why MultiThreadedExecutor alone fails, Reentrant vs separate MutuallyExclusive groups, two nodes per executor, HSV mask."
tags: [course, unit 6, multithreading, callback groups, MultiThreadedExecutor, students]
see: ["[[core-exec-model]]", "[[core-exec-callback-groups]]", "[[core-exec-spin]]", "[[core-recipe-cv-bridge]]"]
requires: []
version_notes: []
---
# Unit 6 exercises: multithreading & callback groups

**TL;DR** Two threads with one default group are still blocked. Unblock the plant detector with a Reentrant group or with separate MutuallyExclusive groups. Reference: [[core-exec-model]], [[core-exec-callback-groups]].

## Unit 6 — Multithreading
- `plant_detector_multithreading.py`: the same node + `MultiThreadedExecutor(num_threads=2)` → STILL blocked (both callbacks are in the default MutuallyExclusive group).
- `plant_detector_multithreading_callbackgroups.py`:
  - Reentrant solution: one `ReentrantCallbackGroup` for subscription + service → works.
  - MutuallyExclusive solution: two separate `MutuallyExclusiveCallbackGroup`s → works (same timeline).
  - Choose Reentrant if there are no shared resources, and separate ME groups to protect shared state.
- `green_detector_node.py`: `PlantDetectorNode` + `GreenDetectorNode(plant_node)` in one executor ([[core-exec-spin]]). Service `/green_detector` gets `plant_node.get_latest_image()`, applies an HSV mask (lower `[34,84,0]`, upper `[179,255,255]`) and shows it with `cv2.imshow` (press q) ([[core-recipe-cv-bridge]]). `green_test.py`: trackbar GUI to tune the HSV ranges. GDK X error on first launch → relaunch, or set `GDK_SYNCHRONIZE=1`.
- Check cores: `python3 -c "import multiprocessing; print(multiprocessing.cpu_count())"`.
- Limitation: there are no callback priorities in the standard executors.
