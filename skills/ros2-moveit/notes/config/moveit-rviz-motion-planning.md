---
id: moveit-rviz-motion-planning
type: reference
owner: equipo-ros2
updated: 2026-10-28
review_by: 2027-04-26
source: manual
confidentiality: internal
title: "Motion planning in RViz2: MotionPlanning panel, planning group, goal state, Plan vs Execute"
domain: moveit
area: config
distro: humble
tested: false
audience: dev
summary: "ros2 launch my_moveit_config move_group.launch.py + moveit_rviz.launch.py; Planning tab, planning group, goal state <random valid> or named pose, Plan, Execute."
tags: [RViz2, MotionPlanning, moveit_rviz.launch.py, move_group.launch.py, Planning tab, Planning Group, Goal State, random valid, Plan, Execute, Plan & Execute, named pose, home, open, close, ur_manipulator, gripper]
see: ["[[moveit-move-group-launch-sim]]", "[[moveit-setup-assistant-model]]", "[[moveit-cpp-move-group-interface]]", "[[moveit-learn-start-here]]"]
requires: [ros2-core]
version_notes:
  - "humble: 'You can start planning now!' printed by move_group; '<random valid>' entry of the start/goal state lists — https://github.com/moveit/moveit2/blob/humble/moveit_ros/visualization/motion_planning_rviz_plugin/src/motion_planning_frame.cpp (MOVEIT-V28)"
---
# Motion planning in RViz2

**TL;DR** Start the core of MoveIt (`move_group`), then RViz2 with the package's MoveIt configuration. In the MotionPlanning panel choose the planning group and a goal state, **Plan** (only shows the trajectory), then **Execute** (moves the robot), or **Plan & Execute** in one click.

## Launch (two terminals)
```bash
ros2 launch my_moveit_config move_group.launch.py
```
It ends with:
```
[move_group-1] You can start planning now!
```
```bash
source ~/ros2_ws/install/setup.bash
ros2 launch my_moveit_config moveit_rviz.launch.py
```
Both launch files come with the generated package. For a simulated robot `move_group` needs `use_sim_time` first, or Execute aborts ([[moveit-move-group-launch-sim]]).

## Plan and execute
1. Open the **Planning** tab of the MotionPlanning panel.
2. **Query → Planning Group**: `ur_manipulator` for the arm (`gripper` for the gripper).
3. **Goal State**: `<random valid>` (a random valid, collision-free state) or one of the named poses of the package (`home`; for the gripper `open` and `close`). The scene shows the goal pose.
4. **Commands → Plan**: MoveIt plans and shows the trajectory. It **does not move** the robot.
5. **Execute**: the robot (simulated or real) follows the planned trajectory. **Plan & Execute** does both.

The course's first demo does the same with a ready-made package (`test_moveit_config`): switch the Planning Group from `gripper` to `ur_manipulator`, choose Goal State `home`, click Plan & Execute ([[moveit-learn-start-here]]).

## Pitfalls
- Execute does nothing and the log says `Execution completed: ABORTED` → the sim-time problem ([[moveit-move-group-launch-sim]]) or a controller name that does not match ([[moveit-config-controllers-yaml]]).
- Source the workspace in every new terminal before launching the package's files.
