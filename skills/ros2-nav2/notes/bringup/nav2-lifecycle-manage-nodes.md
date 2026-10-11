---
id: nav2-lifecycle-manage-nodes
type: reference
owner: equipo-ros2
updated: 2026-10-10
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "ManageLifecycleNodes service: pause, resume, reset from CLI or code"
domain: nav2
area: bringup
distro: humble
tested: false
audience: dev
summary: "<manager>/manage_nodes (nav2_msgs/srv/ManageLifecycleNodes): STARTUP, PAUSE, RESUME, RESET, SHUTDOWN; find it, inspect it, call it from the CLI."
tags: [manage_nodes, ManageLifecycleNodes, nav2_msgs, lifecycle_manager, pause, resume, ros2 service call, is_active]
see: ["[[nav2-lifecycle-manager]]", "[[core-srv-client-async]]", "[[core-cli-cheatsheet]]"]
requires: [ros2-core]
version_notes:
  - "humble: commands STARTUP 0 … SHUTDOWN 4; jazzy: adds CONFIGURE = 5 and CLEANUP = 6 — https://github.com/ros-navigation/navigation2/blob/jazzy/nav2_msgs/srv/ManageLifecycleNodes.srv (NAV2-V22)"
---
# ManageLifecycleNodes service: pause, resume, reset from CLI or code

**TL;DR** Every Nav2 lifecycle manager offers `<its node name>/manage_nodes`. One call starts, pauses, resumes, resets or shuts down all the nodes it manages, so your program needs a single service client instead of handling each node.

## Find and inspect the service
With the map server running ([[nav2-map-server]]):
```bash
ros2 service list | grep lifecycle
```
```
/lifecycle_manager_mapper/describe_parameters
/lifecycle_manager_mapper/get_parameter_types
/lifecycle_manager_mapper/get_parameters
/lifecycle_manager_mapper/is_active
/lifecycle_manager_mapper/list_parameters
/lifecycle_manager_mapper/manage_nodes
/lifecycle_manager_mapper/set_parameters
/lifecycle_manager_mapper/set_parameters_atomically
```
```bash
ros2 service type /lifecycle_manager_mapper/manage_nodes     # nav2_msgs/srv/ManageLifecycleNodes
ros2 interface show nav2_msgs/srv/ManageLifecycleNodes
```
```
uint8 STARTUP = 0
uint8 PAUSE = 1
uint8 RESUME = 2
uint8 RESET = 3
uint8 SHUTDOWN = 4

uint8 command
---
bool success
```
When calling the service, give a number between `0` and `4`: the state to put the navigation system in. It returns a boolean `success`. `is_active` (`std_srvs/srv/Trigger`) tells whether the managed nodes are active.

## Pause and resume
```bash
ros2 service call /lifecycle_manager_mapper/manage_nodes nav2_msgs/srv/ManageLifecycleNodes "{command: 1}"
```
```
requester: making request: nav2_msgs.srv.ManageLifecycleNodes_Request(command=1)

response:
nav2_msgs.srv.ManageLifecycleNodes_Response(success=True)
```
The manager logs (terminal where the nodes run):
```
[lifecycle_manager-2] [INFO] [1655285986.303567128] [lifecycle_manager_mapper]: Terminating bond timer...
[lifecycle_manager-2] [INFO] [1655285986.303659326] [lifecycle_manager_mapper]: Pausing managed nodes...
[lifecycle_manager-2] [INFO] [1655285986.303698330] [lifecycle_manager_mapper]: Deactivating map_server
[map_server-1] [INFO] [1655285986.307166044] [map_server]: Deactivating
[map_server-1] [INFO] [1655285986.307227673] [map_server]: Destroying bond (map_server) to lifecycle manager.
[lifecycle_manager-2] [INFO] [1655285986.412322210] [lifecycle_manager_mapper]: Managed nodes have been paused
```
While paused, the stack is running but inactive: navigation goals are not executed. Resume with `"{command: 2}"`.

## From a program
Create a client for `nav2_msgs/srv/ManageLifecycleNodes` and call it asynchronously ([[core-srv-client-async]]): e.g. PAUSE before a manual operation, RESUME after, RESET to reconfigure.

## Pitfalls
- The service name follows the manager's node name (`lifecycle_manager_mapper`, `lifecycle_manager_localization`…): list services first.
- Pausing only stops the nodes of that manager; with several managers, call each one (or use a single manager, [[nav2-single-launch]]).
