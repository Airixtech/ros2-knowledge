---
id: core-learn-unit3-topics
type: reference
owner: equipo-ros2
updated: 2026-10-09
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "Unit 3 exercises: topics, obstacle avoidance, topics quiz"
domain: core
area: learn
distro: humble
tested: false
audience: students
summary: "Course Unit 3 (pkg mars_rover_tasks): laser subscriber, 6-sector detector, spiral publisher, plant detector, exploration, geofence, custom msg, topics quiz."
tags: [course, unit 3, mars_rover_tasks, topics, LaserScan, quiz, students]
see: ["[[core-topic-pub-sub-py]]", "[[core-recipe-laserscan]]", "[[core-recipe-odom-go-to-goal]]", "[[core-recipe-command-goals]]"]
requires: []
version_notes: []
---
# Unit 3 exercises: topics, obstacle avoidance, topics quiz

**TL;DR** Package `mars_rover_tasks` (deps: rclpy std_msgs sensor_msgs geometry_msgs nav_msgs). Reference code: [[core-topic-pub-sub-py]], [[core-recipe-laserscan]], [[core-recipe-odom-go-to-goal]], [[core-recipe-command-goals]], [[core-iface-package]].

## Unit 3 — Topics (pkg `mars_rover_tasks`)
- **Ex 3.1** Skeleton `subscriber_obstacle_detector.py`, node `obstacle_detector_node`, which logs "<name> Ready...", entry point `subscriber_obstacle_detector_executable`. Build with `--packages-select mars_rover_tasks`.
- **Subscriber**: `/laser_scan` (`sensor_msgs/LaserScan`, QoS RELIABLE depth 10) → log `min(msg.ranges)`.
- **Ex 3.2** 6-sector detector: 200 beams over 252°, indices right→left: Right_Rear 0–33, Right 34–66, Front_Right 67–100, Front_Left 101–133, Left 134–166, Left_Rear 167–199. Detection < 0.8 m. Log the per-sector minimum + the suggested action (priority front > sides > rear; both fronts → arbitrary turn). Solution pattern: [[core-recipe-laserscan]] "Sector minimums".
- **Publisher (Mission 2)** `publish_mars_rover_move.py`, node `move_rover_node`, publishes `/cmd_vel` Twist every 0.5 s (`linear.x=0.5`, `angular.z=0.5` → spiral), entry point `publish_mars_rover_move_executable`. Extra: publish a zero Twist on Ctrl+C ([[core-recipe-stop-and-wait]]).
- **Pub+Sub example** `plant_detector_node.py`: subscribe to `/leo/camera/image_raw` → cv_bridge → `PlantDetector(model_path).predict(rgb)` (>0.5 = plant) → publish `std_msgs/String` on `/plant_detector`. Entry point `image_plant_detector_executable`. Files: clone the course extra-files repository (`basic_ros2_extra_files`, link given in the course) into `~/ros2_ws/src`, then copy `plant_detector/plant_detector.py` into the module folder ([[core-recipe-cv-bridge]]).
- **Ex 3.3** `autonomous_exploration.py` (entry point `autonomous_exploration_executable`): laser sub + cmd_vel pub. Front obstacle → keep turning right (`turning` flag) until clear; side → forward 0.2 + turn away 0.3; rear/none → forward. On this rover, negative `angular.z` = right.
- **Ex 3.4** Add an `/odom` sub. If the distance from the origin is > 5.0 m → `returning_to_origin` (turn toward the origin when |yaw error| > 0.1 rad, else forward 0.5) until back inside. Pattern: [[core-recipe-odom-go-to-goal]] go-to-goal + geofence.
- **Mission 4 / Ex 3.6** Custom msg `custom_interfaces/msg/RoverEvents` (`std_msgs/String info`, `geometry_msgs/Pose rover_location`). The plant detector publishes it on `/mars_rover_events` only when a plant is detected, with the latest odom pose ([[core-iface-package]]).
- **Topics quiz**: pkg `topics_quiz` (deps rclpy sensor_msgs geometry_msgs nav_msgs std_msgs), script `topics_quiz.py`, node `topics_quiz_node`, launch `launch/topics_quiz.launch.py`. Subscribe to `/nasa_mission` (`std_msgs/String`): `Go-Home` → (0.0, 0.0); `Go-Pickup` → (−2.342, −2.432); tolerance 0.1 m; avoid obstacles; stop and wait at the goal; ignore the command if already there; optional status on `/mars_rover_status`; arrive within 90 s. Hints: `is_at_position()` using odom; `rclpy.spin_once(node)` before `spin` to read the initial pose. Pattern: [[core-recipe-command-goals]].
- **Project Part I**: course project (link given in the course).
