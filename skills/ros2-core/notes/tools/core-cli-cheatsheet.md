---
id: core-cli-cheatsheet
title: "Master CLI cheat sheet & 'I want to...' index"
domain: core
area: tools
distro: humble
tested: false
audience: dev
summary: "One-page list of the most used ros2/colcon commands and a task→note reverse index; links to detailed notes."
tags: [cli, cheat sheet, ros2, colcon, ros2 control, ros2 component]
see: ["[[core-shell-workflow]]", "[[core-topic-cli]]", "[[core-debug-triage]]"]
requires: []
version_notes:
  - "jazzy: 'ros2 action type' added; 'ros2 control switch_controllers --start/--stop' removed (use --activate/--deactivate) — https://github.com/ros-controls/ros2_control/blob/jazzy/ros2controlcli/ros2controlcli/verb/switch_controllers.py (V62, V78)"
---
# Master CLI cheat sheet & "I want to..." index

**TL;DR** These commands cover about 90% of daily use. The details live in each linked note. If you are unsure of the verbs, run `ros2 <cmd> -h`, and press Tab twice to autocomplete pkgs, exes, topics and launch files.

## Top commands
```bash
ros2 node list | ros2 node info /n
ros2 topic list -t | ros2 topic info /t -v | ros2 topic echo /t [--once] | ros2 topic hz /t | ros2 topic bw /t
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.2}}"
ros2 interface show <pkg>/<msg|srv|action>/<Type> | ros2 interface proto <type>
ros2 service list -t | ros2 service call /s <type> "{...}"
ros2 action list -t | ros2 action send_goal /a <type> "{...}" -f
ros2 param list /n | get | set | dump | load
ros2 run <pkg> <exe> [--ros-args -r __ns:=/r1 -p k:=v --log-level debug]
ros2 launch <pkg> <file.launch.py> [arg:=v] [--show-args]
ros2 pkg list | executables <pkg> | prefix <pkg> | create ...
colcon build --symlink-install --packages-select <pkg> && source install/setup.bash
ros2 lifecycle get|set|list /n
ros2 bag record -a -o name | ros2 bag play name [--clock -l -r 2]
ros2 run tf2_tools view_frames | ros2 run tf2_ros tf2_echo map base_link
ros2 doctor [--report] | rqt_graph | rviz2
ros2 component list | ros2 component load /container <pkg> <ns::Class> -e use_intra_process_comms:=true
ros2 control list_controllers | list_hardware_interfaces | switch_controllers --activate X --deactivate Y
```
[≥Jazzy: `ros2 action type /a`; `switch_controllers --start/--stop` (deprecated aliases in Humble) removed]

## Reverse index: "I want to…"
| Task | Note |
|---|---|
| build one pkg fast | [[core-colcon-build]] |
| inspect/echo/publish a topic | [[core-topic-cli]] |
| rename/remap/namespace a node at run | [[core-ros-args]] |
| change params at runtime | [[core-param-yaml-cli]] |
| start many nodes | [[core-launch-basics]] |
| record/replay data | [[core-bag-record]], [[core-bag-play]] |
| frames / transforms | [[core-tf-basics]] |
| robot model | [[core-urdf-basics]] |
| callbacks blocked / parallel | [[core-exec-model]] |
| no messages arriving | [[core-qos-usage]], [[core-debug-triage]] |
| python/C++ templates | [[core-node-skeleton]], [[core-topic-pub-sub-py]], [[core-srv-server]], [[core-action-server]] |

## Resources
docs.ros.org/en/humble · index.ros.org (packages) · discourse.ros.org · robotics.stackexchange.com · docs.nav2.org · moveit.picknik.ai/humble · control.ros.org/humble
