---
id: nav2-learn-adv-unit1-features
title: "Advanced Unit 1: setup, Simple Commander demos, waypoints, costmap filters"
domain: nav2
area: learn
distro: humble
tested: false
audience: students
summary: "Advanced Unit 1: warehouse setup, picking and inspection demos, waypoint follower, keepout and speed filters."
tags: [course, students, advanced unit 1, nav2_pkgs, path_planner_server, navigation.launch.py, initialpose, nav2_new_features, navigate_to_pose.py, follow_waypoints.py]
see: ["[[nav2-learn-adv-start-here]]", "[[nav2-commander-picking-demo]]", "[[nav2-commander-inspection-demo]]", "[[nav2-waypoint-follower]]", "[[nav2-keepout-filter]]", "[[nav2-speed-filter]]"]
requires: [ros2-core]
version_notes: []
---
# Advanced Unit 1: setup, Simple Commander demos, waypoints, costmap filters

**TL;DR** Get Nav2 working in the warehouse, then run two Simple Commander demos and extend the navigation launch with the waypoint follower and the costmap filters. In this unit you explore essential methods for building a navigation robot application: `goToPose()`, `goThroughPoses()` and `followWaypoints()`. Understanding these functions allows you to develop more flexible and autonomous navigation behaviors ([[nav2-simple-commander]]).

## 1.2 Setup Nav2
For this unit you need a Nav2 system working correctly. Clone the course repository **`nav2_pkgs`** (branch `humble`, link given in the course) into `~/ros2_ws/src`, then compile and launch:
```bash
cd ~/ros2_ws/
colcon build
source install/setup.bash
ros2 launch path_planner_server navigation.launch.py
```
Set the robot's initial position with the RViz2 **2D Pose Estimate** tool, or programmatically, as you would mock it for a real system (in a new terminal):
```bash
ros2 topic pub --once /initialpose geometry_msgs/msg/PoseWithCovarianceStamped "{header: {stamp: {sec: 0}, frame_id: 'map'}, pose: {pose: {position: {x: 3.45, y: 2.15, z: 0.0}, orientation: {z: 1.0, w: 0.0}}}}"
```
The robot appears initialized at its position and the costmaps update in RViz2. Use the **Nav2 Goal** button to send a goal and play around. If at any time you end up in a bad state, close the application and relaunch it.

## 1.4 Demo: picking (navigate_to_pose.py)
Create the package **`nav2_new_features`** and the script ([[nav2-commander-picking-demo]]). Look at the code and identify where it uses the Simple Commander API and the expected robot behavior. Compile, launch the navigation system (no initial pose from RViz2 needed: the script sets it; reset the robot to its start pose if you moved it), then:
```bash
cd ~/ros2_ws/
colcon build
source install/setup.bash
ros2 launch path_planner_server navigation.launch.py
python3 ~/ros2_ws/src/nav2_new_features/scripts/navigate_to_pose.py
```

## 1.6 Waypoint following
Add the **FollowWaypoints** server to the launch ([[nav2-waypoint-follower]]), compile, and launch the navigation system. Take a moment to ensure you launched the **FollowWaypoints** server correctly: `ros2 action list` must show **`/follow_waypoints`**. Then run the inspection demo ([[nav2-commander-inspection-demo]]):
```bash
python3 ~/ros2_ws/src/nav2_new_features/scripts/follow_waypoints.py
```

## 1.8–1.9 Keepout zones and speed limits
Edit the map, create the mask YAML, configure the filters and add the two filter nodes ([[nav2-costmap-filters]], [[nav2-keepout-filter]], [[nav2-speed-filter]]). Send goals near the zones and watch the plans and the `/speed_limit` topic.

## Conclusions
You used the **Simple Commander API**, waypoint-based navigation with **FollowWaypoints**, **Keepout Zones** and **Speed Restricted Zones** to build a basic autonomous demo in a simulated warehouse.
