---
id: core-exec-model
type: reference
owner: equipo-ros2
updated: 2026-10-09
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "Executor model, fix matrix & thread safety"
domain: core
area: core-api
distro: humble
tested: false
audience: dev
summary: "How executors and callback groups decide which callbacks run in parallel; fix matrix, executor types, thread safety in rclpy."
tags: [executor, MultiThreadedExecutor, callback group, Reentrant, MutuallyExclusive, GIL, threading]
see: ["[[core-exec-callback-groups]]", "[[core-exec-spin]]", "[[core-srv-client-async]]", "[[core-learn-concepts-callbacks]]"]
requires: []
version_notes:
  - "jazzy: rclcpp executors use WaitSet; callback order no longer consistent — https://docs.ros.org/en/rolling/Releases/Release-Jazzy-Jalisco.html (V30)"
  - "lyrical: StaticSingleThreadedExecutor deprecated (Kilted) and removed — https://github.com/ros2/rclcpp/blob/kilted/rclcpp/include/rclcpp/executors/static_single_threaded_executor.hpp (V32)"
  - "lyrical: rclpy EventsExecutor (Kilted, exp.), rclcpp callback-group events executor, rclpy AsyncNode — https://docs.ros.org/en/rolling/Releases/Release-Lyrical-Luth.html (V33)"
---
# Executor model, fix matrix & thread safety

**TL;DR** By default, one thread and one MutuallyExclusive group per node run **one callback at a time**. You get parallelism only with a MultiThreadedExecutor **and** callbacks in a Reentrant group or in separate groups.

## Execution model (must know)
- Events (timer tick, message, service request, action goal, future done) make callbacks ready, and the **executor** runs them.
- Default: `rclpy.spin(node)` uses a `SingleThreadedExecutor`. Every node has ONE default `MutuallyExclusiveCallbackGroup` → **one callback at a time**.
- Order: roughly FIFO only while callbacks finish faster than events arrive. With a backlog, ready entities are served round-robin, **not FIFO**, with no ordering guarantee. [changed in Jazzy: rclcpp explicitly no longer orders callbacks consistently]
- A long callback (sleep, DNN inference, while-loop) delays ALL others: timers miss periods, subscriptions stop updating `self.last_msg`, and service responses are never processed.

## Fix matrix
| Setup | Parallel callbacks? |
|---|---|
| SingleThreadedExecutor (any groups) | No |
| MultiThreadedExecutor + all callbacks in default/same MutuallyExclusive group | **No** (common mistake) |
| MultiThreadedExecutor + ONE `ReentrantCallbackGroup` for both | Yes (even same callback re-entered) |
| MultiThreadedExecutor + SEPARATE `MutuallyExclusiveCallbackGroup` per callback | Yes (each one never overlaps itself) |

Choose Reentrant when callbacks share no mutable state. Choose separate MutuallyExclusive groups when you want each callback serialized (the safer default). You need ≥1 thread per concurrently running callback (`num_threads`, default = CPU count). Templates: [[core-exec-callback-groups]].

## Executor types
| Executor | Use |
|---|---|
| `SingleThreadedExecutor` | default, deterministic, simplest |
| `MultiThreadedExecutor(num_threads=N)` | parallel callbacks (with groups) |
| C++ `StaticSingleThreadedExecutor` | fixed entity set, lower overhead (real-time-ish) [changed in Lyrical: deprecated in Kilted, removed → `SingleThreadedExecutor`] |

There are no built-in callback priorities (research: PICAS, budget-based executors). [≥Jazzy: experimental rclcpp `EventsExecutor`] [≥Lyrical: rclpy `EventsExecutor`, rclcpp callback-group events executor, rclpy `AsyncNode` (asyncio)]

## Thread safety
- The Python GIL ≠ thread safety for compound updates (read-modify-write). With Reentrant groups, protect shared state:
```python
import threading
self._lock = threading.Lock()
with self._lock:
    self.counter += 1
```
- Alternatives: `queue.Queue`, immutable snapshots (assigning a whole object is atomic), separate MutuallyExclusive groups.
- Python threads give concurrency, not CPU parallelism (GIL). For heavy CPU work use C++ or separate processes.
