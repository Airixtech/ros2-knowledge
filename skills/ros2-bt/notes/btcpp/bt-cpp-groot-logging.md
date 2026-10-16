---
id: bt-cpp-groot-logging
type: reference
owner: equipo-ros2
updated: 2026-10-15
review_by: 2027-04-13
source: manual
confidentiality: internal
title: "Groot and FileLogger: log a run, replay it"
domain: bt
area: btcpp
distro: humble
tested: false
audience: dev
summary: "Groot editor for BehaviorTree.CPP v3, FileLogger .fbl log and Log Replay, live view with PublisherZMQ; Groot2 and .btlog for v4."
tags: [Groot, Groot2, FileLogger, fbl, btlog, Log Replay, PublisherZMQ, bt_file_logger.h, visualize, debug]
see: ["[[bt-cpp-registration]]", "[[bt-cpp-subtrees-decorators]]", "[[bt-humble-to-jazzy]]", "[[bt-learn-unit3]]"]
requires: [ros2-core]
version_notes:
  - "all: no ROS 2 distro releases a Groot package; Groot 1 works only with BT.CPP 3.8 (maintenance mode, colcon build discouraged); BT.CPP v4 uses Groot2 — https://github.com/BehaviorTree/Groot/blob/master/README.md (BT-V05)"
  - "v4: FileLogger2 writes .btlog for Groot2; live view with Groot2Publisher — https://github.com/BehaviorTree/BehaviorTree.CPP/blob/master/include/behaviortree_cpp/loggers/bt_file_logger_v2.h (BT-V28)"
---
# Groot and FileLogger: log a run, replay it

**TL;DR** **Groot** is the graphical editor of BehaviorTree.CPP: create and edit trees (saved as XML), and watch their states. With v3.8, add a `FileLogger` once after creating the tree; it records every status change to a `.fbl` file that Groot's **Log Replay** plays tick by tick. [v4: Groot2, `FileLogger2` and `.btlog`]

## Get Groot
- Groot 1 (for BehaviorTree.CPP 3.8): source at [github.com/BehaviorTree/Groot](https://github.com/BehaviorTree/Groot). It is in maintenance mode and works only with BT.CPP 3.8.x. No ROS 2 distro ships a Groot package, and its README discourages building it with colcon; build it as a plain CMake project:
  ```bash
  git clone --recurse-submodules https://github.com/BehaviorTree/Groot.git
  cd Groot
  cmake -S . -B build
  cmake --build build
  ```
- BehaviorTree.CPP 4.x uses **Groot2**, a separate application from [behaviortree.dev](https://www.behaviortree.dev/groot).
- The course starts Groot with `source …/devel/setup.bash` and `rosrun groot Groot`: that is a ROS 1 workspace of the course platform, not a ROS 2 command.

## Record a run (v3.8)
```cpp
#include "behaviortree_cpp_v3/loggers/bt_file_logger.h"
```
Add this line **once**, after the tree is created and above `tree.tickRoot()` (never inside the tick loop):
```cpp
FileLogger logger_file(tree, "bt_trace_unit3.fbl");
```
Rebuild the package and run the program; the file is written in the folder where you run it. Then:
1. Open Groot and press **Log Replay**.
2. In the menu (upper left corner) press **Load Log** and choose the `.fbl` file.
3. Compare the tree with the one you expected, and press **Play** to step through the simulated ticks and watch the states change (the list of state transitions is on the left).

Groot can also model a tree: drag the available nodes from the left panel, connect them with the mouse and save the XML.

## Live view
v3.8 can publish the tree's state while it runs with `PublisherZMQ` (`behaviortree_cpp_v3/loggers/bt_zmq_publisher.h`), which Groot 1 shows live. [v4: `Groot2Publisher`]

## Pitfalls
- Create the `FileLogger` once, outside the tick loop, and keep it alive (same scope) while the tree runs: it only records while it exists.
- Groot 1 "is not expected to work correctly with BehaviorTree.CPP 4.x", and Groot2 is the editor for 4.x: match the editor to the library version ([[bt-humble-to-jazzy]]).
