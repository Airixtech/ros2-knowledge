---
id: cpp-learn-unit7-actions
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "C++ unit 7: rotate action, my_action_client / my_action_server, GoToPose, timeout client, actions quiz"
domain: cpp
area: learn
distro: humble
tested: false
audience: students
summary: "Course unit 7 in C++: ros2 action CLI on /rotate, action client, Nav2 server, custom GoToPose with timeout, actions quiz."
tags: [course, unit 7, actions, rotate, leo_description, my_action_client, my_action_server, GoToPose, actions_quiz, actions_quiz_msg, Distance.action, distance_as, students]
see: ["[[cpp-learn-start-here]]", "[[cpp-action-client]]", "[[cpp-action-server]]", "[[cpp-action-nested-client]]", "[[cpp-action-custom-timeout]]", "[[core-learn-unit7-actions]]"]
requires: [ros2-core]
version_notes:
  - "course: ros2 action list is shown printing rotate; action names are fully qualified, it prints /rotate (as the later /go_to_pose list shows) — https://github.com/ros2/ros2cli/blob/humble/ros2action/ros2action/verb/list.py (CPP-V07)"
  - "course: the quiz says 'DO NOT use custom interfaces defined in external packages, such as custom_interfaces, you can just use leo_description' and also asks for the package actions_quiz_msg with Distance.action; the grader checks actions_quiz_msg (CPP-V16)"
---
# C++ unit 7: actions

**TL;DR** Unit 7 in C++ (the Python twin: [[core-learn-unit7-actions]]). Actions are for long tasks that need feedback and can be cancelled; they are built from services (goal, result) and topics (feedback). CLI first, then a client, a server that drives Nav2, a custom interface with a timeout client, and the quiz. Exact names are graded.

## Example 7.1: the `/rotate` action from the CLI
```bash
ros2 run leo_description rotate_action_server.py       # after sourcing the simulation workspace
ros2 action list                                        # /rotate (the course prints "rotate", CPP-V07)
ros2 action info /rotate -t                             # Action servers: 1  /rotate_action_server [leo_description/action/Rotate]
ros2 interface show leo_description/action/Rotate       # float64 rotation_time --- bool success --- float64 elapsed_time
ros2 action send_goal /rotate leo_description/action/Rotate "{rotation_time: 5.0}" -f
```
`ros2 action send_goal <action_name> <action_type> <values>`; `-f` (`--feedback`) prints every feedback (`elapsed_time: 3.19e-05` … `5.0254967212677`), then `Result: success: true` and `Goal finished with status: SUCCEEDED`; the server logs `Executing goal...` and `Rotation time reached`. Action types are `<pkg_name>/action/<interface_name>`, defined in the package's `action/` folder ([[core-action-cli-status]]).

## Exercises
- **Exercise 7.2**: pkg `my_action_client` (`rclcpp rclcpp_action leo_description`), `src/action_client.cpp`, executable `action_client_node`, launch `launch/example72_launch_file.launch.py`: the rover turns left for 5 s → [[cpp-action-client]].
- **Example 7.3**: pkg `my_action_server`, `src/action_server.cpp`, executable `action_server`, action `/go_to_pose` (`leo_description/action/GoToPose`) forwarding to Nav2 (`ros2 launch leo_description loc_nav.launch.py`; ResetSim first); goal `{x: -8.0, y: 6.0, yaw: 1.57}` → [[cpp-action-server]], [[cpp-action-nested-client]].
- **7.7–7.8**: `custom_interfaces/action/GoToPose.action`, `src/custom_action_client.cpp` → `custom_action_client_node` (30 s timeout + cancel), `src/custom_action_server.cpp` → `custom_action_server_node` → [[cpp-action-custom-timeout]].

## Actions quiz
- Package `actions_quiz_msg` with **only** the interface `Distance.action`:
```
float64 x
float64 y
float64 yaw
---
bool success
float64 distance_traveled
---
float64 distance_left
```
- Package `actions_quiz` with the C++ server and client and the launch files `actions_quiz_server.launch.py` and `actions_quiz_client.launch.py`. Action name `/distance_as`.
- The server sets the initial pose (0, 0, 0), sends Nav2 to the flag at `(8.3, -2.2, -0.2)` (Nav2 running: `ros2 launch leo_description loc_nav.launch.py`), publishes the distance left (from odometry) on `/distance_left` as feedback while navigating and the total distance traveled on `/distance_traveled`, and returns `success = True` with the total distance as result.
- The client calls `/distance_as` and logs: `Sending goal: x=8.3, y=-2.2, yaw=-0.2`, `Goal accepted by the action server.`, `Feedback: Distance left = 8.58 meters` … `0.20 meters`, `Action completed with success: True`, `Total distance traveled: 9.58 meters`, then exits cleanly.
- The quiz text also says not to use interfaces of external packages "such as `custom_interfaces`, you can just use `leo_description`": the graded interface is `actions_quiz_msg`'s `Distance.action`; `leo_description` is only the simulation (CPP-V16).
- Before submitting: clean the workspace (`rm -rf build install log` in `~/ros2_ws`), stop all programs, ResetSim. Grading (in order): package exists → compiles → the action interface compiles → the server starts from its launch file → the action is listed → the traveled distance is right.

## Topics, services or actions?
Use an action when a task needs progress feedback, a result at the end, and the caller keeps doing other work meanwhile (navigate while detecting faces). Without feedback → a service; without a result → a topic (publish a goal, report progress on a second topic). The course's rule of thumb: topics if you can, services if not, actions only if needed, except when a 50 Hz topic would cost more than an on-demand service or action ([[core-bp-comm-choice]]).
