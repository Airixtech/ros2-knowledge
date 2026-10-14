---
id: core-lifecycle-services-cli
type: reference
owner: equipo-ros2
updated: 2026-10-14
review_by: 2027-04-12
source: manual
confidentiality: internal
title: "Driving a managed node: lifecycle services, transition_event, CLI session"
domain: core
area: tools
distro: humble
tested: false
audience: dev
summary: "Services every managed node offers (get_state, change_state…), transition ids, a configure/activate/shutdown CLI session, on_error outcome."
tags: [lifecycle services, change_state, get_state, ros2 lifecycle, transition id, TRANSITION_CONFIGURE, finalized, on_error, ErrorProcessing, LifecyclePublisher]
see: ["[[core-lifecycle-concepts]]", "[[core-lifecycle-cpp-node]]", "[[core-lifecycle-manager-client]]", "[[core-srv-client-async]]"]
requires: []
version_notes:
  - "humble: on_error SUCCESS -> unconfigured, FAILURE/ERROR -> finalized — https://github.com/ros2/rcl/blob/humble/rcl_lifecycle/src/default_state_machine.c (V99)"
  - "all: still no lifecycle class for subscriptions in rclcpp_lifecycle (Humble to Lyrical) — https://github.com/ros2/rclcpp/tree/lyrical/rclcpp_lifecycle/include/rclcpp_lifecycle (V100)"
---
# Driving a managed node: lifecycle services, transition_event, CLI session

**TL;DR** Every managed node offers the services `<node>/change_state`, `<node>/get_state`, `<node>/get_available_states`, `<node>/get_available_transitions` and `<node>/get_transition_graph`. A manager, the `ros2 lifecycle` CLI or a plain `ros2 service call` uses them. Example node: `managed_scan_node` from [[core-lifecycle-cpp-node]]. State diagram: [[core-lifecycle-concepts]].

## 1. After launch: unconfigured, no topic
`/managed_scan` does not exist yet: the publisher is created in `on_configure`, the node's "constructor" for everything it needs before working. Its publisher is a `LifecyclePublisher`, the type that can be activated and deactivated; there is no lifecycle class for subscriptions.
```bash
ros2 service list
ros2 service call /managed_scan_node/get_state lifecycle_msgs/srv/GetState {}
ros2 lifecycle get /managed_scan_node
```
```text
/managed_scan_node/change_state
/managed_scan_node/describe_parameters
/managed_scan_node/get_available_states
/managed_scan_node/get_available_transitions
/managed_scan_node/get_parameter_types
/managed_scan_node/get_parameters
/managed_scan_node/get_state
/managed_scan_node/get_transition_graph
/managed_scan_node/list_parameters
/managed_scan_node/set_parameters
/managed_scan_node/set_parameters_atomically
response:
lifecycle_msgs.srv.GetState_Response(current_state=lifecycle_msgs.msg.State(id=1, label='unconfigured'))
unconfigured [1]
```

## 2. Configure: the topic appears
```bash
ros2 service call /managed_scan_node/change_state lifecycle_msgs/srv/ChangeState "{transition: {id: 1}}"
# same with the CLI: ros2 lifecycle set <node_name> <transition>
ros2 lifecycle set /managed_scan_node configure
```
```text
Transitioning successful
```
`on_configure` runs; `ros2 topic list` now shows `/managed_scan`. The `transition_event` echo shows two steps: `unconfigured` → `configuring` (the callback runs) and `configuring` → `inactive` (it returned `SUCCESS`):
```text
start_state:
  id: 1
  label: unconfigured
goal_state:
  id: 10
  label: configuring
---
start_state:
  id: 10
  label: configuring
goal_state:
  id: 2
  label: inactive
```
`ros2 lifecycle list managed_scan_node -a` prints the full state machine, useful for debugging. The short type `lifecycle_msgs/ChangeState` also works in `ros2 service call`.

## 3. Activate: it publishes
Inactive nodes create topics but do not publish. `ros2 topic echo /managed_scan` stays silent until:
```bash
ros2 lifecycle set /managed_scan_node activate
```

## Transition ids (`lifecycle_msgs/msg/Transition`)
| Id | Transition |
|---|---|
| 1 | `TRANSITION_CONFIGURE` |
| 2 | `TRANSITION_CLEANUP` |
| 3 | `TRANSITION_ACTIVATE` |
| 4 | `TRANSITION_DEACTIVATE` |
| 5 / 6 / 7 | shutdown from unconfigured / inactive / active |

## Results, stop, pause, restart, errors
- Each `on_*` returns `SUCCESS` (go to the requested state) or `FAILURE` (stay in the start state). `ERROR`, or an uncaught exception, goes to *ErrorProcessing* and calls `on_error`.
- `on_error` returning `SUCCESS` recovers to **unconfigured**; `FAILURE` (as in the example) or `ERROR` ends in **finalized**.
- Stop cleanly: `ros2 lifecycle set /managed_scan_node shutdown` calls `on_shutdown` from **any** primary state. A finalized node still appears in `ros2 node list` but can only be destroyed: it cannot come back.
- Pause: `deactivate` calls `on_deactivate`; the node must work again after `activate`.
- Restart from scratch: deactivate → cleanup (`on_cleanup` resets everything to the initial state) → configure → activate.

## Pitfalls
- `ros2 service call … change_state` with a transition that is not available from the current state returns `success: False`.
- Publishing only happens while **active**: an inactive node has its topics but sends nothing, which looks like a QoS or connection problem.
