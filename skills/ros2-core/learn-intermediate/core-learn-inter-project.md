---
id: core-learn-inter-project
type: reference
owner: equipo-ros2
updated: 2026-10-14
review_by: 2027-04-12
source: manual
confidentiality: internal
title: "Intermediate final project: detect circles and drive to the closest"
domain: core
area: learn-intermediate
distro: humble
tested: false
audience: students
summary: "Final project: laser circle detection, RViz marker for the closest circle within 5 m, service that drives the robot there."
tags: [course, final project, ros2_intermediate_project, circle detection, RViz marker, search_and_go_to_closest_circle, go_to_position, multithreading, students]
see: ["[[core-recipe-laser-circles]]", "[[core-learn-inter-unit6-groups-demo]]", "[[core-tf-listener]]", "[[core-exec-callback-groups]]"]
requires: []
version_notes: []
---
# Intermediate final project: detect circles and drive to the closest

**TL;DR** About 8 hours. Create the package `ros2_intermediate_project` with the dependencies used so far, then three parts: a circle-detection class (given), two detection nodes in one multithreaded script, and a movement node with a service that sends the robot to the closest circle.

## 1. Environment
- New package `ros2_intermediate_project`; add every dependency you have used in the course.

## 2. Shape detection class
`laser_data_processing.py` (given) detects circles in a `LaserScan` and returns the center (x, y) and radius of each: [[core-recipe-laser-circles]].

## 3. Detection nodes
- With that class, one node detects circles with the laser and passes them to a second node that publishes an RViz marker per detection.
- Restrictions: both nodes in the same Python script; use multithreading ([[core-exec-callback-groups]]); reuse as much code as possible; publish only the **closest** circle when several are detected; ignore circles farther than **5.0 m**.

## 4. Movement node
- A new node that sends the closest circle center to the robot so that it moves there.
- Restrictions: reuse code; a service server `search_and_go_to_closest_circle` (`std_srvs/Empty`) that triggers the move to the closest circle within 5.0 m; subscribe to `/circles` for the closest circle; a service client of `go_to_position` that receives the position.
- Hint: `base_link` and `lidar_1_link` do not have the same orientation: transform the detected center before sending it ([[core-tf-listener]]).

## Pitfalls
- Plotting (`plot_debug=True`) inside a ROS callback blocks the node: keep it off.
- Without a dedicated thread and group, the service that waits for the move blocks the subscriber that receives new circles.
