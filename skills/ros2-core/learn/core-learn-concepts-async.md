---
id: core-learn-concepts-async
title: "Concepts: async, concurrency, ROS time, reading a LaserScan"
domain: core
area: learn
distro: humble
tested: false
audience: students
summary: "Asynchrony vs concurrency vs parallelism with asyncio example, why ROS time instead of time.time(), a worked LaserScan example, RViz2 role."
tags: [concepts, async, asyncio, GIL, ROS time, LaserScan, students]
see: ["[[core-learn-concepts-callbacks]]", "[[core-time-timers]]", "[[core-recipe-laserscan]]"]
requires: []
version_notes: []
---
# Concepts: async, concurrency, ROS time, reading a LaserScan

**TL;DR** Async means "don't wait", concurrency means juggling several tasks, and parallelism means doing them at the same instant. Use the ROS clock, not `time.time()`. A LaserScan is an array of distances indexed by angle.

## Sync vs async, concurrency vs parallelism
| Term | Meaning | Python |
|---|---|---|
| Asynchrony | "I'll tell you when done, don't wait" | `async` / `await` |
| Concurrency | juggling several tasks (one hand switching fast) | `asyncio`, `threading` |
| Parallelism | several tasks at the same instant (several jugglers/cores) | `multiprocessing` |
```python
import asyncio

async def long_task():
    await asyncio.sleep(2)          # pauses without blocking others
    print('done')

async def main():
    task = asyncio.create_task(long_task())
    print('doing other things meanwhile...')
    await task

asyncio.run(main())
```
The GIL prevents pure-Python threads from running bytecode in parallel on several cores. Threads still help when you are waiting on I/O or ROS events.

## Time in ROS
Use `node.get_clock().now()`, not `time.time()`: in simulation or bag replay, ROS time ≠ wall time (`use_sim_time`). Use logs (`get_logger().info`) instead of `print` ([[core-time-timers]], [[core-logging]]).

## LaserScan reading (worked example)
With `angle_min=-2.2`, `angle_max=2.2` and `angle_increment=0.02211`: samples = (2.2−(−2.2))/0.02211 ≈ 200, and angle(i) = −2.2 + i·0.02211. The middle index 100 ≈ 0 rad = the robot's front. `inf` means nothing was detected within `range_max`. Code: [[core-recipe-laserscan]].

## RViz2 is not a simulator
It only displays what topics carry, coming from a simulator or a real robot ([[core-debug-tools]]).
