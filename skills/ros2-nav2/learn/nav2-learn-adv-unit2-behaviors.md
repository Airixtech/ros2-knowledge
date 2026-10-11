---
id: nav2-learn-adv-unit2-behaviors
type: reference
owner: equipo-ros2
updated: 2026-10-10
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "Advanced Unit 2 exercise: abort on low battery behavior tree"
domain: nav2
area: learn
distro: humble
tested: false
audience: students
summary: "Advanced Unit 2: behavior trees in bt_navigator and recoveries; exercise E2.1 abort_when_low_battery.xml with IsBatteryLow, battery topic /battery, map neobotix_area.yaml."
tags: [course, students, advanced unit 2, exercise E2.1, abort_when_low_battery.xml, IsBatteryLow, Inverter, /battery, neobotix_area.yaml, behavior trees]
see: ["[[nav2-bt-battery-abort]]", "[[nav2-bt-control-nodes]]", "[[nav2-bt-action-nodes]]", "[[nav2-recovery-flow]]", "[[nav2-learn-adv-start-here]]"]
requires: [ros2-core]
version_notes: []
---
# Advanced Unit 2 exercise: abort on low battery behavior tree

**TL;DR** Unit 2 explains how **behavior trees** are integrated into Nav2 to control the robot's navigation, both for standard goal-directed navigation and when the robot meets obstacles or errors ([[nav2-bt-control-nodes]], [[nav2-bt-action-nodes]], [[nav2-recovery-flow]]). A general behavior trees course or the [BehaviorTree.CPP documentation](https://www.behaviortree.dev/) is a good refresher.

## Exercise E2.1
Create a new behavior file named **`abort_when_low_battery.xml`** that does the following:
- Whenever a new goal destination is provided, the robot travels to that goal.
- If the battery is below **25 %** at any point, abort the current goal.
- Call the battery topic **`/battery`**. Publish on that topic a 100 % battery status.
- At some point, change the value published on that topic to 20 %. The robot must change its behavior and abort its goal at that time.

**Note 1**
- Use `behavior.xml` as a template and modify it accordingly ([[nav2-behavior-tree-xml]]).
- Nav2 has a behavior node for battery status detection: `IsBatteryLow` ([IsBatteryLow docs](https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/configuration_guide/core_servers/bt_plugins/conditions/IsBatteryLow.md)).
- `IsBatteryLow` returns FAILURE when the battery level is OK (it checks "is the battery low?"), so use the `<Inverter>` node to negate that check.
- Publish on the battery topic with:
  ```bash
  ros2 topic pub /battery sensor_msgs/BatteryState '{voltage: 12.0, percentage: 1.0, power_supply_status: 3}'
  ```

**Note 2**
- Remove all the filters (keepout masks, speed limits…) created in Unit 1; you can also remove the waypoint follower action server.
- The environment changed: use the map **`neobotix_area.yaml`**:
  ```python
  map_file = os.path.join(get_package_share_directory('map_server'), 'maps', 'neobotix_area.yaml')
  ```

Solution and why it aborts only after six recovery rounds: [[nav2-bt-battery-abort]].

## Conclusions
Behavior trees let `bt_navigator` take decisions dynamically, both in standard navigation and in front of unexpected obstacles or errors.
