---
id: core-learn-unit7-actions
title: "Unit 7 exercises: actions, Nav2 goal, actions quiz"
domain: core
area: learn
distro: humble
tested: false
audience: students
summary: "Course Unit 7: Rotate action CLI, action client, GoToPose server over Nav2, custom action with timeout-cancel, actions quiz."
tags: [course, unit 7, actions, Nav2, GoToPose, quiz, students]
see: ["[[core-action-server]]", "[[core-action-client]]", "[[core-nav2-python-client]]", "[[core-action-cli-status]]"]
requires: []
version_notes: []
---
# Unit 7 exercises: actions, Nav2 goal, actions quiz

**TL;DR** Use an existing action from the CLI, write a client, then a server that forwards goals to Nav2, and finally add timeout-cancel. Reference: [[core-action-server]], [[core-action-client]], [[core-nav2-python-client]].

## Unit 7 — Actions (Leo rover, sim pkg `leo_description`)
- **Ex 7.1** `ros2 run leo_description rotate_action_server.py`; `ros2 action list` → `/rotate`; `ros2 action info /rotate -t` → `leo_description/action/Rotate` (`float64 rotation_time --- bool success --- float64 elapsed_time`); `ros2 action send_goal /rotate leo_description/action/Rotate "{rotation_time: 5.0}" -f`.
- **Ex 7.2** Pkg `my_action_client` (`--dependencies rclpy leo_description`), `action_client.py` with `ActionClient(self, Rotate, 'rotate')`, `send_goal_async(..., feedback_callback)` → `goal_response_callback` → `get_result_async` → `get_result_callback` (prints success, `rclpy.shutdown()`). Entry point `example72`; launch `example72_launch_file.launch.py`.
- **Ex 7.3** Pkg `my_action_server`: `action_server.py` exposes `/go_to_pose` (`GoToPose`: `float64 x, y, yaw --- bool success --- string feedback`). It waits for localization (`/initialpose` subscribers, `/amcl_pose` topic), publishes the initial pose (0,0,0) ×10, and in `async def execute_callback` awaits a Nav2 `NavigateToPose` goal ([[core-nav2-python-client]]). Run: `ros2 launch leo_description loc_nav.launch.py` (T1; tf "map does not exist" errors are normal until the initial pose), `ros2 run my_action_server action_server` (T2), `ros2 action send_goal /go_to_pose leo_description/action/GoToPose "{x: -8.0, y: 6.0, yaw: 1.57}"` (T3). A meteor blocks the path.
- **Custom action** `custom_interfaces/action/GoToPose.action` (same fields): CMake `rosidl_generate_interfaces(... "action/GoToPose.action")`, package.xml `<depend>action_msgs</depend>` + member_of_group ([[core-iface-package]]).
- **Ex 7.5** `custom_action_client.py` (entry point `example75`): goal (−8, 6, 1.57); a timer checks a 30 s timeout → `cancel_goal_async()`; the result callback distinguishes SUCCEEDED / ABORTED / CANCELED. `custom_action_server.py` (entry point `my_action_server`) adds a `cancel_callback` that forwards the cancel to the Nav2 goal and ends with `goal_handle.canceled()`. Server and client MUST import `GoToPose` from the same pkg (`custom_interfaces`). Build: `colcon build --packages-select my_action_server my_action_client custom_interfaces`.
- **Actions quiz**: clean the ws first (`rm -rf build install log`) + reset the sim. Interface pkg `actions_quiz_msg` with only `Distance.action` (`float64 x, y, yaw --- bool success, float64 distance_traveled --- float64 distance_left`). Pkg `actions_quiz` with the server (action `/distance_as`, navigate to the flag (8.3, −2.2, −0.2) via Nav2, publish `/distance_left` as the feedback topic and `/distance_traveled`, result success=True + total distance; use odom for distances) and the client. Launches `actions_quiz_server.launch.py`, `actions_quiz_client.launch.py`. Do not use `custom_interfaces`; `leo_description` is allowed.
- Project Part III: same course project.
