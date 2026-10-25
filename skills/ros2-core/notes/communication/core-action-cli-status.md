---
id: core-action-cli-status
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "Action CLI, GoalStatus codes & custom actions"
domain: core
area: communication
distro: humble
tested: false
audience: dev
summary: "ros2 action list/info/send_goal, cancel from CLI, GoalStatus codes, custom .action setup, when to choose an action."
tags: [ros2 action, send_goal, GoalStatus, custom action, action_msgs]
see: ["[[core-action-server]]", "[[core-action-client]]", "[[core-iface-package]]", "[[core-bp-comm-choice]]"]
requires: []
version_notes:
  - "jazzy: 'ros2 action type' sub-command added (absent in Humble) — https://docs.ros.org/en/rolling/Releases/Release-Jazzy-Jalisco.html (V78)"
---
# Action CLI, GoalStatus codes & custom actions

**TL;DR** Use an action for long, preemptable tasks with progress: navigate, rotate N s, pick & place, mapping. Under the hood it is 2 services (goal, result) + a feedback topic + a status topic. Without feedback, cancel or parallel work → a service. Fire-and-forget → a topic.

## CLI
```bash
ros2 action list [-t]
ros2 action info /rotate [-t]                      # clients/servers (+ type with -t)
ros2 interface show leo_description/action/Rotate  # goal --- result --- feedback
ros2 action send_goal /rotate leo_description/action/Rotate "{rotation_time: 5.0}"
ros2 action send_goal /fibonacci action_tutorials_interfaces/action/Fibonacci "{order: 10}" -f   # -f/--feedback
```
To cancel from the CLI, press Ctrl+C on `send_goal` (it cancels the goal). Types follow `<pkg>/action/<Name>`.
`ros2 action list` prints full names (`/rotate`). `ros2 action info /rotate -t` prints `Action: /rotate`, `Action clients: 0`, `Action servers: 1` and `/rotate_action_server [leo_description/action/Rotate]`. `send_goal` prints `Waiting for an action server to become available...`, `Sending goal:` with the values, `Goal accepted with ID: <id>`, the `Feedback:` blocks (only with `-f`), `Result:` and `Goal finished with status: SUCCEEDED`.
[≥Jazzy: `ros2 action type /fibonacci` prints the type. In Humble use `ros2 action list -t`.]

## GoalStatus codes (`action_msgs.msg.GoalStatus`)
UNKNOWN 0 · ACCEPTED 1 · EXECUTING 2 · CANCELING 3 · SUCCEEDED 4 · CANCELED 5 · ABORTED 6.

## Custom action interface
An `.action` file is goal `---` result `---` feedback. Add it to CMake with `rosidl_generate_interfaces(... "action/GoToPose.action")` and add `<depend>action_msgs</depend>` to package.xml ([[core-iface-package]]). In Python: `from pkg.action import GoToPose` → `GoToPose.Goal/Result/Feedback`. Client package dependencies at creation time: `--dependencies rclpy <iface_pkg>`.

## Pitfalls
- Client and server must use the same interface package.
- Always `wait_for_server()` before sending.
- Choosing between topic, service and action: [[core-bp-comm-choice]].
