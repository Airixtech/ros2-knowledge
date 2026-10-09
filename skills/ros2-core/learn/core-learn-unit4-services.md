---
id: core-learn-unit4-services
title: "Unit 4 exercises: services, custom srv, services quiz"
domain: core
area: learn
distro: humble
tested: false
audience: students
summary: "Course Unit 4: text-recognition node, Trigger server/client, custom TextRecognition.srv, services quiz (Turn.srv, /turn)."
tags: [course, unit 4, services, Trigger, custom srv, quiz, students]
see: ["[[core-srv-server]]", "[[core-srv-client-async]]", "[[core-iface-package]]"]
requires: []
version_notes: []
---
# Unit 4 exercises: services, custom srv, services quiz

**TL;DR** Build a text-recognition (OCR) node, expose it as a Trigger service, then as a custom service. The quiz is a `/turn` service with its own interface package. Reference: [[core-srv-server]], [[core-srv-client-async]], [[core-iface-package]].

## Unit 4 — Services
- **Ex 4.1** `text_recog_node.py` (entry point `text_recog_executable`): subscribe to `/leo/camera/image_raw` (depth 1) and run OCR with the provided `TextRecognition(east_model_path, 0.5, 320, 320, 0.0)` from `basic_ros2_extra_files/text_detector/text_recog.py`. `results = recognize_text(cv_image)` → list of `((start_x, start_y, end_x, end_y), text)`. Clean with `text.rstrip(".\n\x0c")`, and log the text + box. Model: `.../text_detector/frozen_east_text_detection.pb`.
- **Service server example** `mars_rover_status_s_server.py`: `Trigger` service `/get_robot_status` returns simulated battery/temperature/camera/motors in `message` (entry point `mars_rover_s_server_executable`).
- **Ex 4.2** `text_recog_s_server.py` (entry point `text_recog_s_server_executable`): Trigger service `/text_recognition_service`. `success=True` only if the last detected text is FOOD or WASTE; `message` = the detected text or "No text detected".
- **Client example** `mars_rover_status_s_client.py`: `create_client(Trigger, ...)`, `wait_for_service`, `call_async`, `spin_once` loop until `future.done()` ([[core-srv-client-async]]).
- **Ex 4.3** `text_recog_s_client.py` (entry point `text_recog_s_client_executable`) calls `/text_recognition_service` and logs success + text.
- **Custom srv** `custom_interfaces/srv/TextRecognition.srv`: `string label --- bool success, int32 start_x, start_y, end_x, end_y`.
- **Ex 4.4** `text_recog_s_server_custom.py` / `text_recog_s_client_custom.py` (entry points `..._custom_executable`), service `/text_recognition_service_custom`: success only if `request.label.upper()` equals the detected text; bbox, else all 0. The client requests "FOOD".
- **Services quiz**: interface pkg `services_quiz_srv` with only `Turn.srv` (`string direction`, `float64 angular_velocity`, `float64 time` `---` `bool success`). Pkg `services_quiz` with `turn_s_server.py` (service `/turn`: spin left/right at the given rad/s for the given s, then stop, return True) and `turn_s_client.py` (right, 0.2 rad/s, 10 s; must exit cleanly). Launches `services_quiz_server.launch.py` (server only) and `services_quiz_client.launch.py` (client only).
- Reset sim: `ros2 service call /reset_world std_srvs/srv/Empty {}`.
