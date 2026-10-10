---
id: nav2-multirobot-mapping
title: "Multi-robot mapping: one robot maps, one shared map_server"
domain: nav2
area: multi-robot
distro: humble
tested: false
audience: dev
summary: "Map with one namespaced robot (cartographer_multi.lua frames, topic remappings), save the map, erase the other robot from it; one map_server for all."
tags: [multi-robot, cartographer_multi.lua, multi_cartographer.launch.py, remappings, map_saver_cli, GIMP, pgm, shared map_server]
see: ["[[nav2-cartographer-lua]]", "[[nav2-cartographer-launch]]", "[[nav2-map-saver]]", "[[nav2-multirobot-localization]]"]
requires: [ros2-core]
version_notes:
  - "humble: same cartographer_ros executables in all three distros — https://github.com/ros2/cartographer_ros/blob/ros2/cartographer_ros/CMakeLists.txt (NAV2-V37)"
---
# Multi-robot mapping: one robot maps, one shared map_server

**TL;DR** Every robot gets its own full navigation system (localization, planner, controller, bt_navigator…), except the **map server: one for all robots**, since they share the map. Build the map with one robot of the fleet, save it, and serve it once. Collaborative multi-robot mapping is a more complex subject, not covered here.

## 1. Cartographer for robot tb3_0
`config/cartographer_multi.lua`: same content as [[nav2-cartographer-lua]] except the frames of `tb3_0`:
```lua
  tracking_frame = "tb3_0/base_footprint",
  published_frame = "tb3_0/odom",
  odom_frame = "tb3_0/odom",
```
`launch/multi_cartographer.launch.py`: same as [[nav2-cartographer-launch]] with `configuration_basename = 'cartographer_multi.lua'` and, in the `cartographer_node`, remappings to the robot's topics (Cartographer's topic names are fixed):
```python
            remappings=[('/cmd_vel', '/tb3_0/cmd_vel'), ('/odom', '/tb3_0/odom'), ('/scan', '/tb3_0/scan'),],
```

## 2. Map with tb3_0
```bash
cd ~/ros2_ws
source install/setup.bash
colcon build
source install/setup.bash
ros2 launch cartographer_slam multi_cartographer.launch.py
```
```bash
rviz2 -d ~/ros2_ws/src/cartographer_slam/rviz/cartographer.rviz
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args --remap cmd_vel:=/tb3_0/cmd_vel
```
Use the RViz config from the mapping unit; robot models not showing does not matter yet ([[nav2-multirobot-rviz]]).

## 3. Save it where the map server reads it
```bash
cd ~/ros2_ws/src/map_server/config
ros2 run nav2_map_server map_saver_cli -f turtlebot_area_two_robots
```
Then stop Cartographer.

## 4. Erase the other robot from the map
The second robot was mapped as an **obstacle** in the new map. The robots then think there is an obstacle where there is none, and the robot standing on that spot believes it is in collision and does not move. Edit the `.pgm` (e.g. with GIMP) to paint that spot free, and save the result under a new name, `turtlebot_area_two_robots_clean` (`.pgm` + `.yaml`), to avoid confusion with the original. The course also provides this clean map in its extra-material repository (link given in the course): copy `nav_maps/turtlebot_area_two_robots_clean.pgm` and `.yaml` into `map_server/config`.

## Pitfalls
- Teleop without the remap drives nothing (`/cmd_vel` has no subscriber).
- Forgetting to rebuild after saving the map into `src/…/config` → the map server loads the old installed files.
