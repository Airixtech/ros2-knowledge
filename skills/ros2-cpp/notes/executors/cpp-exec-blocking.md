---
id: cpp-exec-blocking
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "A long callback blocks the others: single-threaded executor, stale data, the default MutuallyExclusive group"
domain: cpp
area: executors
distro: humble
tested: false
audience: dev
summary: "A 10 s service callback stops the image callback on rclcpp::spin, so the detector loops on a stale image."
tags: [single-threaded executor, blocking callback, stale data, detect_plants, service callback, subscription callback, rclcpp::spin, MutuallyExclusive, default callback group]
see: ["[[cpp-exec-plant-detector-demo]]", "[[cpp-exec-multithreaded]]", "[[cpp-exec-callback-groups]]", "[[core-exec-model]]", "[[cpp-callbacks-functions]]"]
requires: [ros2-core]
version_notes: []
---
# A long callback blocks the others

**TL;DR** With `rclcpp::spin(node)` one thread runs all callbacks of the node, one at a time. A service callback that loops for up to 10 s ("turn until a plant is seen") stops the image callback for that whole time, so the loop keeps analysing the **same** image while the robot turns: it never sees the plant unless it was already in view. The fix needs two ingredients: more executor threads **and** callback groups that allow the two callbacks to overlap ([[cpp-exec-multithreaded]], [[cpp-exec-callback-groups]]).

## The situation (plant detector, unit 5.5)
- `listener_callback()`: triggered by every new image on `/leo/camera/image_raw` (an event, not a timer); stores it in `last_image_`.
- `detect_plants_callback()`: triggered by the service `/detect_plants` (`std_srvs/srv/Trigger`); publishes a turn on `/cmd_vel` (angular −0.2), then loops every 100 ms reading `last_image_` until a plant is detected or 10 s pass, then stops the robot.
- Full program, launch, CMake and runs: [[cpp-exec-plant-detector-demo]].

## What the runs show
| Start position | Result | Why |
|---|---|---|
| Plant not in view | `success=False` after the 10 s timeout, `❌ No Plant Detected` every 100 ms, no `Receiving video frame` lines meanwhile | `listener_callback()` cannot run while the service callback runs: `last_image_` stays the image taken before the turn |
| Plant already in view | `success=True`, `🌱 Plant Detected!` almost at once | the stale image already contains the plant |

The CSV timeline of the run makes it visible: the regular `listener_callback` executions stop exactly when `detect_plants_callback` starts and resume when it ends (in the course's run: 45 listener executions of 2–9 ms, 2 detection executions of 1.25 s and 10.04 s).

## Why only one at a time
The default executor of `rclcpp::spin()` has one thread. And every subscription, timer and service without an explicit group belongs to the node's **default callback group, which is MutuallyExclusive**: even with more threads, two callbacks of that group never run together ([[cpp-exec-callback-groups]], [[core-exec-model]]).

## Pitfalls
- Sleeping or polling inside a callback (`sleep_for(100ms)` in a loop) is the pattern that starves the rest of the node; on one thread keep callbacks short, or move the long work to another group/thread.
- A sensor value read inside a long callback is only fresh if another thread can update it, and then it needs a lock ([[cpp-exec-callback-groups]]).
