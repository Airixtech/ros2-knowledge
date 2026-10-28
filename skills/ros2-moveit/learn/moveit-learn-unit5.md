---
id: moveit-learn-unit5
type: reference
owner: equipo-ros2
updated: 2026-10-28
review_by: 2027-04-26
source: manual
confidentiality: internal
title: "Unit 5 exercises: object detection, object pose client, filtering, pick and place with perception"
domain: moveit
area: learn
distro: humble
tested: false
audience: students
order: 4
summary: "Exercises 5.1-5.5: find_objects action server and RViz2 clouds, get_object_pose_action_client, several objects, box filter, pick and place with perception (no solution)."
tags: [course, exercises, unit 5, perception, simple_grasping, find_objects, get_object_pose_action_client, filter objects, pick and place with perception]
see: ["[[moveit-learn-unit4]]", "[[moveit-simple-grasping]]", "[[moveit-find-objects-action]]", "[[moveit-cpp-get-object-pose]]", "[[moveit-pick-and-place]]"]
requires: [ros2-core]
version_notes:
  - "course: exercise numbering repeats 5.2 and uses 5.1.2/5.1.3; 5.3 names get_pose_client.cpp for get_object_pose_action_client.cpp (MOVEIT-V45)"
---
# Unit 5: exercises

**TL;DR** Perception lets the robot interpret its surroundings from sensor data. For pick and place it answers "where exactly is the object?": unit 5 runs `simple_grasping` on the wrist depth camera, reads the object poses from a C++ action client, filters them, and ends with a pick and place that uses the detected pose.

| Exercise (course title) | Task | Note |
|---|---|---|
| 5.1 Verify the action server has been properly started | `basic_grasping_perception_node` with `debug_topics:=true`; `/find_objects`, `/object_cloud`, `/support_cloud` | [[moveit-find-objects-action]] |
| 5.2 Call the action server to ACTIVATE the object detection | `ros2 action send_goal /find_objects … "{plan_grasps: false}"`, read the result | [[moveit-find-objects-action]], [[moveit-grasping-msgs]] |
| 5.1.3 Visualize the detections in RViz2 | two `PointCloud2` displays with Best Effort; save `perception.rviz` | [[moveit-find-objects-action]] |
| 5.2 (package `get_object_pose_action_client`) | client node that sends the goal with `plan_grasps` false and prints the object's `[X, Y]` | [[moveit-cpp-get-object-pose]] |
| 5.3 | spawn `grasp_box2.urdf`; print type, dimensions and position of every object | [[moveit-cpp-filter-objects]], [[moveit-scene-grasp-boxes]] |
| 5.4 | keep only the box within 0.05 × 0.05 × 0.10 m | [[moveit-cpp-filter-objects]] |
| 5.5 | pick and place with perception (below) | this note |

The course numbers two exercises 5.2 and closes "Exercise 5.1.2"; exercise 5.3 says "update the code in `get_pose_client.cpp`", meaning `get_object_pose_action_client.cpp` (MOVEIT-V45).

## Exercise 5.5: pick and place with perception
The pick and place of unit 4 sends the robot to a hard-coded pose; in real scenarios you rarely know the pose of the objects. Update `pick_and_place_trajectory.cpp` ([[moveit-pick-and-place]]):
1. Add an action client that sends a goal to `/find_objects` to search the environment for objects ([[moveit-cpp-get-object-pose]]).
2. Take the pose of the object to pick and use it to send the end effector near the object, right before the approach motion.

The course gives no solution on purpose (it is a combination of this unit's client and the pick-and-place program); no solution is written here either. Things to keep from the notes: check that an object was found (MOVEIT-V08), use the pose of the selected object (MOVEIT-V09), and keep the gripper orientation of the pregrasp pose.
