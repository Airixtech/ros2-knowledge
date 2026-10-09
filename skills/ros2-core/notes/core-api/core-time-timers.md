---
id: core-time-timers
title: "ROS time, sim time (use_sim_time) & timers"
domain: core
area: core-api
distro: humble
tested: false
audience: dev
summary: "get_clock().now(), Time/Duration math, create_timer, use_sim_time rules for simulation and bags, sim vs real configs."
tags: [time, Duration, create_timer, use_sim_time, clock, sim]
see: ["[[core-node-skeleton]]", "[[core-bag-play]]", "[[core-tf-basics]]", "[[core-exec-model]]"]
requires: []
version_notes:
  - "jazzy: ros2 topic hz/bw/pub honor use_sim_time (Iron) — https://docs.ros.org/en/rolling/Releases/Release-Iron-Irwini.html (V26)"
---
# ROS time, sim time (use_sim_time) & timers

**TL;DR** Use the node clock (`self.get_clock().now()`) and timers, never `time.time()` or `time.sleep` loops. With `use_sim_time:=true` the clock follows `/clock`, and every time-using node in a simulation must have it set.

## Time
```python
from rclpy.duration import Duration
from rclpy.time import Time
now = self.get_clock().now()                 # rclpy.time.Time
stamp = now.to_msg()                         # builtin_interfaces/Time for header.stamp
elapsed = self.get_clock().now() - start     # Duration
if elapsed > Duration(seconds=10): ...
secs = elapsed.nanoseconds / 1e9
t = Time.from_msg(msg.header.stamp)
```
Never use `time.time()` for robot logic: it breaks sim and bag time.

## Timers
```python
self.timer = self.create_timer(0.1, self.cb)             # 10 Hz; period in seconds
self.timer.cancel()      # stop   (one-shot: call cancel() inside cb)
self.timer.reset()       # restart period
self.destroy_timer(self.timer)
```
C++: `create_wall_timer(500ms, std::bind(&C::cb, this))` uses the wall clock, and `create_timer` uses the node clock.
The timer period is the callback rate. Processing time must stay below the period, or callbacks pile up ([[core-exec-model]]).

## use_sim_time rules
- Never on a real robot. In simulation, set it on EVERY time-using node, ideally once in the top launch file: `SetParameter(name='use_sim_time', value=...)` ([[core-launch-args-include]]).
- The simulator, or `ros2 bag play --clock` ([[core-bag-play]]), must publish `/clock`. If one node is missing it → `TF_OLD_DATA` / extrapolation errors ([[core-tf-basics]]).
- Simulated rates are ideal (exactly 30.0 Hz). Always use stamp differences, never assume a constant dt, and add sensor noise in sim.
- [≥Jazzy: `ros2 topic hz/bw/pub` also honor `use_sim_time`]

## Sim vs real configs
Keep the same packages and change only the launch files and YAML: `config/real.yaml`, `config/sim.yaml`, `bringup_real.launch.py`, `bringup_sim.launch.py` (the sim one sets `use_sim_time`). For CI without hardware, use ros2_control mock hardware ([[core-ros2-control-overview]]).

## Pitfalls
- `Time` objects with different clock types (ROS vs system) cannot be subtracted. Take both values from `self.get_clock()`.
- Before the first `/clock` message arrives, sim time is 0, so a check like `now - start > timeout` can misfire at startup.
