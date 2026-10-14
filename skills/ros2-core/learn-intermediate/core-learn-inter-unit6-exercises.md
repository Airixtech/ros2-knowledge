---
id: core-learn-inter-unit6-exercises
type: reference
owner: equipo-ros2
updated: 2026-10-14
review_by: 2027-04-12
source: manual
confidentiality: internal
title: "Intermediate Unit 6: service + timer exercises (workers and conveyor belts)"
domain: core
area: learn-intermediate
distro: humble
tested: false
audience: students
summary: "Unit 6 exercises 6.4–6.6: a slow SetBool service blocks a timer; threads and callback groups fix it."
tags: [course, unit 6, multithreading_ros2_examples, SetBool, start_turn, calculations, callback groups, threads, analogy, students]
see: ["[[core-exec-callback-groups]]", "[[core-learn-inter-unit6-executor]]", "[[core-learn-inter-unit6-groups-demo]]", "[[core-srv-server]]"]
requires: []
version_notes: []
---
# Intermediate Unit 6: service + timer exercises (workers and conveyor belts)

**TL;DR** A service callback that sleeps 15 s stops the 1 s timer that publishes `cmd_vel`, because each node has **one** MutuallyExclusive callback group by default and a script has **one** thread by default. Two callbacks in parallel need at least two threads **and** two callback groups. Patterns: [[core-exec-callback-groups]].

## Exercise 6.4
1. New package `multithreading_ros2_examples`, dependencies `std_msgs`, `geometry_msgs`, `std_srvs`.
2. `multithreading_movement_server.py` with a class `ServiceServer(Node)` that starts:
   - a service server `/start_turn` (`std_srvs/SetBool`) whose callback is named `SetBool_callback`: `True` sets `self.cmd` (`geometry_msgs/Twist`) to turn at 0.3 rad/s, `False` to go forward. Inside it, `time.sleep(15.0)`, logging the waiting time;
   - a publisher on `/cmd_vel` named `publisher_`;
   - a 1.0 s timer that publishes `self.cmd` (initialized as `Twist()` in `__init__`) and logs it.
Without threads and groups: the timer runs every second until the service is called, then waits until `SetBool_callback` ends. The robot does not move during the 15 s: the publish is in the timer callback.
```bash
ros2 service call /reset_world std_srvs/srv/Empty "{}"
ros2 service call /start_turn std_srvs/srv/SetBool "data: true"
```

## The analogy
- **Callbacks are boxes**: `SetBool_callback` is a red box, put on the belt each time `/start_turn` is called; `timer_callback` is a blue box, put on the belt every second.
- **Callback groups are conveyor belts** where the script places each callback to be processed.
- **Threads are workers**: a worker processes one box at a time, in the order they are on the belt. While `SetBool_callback` takes 15 s, no other box is processed.

## Exercise 6.5
`multithreading_movement_server_parallel.py`, based on 6.4, that processes `SetBool_callback` and `timer_callback` at the same time. You need two workers (a `MultiThreadedExecutor` with at least two threads) and two belts (two callback groups, one per callback): two workers on one belt still process one box at a time. Result: the robot moves at once; `timer_callback` keeps publishing every second while the service sleeps, because `self.cmd` was set before the wait.

## Exercise 6.6
`multithreading_movement_server_and_calculation_server.py`, based on 6.5:
- `/start_turn` and the timer as before, but publish only at start and when the service is called (a flag);
- a second Node class `CalculationsServiceServer` with a service `/calculations` (`std_srvs/SetBool`), subscribed to the laser (`self.laser_forward = msg.ranges[359]`): read the front value, wait 5 s, read again, answer according to the sign of the difference and publish on `cmd_vel` to go backward or forward;
- both nodes in the same script; decide how many threads and groups you need.
In ROS 2 Python each Node object has **its own** default group, so two nodes could run two callbacks at once, but a script has **one thread** by default: declare as many threads as callbacks you want simultaneously.
```bash
ros2 service call /start_turn std_srvs/srv/SetBool "data: true"
ros2 service call /calculations std_srvs/srv/SetBool "data: false"
```
Expected: both services work without stopping each other or the timer. Then try 2 and 1 threads and watch the services wait for each other.

## Pitfalls
- More threads than callbacks waste resources; fewer than parallel callbacks serialize them.
- A long `time.sleep()` in a service callback is a design smell: prefer an action or a timer-driven state machine ([[core-bp-comm-choice]]).
