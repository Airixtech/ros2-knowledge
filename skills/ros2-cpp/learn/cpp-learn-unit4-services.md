---
id: cpp-learn-unit4-services
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "C++ unit 4: text recognition node, status and text servers and clients, custom srv, services quiz"
domain: cpp
area: learn
distro: humble
tested: false
audience: students
summary: "Course unit 4 in C++: text_recog_node, mars_rover_status server/client, text_recognition service, TextRecognition.srv, services quiz /turn with Turn.srv."
tags: [course, unit 4, services, mars_rover_tasks, get_robot_status, text_recognition_service, TextRecognition.srv, services_quiz, services_quiz_srv, Turn.srv, turn, students]
see: ["[[cpp-learn-start-here]]", "[[cpp-srv-server]]", "[[cpp-srv-client]]", "[[cpp-srv-custom]]", "[[core-learn-unit4-services]]"]
requires: [ros2-core]
version_notes: []
---
# C++ unit 4: services

**TL;DR** Unit 4 in C++ (the Python twin: [[core-learn-unit4-services]]). A service answers on demand: a face recognizer or a box-label reader runs only when a client asks, which saves computation and, between Mars and Earth, bandwidth. One server, many possible clients. Exact names below are graded.

## Examples and exercises (pkg `mars_rover_tasks`)
- **Example 4.1** `src/text_recog_node.cpp` → executable `text_recog_executable`, node `text_recognition_node`: subscribes to `/leo/camera/image_raw`, logs `Detected label: FOOD|WASTE` → [[cpp-recipe-text-labels]].
- **Example 4.2** `src/mars_rover_status_s_server.cpp` → `mars_rover_s_server_executable`, node `robot_status_service`, service `/get_robot_status` (`std_srvs/srv/Trigger`, random battery/temperature/camera/motor status) → [[cpp-srv-server]].
- **Exercise 4.1** `src/text_recog_s_server.cpp` → `text_recog_s_server_executable`, service `/text_recognition_service` (`Trigger`): `success` true when the text is `FOOD` or `WASTE`, `message` = the detected text. Test: `ros2 service call /text_recognition_service std_srvs/srv/Trigger "{}"` → `success=True, message='FOOD'`.
- **Client** `src/mars_rover_status_s_client.cpp` → `mars_rover_status_s_client_executable`, node `robot_status_client` → [[cpp-srv-client]].
- **Exercise 4.2** `src/text_recog_s_client.cpp` → `text_recog_s_client_executable` (node `text_recognition_client`): `Success: true, Detected text: FOOD`.
- **Sync vs async** (4.6) → [[cpp-srv-sync-async]].
- **Custom srv** (4.7): `custom_interfaces/srv/TextRecognition.srv` (`string label` → `bool success`, `int32 start_x/start_y/end_x/end_y`); steps: `srv` dir → file → CMakeLists → package.xml → build and source → use ([[core-iface-package]]).
- **Exercise 4.3** `src/text_recog_s_server_custom.cpp` / `src/text_recog_s_client_custom.cpp` → `text_recog_s_server_custom_executable` / `text_recog_s_client_custom_executable`, service `/text_recognition_service_custom`: success only when the requested label matches; the box is all 0 otherwise → [[cpp-srv-custom]].

## Services quiz
- Service `/turn` with the custom interface `Turn`, in a package `services_quiz_srv` that contains **only** `Turn.srv`:
```
string direction               # Direction to spin (right or left)
float64 angular_velocity       # Angular velocity in rad/s
float64 time                   # Time in seconds
---
bool success                   # Did it achieve it?
```
- Package `services_quiz` with `turn_s_server.cpp` and `turn_s_client.cpp` and the launch files `services_quiz_server.launch.py` (server only) and `services_quiz_client.launch.py` (client only).
- The server turns the robot `left` or `right` at `angular_velocity` rad/s for `time` s, then returns `success = true`.
- The client calls `/turn` with direction `right`, `0.2` rad/s, `10` s, and **must exit cleanly** after the movement and the response.
- Grading (in order, a failed step skips the rest): package exists → builds → custom interface created → server launch works → client launch works → the robot moves as requested.

## Checks
- `ros2 service list | grep <name>`, `ros2 service type <name>`, `ros2 interface proto <type>` before a `ros2 service call`.
- Source the workspace in every terminal after building `custom_interfaces`.
