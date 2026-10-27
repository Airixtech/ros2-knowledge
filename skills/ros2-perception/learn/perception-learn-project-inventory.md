---
id: perception-learn-project-inventory
type: reference
owner: equipo-ros2
updated: 2026-10-27
review_by: 2027-04-25
source: manual
confidentiality: internal
title: "Course project, part 2: YOLO detection with start/stop Trigger services, shelf counts, missing and misplaced items"
domain: perception
area: learn
distro: humble
tested: false
audience: students
order: 3
summary: "Inventory project part 2 spec: object_detection with start/stop Trigger services and ObjectCount, inventory_checking with head moves, expected stock, scenarios."
tags: [course project, inventory checking, object_detection.py, inventory_checking.py, Trigger, std_srvs, start_detection, stop_detection, ObjectCount, detected_object_count, excluded_objects, trajectory_sender.py, missing items, misplaced items]
see: ["[[perception-learn-project]]", "[[perception-learn-project-detection-solution]]", "[[perception-learn-project-inventory-solution]]", "[[perception-yolo-object-detection]]", "[[core-srv-server]]"]
requires: [ros2-core]
version_notes:
  - "humble: std_srvs/Trigger = empty request, `bool success`, `string message` — https://github.com/ros2/common_interfaces/blob/humble/std_srvs/srv/Trigger.srv (PERC-V01, PERC-V42)"
  - "course solution: the excluded classes also include 'chair' (PERC-V43)"
---
# Course project, part 2: inventory checking (spec)

**TL;DR** At the AOI, detect the shelf items with YOLOv8 in two passes (upper shelf, lower shelf), controlled by two `Trigger` services; sum the counts, then report missing and misplaced items against the expected stock of that AOI. Solutions: [[perception-learn-project-detection-solution]], [[perception-learn-project-inventory-solution]].

## The pipeline
Once at an AOI, the robot recognizes and counts the items on the shelf (food and electronic devices) with the perception techniques of the course. It must: **do a total inventory count**, **check for missing items**, **check for misplaced items**. First an **object detection** node with YOLOv8, then an **inventory checking** node that uses it twice (upper and lower shelf).

## 7.5.1 `object_detection.py`
- Template: the unit 6 detection node ([[perception-yolo-object-detection]]); the `yolov8n.pt` model goes to `~/ros2_ws/src/final_project/data/yolov8n.pt`.
- Two detections must be **controlled**: two services start and stop the detection, of type `std_srvs/Trigger` (a request with no fields; a response with `bool success` and `string message`; typical for toggling a process) ([[core-srv-server]]).
- Fewer detection errors: filter unwanted detections, `excluded_objects = ['dining table', 'keyboard', 'umbrella', 'remote']`, and drop `cell phone` boxes **lower than 100 pixels** (often misinterpreted).
- Three publishers: `self.yolov8_pub` (the unit 6 message `Yolov8Inference`), `self.img_pub` (`Image`), `self.object_count_pub` (`ObjectCount` on `/detected_object_count`: `header`, `string[] classes`, `int32[] counts`, [[perception-custom-msgs]]).
- One subscriber `self.img_sub` (the camera); two services `self.start_service` (starts detection) and `self.stop_service` (stops it).

## 7.5.2 `inventory_checking.py`
- Split the problem in **two detections**, upper and lower shelf; move the head with the given action-client script `trajectory_sender.py`, on the joints `deepmind_robot1_head_base_joint` and `deepmind_robot1_head_joint`.
- Flow: head up to the upper shelf → start detection (service of `object_detection.py`) → wait for it and store `self.upper_count` (a dict of counts per object type) → stop detection → head down to the lower shelf → start → store `self.lower_count` → stop → total count and inventory status (missing or misplaced items).
- Two subscribers: `self.object_count_sub` (`/detected_object_count`) and `self.aoi_choice_sub` (`String` on `/aoi_choice`): each AOI has its own expected stock.

Full stock: at the **yellow or green** AOI, **8 cell phones and 4 laptops**; at the blue or red AOI, **6 bananas and 4 pizzas**. The simulation has missing and misplaced items on purpose, to test the node.

## Expected results
Scenario 1, nothing missing or misplaced (blue AOI):
```text
[INFO] [1718.1905032] [inventory_checking_node]: Total inventory count: {'banana': 6, 'pizza': 4}
[INFO] [1718.1911435] [inventory_checking_node]: Lets check the inventory:
[INFO] [1718.1917640] [inventory_checking_node]: No missing items.
[INFO] [1718.1923650] [inventory_checking_node]: No misplaced items.
```
Scenario 2, missing items, nothing misplaced (yellow AOI):
```text
[INFO] [1718.3658203] [inventory_checking_node]: Total inventory count: {'cell phone': 5, 'laptop': 2}
[INFO] [1718.3662820] [inventory_checking_node]: Lets check the inventory:
[INFO] [1718.3666678] [inventory_checking_node]: Missing items: {'cell phone': 3, 'laptop': 2}
[INFO] [1718.3670482] [inventory_checking_node]: No misplaced items.
```
Scenario 3, missing and misplaced items (red AOI):
```text
[INFO] [1718.5570715] [inventory_checking_node]: Total inventory count: {'banana': 5, 'cell phone': 1, 'pizza': 3}
[INFO] [1718.5576096] [inventory_checking_node]: Lets check the inventory:
[INFO] [1718.5630978] [inventory_checking_node]: Missing items: {'banana': 1, 'pizza': 1}
[INFO] [1718.5638198] [inventory_checking_node]: Misplaced items: {'cell phone': 1}
```
The course gives its solutions in a repository (link in the course) and asks to use them only when really stuck.
