---
id: control-learn-unit3-manager
type: reference
owner: equipo-ros2
updated: 2026-10-24
review_by: 2027-04-22
source: manual
confidentiality: internal
title: "Unit 3 exercises 3.2–3.4: controller states from the CLI, service calls, the spawner"
domain: control
area: learn
distro: jazzy
tested: false
audience: students
summary: "Unit 3 exercises 3.2.1–3.4.1: list_controller_types, list_controllers, set_controller_state, unload/load, service list and ListControllers call, spawner on a loaded controller."
tags: [unit 3, controller manager, exercise 3.2.1, exercise 3.3.1, exercise 3.4.1, set_controller_state, unload_controller, load_controller, ListControllers, spawner]
see: ["[[control-controller-lifecycle]]", "[[control-cli-list]]", "[[control-cli-state-changes]]", "[[control-services-spawner]]", "[[control-learn-unit2-test]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: the course's messages 'successfully started' and 'Configured and started' come from an older release (CONTROL-V08, CONTROL-V09)"
---
# Unit 3 exercises 3.2–3.4: controller states from the CLI, service calls, the spawner

**TL;DR** With the two-joint robot of unit 2 running, walk each controller through its states and watch what changes: whether the robot moves, which topics exist. Then use the same functions through services and the spawner.

## Start
Start the unit's simulation (course script, empty world), then:
```bash
cd ~/ros2_ws && colcon build && source install/setup.bash
ros2 launch my_robot_bringup my_robot.launch.py
```
Wait until the robot is in the simulation. Unit 2 must be finished: both joints controlled.

## Exercise 3.2.1: the command line
1. `ros2 control list_controller_types`: what could be loaded; `ros2 control list_controllers`: the broadcaster and the forward controller are `active` ([[control-cli-list]]).
2. Set both `inactive`, publish a command: the robot does not move ([[control-controller-lifecycle]]).
3. Unload both: `No controllers are currently loaded!`.
4. Load both again: `unconfigured`, and `/dynamic_joint_states` and `/forward_position_controller/commands` are gone.
5. Set both `inactive` (configure), then `active`; publish: the robot moves.
Commands and messages: [[control-cli-state-changes]]. Why it matters: without knowing the states you cannot tell which situation caused an error, or you miss a problem completely.

## Exercise 3.3.1: services
`ros2 service list | grep controller_manager`, then call `/controller_manager/list_controllers` and read the response ([[control-services-spawner]]). From the command line this only prints information; services are meant for other nodes that load, start, stop and switch controllers.

## Exercise 3.4.1: the spawner
`ros2 run controller_manager spawner joint_state_broadcaster` fails on the loaded controller ("Controller already loaded, skipping load_controller", "Failed to configure controller"): expected. Deactivate and unload it, run the spawner again: one command loads, configures and activates it, and `list_controllers` shows it `active` ([[control-services-spawner]]).

## What the controller manager does
Manages the controllers' life cycle from loading to unloading; loads only controllers of a valid type; connects controllers with hardware interfaces; provides topics and services to command and read state; prevents two controllers from claiming the same command interface ([[control-overview]]).
